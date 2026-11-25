import hashlib
import threading
from pathlib import Path

import pymupdf

from .. import config

# PyMuPDF is not thread-safe: every access (rendering, opening, background covers)
# goes through this lock. It is reentrant, so it can be nested safely.
MUPDF_LOCK = threading.RLock()


class NeedsPassword(Exception):
    """The PDF is protected and no password (or a wrong one) was provided."""


def open_document(path: str) -> pymupdf.Document:
    with MUPDF_LOCK:
        return pymupdf.open(path)


def page_count(path: str) -> int:
    try:
        with MUPDF_LOCK, pymupdf.open(path) as d:
            return 0 if d.needs_pass else d.page_count
    except Exception:
        return 0


def cover_file(path: str) -> Path:
    """Location of the cached cover (reads and creates nothing)."""
    return config.CACHE_DIR / (hashlib.md5(path.encode()).hexdigest() + "_400.png")


def make_cover(path: str):
    """Generate the cover if needed. Return its path, or None (protected, empty or unreadable PDF)."""
    f = cover_file(path)
    if f.exists():
        return f
    try:
        with MUPDF_LOCK, pymupdf.open(path) as d:
            if d.needs_pass or d.page_count == 0:
                return None
            p = d[0]
            z = 400 / p.rect.height
            f.parent.mkdir(parents=True, exist_ok=True)
            p.get_pixmap(matrix=pymupdf.Matrix(z, z), alpha=False).save(str(f))
    except Exception:
        return None
    return f


def clear_cover_cache():
    for f in config.CACHE_DIR.glob("*.png"):
        f.unlink(missing_ok=True)


def clean_copy(src: str, dst: str, password: str = None):
    """Save a copy without JavaScript, attachments or automatic actions.

    Raises NeedsPassword if the PDF is protected (missing or wrong password) and
    ValueError if the destination is the source file.
    """
    if Path(src).resolve() == Path(dst).resolve():
        raise ValueError("Choisissez un autre fichier que l'original.")
    with MUPDF_LOCK, pymupdf.open(src) as d:
        if d.needs_pass and not d.authenticate(password or ""):
            raise NeedsPassword(src)
        d.scrub(
            javascript=True,
            attached_files=True,
            embedded_files=True,
            reset_fields=True,
            reset_responses=True,
            remove_links=True,
            hidden_text=False,
        )
        cat = d.pdf_catalog()
        for key in ("OpenAction", "AA"):
            d.xref_set_key(cat, key, "null")
        d.save(dst, garbage=4, deflate=True)
