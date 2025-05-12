from dotenv import load_dotenv
import os
import json
from copy import deepcopy
from .utils import get_chatbot_response
from openai import OpenAI
from together import Together
load_dotenv()
import re
def extract_json_from_output(output):
        """
        Extract the first valid JSON object from the model output.
        Strips any leading non-JSON text.
        """
        match = re.search(r'\{.*\}', output, re.DOTALL)  # Search for a JSON object
        if match:
            return match.group(0)  # Return the first match
        raise ValueError("No JSON object found in the model output.")


class ClassificationAgent():
    def __init__(self):
        self.client = Together(
            api_key=os.getenv("TOGETHER_API_KEY"),
            
        )
        self.model_name = os.getenv("MODEL_NAME")
    
    def get_response(self,messages):
        messages = deepcopy(messages)

        system_prompt = """
            You are a helpful AI assistant for a coffee shop application.
            Your task is to determine what agent should handle the user input. You have 3 agents to choose from:
            1. details_agent: This agent is responsible for answering questions about the coffee shop, like location, delivery places, working hours, details about menue items. Or listing items in the menu items. Or by asking what we have.
            2. order_taking_agent: This agent is responsible for taking orders from the user. It's responsible to have a conversation with the user about the order untill it's complete.
            3. recommendation_agent: This agent is responsible for giving recommendations to the user about what to buy. If the user asks for a recommendation, this agent should be used.

            Your output should be in a structured json format like so. each key is a string and each value is a string. Make sure to follow the format exactly:
            {
            "chain of thought": go over each of the agents above and write some your thoughts about what agent is this input relevant to.
            "decision": "details_agent" or "order_taking_agent" or "recommendation_agent". Pick one of those. and only write the word.
            "message": leave the message empty.
            }
            """
        
        input_messages = [{"role": "system", "content": system_prompt}] + messages[-3:]

        chatbot_output =get_chatbot_response(self.client,self.model_name,input_messages)
        
        print("Raw chatbot output:", repr(chatbot_output))  # Debug print

            # Extract clean JSON from the response
        clean_output = extract_json_from_output(chatbot_output)

        output = self.postprocess(clean_output)
        
        return output

    def postprocess(self,output):
        if not output:
            raise ValueError("Empty chatbot output. Cannot parse as JSON.")

        try:
            parsed = json.loads(output)
        except json.JSONDecodeError as e:
            print("Invalid JSON output received:")
            print("Raw output:", repr(output))
            raise e

        dict_output = {
            "role": "assistant",
            "content": parsed['message'],
            "memory": {"agent":"classification_agent",
                       "classification_decision": parsed['decision']
                      }
        }
        return dict_output

    
