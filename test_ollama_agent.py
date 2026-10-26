from ollama_agent import run_ollama_agent


result = run_ollama_agent("Cancel order #789")

print("Output:")
print(result["output"])

print("\nTool calls:")
print(result["tool_calls"])