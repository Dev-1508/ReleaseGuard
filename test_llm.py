from llm_client import ask_model

print("Sending request to Ollama...")

response = ask_model(
    "Reply with exactly: ReleaseGuard local AI connection successful"
)

print("Response received:")
print(response)