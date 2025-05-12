from agent_controller import AgentController
import gradio as gr

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
dc = AgentController()

def chat_fn(user_message: str):
    """
    Gradio function: takes a user message string,
    wraps it into the expected input format, calls the controller,
    and returns a string to display.
    """
    input_payload = {"input": {"messages": [{"role": "user", "content": user_message}]}}
    result = dc.get_response(input_payload)
    # If the result is a dict with a 'response' key, extract it; else stringify
    if isinstance(result, dict) and "response" in result:
        return result["response"]
    return str(result)

# Build Gradio interface
iface = gr.Interface(
    fn=chat_fn,
    inputs=gr.Textbox(lines=2, placeholder="Enter your message here...", label="User Message"),
    outputs=gr.Textbox(lines=5, label="Agent Response"),
    title="Coffee Shop Chatbot AI",
    description="Interact with the multi-agent system via Gradio"
)

if __name__ == "__main__":
    iface.launch()

