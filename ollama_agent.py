from ollama import chat

from agent_tools import cancel_order, get_order_status


def run_ollama_agent(input_text):

    messages = [
        {
            "role": "system",
            "content": (
                "You are a customer support agent. "
                "Use the available tools when necessary."
                "When you use a tool, base your answer only on the information returned by that tool."
                "Do not invent additional information."
                "Return the tool result exactly as your final answer"
            )
        },
        {
            "role": "user",
            "content": input_text
        }
    ]

    available_functions = {
        "cancel_order": cancel_order,
        "get_order_status": get_order_status
    }


    response = chat(
        model="qwen3.5:4b",
        messages=messages,
        tools=[
            cancel_order,
            get_order_status
        ]
    )


    tool_calls = []

    if response.message.tool_calls:

        messages.append(response.message)

        for tool_call in response.message.tool_calls:

            tool_name = tool_call.function.name
            arguments = tool_call.function.arguments

            function_to_call = available_functions.get(tool_name)

            if function_to_call is None:
                continue

            tool_result = function_to_call(**arguments)

            tool_calls.append({
                "tool": tool_name,
                "arguments": arguments,
                "result": tool_result
            })

            messages.append({
                "role": "tool",
                "content": str(tool_result),
                "tool_name": tool_name
            })


        output = tool_calls[-1]["result"]

    else:
        output = response.message.content


    return {
        "output": output,
        "tool_calls": tool_calls
    }