import os
import shutil
from pathlib import Path

from platformdirs import user_data_dir

# Data folder: the system's per-user data directory (can be overridden with
# the PYFOLIO_DATA_DIR environment variable, useful for a portable version or for tests).
APP_DIR = Path(os.environ.get("PYFOLIO_DATA_DIR") or user_data_dir("PyFolio", appauthor=False))
CACHE_DIR = APP_DIR / "covers"
DATA_FILE = APP_DIR / "data.json"

# Old location (inside the code): migrated automatically on first launch.
LEGACY_DIR = Path(__file__).resolve().parent / "saved_data"


def ensure_dirs():
    """Create the data folders and import the old library if there is one."""
    APP_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    legacy = LEGACY_DIR / "data.json"
    if legacy.is_file() and not DATA_FILE.exists():
        try:
            shutil.copy2(legacy, DATA_FILE)
        except OSError:
            pass


PAGE_MARGIN = 22
CARD_W, CARD_H = 184, 300

# Pixel cap when rendering a page (or a double page)
MAX_RENDER_PIXELS = 36_000_000

THEME_NAMES = ("light", "dark")
FIT_MODES = ("page", "width", "zoom")

SORT_RECENT, SORT_TITLE, SORT_PROGRESS = 0, 1, 2

DEFAULTS = {
    "theme": "dark", "double": False, "fit_mode": "page", "zoom": 1.2,
    "sort": SORT_RECENT, "geometry": "",
    "font_size": 10,
    "shadow": True,
    "rtl": False,
    "click_nav": True,
    "click_zone": 30,
    "wheel_turns": True,
    "zoom_step": 15,
    "hide_chrome_on_open": False,
    "reopen_last": False,
}

# Allowed values (an out-of-range value in data.json is reset to the default / clamped).
CHOICES = {
    "theme": THEME_NAMES,
    "fit_mode": FIT_MODES,
    "sort": (SORT_RECENT, SORT_TITLE, SORT_PROGRESS),
}
RANGES = {
    "zoom": (0.2, 6.0),
    "zoom_step": (5, 50),
    "click_zone": (10, 45),
    "font_size": (8, 16),
}
