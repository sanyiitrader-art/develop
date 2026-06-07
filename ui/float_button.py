from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel, QApplication
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPoint, QTimer
from PyQt6.QtGui import QFont
from core.capture import capture_screen_live
from core.sound import play_scanning, play_success, play_error
from config import CAPTURE_DURATION


class ScanWorker(QThread):
    """
    Runs screen capture countdown in background thread.
    """
    progress = pyqtSignal(int)   # seconds remaining
    finished = pyqtSignal(str)   # image path when done
    error = pyqtSignal(str)      # error message

    def __init__(self):
        super().__init__()
        self.stop_flag = [False]

    def run(self):
        try:
            path = capture_screen_live(
                progress_callback=lambda s: self.progress.emit(s),
                stop_flag=self.stop_flag
            )
            self.finished.emit(path)
        except Exception as e:
            self.error.emit(str(e))

    def stop(self):
        self.stop_flag[0] = True


class FloatButton(QWidget):
    """
    Always-on-top floating button.
    Starts countdown on click, captures screen, emits result.
    """
    scan_complete = pyqtSignal(str)  # emits image path to dashboard

    def __init__(self):
        super().__init__()
        self.scan_worker = None
        self.is_scanning = False
        self._drag_pos = QPoint()
        self._init_ui()

    def _init_ui(self):
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(110, 120)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Main button
        self.btn = QPushButton("📊\nSCAN")
        self.btn.setFixedSize(100, 100)
        self.btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.btn.clicked.connect(self._on_click)
        self._set_idle_style()

        # Countdown label
        self.progress_label = QLabel("")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_label.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        self.progress_label.setStyleSheet(
            "color: #f59e0b; background: transparent;")
        self.progress_label.setFixedWidth(110)

        layout.addWidget(self.btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.progress_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

        # Position bottom right
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - 130, screen.height() - 200)

    def _on_click(self):
        if self.is_scanning:
            self._stop_scan()
        else:
            self._start_scan()

    def _start_scan(self):
        self.is_scanning = True
        self._set_scanning_style()
        self.progress_label.setText(f"{CAPTURE_DURATION}s")
        play_scanning()

        self.scan_worker = ScanWorker()
        self.scan_worker.progress.connect(self._on_progress)
        self.scan_worker.finished.connect(self._on_finished)
        self.scan_worker.error.connect(self._on_error)
        self.scan_worker.start()

    def _stop_scan(self):
        if self.scan_worker:
            self.scan_worker.stop()
        self._reset()

    def _on_progress(self, seconds_remaining):
        if seconds_remaining > 0:
            self.progress_label.setText(f"{seconds_remaining}s")
        else:
            self.progress_label.setText("📸")

    def _on_finished(self, image_path):
        play_success()
        self.progress_label.setText("✓")
        self._reset()

        # Emit to dashboard after short delay
        QTimer.singleShot(300, lambda: self.scan_complete.emit(image_path))

    def _on_error(self, error_msg):
        play_error()
        self.progress_label.setText("✗")
        self._reset()
        print(f"[FloatButton] Error: {error_msg}")

    def _reset(self):
        self.is_scanning = False
        self._set_idle_style()
        self.btn.setText("📊\nSCAN")
        QTimer.singleShot(2000, lambda: self.progress_label.setText(""))

    def _set_idle_style(self):
        self.btn.setStyleSheet("""
            QPushButton {
                background: qradialgradient(
                    cx:0.5, cy:0.5, radius:0.5,
                    fx:0.5, fy:0.5,
                    stop:0 #1a1a2e,
                    stop:1 #16213e
                );
                color: #f59e0b;
                border: 2px solid #f59e0b;
                border-radius: 50px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #f59e0b;
                color: #000000;
            }
        """)

    def _set_scanning_style(self):
        self.btn.setText("⏹\nSTOP")
        self.btn.setStyleSheet("""
            QPushButton {
                background: #1a0000;
                color: #ef4444;
                border: 2px solid #ef4444;
                border-radius: 50px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #ef4444;
                color: #ffffff;
            }
        """)

    # Drag to move
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = (event.globalPosition().toPoint()
                              - self.frameGeometry().topLeft())

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)