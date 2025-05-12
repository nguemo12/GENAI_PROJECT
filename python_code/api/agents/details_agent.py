from dotenv import load_dotenv
import os
from .utils import get_chatbot_response, get_embedding
from openai import OpenAI
from copy import deepcopy
from pinecone import Pinecone
from together import Together
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class DetailsAgent():
    def __init__(self):
        try:
            # Initialize Together API client
            self.client = Together(
                api_key=os.getenv("TOGETHER_API_KEY"),
            )
            
            # Initialize the embedding client
            self.embedding_client = Together(
                api_key=os.getenv("TOGETHER_API_KEY"),
            )
            
            # Get model names from environment variables
            self.chat_model_name = os.getenv("MODEL_NAME")
            self.embedding_model_name = os.getenv("EMBEDDING_MODEL_NAME", self.chat_model_name)
            
            # Initialize Pinecone client
            self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
            self.index_name = os.getenv("PINECONE_INDEX_NAME")
            
            # Check if index exists before initializing
            try:
                # List available indexes
                indexes = self.pc.list_indexes()
                logger.info(f"Available indexes: {indexes}")
                
                if not indexes or self.index_name not in [idx['name'] for idx in indexes]:
                    raise ValueError(f"Index '{self.index_name}' not found in Pinecone. Available indexes: {[idx['name'] for idx in indexes]}")
                
                self.index = self.pc.Index(self.index_name)
                logger.info(f"DetailsAgent initialized with index: {self.index_name}")
            except Exception as e:
                logger.error(f"Error initializing Pinecone index: {str(e)}")
                raise ValueError(f"Failed to initialize Pinecone index. Please check your index name and API key. Error: {str(e)}")
        except Exception as e:
            logger.error(f"Error initializing DetailsAgent: {str(e)}")
            raise

    def get_closest_results(self, input_embeddings, top_k=2):
        try:
            results = self.index.query(
                vector=input_embeddings,
                top_k=top_k,
                include_metadata=True
            )
            
            return results
        except Exception as e:
            logger.error(f"Error in get_closest_results: {str(e)}")
            return {"matches": []}

    def get_response(self, messages):
        try:
            # Check if Pinecone index is properly initialized
            if not hasattr(self, 'index'):
                return {
                    "role": "assistant",
                    "content": "I apologize, but I'm unable to access the knowledge base. The Pinecone index is not properly configured.",
                    "memory": {"agent": "details_agent", "error": "Pinecone index not initialized"}
                }
                
            messages = deepcopy(messages)
            
            # Get the latest user message
            user_message = messages[-1]['content']
            
            # Get embedding for the user's message
            embedding = get_embedding(self.embedding_client, self.embedding_model_name, user_message)
            
            # If embedding is a list with one item containing the vector
            if isinstance(embedding, list) and len(embedding) > 0:
                embedding = embedding[0]
            
            # Query Pinecone for similar documents
            result = self.get_closest_results(embedding, top_k=2)
            
            # Extract relevant information from the results
            if 'matches' in result and result['matches']:
                source_knowledge = "\n".join([x['metadata']['text'].strip()+'\n' for x in result['matches']])
            else:
                source_knowledge = "No relevant information found."
            
            # Construct the prompt with the retrieved information
            prompt = f"""
            Using the contexts below, answer the query.
            
            Contexts:
            {source_knowledge}
            
            Query: {user_message}
            """
            
            # System prompt for the coffee shop assistant
            system_prompt = """You are a customer support agent for a coffee shop called Merry's way. You should answer every question as if you are waiter and provide the necessary information to the user regarding their orders"""
            
            # Replace the user message with the constructed prompt
            messages[-1]['content'] = prompt
            
            # Use the last few messages to maintain context
            input_messages = [{"role": "system", "content": system_prompt}] + messages[-3:]
            
            # Get response from the chatbot
            chatbot_output = get_chatbot_response(self.client, self.chat_model_name, input_messages)
            
            # Process and return the output
            output = self.postprocess(chatbot_output)
            return output
            
        except Exception as e:
            logger.error(f"Error in get_response: {str(e)}")
            return {
                "role": "assistant",
                "content": "I apologize, but I'm having trouble processing your request right now. Please try again.",
                "memory": {"agent": "details_agent", "error": str(e)}
            }

    def postprocess(self, output):
        return {
            "role": "assistant",
            "content": output,
            "memory": {"agent": "details_agent"}
        }