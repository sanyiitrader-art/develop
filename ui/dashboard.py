
import sys
import pyttsx3
from pathlib import Path
from PyQt6.QtCore import Qt, QPoint, QTimer
from PyQt6.QtWidgets import (QMainWindow, QWidget, QPushButton, QVBoxLayout, 
                             QHBoxLayout, QLabel, QStackedWidget, QTextEdit)
from PyQt6.QtGui import QIcon, QPixmap

# Pull live execution modules smoothly across your local architecture
from core.capture import capture_live_screen
from core.analyser import ChartVisionAnalyser
from core.drawer import ChartDrawingEngine
from core.history import LocalHistoryManager
from ui.analysis_panel import ChartAnalysisImagePanel

class FloatingAssistantButton(QWidget):
    """
    A small borderless overlay bubble that floats permanently on top 
    of external trading windows (MT5 / TradingView) on Windows 11.
    """
    def __init__(self, parent_dashboard):
        super().__init__()
        self.main_app = parent_dashboard
        self.init_ui()
        self.drag_position = QPoint()

    def init_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                            Qt.WindowType.WindowStaysOnTopHint | 
                            Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(60, 60)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.btn = QPushButton(self)
        self.btn.setObjectName("FloatAssistantButton")
        self.btn.setFixedSize(50, 50)
        
        icon_path = Path(__file__).resolve().parent.parent / "assets" / "icons" / "float_button.png"
        if icon_path.exists():
            self.btn.setIcon(QIcon(str(icon_path)))
            self.btn.setIconSize(self.btn.size() * 0.6)
            
        self.btn.clicked.connect(self.trigger_live_scan)
        layout.addWidget(self.btn, alignment=Qt.AlignmentFlag.AlignCenter)

    def trigger_live_scan(self):
        self.hide()
        QTimer.singleShot(400, self.execute_capture_sequence)

    def execute_capture_sequence(self):
        # 1. Capture primary display workspace coordinates
        saved_img_path = capture_live_screen("live_chart.png")
        
        # 2. Trigger native Windows TTS sound confirmation
        try:
            tts_engine = pyttsx3.init()
            tts_engine.setProperty('rate', 160)
            tts_engine.say("Successfully scanned")
            tts_engine.runAndWait()
        except Exception as e:
            print(f"[Audio Error] TTS failed to execute: {e}")

        # 3. Bring back the main dashboard interface layout frames and process data
        self.main_app.process_captured_chart(saved_img_path)
        self.show()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()


