import os
import json
import base64
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL, SMC_SYSTEM_PROMPT

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)


def _encode_image(image_path):
    """
    Converts image file to base64 string for Groq vision API.
    """
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def analyse_chart(image_path):
    """
    Sends chart image to Groq Vision AI.
    Returns parsed JSON analysis dict or None on failure.
    """
    raw_text = ""
    try:
        if not os.path.exists(image_path):
            print(f"[Analyser] Image not found: {image_path}")
            return None

        print("[Analyser] Encoding image...")
        image_data = _encode_image(image_path)

        print("[Analyser] Sending chart to Groq AI...")
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": SMC_SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_data}"
                            }
                        },
                        {
                            "type": "text",
                            "text": "Analyse this trading chart using full SMC/ICT methodology. Return JSON only."
                        }
                    ]
                }
            ],
            max_tokens=2048,
            temperature=0.1
        )

        # Extract response text
        raw_text = response.choices[0].message.content.strip()

        # Clean markdown if present
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]
        raw_text = raw_text.strip()

        # Parse JSON
        result = json.loads(raw_text)
        print("[Analyser] Analysis complete.")
        return result

    except json.JSONDecodeError as e:
        print(f"[Analyser] JSON parse error: {e}")
        print(f"[Analyser] Raw response: {raw_text}")
        return None

    except Exception as e:
        print(f"[Analyser] Error: {e}")
        return None


def get_direction(analysis):
    if analysis:
        return analysis.get("direction", "NEUTRAL")
    return "NEUTRAL"


def get_short_analysis(analysis):
    if analysis:
        return analysis.get("short_analysis", "No analysis available.")
    return "No analysis available."


def get_deep_analysis(analysis):
    if analysis:
        return analysis.get("deep_analysis", "No detailed analysis available.")
    return "No detailed analysis available."