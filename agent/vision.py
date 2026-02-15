import requests
import base64
import json

OLLAMA_URL = "http://localhost:11434/api/generate"

def encode_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def decide_action(image_path, goal):
    image_base64 = encode_image(image_path)

    prompt = f"""
    The user goal is: {goal}
    The screenshot contains numbered UI elements.
    
    You must respond in VALID JSON format.
    Decide:
    - Which number to click to get closer to the goal.
    - Or "scroll" if the target isn't visible.
    - Or "done" if the goal is reached.

    JSON Structure:
    {{
      "action": "click" | "scroll" | "done",
      "target": number or null
    }}
    """

    try:
        res = requests.post(OLLAMA_URL, json={
            "model": "ministral-3:latest", # Double check this name with 'ollama list'
            "prompt": prompt,
            "images": [image_base64],
            "stream": False,
            "format": "json" # Forces Ollama to agent/output valid JSON
        }, timeout=60)

        res_json = res.json()
        
        if "error" in res_json:
            print(f"Ollama Error: {res_json['error']}")
            return {"action": "scroll", "target": None}

        # Extract the response text
        raw_response = res_json.get("response", "")
        return json.loads(raw_response)

    except Exception as e:
        print(f"Vision Error: {e}")
        # Default fallback so the loop doesn't crash
        return {"action": "scroll", "target": None}