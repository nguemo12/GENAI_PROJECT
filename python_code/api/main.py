# from agent_controller import AgentController
# import gradio as gr

# def main():
#     controller = AgentController()

#     # Example input format expected by `get_response`
#     input_data = {
#         "input": {
#             "messages": [
#                 {"role": "user", "content": "Give me the best coffee in your shop for a romantic dinner"}
#             ]
#         }
#     }

#     response = controller.get_response(input_data)
#     print(response)

# if __name__ == "__main__":
#     main()
# # dc = AgentController()

# # def chat_fn(user_message: str):
# #     """
# #     Gradio function: takes a user message string,
# #     wraps it into the expected input format, calls the controller,
# #     and returns a string to display.
# #     """
# #     input_payload = {"input": {"messages": [{"role": "user", "content": user_message}]}}
# #     result = dc.get_response(input_payload)
# #     # If the result is a dict with a 'response' key, extract it; else stringify
# #     if isinstance(result, dict) and "response" in result:
# #         return result["response"]
# #     return str(result)

# # # Build Gradio interface
# # iface = gr.Interface(
# #     fn=chat_fn,
# #     inputs=gr.Textbox(lines=2, placeholder="Enter your message here...", label="User Message"),
# #     outputs=gr.Textbox(lines=5, label="Agent Response"),
# #     title="Coffee Shop Chatbot AI",
# #     description="Interact with the multi-agent system via Gradio"
# # )

# # if __name__ == "__main__":
# #     iface.launch()

# backend/app.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
from agent_controller import AgentController
import uvicorn

app = FastAPI(title="Agent Controller API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the controller
controller = AgentController()

# Pydantic models for request/response
class Message(BaseModel):
    role: str
    content: str

class ChatInput(BaseModel):
    messages: List[Message]

class ChatRequest(BaseModel):
    input: ChatInput

class ChatResponse(BaseModel):
    response: Any
    status: str = "success"

@app.get("/")
async def root():
    return {"message": "Agent Controller API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        # Convert the request to the format expected by AgentController
        input_data = {
            "input": {
                "messages": [
                    {"role": msg.role, "content": msg.content} 
                    for msg in request.input.messages
                ]
            }
        }
        
        # Get response from the controller
        response = controller.get_response(input_data)
        
        return ChatResponse(response=response)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.post("/simple-chat")
async def simple_chat(message: str):
    """Simplified endpoint that takes just a message string"""
    try:
        input_data = {
            "input": {
                "messages": [
                    {"role": "user", "content": message}
                ]
            }
        }
        
        response = controller.get_response(input_data)
        return {"response": response, "status": "success"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )
