from PySide6.QtCore import QObject, QRunnable, Signal

from ..core import pdf_tools


class _Signals(QObject):
    done = Signal(str, int)   # path, page count (0 if unreadable or protected)


class PrepareTask(QRunnable):
    """Count the pages and prepare the cover of a PDF, off the UI thread."""

    def __init__(self, path: str, signals: _Signals):
        super().__init__()
        self.path = path
        self.signals = signals

    def run(self):
        pages = pdf_tools.page_count(self.path)
        pdf_tools.make_cover(self.path)
        self.signals.done.emit(self.path, pages)
