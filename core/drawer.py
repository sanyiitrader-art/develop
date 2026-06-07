import cv2
import numpy as np
from PIL import Image
import os
from config import ANALYZED_IMAGE_PATH, LIVE_CHART_PATH


def draw_levels(analysis):
    """
    Draws Entry, Stop Loss and Take Profit levels
    geometrically on the captured chart image.
    Saves result to analyzed_chart.png.
    Returns path to the analyzed image.
    """
    try:
        # Load the captured chart
        if not os.path.exists(LIVE_CHART_PATH):
            print("[Drawer] No chart image found.")
            return None

        # Open with PIL then convert to OpenCV format
        pil_img = Image.open(LIVE_CHART_PATH).convert("RGB")
        img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

        height, width = img.shape[:2]

        # Get y positions from analysis (0.0 = top, 1.0 = bottom)
        entry_y = int(analysis.get("entry_y_percent", 0.5) * height)
        sl_y = int(analysis.get("sl_y_percent", 0.6) * height)
        tp_y = int(analysis.get("tp_y_percent", 0.3) * height)

        direction = analysis.get("direction", "NEUTRAL")
        entry_price = analysis.get("entry", "")
        sl_price = analysis.get("stop_loss", "")
        tp_price = analysis.get("take_profit", "")
        rr = analysis.get("risk_reward", "")

        # --- COLORS ---
        COLOR_ENTRY = (0, 191, 255)    # Deep sky blue
        COLOR_SL = (0, 60, 220)        # Red (BGR)
        COLOR_TP = (0, 200, 80)        # Green (BGR)
        COLOR_ZONE_SL = (0, 60, 220)
        COLOR_ZONE_TP = (0, 200, 80)
        ALPHA = 0.15                    # Zone transparency

        line_thickness = 2
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        label_thickness = 2

        # --- DRAW ZONE FILLS ---
        overlay = img.copy()

        # SL Zone (entry to sl)
        sl_zone_top = min(entry_y, sl_y)
        sl_zone_bot = max(entry_y, sl_y)
        cv2.rectangle(overlay, (0, sl_zone_top), (width, sl_zone_bot),
                      COLOR_ZONE_SL, -1)

        # TP Zone (entry to tp)
        tp_zone_top = min(entry_y, tp_y)
        tp_zone_bot = max(entry_y, tp_y)
        cv2.rectangle(overlay, (0, tp_zone_top), (width, tp_zone_bot),
                      COLOR_ZONE_TP, -1)

        # Blend overlay
        cv2.addWeighted(overlay, ALPHA, img, 1 - ALPHA, 0, img)

        # --- DRAW LINES ---

        # Entry line
        cv2.line(img, (0, entry_y), (width, entry_y), COLOR_ENTRY, line_thickness)

        # Stop Loss line
        cv2.line(img, (0, sl_y), (width, sl_y), COLOR_SL, line_thickness)

        # Take Profit line
        cv2.line(img, (0, tp_y), (width, tp_y), COLOR_TP, line_thickness)

        # --- DRAW LABELS ---

        # Entry label
        _draw_label(img, f"ENTRY  {entry_price}", (width - 220, entry_y - 8),
                    COLOR_ENTRY, font, font_scale, label_thickness)

        # SL label
        _draw_label(img, f"SL  {sl_price}", (width - 220, sl_y - 8),
                    COLOR_SL, font, font_scale, label_thickness)

        # TP label
        _draw_label(img, f"TP  {tp_price}", (width - 220, tp_y - 8),
                    COLOR_TP, font, font_scale, label_thickness)

        # --- DRAW DIRECTION BADGE ---
        badge_color = (0, 200, 80) if direction == "BUY" else \
                      (0, 60, 220) if direction == "SELL" else (100, 100, 100)

        cv2.rectangle(img, (20, 20), (160, 65), badge_color, -1)
        cv2.putText(img, direction, (30, 55),
                    font, 1.2, (255, 255, 255), 2, cv2.LINE_AA)

        # --- DRAW R:R BADGE ---
        cv2.rectangle(img, (20, 75), (160, 110), (30, 30, 30), -1)
        cv2.putText(img, f"R:R  {rr}", (28, 100),
                    font, 0.55, (255, 200, 0), 1, cv2.LINE_AA)

        # --- DRAW ARROW ---
        arrow_x = width - 60
        if direction == "BUY":
            # Arrow pointing up from SL to TP
            cv2.arrowedLine(img, (arrow_x, sl_y), (arrow_x, tp_y),
                            COLOR_TP, 3, tipLength=0.04)
        elif direction == "SELL":
            # Arrow pointing down from SL to TP
            cv2.arrowedLine(img, (arrow_x, sl_y), (arrow_x, tp_y),
                            COLOR_SL, 3, tipLength=0.04)

        # --- SAVE RESULT ---
        result_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        pil_result = Image.fromarray(result_img)
        pil_result.save(ANALYZED_IMAGE_PATH)

        print(f"[Drawer] Chart saved to {ANALYZED_IMAGE_PATH}")
        return ANALYZED_IMAGE_PATH

    except Exception as e:
        print(f"[Drawer] Error: {e}")
        return None


def _draw_label(img, text, pos, color, font, scale, thickness):
    """
    Draws a label with a dark background box for readability.
    """
    x, y = pos
    (text_w, text_h), _ = cv2.getTextSize(text, font, scale, thickness)
    # Background box
    cv2.rectangle(img, (x - 4, y - text_h - 4),
                  (x + text_w + 4, y + 4), (0, 0, 0), -1)
    # Text
    cv2.putText(img, text, (x, y), font, scale, color, thickness, cv2.LINE_AA)