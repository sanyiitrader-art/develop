from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                              QHBoxLayout, QPushButton, QLabel,
                              QFrame, QScrollArea, QApplication)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QPoint
from PyQt6.QtGui import QFont, QPixmap
import os

from ui.float_button import FloatButton
from ui.result_panel import ResultPanel
from ui.image_result import ImageResultWindow
from ui.analysis_panel import AnalysisPanelWindow
from core.analyser import analyse_chart
from core.drawer import draw_levels
from core.history import save_analysis, load_history
from core.sound import play_success, play_error
from config import APP_NAME, APP_VERSION, ANALYZED_IMAGE_PATH


class AnalyseWorker(QThread):
    """
    Runs AI analysis in background thread.
    Prevents UI from freezing during API call.
    """
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path

    def run(self):
        try:
            result = analyse_chart(self.image_path)
            if result:
                self.finished.emit(result)
            else:
                self.error.emit("AI analysis returned no result.")
        except Exception as e:
            self.error.emit(str(e))


class Dashboard(QMainWindow):
    """
    Main application window.
    Controls all windows and connects all components.
    """

    def __init__(self):
        super().__init__()
        self.current_analysis = None
        self.analyse_worker = None
        self.image_path = None

        # Initialize child windows
        self.float_button = FloatButton()
        self.result_panel = ResultPanel()
        self.image_window = ImageResultWindow()
        self.analysis_window = AnalysisPanelWindow()

        # Connect signals
        self.float_button.scan_complete.connect(self._on_scan_complete)
        self.result_panel.show_image.connect(self._show_image_result)
        self.result_panel.show_description.connect(self._show_description)
        self.result_panel.show_direction.connect(self._show_direction)

        self._init_ui()
        self.float_button.show()

    def _init_ui(self):
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(980, 680)
        self.setStyleSheet("background-color: #0a0c0f;")

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Header ---
        header = QWidget()
        header.setFixedHeight(60)
        header.setStyleSheet(
            "background: #111318; border-bottom: 1px solid #1e2330;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)

        logo = QLabel("📊  CHARTMIND AI")
        logo.setFont(QFont("Arial", 15, QFont.Weight.Bold))
        logo.setStyleSheet("color: #f59e0b;")

        version = QLabel(f"v{APP_VERSION}")
        version.setStyleSheet("color: #2d3748; font-size: 11px;")

        self.status_label = QLabel("● Ready")
        self.status_label.setStyleSheet("color: #10b981; font-size: 12px;")

        header_layout.addWidget(logo)
        header_layout.addWidget(version)
        header_layout.addStretch()
        header_layout.addWidget(self.status_label)
        main_layout.addWidget(header)

        # --- Body ---
        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        # Left sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet(
            "background: #0d1117; border-right: 1px solid #1e2330;")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(16, 20, 16, 20)
        sidebar_layout.setSpacing(8)

        sidebar_layout.addWidget(self._sidebar_label("ACTIONS"))
        sidebar_layout.addWidget(self._sidebar_btn(
            "📷  Scan Now", self._manual_scan, "#f59e0b"))
        sidebar_layout.addWidget(self._sidebar_btn(
            "📈  View Chart", self._show_image_result, "#10b981"))
        sidebar_layout.addWidget(self._sidebar_btn(
            "📝  View Analysis", self._show_description, "#3b82f6"))
        sidebar_layout.addWidget(self._sidebar_btn(
            "🗑  Clear History", self._clear_history, "#ef4444"))

        sidebar_layout.addSpacing(20)
        sidebar_layout.addWidget(self._sidebar_label("FLOAT BUTTON"))
        sidebar_layout.addWidget(self._sidebar_btn(
            "👁  Show Float Btn", self.float_button.show, "#8b5cf6"))
        sidebar_layout.addWidget(self._sidebar_btn(
            "🙈  Hide Float Btn", self.float_button.hide, "#4a5568"))

        sidebar_layout.addStretch()

        # Version info at bottom
        ver_label = QLabel(f"ChartMind AI\nv{APP_VERSION}")
        ver_label.setStyleSheet(
            "color: #2d3748; font-size: 10px; background: transparent;")
        ver_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(ver_label)

        body_layout.addWidget(sidebar)

        # Main content area
        content = QWidget()
        content.setStyleSheet("background: #0a0c0f;")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setSpacing(16)

        # Status card
        self.status_card = self._build_status_card()
        content_layout.addWidget(self.status_card)

        # Last analysis preview
        content_layout.addWidget(self._section_label("LAST ANALYSIS"))
        self.preview_card = self._build_preview_card()
        content_layout.addWidget(self.preview_card)

        # History section
        content_layout.addWidget(self._section_label("RECENT HISTORY"))
        self.history_scroll = self._build_history_section()
        content_layout.addWidget(self.history_scroll)

        body_layout.addWidget(content)
        main_layout.addWidget(body)

        self._refresh_history()

    # ─── SCAN ────────────────────────────────────────────────

    def _manual_scan(self):
        """Triggers a single screen capture then analyses."""
        from core.capture import capture_screen_once
        self._set_status("Capturing screen...", "#f59e0b")
        try:
            path = capture_screen_once()
            self.image_path = path
            self._run_analysis(path)
        except Exception as e:
            self._set_status("Capture failed", "#ef4444")
            play_error()

    def _on_scan_complete(self, image_path):
        """Called when float button finishes live scan."""
        self.image_path = image_path
        self._set_status("Analysing chart...", "#f59e0b")
        self._run_analysis(image_path)

    def _run_analysis(self, image_path):
        """Sends image to Gemini AI in background thread."""
        self._set_status("● AI Analysing...", "#f59e0b")
        self.analyse_worker = AnalyseWorker(image_path)
        self.analyse_worker.finished.connect(self._on_analysis_done)
        self.analyse_worker.error.connect(self._on_analysis_error)
        self.analyse_worker.start()

    def _on_analysis_done(self, result):
        """Called when AI analysis completes successfully."""
        self.current_analysis = result

        # Draw levels on chart
        draw_levels(result)

        # Save to history
        save_analysis(result, ANALYZED_IMAGE_PATH)

        # Update child windows
        self.result_panel.set_analysis(result)
        self.image_window.set_analysis(result)
        self.analysis_window.set_analysis(result)

        # Update dashboard preview
        self._update_preview(result)
        self._refresh_history()

        play_success()
        self._set_status("● Analysis Complete", "#10b981")

        # Show result panel
        self.result_panel.show()
        self.result_panel.raise_()

    def _on_analysis_error(self, error_msg):
        play_error()
        self._set_status("● Analysis Failed", "#ef4444")
        print(f"[Dashboard] Analysis error: {error_msg}")

    # ─── RESULT VIEWS ────────────────────────────────────────

    def _show_image_result(self):
        if self.current_analysis:
            self.image_window.show()
            self.image_window.raise_()

    def _show_description(self):
        if self.current_analysis:
            self.analysis_window.show()
            self.analysis_window.raise_()

    def _show_direction(self):
        """Shows one-word direction in result panel badge."""
        if self.current_analysis:
            self.result_panel.show()
            self.result_panel.raise_()

    # ─── UI BUILDERS ─────────────────────────────────────────

    def _build_status_card(self):
        card = QWidget()
        card.setFixedHeight(90)
        card.setStyleSheet("""
            background: #111318;
            border: 1px solid #1e2330;
            border-radius: 12px;
        """)
        layout = QHBoxLayout(card)
        layout.setContentsMargins(20, 0, 20, 0)

        left = QVBoxLayout()
        self.card_title = QLabel("Waiting for scan...")
        self.card_title.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        self.card_title.setStyleSheet("color: #e2e8f0; background: transparent;")
        self.card_sub = QLabel(
            "Press the floating 📊 button on your screen to start scanning")
        self.card_sub.setStyleSheet(
            "color: #4a5568; font-size: 11px; background: transparent;")
        left.addWidget(self.card_title)
        left.addWidget(self.card_sub)

        self.card_badge = QLabel("—")
        self.card_badge.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        self.card_badge.setFixedSize(100, 50)
        self.card_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.card_badge.setStyleSheet(
            "background: #1e2330; color: #2d3748; border-radius: 8px;")

        layout.addLayout(left)
        layout.addStretch()
        layout.addWidget(self.card_badge)
        return card

    def _build_preview_card(self):
        card = QWidget()
        card.setFixedHeight(130)
        card.setStyleSheet("""
            background: #111318;
            border: 1px solid #1e2330;
            border-radius: 12px;
        """)
        layout = QHBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(20)

        # Chart thumbnail
        self.thumb_label = QLabel("No chart yet")
        self.thumb_label.setFixedSize(140, 90)
        self.thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumb_label.setStyleSheet(
            "background: #0d1117; color: #2d3748; "
            "border-radius: 6px; font-size: 11px;")

        # Info
        info = QVBoxLayout()
        info.setSpacing(6)
        self.prev_direction = QLabel("Direction: —")
        self.prev_direction.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.prev_direction.setStyleSheet(
            "color: #94a3b8; background: transparent;")
        self.prev_entry = QLabel("Entry: —  |  SL: —  |  TP: —")
        self.prev_entry.setStyleSheet(
            "color: #4a5568; font-size: 11px; background: transparent;")
        self.prev_rr = QLabel("R:R: —")
        self.prev_rr.setStyleSheet(
            "color: #f59e0b; font-size: 11px; background: transparent;")
        self.prev_conf = QLabel("Confidence: —")
        self.prev_conf.setStyleSheet(
            "color: #4a5568; font-size: 11px; background: transparent;")

        info.addWidget(self.prev_direction)
        info.addWidget(self.prev_entry)
        info.addWidget(self.prev_rr)
        info.addWidget(self.prev_conf)

        layout.addWidget(self.thumb_label)
        layout.addLayout(info)
        layout.addStretch()
        return card

    def _build_history_section(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:vertical {
                background: #0a0c0f; width: 5px; border-radius: 2px;
            }
            QScrollBar::handle:vertical {
                background: #1e2330; border-radius: 2px;
            }
        """)
        self.history_widget = QWidget()
        self.history_widget.setStyleSheet("background: transparent;")
        self.history_layout = QVBoxLayout(self.history_widget)
        self.history_layout.setContentsMargins(0, 0, 0, 0)
        self.history_layout.setSpacing(6)
        scroll.setWidget(self.history_widget)
        return scroll

    def _refresh_history(self):
        """Reloads history from file and updates UI."""
        while self.history_layout.count():
            item = self.history_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        history = load_history()
        if not history:
            empty = QLabel("No history yet.")
            empty.setStyleSheet(
                "color: #2d3748; font-size: 12px; padding: 12px;")
            self.history_layout.addWidget(empty)
            return

        for entry in history[:20]:
            self.history_layout.addWidget(self._history_row(entry))
        self.history_layout.addStretch()

    def _history_row(self, entry):
        row = QWidget()
        row.setFixedHeight(48)
        row.setStyleSheet("""
            background: #111318;
            border: 1px solid #1e2330;
            border-radius: 8px;
        """)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(14, 0, 14, 0)
        layout.setSpacing(12)

        direction = entry.get("direction", "—")
        color = ("#10b981" if direction == "BUY"
                 else "#ef4444" if direction == "SELL"
                 else "#94a3b8")

        badge = QLabel(direction)
        badge.setFixedSize(52, 26)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        badge.setStyleSheet(
            f"background: {color}22; color: {color}; "
            f"border: 1px solid {color}55; border-radius: 4px;")

        time_label = QLabel(entry.get("timestamp", ""))
        time_label.setStyleSheet(
            "color: #4a5568; font-size: 11px; background: transparent;")

        conf = QLabel(f"{entry.get('confidence', 0)}%")
        conf.setStyleSheet(
            "color: #64748b; font-size: 11px; background: transparent;")

        rr = QLabel(f"R:R {entry.get('risk_reward', '—')}")
        rr.setStyleSheet(
            "color: #f59e0b; font-size: 11px; background: transparent;")

        layout.addWidget(badge)
        layout.addWidget(time_label)
        layout.addStretch()
        layout.addWidget(conf)
        layout.addWidget(rr)
        return row

    def _update_preview(self, result):
        """Updates the last analysis preview card."""
        direction = result.get("direction", "—")
        color = ("#10b981" if direction == "BUY"
                 else "#ef4444" if direction == "SELL"
                 else "#94a3b8")
        bg = ("#0a1f14" if direction == "BUY"
              else "#1f0a0a" if direction == "SELL"
              else "#1e2330")

        self.card_badge.setText(direction)
        self.card_badge.setStyleSheet(
            f"background: {bg}; color: {color}; "
            f"border-radius: 8px; font-size: 22px; font-weight: bold;")
        self.card_title.setText("Analysis Complete")
        self.card_sub.setText(result.get("short_analysis", "")[:80] + "...")

        self.prev_direction.setText(f"Direction: {direction}")
        self.prev_direction.setStyleSheet(
            f"color: {color}; font-size: 12px; "
            f"font-weight: bold; background: transparent;")
        self.prev_entry.setText(
            f"Entry: {result.get('entry','—')}  |  "
            f"SL: {result.get('stop_loss','—')}  |  "
            f"TP: {result.get('take_profit','—')}")
        self.prev_rr.setText(f"R:R: {result.get('risk_reward','—')}")
        self.prev_conf.setText(
            f"Confidence: {result.get('confidence', 0)}%")

        # Thumbnail
        if os.path.exists(ANALYZED_IMAGE_PATH):
            pixmap = QPixmap(ANALYZED_IMAGE_PATH)
            scaled = pixmap.scaled(
                140, 90,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
            self.thumb_label.setPixmap(scaled)

    def _clear_history(self):
        from core.history import clear_history
        clear_history()
        self._refresh_history()

    def _set_status(self, text, color):
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"color: {color}; font-size: 12px;")

    def _sidebar_label(self, text):
        label = QLabel(text)
        label.setStyleSheet(
            "color: #2d3748; font-size: 9px; font-weight: bold; "
            "letter-spacing: 2px; background: transparent; padding-top: 4px;")
        return label

    def _sidebar_btn(self, text, callback, color):
        btn = QPushButton(text)
        btn.setFixedHeight(38)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFont(QFont("Arial", 10))
        btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {color};
                border: 1px solid {color}33;
                border-radius: 8px;
                text-align: left;
                padding-left: 12px;
            }}
            QPushButton:hover {{
                background: {color}15;
                border-color: {color}88;
            }}
            QPushButton:pressed {{
                background: {color}25;
            }}
        """)
        btn.clicked.connect(callback)
        return btn

    def _section_label(self, text):
        label = QLabel(text)
        label.setStyleSheet(
            "color: #2d3748; font-size: 9px; font-weight: bold; "
            "letter-spacing: 2px; background: transparent;")
        return label

    def closeEvent(self, event):
        """Clean up all windows on close."""
        self.float_button.close()
        self.result_panel.close()
        self.image_window.close()
        self.analysis_window.close()
        event.accept()