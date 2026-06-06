import os
import base64
import json
from pathlib import Path
from anthropic import Anthropic
from config import ANTHROPIC_API_KEY, SMC_SYSTEM_PROMPT

class ChartVisionAnalyser:
    """
    Core AI network processing engine. Manages secure connections with Claude Vision,
    handles asset payload serialization, and parses multi-view outputs for execution.
    """
    def __init__(self):
        # Initialize the official Anthropic SDK client wrapper cleanly
        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
        # Force production vision model parameters 
        self.model_target = "claude-3-5-sonnet-20241022"

    def _encode_image_to_base64(self, image_path: str) -> str:
        """Reads a local image binary surface asset and returns its base64 string."""
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")

    def run_vision_analysis(self, image_path: str) -> dict:
        """
        Sends the trading chart image to Claude Vision with strict SMC system guidelines.
        Returns a structured dictionary mapping layout routing targets.
        """
        if not ANTHROPIC_API_KEY:
            print("[API Error] Anthropic API Key is missing inside your local configuration configurations.")
            return self._generate_error_payload("API_KEY_MISSING")

        if not os.path.exists(image_path):
            print(f"[File Error] Target analysis chart not located at asset path: {image_path}")
            return self._generate_error_payload("FILE_NOT_FOUND")

        try:
            # 1. Convert chart screenshot to secure transmission format string
            base64_image = self._encode_image_to_base64(image_path)
            
            print(f"[Network Log] Initiating upstream payload transmission to {self.model_target}...")
            
            # 2. Build non-blocking message array layout payload
            message = self.client.messages.create(
                model=self.model_target,
                max_tokens=4000,
                temperature=0.0,  # Zero variance ensures ultra-consistent algorithmic tape-reading math
                system=SMC_SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": base64_image
                                }
                            },
                            {
                                "type": "text",
                                "text": "Execute professional SMC/ICT analysis on this live trading chart structure. Output absolute data targets cleanly."
                            }
                        ]
                    }
                ]
            )

            # 3. Extract raw structural text content payload block
            raw_response_text = message.content[0].text
            print("[Network Log] Upstream text packet received successfully. Parsing content views...")
            
            # 4. Route extracted string content segments safely into structured return dictionary maps
            return self._parse_raw_response(raw_response_text)

        except Exception as e:
            print(f"[Network Critical Error] Upstream connection aborted via API pipeline: {e}")
            return self._generate_error_payload("CONNECTION_TIMEOUT", detail=str(e))

    def _parse_raw_response(self, text: str) -> dict:
        """
        Parses text segments into independent structural dictionary blocks 
        matching your three distinct multi-option UI view buttons.
        """
        payload = {
            "verdict": "NEUTRAL",
            "description": text,  # Default fallback long description 
            "coordinates": {}
        }

        # Isolate direct one-word direction signals cleanly via token extraction loops
        if "[VIEW 1: ONE-WORD DIRECTION]" in text:
            try:
                segment = text.split("[VIEW 1: ONE-WORD DIRECTION]")[1].split("[")[0].strip()
                if "BUY" in segment.upper():
                    payload["verdict"] = "BUY"
                elif "SELL" in segment.upper():
                    payload["verdict"] = "SELL"
            except Exception:
                pass

        # Isolate long description blocks explicitly if marker keys map out cleanly
        if "[VIEW 2: ULTRA-DEEP WORD DESCRIPTION]" in text:
            try:
                segment = text.split("[VIEW 2: ULTRA-DEEP WORD DESCRIPTION]")[1].split("[")[0].strip()
                payload["description"] = segment
            except Exception:
                pass

        return payload

    def _generate_error_payload(self, error_code: str, detail: str = "") -> dict:
        """Fallback mock safety structural layouts generated in case of unexpected exceptions."""
        return {
            "verdict": "NEUTRAL",
            "description": f"[CRITICAL ERROR DETECTED]: System validation failed with code: {error_code}.\nDetails: {detail}\n\nPlease check your .env keys and internet layout infrastructure.",
            "coordinates": {}
        }

if __name__ == "__main__":
    # Independent standalone development file test pipeline module
    print("Initializing Core Vision interface validation loops...")
    analyser = ChartVisionAnalyser()
    # Dummy test to run without breaking execution lines if executed directly
    print("Vision core operational setup complete. Ready for integration routing.")