import json
import time
from pathlib import Path
from config import HISTORY_DIR

class LocalHistoryManager:
    """
    Local data storage system. Safely reads and writes structured JSON logs 
    to track past chart analysis parameters without an external database.
    """
    def __init__(self):
        self.history_file_path = HISTORY_DIR / "history.json"
        self._initialize_history_file()

    def _initialize_history_file(self):
        """Creates the history.json file with a clean empty list array if it doesn't exist."""
        try:
            if not self.history_file_path.exists():
                with open(self.history_file_path, "w", encoding="utf-8") as f:
                    json.dump([], f, indent=4)
        except Exception as e:
            print(f"[Storage Error] Failed to initialize history storage container: {e}")

    def log_analysis_session(self, verdict: str, description: str, screenshot_path: str):
        """
        Appends a new structural trading session log record into the local database history.
        """
        try:
            # 1. Read existing historical data array logs safely
            with open(self.history_file_path, "r", encoding="utf-8") as f:
                history_data = json.load(f)
        except Exception:
            history_data = []

        # 2. Construct a modern, structured data entry packet
        new_record = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "verdict": verdict,
            "screenshot_source": screenshot_path,
            "institutional_commentary": description
        }

        # 3. Prepend entry so the newest chart setups are always displayed first
        history_data.insert(0, new_record)

        try:
            # 4. Write back structural parameters using standard formatted layout spacing
            with open(self.history_file_path, "w", encoding="utf-8") as f:
                json.dump(history_data, f, indent=4)
            print(f"[Storage Log] Analysis session successfully recorded in history tracking log.")
        except Exception as e:
            print(f"[Storage Error] Failed to write record to history database logs: {e}")

    def load_all_records(self) -> list:
        """Retrieves all past trading log entries from the local file."""
        try:
            if self.history_file_path.exists():
                with open(self.history_file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"[Storage Error] Failed to load historical tracking data: {e}")
        return []

if __name__ == "__main__":
    print("Testing standalone configuration loggers for History Engine...")
    manager = LocalHistoryManager()
    manager.log_analysis_session("BUY", "Test structural commentary stream data log parameters.", "assets/live_chart.png")
    print(f"History load testing: Found {len(manager.load_all_records())} past entries.")