def run_agent(input_text, agent_version_id):
    if input_text == "Cancel Order #123":
        return "Order cancelled successfully"

    if agent_version_id == 2:
        if input_text == "Where is order #456":
            return "Order #456 is currently in transit"

    return "I don't know how to handle that request"