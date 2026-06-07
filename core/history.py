import json
import os
from datetime import datetime
from config import HISTORY_FILE


def _ensure_file():
    """
    Creates history file if it does not exist.
    """
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "w") as f:
            json.dump([], f)


def save_analysis(analysis, image_path=None):
    """
    Saves one analysis result to history.
    """
    _ensure_file()

    try:
        # Load existing history
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)

        # Build history entry
        entry = {
            "id": len(history) + 1,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "direction": analysis.get("direction", "NEUTRAL"),
            "bias": analysis.get("bias", "neutral"),
            "confidence": analysis.get("confidence", 0),
            "entry": analysis.get("entry", ""),
            "stop_loss": analysis.get("stop_loss", ""),
            "take_profit": analysis.get("take_profit", ""),
            "risk_reward": analysis.get("risk_reward", ""),
            "confluences": analysis.get("confluences", []),
            "short_analysis": analysis.get("short_analysis", ""),
            "image_path": image_path or ""
        }

        # Add to history
        history.insert(0, entry)

        # Keep only last 100 entries
        history = history[:100]

        # Save back
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=2)

        print(f"[History] Saved analysis #{entry['id']}")
        return entry

    except Exception as e:
        print(f"[History] Error saving: {e}")
        return None


def load_history():
    """
    Loads all history entries.
    Returns list of dicts.
    """
    _ensure_file()

    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"[History] Error loading: {e}")
        return []


def clear_history():
    """
    Clears all history entries.
    """
    _ensure_file()

    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump([], f)
        print("[History] History cleared.")
        return True
    except Exception as e:
        print(f"[History] Error clearing: {e}")
        return False


def get_last_analysis():
    """
    Returns the most recent analysis entry.
    """
    history = load_history()
    if history:
        return history[0]
    return None