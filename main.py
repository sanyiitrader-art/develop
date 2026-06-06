import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from ui.dashboard import MainDashboard

def load_stylesheet(app_instance: QApplication, stylesheet_path: Path):
    """
    Safely reads the QSS style sheet file and applies it globally 
    to the entire desktop application interface.
    """
    if stylesheet_path.exists():
        with open(stylesheet_path, "r", encoding="utf-8") as f:
            app_instance.setStyleSheet(f.read())
    else:
        print(f"[Warning] Stylesheet not found at: {stylesheet_path}")
        print("Application will load using default Windows OS styling.")

def main():
    """
    The master entry point for ChartMind AI. Sets up system configurations,
    mounts the UI components, and starts the core event cycle.
    """
    # 1. Initialize the application engine
    app = QApplication(sys.argv)
    
    # 2. Define internal filesystem paths
    base_dir = Path(__file__).resolve().parent
    qss_path = base_dir / "ui" / "styles.qss"
    
    # 3. Apply custom dark institutional CSS layout styling
    load_stylesheet(app, qss_path)
    
    # 4. Initialize and show the main dashboard window frame
    window = MainDashboard()
    window.show()
    
    # 5. Execute application loop and pass the termination signal to the OS
    sys.exit(app.exec())

if __name__ == "__main__":
    main()