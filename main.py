"""
Advance Editor — AI-Powered Photo Editor
Entry point. Handles both development and frozen (.exe) environments.
"""
import sys
import os

# ── Frozen (.exe) path resolution ─────────────────────────────
# When running as PyInstaller bundle, __file__ is inside _MEIPASS temp dir.
# We need to add the original project root so engine/ui imports work.
if getattr(sys, 'frozen', False):
    # Running as compiled .exe
    BASE_DIR = sys._MEIPASS
    # Set HuggingFace cache inside the user's AppData so models persist across runs
    os.environ.setdefault(
        "TRANSFORMERS_CACHE",
        os.path.join(os.path.expanduser("~"), ".cache", "advance_editor", "models")
    )
    os.environ.setdefault(
        "HF_HOME",
        os.path.join(os.path.expanduser("~"), ".cache", "advance_editor")
    )
else:
    # Running in development
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, BASE_DIR)

# ── Qt High DPI & Platform ────────────────────────────────────
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

# Fix OpenCV / ONNX Runtime DLL loading on Windows
if sys.platform == "win32":
    os.add_dll_directory(BASE_DIR) if hasattr(os, "add_dll_directory") else None

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Advance Editor")
    app.setOrganizationName("AdvanceEditor")
    app.setApplicationVersion("3.0")

    # Premium font
    font = QFont("Segoe UI", 10)
    font.setHintingPreference(QFont.HintingPreference.PreferFullHinting)
    app.setFont(font)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
