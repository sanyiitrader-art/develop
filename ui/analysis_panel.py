from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                              QPushButton, QLabel, QScrollArea,
                              QFrame, QTextEdit)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QFont, QTextCharFormat, QColor


class AnalysisPanelWindow(QWidget):
    """
    Displays the full deep structured word analysis.
    Professional trading report style.
    """

    def __init__(self, analysis=None):
        super().__init__()
        self.analysis = analysis
        self._drag_pos = QPoint()
        self._init_ui()

    def set_analysis(self, analysis):
        """Update analysis and refresh all sections."""
        self.analysis = analysis
        self._populate()

    def _init_ui(self):
        self.setWindowTitle("ChartMind AI — Deep Analysis")
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint
        )
        self.setMinimumSize(720, 700)
        self.setStyleSheet("background-color: #0a0c0f;")

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # --- Title Bar ---
        title_bar = QWidget()
        title_bar.setFixedHeight(48)
        title_bar.setStyleSheet(
            "background: #111318; border-bottom: 1px solid #1e2330;")
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(16, 0, 16, 0)

        title_label = QLabel("📝  ChartMind AI — Deep Analysis Report")
        title_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #f59e0b;")

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(32, 32)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #4a5568;
                border: none;
                font-size: 14px;
                border-radius: 6px;
            }
            QPushButton:hover { background: #ef4444; color: white; }
        """)
        close_btn.clicked.connect(self.hide)

        minimize_btn = QPushButton("—")
        minimize_btn.setFixedSize(32, 32)
        minimize_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        minimize_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #4a5568;
                border: none;
                font-size: 14px;
                border-radius: 6px;
            }
            QPushButton:hover { background: #1e2330; color: white; }
        """)
        minimize_btn.clicked.connect(self.showMinimized)

        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(minimize_btn)
        title_layout.addWidget(close_btn)
        layout.addWidget(title_bar)

        # --- Summary Bar ---
        self.summary_bar = QWidget()
        self.summary_bar.setFixedHeight(64)
        self.summary_bar.setStyleSheet(
            "background: #0d1117; border-bottom: 1px solid #1e2330;")
        summary_layout = QHBoxLayout(self.summary_bar)
        summary_layout.setContentsMargins(16, 0, 16, 0)
        summary_layout.setSpacing(12)

        self.direction_badge = QLabel("—")
        self.direction_badge.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.direction_badge.setFixedSize(90, 40)
        self.direction_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.direction_badge.setStyleSheet(
            "background: #1e2330; color: #94a3b8; border-radius: 8px;")

        self.confidence_label = QLabel("Confidence: —")
        self.confidence_label.setStyleSheet(
            "color: #64748b; font-size: 12px; background: transparent;")

        self.rr_badge = QLabel("R:R  —")
        self.rr_badge.setStyleSheet("""
            background: #1a1500;
            color: #f59e0b;
            border: 1px solid #f59e0b55;
            border-radius: 6px;
            padding: 4px 12px;
            font-size: 12px;
            font-weight: bold;
        """)

        summary_layout.addWidget(self.direction_badge)
        summary_layout.addWidget(self.confidence_label)
        summary_layout.addStretch()
        summary_layout.addWidget(self.rr_badge)

        # Copy button
        copy_btn = QPushButton("📋  Copy Report")
        copy_btn.setFixedHeight(34)
        copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        copy_btn.setStyleSheet("""
            QPushButton {
                background: #111a2e;
                color: #3b82f6;
                border: 1px solid #3b82f655;
                border-radius: 6px;
                padding: 0 12px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #3b82f622;
                border-color: #3b82f6;
            }
        """)
        copy_btn.clicked.connect(self._copy_report)
        summary_layout.addWidget(copy_btn)

        layout.addWidget(self.summary_bar)

        # --- Scroll Area ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { background: #0a0c0f; border: none; }
            QScrollBar:vertical {
                background: #0a0c0f; width: 6px; border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: #1e2330; border-radius: 3px;
            }
        """)

        content_widget = QWidget()
        content_widget.setStyleSheet("background: #0a0c0f;")
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setContentsMargins(24, 20, 24, 24)
        self.content_layout.setSpacing(16)

        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

        self.setLayout(layout)

        # Center on screen
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        self.move(
            screen.width() // 2 - self.width() // 2,
            screen.height() // 2 - self.height() // 2
        )

        if self.analysis:
            self._populate()

    def _populate(self):
        """Fills all sections with analysis data."""
        if not self.analysis:
            return

        # Clear existing content
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        direction = self.analysis.get("direction", "NEUTRAL")
        confidence = self.analysis.get("confidence", 0)
        entry = self.analysis.get("entry", "—")
        sl = self.analysis.get("stop_loss", "—")
        tp = self.analysis.get("take_profit", "—")
        rr = self.analysis.get("risk_reward", "—")
        confluences = self.analysis.get("confluences", [])
        structure = self.analysis.get("market_structure", [])
        short_analysis = self.analysis.get("short_analysis", "")
        deep_analysis = self.analysis.get("deep_analysis", "")

        # Update summary bar
        if direction == "BUY":
            color, bg = "#10b981", "#0a1f14"
        elif direction == "SELL":
            color, bg = "#ef4444", "#1f0a0a"
        else:
            color, bg = "#94a3b8", "#1e2330"

        self.direction_badge.setText(direction)
        self.direction_badge.setStyleSheet(
            f"background: {bg}; color: {color}; "
            f"border-radius: 8px; font-weight: bold; font-size: 16px;")
        self.confidence_label.setText(f"Confidence: {confidence}%")
        self.rr_badge.setText(f"R:R  {rr}")

        # --- Section: Quick Summary ---
        self.content_layout.addWidget(
            self._section_title("⚡ Quick Summary"))
        self.content_layout.addWidget(
            self._text_box(short_analysis, "#e2e8f0", "#111827"))

        # --- Section: Trade Levels ---
        self.content_layout.addWidget(
            self._section_title("🎯 Trade Levels"))
        levels_widget = QWidget()
        levels_widget.setStyleSheet(
            "background: #111318; border-radius: 10px; padding: 4px;")
        levels_layout = QHBoxLayout(levels_widget)
        levels_layout.setContentsMargins(16, 12, 16, 12)
        levels_layout.setSpacing(0)
        levels_layout.addWidget(self._level_card("ENTRY", entry, "#00bfff"))
        levels_layout.addWidget(self._vline())
        levels_layout.addWidget(self._level_card("STOP LOSS", sl, "#ef4444"))
        levels_layout.addWidget(self._vline())
        levels_layout.addWidget(self._level_card("TAKE PROFIT", tp, "#10b981"))
        levels_layout.addWidget(self._vline())
        levels_layout.addWidget(self._level_card("RISK:REWARD", rr, "#f59e0b"))
        self.content_layout.addWidget(levels_widget)

        # --- Section: Market Structure ---
        if structure:
            self.content_layout.addWidget(
                self._section_title("📊 Market Structure"))
            for item in structure:
                self.content_layout.addWidget(
                    self._structure_row(
                        item.get("type", ""),
                        item.get("description", "")))

        # --- Section: Confluences ---
        if confluences:
            self.content_layout.addWidget(
                self._section_title("🔗 Detected Confluences"))
            chips_widget = QWidget()
            chips_widget.setStyleSheet("background: transparent;")
            chips_layout = QHBoxLayout(chips_widget)
            chips_layout.setContentsMargins(0, 0, 0, 0)
            chips_layout.setSpacing(8)
            for c in confluences:
                chips_layout.addWidget(self._chip(c))
            chips_layout.addStretch()
            self.content_layout.addWidget(chips_widget)

        # --- Section: Deep Analysis ---
        self.content_layout.addWidget(
            self._section_title("🧠 Full Institutional Analysis"))
        # CHANGE THIS LINE BELOW:
        self.content_layout.addWidget(
            self._text_box(str(deep_analysis), "#cbd5e1", "#0d1117", large=True))

        self.content_layout.addStretch()

    def _section_title(self, text):
        label = QLabel(text)
        label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        label.setStyleSheet("color: #f59e0b; background: transparent; padding-top: 8px;")
        return label

    def _text_box(self, text, color, bg, large=False):
        box = QTextEdit()
        box.setReadOnly(True)
        box.setPlainText(text)
        box.setFont(QFont("Arial", 11 if large else 10))
        box.setStyleSheet(f"""
            QTextEdit {{
                background: {bg};
                color: {color};
                border: 1px solid #1e2330;
                border-radius: 10px;
                padding: 14px;
                line-height: 1.8;
            }}
        """)
        if large:
            box.setMinimumHeight(300)
        else:
            box.setFixedHeight(90)
        return box

    def _level_card(self, label, value, color):
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        vl = QVBoxLayout(w)
        vl.setContentsMargins(12, 4, 12, 4)
        vl.setSpacing(4)
        lbl = QLabel(label)
        lbl.setStyleSheet("color: #4a5568; font-size: 9px; font-weight: bold;"
                          " letter-spacing: 1px; background: transparent;")
        val = QLabel(value)
        val.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        val.setStyleSheet(f"color: {color}; background: transparent;")
        vl.addWidget(lbl)
        vl.addWidget(val)
        return w

    def _structure_row(self, tag, description):
        w = QWidget()
        w.setStyleSheet(
            "background: #111318; border-radius: 8px; margin: 2px 0;")
        hl = QHBoxLayout(w)
        hl.setContentsMargins(12, 8, 12, 8)
        hl.setSpacing(12)

        colors = {
            "HH": "#10b981", "HL": "#6ee7b7",
            "LH": "#fca5a5", "LL": "#ef4444",
            "BOS": "#60a5fa", "CHOCH": "#f59e0b"
        }
        color = colors.get(tag, "#94a3b8")

        tag_label = QLabel(tag)
        tag_label.setFixedSize(52, 24)
        tag_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tag_label.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        tag_label.setStyleSheet(
            f"background: {color}22; color: {color}; "
            f"border: 1px solid {color}55; border-radius: 4px;")

        desc_label = QLabel(description)
        desc_label.setStyleSheet(
            "color: #8892a4; font-size: 12px; background: transparent;")

        hl.addWidget(tag_label)
        hl.addWidget(desc_label)
        hl.addStretch()
        return w

    def _chip(self, text):
        label = QLabel(text)
        label.setStyleSheet("""
            background: #1a1a2e;
            color: #a78bfa;
            border: 1px solid #4c1d9555;
            border-radius: 12px;
            padding: 3px 10px;
            font-size: 11px;
        """)
        return label

    def _vline(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.VLine)
        line.setStyleSheet("color: #1e2330; background: #1e2330;")
        line.setFixedWidth(1)
        return line

    def _copy_report(self):
        """Copies full analysis text to clipboard."""
        from PyQt6.QtWidgets import QApplication
        if not self.analysis:
            return
        report = f"""
CHARTMIND AI — ANALYSIS REPORT
================================
Direction  : {self.analysis.get('direction', '—')}
Bias       : {self.analysis.get('bias', '—')}
Confidence : {self.analysis.get('confidence', '—')}%
Entry      : {self.analysis.get('entry', '—')}
Stop Loss  : {self.analysis.get('stop_loss', '—')}
Take Profit: {self.analysis.get('take_profit', '—')}
Risk:Reward: {self.analysis.get('risk_reward', '—')}

CONFLUENCES:
{chr(10).join(['• ' + c for c in self.analysis.get('confluences', [])])}

DEEP ANALYSIS:
{self.analysis.get('deep_analysis', '')}
        """.strip()
        QApplication.clipboard().setText(report)

    # --- Drag to move ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = (event.globalPosition().toPoint()
                              - self.frameGeometry().topLeft())

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)