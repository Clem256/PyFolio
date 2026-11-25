import json
import time

from PySide6.QtCore import QTimer

from .. import config


class Storage:
    SAVE_DELAY_MS = 600

    def __init__(self, path=None):
        self.path = path or config.DATA_FILE
        self.data = {"settings": {}, "books": {}}
        # Set if the existing file was unreadable (it is then set aside, not overwritten).
        self.recovered_from = None
        self.last_error = None
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.setInterval(self.SAVE_DELAY_MS)
        self._timer.timeout.connect(self.flush)
        self._load()

    def _quarantine(self):
        """Rename the unreadable file so the next save does not overwrite it."""
        target = self.path.with_name(f"{self.path.name}.corrupt-{time.strftime('%Y%m%d-%H%M%S')}")
        try:
            self.path.replace(target)
            self.recovered_from = target
        except OSError:
            self.recovered_from = self.path

    def _load(self):
        if not self.path.exists():
            return
        try:
            loaded = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(loaded, dict):
                raise ValueError("racine JSON inattendue")
            st = loaded.get("settings", {})
            books = loaded.get("books", {})
            if not isinstance(st, dict) or not isinstance(books, dict):
                raise ValueError("structure JSON inattendue")
        except (ValueError, OSError):  # JSONDecodeError and UnicodeDecodeError inherit from ValueError
            self._quarantine()
            return

        if "theme" not in st and "night" in st:
            st["theme"] = "dark" if st["night"] else "light"
        if "fit_mode" not in st and "fit" in st:
            st["fit_mode"] = "page" if st["fit"] else "zoom"
        self.data["settings"] = st
        self.data["books"] = books

    def schedule_save(self):
        self._timer.start()

    def flush(self):
        self._timer.stop()
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_suffix(".tmp")
            tmp.write_text(json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8")
            tmp.replace(self.path)
            self.last_error = None
        except OSError as e:
            # Disk full, read-only folder…: don't crash, we'll retry.
            self.last_error = e
