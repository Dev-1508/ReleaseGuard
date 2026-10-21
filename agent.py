from agent_tools import cancel_order, get_order_status


def run_agent(input_text, agent_version_id):
    if input_text.startswith("Cancel Order #"):
        order_id = int(input_text.split("#")[1])

        tool_result = cancel_order(order_id)

        return {
            "output": "Order cancelled successfully",
            "tool_calls": [
                {
                    "tool": "cancel_order",
                    "arguments": {
                        "order_id": order_id
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