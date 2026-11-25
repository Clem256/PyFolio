import os
import sys
from pathlib import Path

os.environ.setdefault("QT_LOGGING_RULES", "qt.qpa.wayland.textinput=false")

from PySide6.QtWidgets import QApplication, QMessageBox  # noqa: E402

from . import config  # noqa: E402
from .core.library import Library  # noqa: E402
from .core.settings import Settings  # noqa: E402
from .core.storage import Storage  # noqa: E402
from .ui.main_window import MainWindow  # noqa: E402


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("PyFolio")

    config.ensure_dirs()
    storage = Storage()
    settings = Settings(storage)
    library = Library(storage)

    win = MainWindow(storage, settings, library)
    win.show()

    if storage.recovered_from:
        QMessageBox.warning(
            win, "Données illisibles",
            "Le fichier de bibliothèque était illisible. Il a été conservé ici :\n"
            f"{storage.recovered_from}\n\nPyFolio repart d'une bibliothèque vide.")

    if len(sys.argv) > 1 and Path(sys.argv[1]).is_file():
        win.open_book(sys.argv[1])
    elif settings["reopen_last"]:
        last = library.last_opened()
        if last:
            win.open_book(last)
    sys.exit(app.exec())
