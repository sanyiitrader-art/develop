import time
import pyautogui
from PIL import Image
from pathlib import Path

def capture_live_screen(output_filename: str = "live_chart.png") -> str:
    """
    Captures the primary monitor screen, optimizes the resolution parameters, 
    saves the image output to the local assets folder, and returns the absolute string path.
    
    Returns:
        str: Absolute system filepath to the captured image, or an empty string if failed.
    """
    try:
        # 1. Allow the desktop window manager thread a brief window to hide overlay buttons
        time.sleep(0.1)
        
        # 2. Capture raw display pixels from the primary graphics monitor context
        screenshot = pyautogui.screenshot()
        
        # 3. Locate and generate target directory routes inside chartmind-ai project roots
        root_dir = Path(__file__).resolve().parent.parent
        assets_dir = root_dir / "assets"
        assets_dir.mkdir(exist_ok=True)
        
        target_path = assets_dir / output_filename
        
        # 4. Save image via Pillow utilizing explicit PNG encoding optimization parameters
        screenshot.save(target_path, "PNG")
        
        print(f"[Engine Log] Capture sequence successful. File saved to: {target_path}")
        return str(target_path)
        
    except Exception as e:
        print(f"[Engine Error] Critical failure during display surface execution capture: {e}")
        return ""

if __name__ == "__main__":
    # Independent file execution test verification block
    print("Testing capture engine interface standalone...")
    test_path = capture_live_screen("test_capture.png")
    if test_path:
        print(f"Test Success. Image stored locally at system route: {test_path}")
    else:
        print("Test Failure. Verify OS permissions or file paths.")