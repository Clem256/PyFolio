import math

from PySide6.QtCore import QObject, Signal

from ..config import CHOICES, DEFAULTS, RANGES


def _coerce(key, value, default):
    """Coerce a value read from data.json to the right type and within bounds, else to the default."""
    if isinstance(default, bool):
        return value if isinstance(value, bool) else default
    if isinstance(default, str):
        value = value if isinstance(value, str) else default
    elif isinstance(default, (int, float)):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            return default
        value = float(value) if isinstance(default, float) else int(value)
    if key in CHOICES and value not in CHOICES[key]:
        return default
    if key in RANGES:
        lo, hi = RANGES[key]
        value = max(lo, min(hi, value))
    return value


def sanitize(raw: dict) -> dict:
    """Complete, valid settings (unknown or old keys discarded)."""
    return {k: _coerce(k, raw.get(k, d), d) for k, d in DEFAULTS.items()}


class Settings(QObject):
    changed = Signal(str, object)

    def __init__(self, storage):
        super().__init__()
        self._storage = storage
        merged = sanitize(storage.data["settings"])
        storage.data["settings"] = merged
        self._d = merged

    def __getitem__(self, key):
        return self._d[key]

    def get(self, key, default=None):
        return self._d.get(key, default)

    def set(self, key, value, notify=True):
        if self._d.get(key) == value:
            return
        self._d[key] = value
        self._storage.schedule_save()
        if notify:
            self.changed.emit(key, value)

    def reset(self, keys):
        for k in keys:
            self.set(k, DEFAULTS[k])
