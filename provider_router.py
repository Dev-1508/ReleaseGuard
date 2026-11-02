from ollama_agent import run_ollama_agent


def run_provider_agent(
    provider,
    model_name,
    input_text
):
    if provider == "ollama":
        return run_ollama_agent(
            input_text,
            model_name
        )

    raise ValueError(
        f"Unsupported provider: {provider}"
    )