class MainDashboard(QMainWindow):
    """
    The master desktop frame layout for ChartMind AI. Manages view structures, 
    historical layout storage routing, and processes multi-option output choices.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChartMind AI — Institutional Trading Analyser")
        self.resize(1100, 750)
        
        # Instantiate system module helper components
        self.analyser_engine = ChartVisionAnalyser()
        self.drawing_engine = ChartDrawingEngine()
        self.history_engine = LocalHistoryManager()
        
        self.floating_widget = FloatingAssistantButton(self)
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        master_layout = QVBoxLayout(central_widget)

        # Top Control Bar Layout
        top_bar = QHBoxLayout()
        self.title_lbl = QLabel("CHARTMIND AI // CORE ENGINE")
        self.title_lbl.setStyleSheet("font-weight: bold; color: #38BDF8; font-size: 16px;")
        
        self.minimize_to_float_btn = QPushButton("Launch Float Assistant Over Trading Screen")
        self.minimize_to_float_btn.setStyleSheet("background-color: #0369A1; padding: 8px; border-radius: 4px; font-weight: bold;")
        self.minimize_to_float_btn.clicked.connect(self.enter_floating_mode)
        
        top_bar.addWidget(self.title_lbl)
        top_bar.addStretch()
        top_bar.addWidget(self.minimize_to_float_btn)
        master_layout.addLayout(top_bar)

        # Multi-Option Interface Execution Routing Selectors
        options_layout = QHBoxLayout()
        self.btn_img = QPushButton("See Analysis Result: Image")
        self.btn_word = QPushButton("See Analysis Result: Description")
        self.btn_signal = QPushButton("See Analysis Result: Direct Signal")

        self.btn_img.setObjectName("ViewImageOption")
        self.btn_word.setObjectName("ViewWordOption")
        self.btn_signal.setObjectName("ViewSignalOption")

        for b in [self.btn_img, self.btn_word, self.btn_signal]:
            b.setProperty("class", "ActionOptionButton")
            options_layout.addWidget(b)
            
        master_layout.addLayout(options_layout)

        # Core Stacked Interior View Engine (Like browser tabs for layout views)
        self.stacked_view = QStackedWidget()
        master_layout.addWidget(self.stacked_view)

        # View Card 1: Custom Structural Image Panel (Loads code from ui/analysis_panel.py)
        self.image_panel_view = ChartAnalysisImagePanel()
        self.stacked_view.addWidget(self.image_panel_view)

        # View Card 2: Micro-Structured Multi-Page Text Block Area
        self.text_display_field = QTextEdit()
        self.text_display_field.setObjectName("DeepAnalysisDisplay")
        self.text_display_field.setReadOnly(True)
        self.text_display_field.setText("No active session analysis indexed. Run a scan via the float assistant button bubble.")
        self.stacked_view.addWidget(self.text_display_field)

        # View Card 3: Single Word Macro Verdict Panel
        self.verdict_display_lbl = QLabel("WAIT")
        self.verdict_display_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.verdict_display_lbl.setStyleSheet("font-size: 84px; font-weight: 900; color: #64748B; background: #020617; border-radius: 8px;")
        self.stacked_view.addWidget(self.verdict_display_lbl)

        # Assign button tracking mechanics to the stacked screen integer layout index numbers
        self.btn_img.clicked.connect(lambda: self.stacked_view.setCurrentIndex(0))
        self.btn_word.clicked.connect(lambda: self.stacked_view.setCurrentIndex(1))
        self.btn_signal.clicked.connect(lambda: self.stacked_view.setCurrentIndex(2))

    def enter_floating_mode(self):
        self.hide()
        self.floating_widget.move(100, 100)
        self.floating_widget.show()

    def process_captured_chart(self, raw_screenshot_path: str):
        """
        Runs the full backend automation stack: transmits images upstream to Claude, 
        paints geometric risk parameter overlays, updates GUI tabs, and saves logs.
        """
        self.show()
        if not raw_screenshot_path:
            return

        # 1. Execute live Claude Vision API network parsing pipeline
        ai_result = self.analyser_engine.run_vision_analysis(raw_screenshot_path)
        verdict = ai_result.get("verdict", "NEUTRAL")
        description = ai_result.get("description", "")

        # 2. Pass textual output to geometric engine to draw risk parameter boxes
        analyzed_image_path = self.drawing_engine.apply_geometric_overlay(raw_screenshot_path, description)

        # 3. Save session parameters into local history logs database
        self.history_engine.log_analysis_session(verdict, description, raw_screenshot_path)

        # 4. Refresh GUI Text Fields with deep word description data streams
        self.text_display_field.setText(description)
        
        # 5. Refresh GUI Macro Verdict Panel Styles
        self.verdict_display_lbl.setText(verdict)
        if verdict == "BUY":
            self.verdict_display_lbl.setStyleSheet("font-size: 84px; font-weight: 900; color: #10B981; background: #020617; border-radius: 8px;")
        elif verdict == "SELL":
            self.verdict_display_lbl.setStyleSheet("font-size: 84px; font-weight: 900; color: #EF4444; background: #020617; border-radius: 8px;")
        else:
            self.verdict_display_lbl.setStyleSheet("font-size: 84px; font-weight: 900; color: #64748B; background: #020617; border-radius: 8px;")

        # 6. Pass generated output target path to image panel to force rendering
        self.image_panel_view.display_analyzed_chart(analyzed_image_path)
        self.stacked_view.setCurrentIndex(0) # Automatically shift view to image display card upon capture completion