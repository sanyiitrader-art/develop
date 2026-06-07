import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt


def main():
    # Enable high DPI scaling for Windows 11
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    app = QApplication(sys.argv)
    app.setApplicationName("ChartMind AI")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("ChartMind")

    # Global font
    font = QFont("Arial", 12)
    app.setFont(font)

    # Load global stylesheet
    qss_path = os.path.join(os.path.dirname(__file__), "ui", "styles.qss")
    if os.path.exists(qss_path):
        with open(qss_path, "r") as f:
            app.setStyleSheet(f.read())

    # App icon
    icon_path = os.path.join(
        os.path.dirname(__file__), "assets", "icons", "app_icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Launch dashboard
    from ui.dashboard import Dashboard
    window = Dashboard()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()