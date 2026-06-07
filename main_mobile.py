import flet as ft
import os
import threading
import shutil
from core.analyser import analyse_chart
from core.drawer import draw_levels
from core.history import save_analysis, load_history
from config import ANALYZED_IMAGE_PATH, LIVE_CHART_PATH

GOLD = "#f59e0b"
GREEN = "#10b981"
RED = "#ef4444"
BLUE = "#3b82f6"
BG2 = "#111318"
BG3 = "#0d1117"


def main(page: ft.Page):
    page.title = "ChartMind AI"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0a0c0f"
    page.padding = 16
    page.scroll = ft.ScrollMode.AUTO
    page.window_width = 390
    page.window_height = 844

    current_analysis = {"data": None}

    # ── STATUS ──────────────────────────────────────────────
    status_text = ft.Text(
        "Upload a chart to begin",
        size=12, color="#4a5568",
        text_align=ft.TextAlign.CENTER
    )

    # ── CHART IMAGE ─────────────────────────────────────────
    chart_image = ft.Image(
        src="assets/live_chart.png",
        width=360, height=200,
        visible=False,
    )

    chart_placeholder = ft.Container(
        content=ft.Column([
            ft.Text("📈", size=40),
            ft.Text("No chart uploaded yet",
                    size=13, color="#2d3748",
                    text_align=ft.TextAlign.CENTER),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER),
        width=360, height=200,
        bgcolor=BG3,
        border_radius=10,
    )

    # ── DIRECTION BADGE ─────────────────────────────────────
    direction_text = ft.Text(
        "—", size=36,
        weight=ft.FontWeight.BOLD,
        color="#2d3748",
        text_align=ft.TextAlign.CENTER
    )
    direction_badge = ft.Container(
        content=direction_text,
        bgcolor=BG3,
        border_radius=10,
        padding=12,
        width=360,
        visible=False,
    )

    # ── ENTRY INFO ──────────────────────────────────────────
    entry_info = ft.Container(visible=False, width=360)

    # ── ANALYSIS TEXT ───────────────────────────────────────
    analysis_box = ft.Container(
        visible=False,
        width=360,
        height=340,
        bgcolor=BG3,
        border_radius=10,
        padding=14,
    )

    # ── OPTIONS ─────────────────────────────────────────────
    options_col = ft.Container(visible=False)

    def show_image_result(e):
        if not current_analysis["data"]:
            return
        if os.path.exists(ANALYZED_IMAGE_PATH):
            chart_image.src = ANALYZED_IMAGE_PATH
            chart_image.visible = True
            chart_placeholder.visible = False
            entry_info.visible = True
            analysis_box.visible = False
            direction_badge.visible = False
            page.update()

    def show_description_result(e):
        if not current_analysis["data"]:
            return
        deep = current_analysis["data"].get(
            "deep_analysis", "No analysis available.")
        analysis_box.content = ft.Column([
            ft.Text("🧠 Full Analysis", size=13,
                    weight=ft.FontWeight.BOLD, color=GOLD),
            ft.Text(deep, size=11, color="#cbd5e1", selectable=True),
        ], scroll=ft.ScrollMode.AUTO)
        analysis_box.visible = True
        entry_info.visible = False
        direction_badge.visible = False
        page.update()

    def show_direction_result(e):
        if not current_analysis["data"]:
            return
        direction = current_analysis["data"].get("direction", "NEUTRAL")
        color = (GREEN if direction == "BUY"
                 else RED if direction == "SELL"
                 else "#94a3b8")
        bg = ("#0a1f14" if direction == "BUY"
              else "#1f0a0a" if direction == "SELL"
              else BG3)
        direction_text.value = direction
        direction_text.color = color
        direction_badge.bgcolor = bg
        direction_badge.visible = True
        entry_info.visible = False
        analysis_box.visible = False
        page.update()

    options_col = ft.Container(
        content=ft.Column([
            ft.Text("How do you want to see the result?",
                    size=12, color="#8892a4",
                    text_align=ft.TextAlign.CENTER),
            ft.ElevatedButton(
                "📈  By Image",
                on_click=show_image_result,
                bgcolor="#1a2a1a",
                color=GREEN,
                width=340, height=50,
            ),
            ft.ElevatedButton(
                "📝  By Description",
                on_click=show_description_result,
                bgcolor="#111a2e",
                color=BLUE,
                width=340, height=50,
            ),
            ft.ElevatedButton(
                "⚡  Buy or Sell",
                on_click=show_direction_result,
                bgcolor="#1a1500",
                color=GOLD,
                width=340, height=50,
            ),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=8),
        visible=False,
        padding=8,
    )

    # ── ANALYSIS ENGINE ─────────────────────────────────────
    def run_analysis(image_path):
        status_text.value = "🧠 AI Analysing chart..."
        status_text.color = GOLD
        page.update()

        def _analyse():
            result = analyse_chart(image_path)
            if result:
                current_analysis["data"] = result
                draw_levels(result)
                save_analysis(result, ANALYZED_IMAGE_PATH)

                entry_info.content = ft.Row([
                    ft.Column([
                        ft.Text("ENTRY", size=9, color="#4a5568",
                                weight=ft.FontWeight.BOLD),
                        ft.Text(result.get("entry", "—"),
                                size=11, color="#00bfff",
                                weight=ft.FontWeight.BOLD),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Column([
                        ft.Text("SL", size=9, color="#4a5568",
                                weight=ft.FontWeight.BOLD),
                        ft.Text(result.get("stop_loss", "—"),
                                size=11, color=RED,
                                weight=ft.FontWeight.BOLD),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Column([
                        ft.Text("TP", size=9, color="#4a5568",
                                weight=ft.FontWeight.BOLD),
                        ft.Text(result.get("take_profit", "—"),
                                size=11, color=GREEN,
                                weight=ft.FontWeight.BOLD),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Column([
                        ft.Text("R:R", size=9, color="#4a5568",
                                weight=ft.FontWeight.BOLD),
                        ft.Text(result.get("risk_reward", "—"),
                                size=11, color=GOLD,
                                weight=ft.FontWeight.BOLD),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ],
                alignment=ft.MainAxisAlignment.SPACE_AROUND)
                entry_info.visible = True
                options_col.visible = True
                status_text.value = "✅ Done — choose view below"
                status_text.color = GREEN
            else:
                status_text.value = "❌ Analysis failed. Try again."
                status_text.color = RED
            page.update()

        thread = threading.Thread(target=_analyse, daemon=True)
        thread.start()

    # ── FILE PICKER ─────────────────────────────────────────
    def on_file_picked(e: ft.FilePickerResultEvent):
        if not e.files:
            return
        src_path = e.files[0].path
        if not src_path or not os.path.exists(src_path):
            status_text.value = "Could not read file."
            status_text.color = RED
            page.update()
            return
        shutil.copy(src_path, LIVE_CHART_PATH)
        chart_image.src = LIVE_CHART_PATH
        chart_image.visible = True
        chart_placeholder.visible = False
        options_col.visible = False
        direction_badge.visible = False
        entry_info.visible = False
        analysis_box.visible = False
        status_text.value = "Chart loaded. Analysing..."
        status_text.color = GOLD
        page.update()
        run_analysis(LIVE_CHART_PATH)

    file_picker = ft.FilePicker(on_result=on_file_picked)
    page.overlay.append(file_picker)

    # ── UPLOAD BUTTON ───────────────────────────────────────
    upload_btn = ft.ElevatedButton(
        "📷  Upload Chart",
        on_click=lambda e: file_picker.pick_files(
            allowed_extensions=["png", "jpg", "jpeg", "webp"],
            allow_multiple=False,
        ),
        bgcolor="#1a1500",
        color=GOLD,
        width=340,
        height=52,
    )

    # ── HISTORY ─────────────────────────────────────────────
    def build_history():
        history = load_history()
        if not history:
            return ft.Text("No history yet.", size=12, color="#2d3748")
        rows = []
        for h in history[:10]:
            direction = h.get("direction", "—")
            color = (GREEN if direction == "BUY"
                     else RED if direction == "SELL"
                     else "#94a3b8")
            rows.append(ft.Container(
                content=ft.Row([
                    ft.Text(direction, size=11,
                            weight=ft.FontWeight.BOLD,
                            color=color, width=60),
                    ft.Text(h.get("timestamp", ""),
                            size=10, color="#4a5568",
                            expand=True),
                    ft.Text(f"R:R {h.get('risk_reward','—')}",
                            size=10, color=GOLD),
                ]),
                bgcolor=BG2,
                border_radius=8,
                padding=10,
            ))
        return ft.Column(rows, spacing=6)

    # ── LAYOUT ──────────────────────────────────────────────
    page.add(
        ft.Container(
            content=ft.Row([
                ft.Text("📊  CHARTMIND AI", size=16,
                        weight=ft.FontWeight.BOLD, color=GOLD),
                ft.Container(expand=True),
                ft.Text("● Ready", size=11, color=GREEN),
            ]),
            bgcolor=BG2,
            padding=14,
        ),
        ft.Container(height=12),
        status_text,
        ft.Container(height=12),
        chart_placeholder,
        chart_image,
        ft.Container(height=12),
        upload_btn,
        ft.Container(height=8),
        options_col,
        direction_badge,
        entry_info,
        analysis_box,
        ft.Container(height=16),
        ft.Text("RECENT HISTORY", size=9, color="#2d3748",
                weight=ft.FontWeight.BOLD),
        ft.Container(height=6),
        build_history(),
        ft.Container(height=24),
    )


ft.app(target=main)