import ollama

def ask_ollama(prompt):
    try:
        response = ollama.generate(
            model="gemma3:1b",
            prompt=prompt,
            stream=False,
            system="You are a helpful writing assistant. Provide only the requested output without any preamble, explanations, or meta-commentary. Do not include phrases like 'Here is', 'Here's', or 'Summary:'. Just provide the direct result."
        )
        return response["response"]
    except Exception as e:
        return f"Error: {str(e)}"