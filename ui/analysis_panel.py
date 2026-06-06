from pathlib import Path
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QPixmap

class ChartAnalysisImagePanel(QWidget):
    """
    A dedicated visual layout component that displays the final image 
    with custom geometric trade setups (Entry, TP, SL lines).
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        # Establish a clean layout environment for the visual wrapper
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Core container label designed to safely project image frames
        self.image_container = QLabel("No active chart analysis loaded. Initialize a scan using the floating overlay bubble.")
        self.image_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Match the institutional sleek dark panel styling from styles.qss
        self.image_container.setStyleSheet(
            "border: 2px dashed #1E293B; "
            "border-radius: 8px; "
            "background-color: #020617; "
            "color: #64748B; "
            "font-weight: 500;"
        )
        
        layout.addWidget(self.image_container)

    def display_analyzed_chart(self, image_path: str):
        """
        Safely loads the newly drawn PNG file from disk, handles monitor scaling,
        and paints it cleanly inside the application viewport frame.
        """
        if not image_path or not Path(image_path).exists():
            self.image_container.setText("[File Error] Unable to trace the visual analysis file on disk storage.")
            return

        try:
            # Load raw pixel matrix via system memory frame paths
            pixmap = QPixmap(image_path)
            
            if not pixmap.isNull():
                # Scale image proportionally based on screen size layout constraints
                scaled_pixmap = pixmap.scaled(
                    self.image_container.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.image_container.setPixmap(scaled_pixmap)
                # Clear structural text layout padding frames
                self.image_container.setStyleSheet("border: 1px solid #1E293B; border-radius: 8px; background-color: #020617;")
            else:
                self.image_container.setText("[Render Error] Chart image asset corrupted or unreadable.")
        except Exception as e:
            print(f"[Panel Error] Failed to map image data stream to interface: {e}")
            self.image_container.setText(f"[System Error] Layout rendering engine failure: {e}")

    def clear_panel(self):
        """Resets the container back to its original clean state profile."""
        self.image_container.clear()
        self.image_container.setText("Chart analysis history flushed. Awaiting live workspace execution scan input parameters.")
        self.image_container.setStyleSheet("border: 2px dashed #1E293B; border-radius: 8px; background-color: #020617; color: #64748B;")