from agent_tools import cancel_order, get_order_status
from ollama_agent import run_ollama_agent
from database import get_database_connection

def run_agent(input_text, agent_version_id):

    if agent_version_id == 4:
        return run_ollama_agent(
            input_text,
            "qwen3.5:4b"
        )

    if agent_version_id == 5:
        return run_ollama_agent(
            input_text,
            "qwen3:1.7b"
        )

    if agent_version_id == 3 and input_text == "Cancel Order #789":
        tool_result = get_order_status(789)

        return {
            "output": "Order cancelled successfully",
            "tool_calls": [
                {
                    "tool": "get_order_status",
                    "arguments": {
                        "order_id": 789
                    },
                    "result": tool_result
                }
            ]
        }

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

    if agent_version_id >= 2:
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


    if agent_version_id >= 4:

        connection = get_database_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT provider, model_name
            FROM agent_versions
            WHERE id = ?
            """,
            (agent_version_id,)
        )

        agent_metadata = cursor.fetchone()

        connection.close()

        if agent_metadata is not None:
            provider = agent_metadata[0]
            model_name = agent_metadata[1]

            if provider == "ollama":
                return run_ollama_agent(
                    input_text,
                    model_name
                )

    return {
        "output": "I don't know how to handle that request",
        "tool_calls": []
    }   