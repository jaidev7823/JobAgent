import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"

def plan_strategy(prompt):
    planning_prompt = f"""
    You are a web automation planner.
    Convert user goal into a step-by-step browsing strategy.
    
    Return ONLY a JSON object with:
    "goal": string
    "steps": list of strings

    User goal:
    {prompt}
    """

    try:
        res = requests.post(OLLAMA_URL, json={
            "model": "ministral-3:latest",
            "prompt": planning_prompt,
            "stream": False,
            "format": "json"  # <--- This is the key fix
        }, timeout=30)
        
        res.raise_for_status() # Check for HTTP errors (404, 500, etc)
        
        response_data = res.json()
        raw_text = response_data.get("response", "").strip()

        if not raw_text:
            print("Error: LLM returned an empty response.")
            return {"goal": prompt, "steps": []}

        return json.loads(raw_text)

    except requests.exceptions.RequestException as e:
        print(f"Network error connecting to Ollama: {e}")
        return {"goal": prompt, "steps": ["Check if Ollama is running"]}
    except json.JSONDecodeError as e:
        print(f"Failed to parse LLM response: {raw_text}")
        return {"goal": prompt, "steps": []}