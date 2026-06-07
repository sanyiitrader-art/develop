from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                              QPushButton, QLabel, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class ResultPanel(QWidget):
    """
    Shows 3 option buttons after scan completes.
    User chooses how they want to see the analysis.
    """
    show_image = pyqtSignal()        # user chose image view
    show_description = pyqtSignal()  # user chose word description
    show_direction = pyqtSignal()    # user chose buy/sell only

    def __init__(self, analysis=None):
        super().__init__()
        self.analysis = analysis
        self._init_ui()

    def set_analysis(self, analysis):
        """Update analysis data and refresh direction badge."""
        self.analysis = analysis
        if analysis:
            direction = analysis.get("direction", "NEUTRAL")
            confidence = analysis.get("confidence", 0)
            self._update_badge(direction, confidence)

    def _init_ui(self):
        self.setWindowTitle("ChartMind AI — Analysis Ready")
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint
        )
        self.setFixedSize(340, 420)
        self.setStyleSheet("""
            QWidget {
                background-color: #0a0c0f;
                border-radius: 16px;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # --- Header ---
        header = QLabel("📊  Analysis Ready")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header.setStyleSheet("color: #f59e0b; background: transparent;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # --- Divider ---
        layout.addWidget(self._divider())

        # --- Direction Badge ---
        self.badge_label = QLabel("ANALYSING...")
        self.badge_label.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        self.badge_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.badge_label.setFixedHeight(70)
        self.badge_label.setStyleSheet("""
            color: #94a3b8;
            background: #111318;
            border-radius: 10px;
            padding: 8px;
        """)
        layout.addWidget(self.badge_label)

        # --- Confidence label ---
        self.conf_label = QLabel("")
        self.conf_label.setFont(QFont("Arial", 10))
        self.conf_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.conf_label.setStyleSheet("color: #64748b; background: transparent;")
        layout.addWidget(self.conf_label)

        # --- Divider ---
        layout.addWidget(self._divider())

        # --- Subtitle ---
        sub = QLabel("How do you want to see the result?")
        sub.setFont(QFont("Arial", 10))
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet("color: #8892a4; background: transparent;")
        layout.addWidget(sub)

        # --- Option Buttons ---
        self.btn_image = self._make_button(
            "📈  By Image",
            "Entry, TP & SL drawn on chart",
            "#1a2a1a", "#10b981"
        )
        self.btn_image.clicked.connect(self.show_image.emit)
        layout.addWidget(self.btn_image)

        self.btn_words = self._make_button(
            "📝  By Description",
            "Full deep professional analysis",
            "#1a1a2a", "#3b82f6"
        )
        self.btn_words.clicked.connect(self.show_description.emit)
        layout.addWidget(self.btn_words)

        self.btn_signal = self._make_button(
            "⚡  Buy or Sell",
            "One word. Instant decision.",
            "#2a1a0a", "#f59e0b"
        )
        self.btn_signal.clicked.connect(self.show_direction.emit)
        layout.addWidget(self.btn_signal)

        # --- Close button ---
        close_btn = QPushButton("✕  Close")
        close_btn.setFixedHeight(36)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #4a5568;
                border: 1px solid #1e2330;
                border-radius: 8px;
                font-size: 12px;
            }
            QPushButton:hover {
                color: #ef4444;
                border-color: #ef4444;
            }
        """)
        close_btn.clicked.connect(self.hide)
        layout.addWidget(close_btn)

        self.setLayout(layout)

        # Center on screen
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        self.move(
            screen.width() // 2 - self.width() // 2,
            screen.height() // 2 - self.height() // 2
        )

    def _update_badge(self, direction, confidence):
        """Updates the direction badge color and text."""
        if direction == "BUY":
            color = "#10b981"
            bg = "#0a1f14"
            border = "#10b981"
        elif direction == "SELL":
            color = "#ef4444"
            bg = "#1f0a0a"
            border = "#ef4444"
        else:
            color = "#94a3b8"
            bg = "#111318"
            border = "#2d3748"

        self.badge_label.setText(direction)
        self.badge_label.setStyleSheet(f"""
            color: {color};
            background: {bg};
            border: 2px solid {border};
            border-radius: 10px;
            padding: 8px;
        """)
        self.conf_label.setText(f"Confidence: {confidence}%")

    def _make_button(self, title, subtitle, bg, accent):
        """Creates a styled option button."""
        btn = QPushButton()
        btn.setFixedHeight(58)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setText(f"{title}\n{subtitle}")
        btn.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {bg};
                color: {accent};
                border: 1px solid {accent}55;
                border-radius: 10px;
                text-align: left;
                padding-left: 16px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background: {accent}22;
                border: 1px solid {accent};
            }}
            QPushButton:pressed {{
                background: {accent}33;
            }}
        """)
        return btn

    def _divider(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #1e2330; background: #1e2330;")
        line.setFixedHeight(1)
        return line

    # --- Drag to move ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)