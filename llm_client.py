from ollama import chat


def ask_model(prompt):
    response = chat(
        model="qwen3.5:4b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.message.content