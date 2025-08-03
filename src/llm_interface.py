import os

LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "http://localhost:12434/")
MODEL = os.environ.get("LLM_MODEL", "ai/gemma3")


def ask_llm(prompt):
    import requests
    import json

    api_url = f"{LLM_BASE_URL}engines/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
    }
    try:
        response = requests.post(
            api_url, headers=headers, data=json.dumps(payload), timeout=60
        )
        response.raise_for_status()
        data = response.json()
        # Extract the assistant's message content from the response
        choices = data.get("choices", [])
        if choices and "message" in choices[0]:
            return choices[0]["message"].get("content", "[No response from LLM]")
        return "[No response from LLM]"
    except Exception as e:
        return f"[LLM API error]: {e}"
