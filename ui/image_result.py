from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                              QPushButton, QLabel, QScrollArea,
                              QFrame)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QFont, QPixmap, QColor
from config import ANALYZED_IMAGE_PATH


class ImageResultWindow(QWidget):
    """
    Displays the analyzed chart image with
    Entry, TP and SL lines drawn geometrically on it.
    """

    def __init__(self, analysis=None):
        super().__init__()
        self.analysis = analysis
        self._drag_pos = QPoint()
        self._init_ui()

    def set_analysis(self, analysis):
        """Update analysis and reload image."""
        self.analysis = analysis
        self._load_image()
        self._update_info_bar()

    def _init_ui(self):
        self.setWindowTitle("ChartMind AI — Chart Analysis")
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint
        )
        self.setMinimumSize(900, 620)
        self.setStyleSheet("background-color: #0a0c0f;")

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # --- Title Bar ---
        title_bar = QWidget()
        title_bar.setFixedHeight(48)
        title_bar.setStyleSheet("background: #111318; border-bottom: 1px solid #1e2330;")
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(16, 0, 16, 0)

        title_label = QLabel("📊  ChartMind AI — Visual Analysis")
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
            QPushButton:hover {
                background: #ef4444;
                color: white;
            }
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
            QPushButton:hover {
                background: #1e2330;
                color: white;
            }
        """)
        minimize_btn.clicked.connect(self.showMinimized)

        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(minimize_btn)
        title_layout.addWidget(close_btn)
        layout.addWidget(title_bar)

        # --- Info Bar ---
        self.info_bar = QWidget()
        self.info_bar.setFixedHeight(52)
        self.info_bar.setStyleSheet("background: #0d1117; border-bottom: 1px solid #1e2330;")
        info_layout = QHBoxLayout(self.info_bar)
        info_layout.setContentsMargins(16, 0, 16, 0)
        info_layout.setSpacing(16)

        self.direction_badge = QLabel("—")
        self.direction_badge.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        self.direction_badge.setFixedSize(80, 32)
        self.direction_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.direction_badge.setStyleSheet(
            "background: #1e2330; color: #94a3b8; border-radius: 6px;")

        self.entry_label = self._info_chip("ENTRY", "—", "#00bfff")
        self.sl_label = self._info_chip("SL", "—", "#ef4444")
        self.tp_label = self._info_chip("TP", "—", "#10b981")
        self.rr_label = self._info_chip("R:R", "—", "#f59e0b")

        info_layout.addWidget(self.direction_badge)
        info_layout.addWidget(self._vline())
        info_layout.addWidget(self.entry_label)
        info_layout.addWidget(self.sl_label)
        info_layout.addWidget(self.tp_label)
        info_layout.addWidget(self.rr_label)
        info_layout.addStretch()

        # Save button
        save_btn = QPushButton("💾  Save Image")
        save_btn.setFixedHeight(32)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet("""
            QPushButton {
                background: #1a2a1a;
                color: #10b981;
                border: 1px solid #10b98155;
                border-radius: 6px;
                padding: 0 12px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #10b98122;
                border-color: #10b981;
            }
        """)
        save_btn.clicked.connect(self._save_image)
        info_layout.addWidget(save_btn)

        layout.addWidget(self.info_bar)

        # --- Chart Image Area ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                background: #050608;
                border: none;
            }
            QScrollBar:vertical {
                background: #0a0c0f;
                width: 6px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: #1e2330;
                border-radius: 3px;
            }
            QScrollBar:horizontal {
                background: #0a0c0f;
                height: 6px;
                border-radius: 3px;
            }
            QScrollBar::handle:horizontal {
                background: #1e2330;
                border-radius: 3px;
            }
        """)

        self.chart_label = QLabel()
        self.chart_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.chart_label.setStyleSheet("background: #050608;")
        self.chart_label.setText("No chart loaded yet.")
        self.chart_label.setStyleSheet("color: #4a5568; background: #050608;")

        scroll.setWidget(self.chart_label)
        layout.addWidget(scroll)

        # --- Legend Bar ---
        legend = QWidget()
        legend.setFixedHeight(36)
        legend.setStyleSheet("background: #111318; border-top: 1px solid #1e2330;")
        legend_layout = QHBoxLayout(legend)
        legend_layout.setContentsMargins(16, 0, 16, 0)
        legend_layout.setSpacing(20)

        legend_layout.addWidget(self._legend_dot("#00bfff", "Entry Line"))
        legend_layout.addWidget(self._legend_dot("#10b981", "Take Profit Zone"))
        legend_layout.addWidget(self._legend_dot("#ef4444", "Stop Loss Zone"))
        legend_layout.addStretch()

        layout.addWidget(legend)
        self.setLayout(layout)

        # Center on screen
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        self.move(
            screen.width() // 2 - self.width() // 2,
            screen.height() // 2 - self.height() // 2
        )

        self._load_image()

    def _load_image(self):
        """Loads and displays the analyzed chart image."""
        import os
        if os.path.exists(ANALYZED_IMAGE_PATH):
            pixmap = QPixmap(ANALYZED_IMAGE_PATH)
            scaled = pixmap.scaled(
                self.width() - 20,
                500,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.chart_label.setPixmap(scaled)
            self.chart_label.setStyleSheet("background: #050608;")
        else:
            self.chart_label.setText("Analyzed chart not found.")

    def _update_info_bar(self):
        """Updates info bar with analysis data."""
        if not self.analysis:
            return

        direction = self.analysis.get("direction", "NEUTRAL")
        entry = self.analysis.get("entry", "—")
        sl = self.analysis.get("stop_loss", "—")
        tp = self.analysis.get("take_profit", "—")
        rr = self.analysis.get("risk_reward", "—")

        # Direction badge color
        if direction == "BUY":
            color = "#10b981"
            bg = "#0a1f14"
        elif direction == "SELL":
            color = "#ef4444"
            bg = "#1f0a0a"
        else:
            color = "#94a3b8"
            bg = "#1e2330"

        self.direction_badge.setText(direction)
        self.direction_badge.setStyleSheet(
            f"background: {bg}; color: {color}; "
            f"border-radius: 6px; font-weight: bold; font-size: 13px;")

        # Update chips
        self._set_chip(self.entry_label, "ENTRY", entry, "#00bfff")
        self._set_chip(self.sl_label, "SL", sl, "#ef4444")
        self._set_chip(self.tp_label, "TP", tp, "#10b981")
        self._set_chip(self.rr_label, "R:R", rr, "#f59e0b")

    def _info_chip(self, label, value, color):
        """Creates an info chip widget."""
        widget = QLabel(f"<span style='color:#4a5568;font-size:9px;'>{label}</span>"
                        f"<br><span style='color:{color};font-size:12px;"
                        f"font-weight:bold;'>{value}</span>")
        widget.setStyleSheet("background: transparent;")
        widget.setFixedWidth(90)
        return widget

    def _set_chip(self, widget, label, value, color):
        widget.setText(
            f"<span style='color:#4a5568;font-size:9px;'>{label}</span>"
            f"<br><span style='color:{color};font-size:12px;"
            f"font-weight:bold;'>{value}</span>")

    def _legend_dot(self, color, label):
        w = QLabel(f"● {label}")
        w.setStyleSheet(f"color: {color}; font-size: 11px; background: transparent;")
        return w

    def _vline(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.VLine)
        line.setStyleSheet("color: #1e2330;")
        return line

    def _save_image(self):
        """Saves analyzed chart to user chosen location."""
        from PyQt6.QtWidgets import QFileDialog
        import shutil
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Analyzed Chart", "analyzed_chart.png",
            "PNG Images (*.png);;All Files (*)")
        if path:
            shutil.copy(ANALYZED_IMAGE_PATH, path)

    # --- Drag to move ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = (event.globalPosition().toPoint()
                              - self.frameGeometry().topLeft())

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)