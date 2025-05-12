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

class GuardAgent():
    def __init__(self):
        self.client = Together(
            api_key=os.getenv("TOGETHER_API_KEY"),
            
        )
        self.model_name = os.getenv("MODEL_NAME")
    
    
    def get_response(self,messages):
        messages = deepcopy(messages)

        system_prompt = """
            You are a helpful AI assistant for a coffee shop application which serves drinks and pastries.
            Your task is to determine whether the user is asking something relevant to the coffee shop or not.
            The user is allowed to:
            1. Ask questions about the coffee shop, like location, working hours, menue items and coffee shop related questions.
            2. Ask questions about menue items, they can ask for ingredients in an item and more details about the item.
            3. Make an order.
            4. ASk about recommendations of what to buy.

            The user is NOT allowed to:
            1. Ask questions about anything else other than our coffee shop.
            2. Ask questions about the staff or how to make a certain menue item.

            Your output should be in a structured json format like so. each key is a string and each value is a string. Make sure to follow the format exactly:
            {
            "chain of thought": go over each of the points above and make see if the message lies under this point or not. Then you write some your thoughts about what point is this input relevant to.
            "decision": "allowed" or "not allowed". Pick one of those. and only write the word.
            "message": leave the message empty if it's allowed, otherwise write "Sorry, I can't help with that. Can I help you with your order?"
            }
            """
        
        input_messages = [{"role": "system", "content": system_prompt}] + messages[-3:]

        chatbot_output =get_chatbot_response(self.client,self.model_name,input_messages)
        
        print("Raw chatbot output:", repr(chatbot_output))  # Debug print

            # Extract clean JSON from the response
        clean_output = extract_json_from_output(chatbot_output)

        output = self.postprocess(clean_output)
        
        return output

    def postprocess(self, output):
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
            "memory": {
                "agent": "guard_agent",
                "guard_decision": parsed['decision']
            }
        }
        return dict_output




    
