from agent_controller import AgentController

def main():
    controller = AgentController()

    # Example input format expected by `get_response`
    input_data = {
        "input": {
            "messages": [
                {"role": "user", "content": "Give me the best coffee in your shop for a romantic dinner"}
            ]
        }
    }

    response = controller.get_response(input_data)
    print(response)

if __name__ == "__main__":
    main()
