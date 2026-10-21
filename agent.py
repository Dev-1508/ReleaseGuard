from agent_tools import cancel_order, get_order_status


def run_agent(input_text, agent_version_id):
    if input_text == "Cancel Order #123":
        tool_result = cancel_order(123)

        return {
            "output": "Order cancelled successfully",
            "tool_calls": [
                {
                    "tool": "cancel_order",
                    "arguments": {
                        "order_id": 123
                    },
                    "result": tool_result
                }
            ]
        }

    if agent_version_id == 2:
        if input_text == "Where is order #456":
            tool_result = get_order_status(456)

            return {
                "output": "Order #456 is currently in transit",
                "tool_calls": [
                    {
                        "tool": "get_order_status",
                        "arguments": {
                            "order_id": 456
                        },
                        "result": tool_result
                    }
                ]
            }

    return {
        "output": "I don't know how to handle that request",
        "tool_calls": []
    }   