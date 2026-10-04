import sys
import traceback
from datetime import datetime
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import QFontDatabase, QFont
from PySide6.QtCore import Qt
from database import init_db, SessionLocal, BASE_DIR
from ui.login import LoginDialog
from ui.dashboard import Dashboard
from ui.theme import QSS

LOG_FILE = BASE_DIR / "error_log.txt"


def install_error_handler(app):
    """Show any unexpected error in a popup (with the real message) instead of letting it
    disappear silently in a console window, and also keep a log file for later review."""
    def handle(exc_type, exc_value, exc_tb):
        text = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"\n--- {datetime.now().isoformat()} ---\n{text}\n")
        except Exception:
            pass
        box = QMessageBox()
        box.setIcon(QMessageBox.Critical)
        box.setWindowTitle("خطای غیرمنتظره")
        box.setText("یک خطا رخ داد. جزئیات زیر را برای بررسی می‌توانید کپی یا ارسال کنید:")
        box.setDetailedText(text)
        box.exec()
    sys.excepthook = handle


def load_fonts():
    font_dir = BASE_DIR / "fonts"
    family = None
    for f in font_dir.glob("*.ttf"):
        fid = QFontDatabase.addApplicationFont(str(f))
        if fid != -1:
            families = QFontDatabase.applicationFontFamilies(fid)
            if families:
                family = families[0]
    return family


def main():
    app = QApplication(sys.argv)
    install_error_handler(app)
    app.setLayoutDirection(Qt.RightToLeft)
    family = load_fonts()
    if family:
        app.setFont(QFont(family, 10))
    app.setStyleSheet(QSS)

    init_db()

    login = LoginDialog(SessionLocal)
    if login.exec():
        window = Dashboard(SessionLocal, login.accepted_user)
        window.show()
        sys.exit(app.exec())


if __name__ == "__main__":
    main()
