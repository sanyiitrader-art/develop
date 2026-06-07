import mss
import mss.tools
from PIL import Image
import time
import os
from config import LIVE_CHART_PATH, CAPTURE_DURATION


def capture_screen_once():
    """
    Captures the full screen once and saves it.
    Returns the path to the saved image.
    """
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        screenshot = sct.grab(monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        os.makedirs(os.path.dirname(LIVE_CHART_PATH), exist_ok=True) if os.path.dirname(LIVE_CHART_PATH) else None
        img.save(LIVE_CHART_PATH)
    return LIVE_CHART_PATH


def capture_screen_live(progress_callback=None, stop_flag=None):
    """
    Waits CAPTURE_DURATION seconds while showing countdown,
    then takes one clean screenshot at the end.
    Returns the path to the saved image.
    """
    if stop_flag is None:
        stop_flag = [False]

    # Countdown
    for remaining in range(CAPTURE_DURATION, 0, -1):
        if stop_flag[0]:
            break
        if progress_callback:
            progress_callback(remaining)
        time.sleep(1)

    if stop_flag[0]:
        return LIVE_CHART_PATH

    # Take the final screenshot
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        screenshot = sct.grab(monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        img.save(LIVE_CHART_PATH)

    if progress_callback:
        progress_callback(0)

    return LIVE_CHART_PATH


def get_captured_image():
    """
    Returns the last captured image as a PIL Image object.
    Returns None if no image has been captured yet.
    """
    if os.path.exists(LIVE_CHART_PATH):
        return Image.open(LIVE_CHART_PATH)
    return None