import time
from pathlib import Path

from ..config import SORT_PROGRESS, SORT_TITLE


def progress_fraction(info: dict) -> float:
    """Fraction read (0 if the book was never started: page 1 = "new")."""
    n, page = info.get("pages", 0), info.get("page", 0)
    return (page + 1) / n if n and page > 0 else 0.0


def _clean_entry(path: str, raw) -> dict:
    """Valid book entry built from what was read in data.json."""
    raw = raw if isinstance(raw, dict) else {}

    def num(key, kind):
        v = raw.get(key, 0)
        return kind(v) if isinstance(v, (int, float)) and not isinstance(v, bool) and v >= 0 else kind(0)

    title = raw.get("title")
    return {"title": title if isinstance(title, str) and title.strip() else Path(path).stem,
            "page": num("page", int), "pages": num("pages", int),
            "last_opened": num("last_opened", float)}


class Library:
    def __init__(self, storage):
        self._storage = storage
        # Same dict as in storage (modified in place, then saved).
        self._books = storage.data["books"]
        for p in list(self._books):
            self._books[p] = _clean_entry(p, self._books[p])
        self._exists = {}

    # --- file presence (cached: one exists() per book on every keystroke is slow,
    # especially on a network drive) ---
    def _present(self, path: str) -> bool:
        if path not in self._exists:
            self._exists[path] = Path(path).exists()
        return self._exists[path]

    def rescan(self):
        """Forget the presence cache (call when returning to the library)."""
        self._exists.clear()

    def missing(self) -> list:
        return [p for p in self._books if not self._present(p)]

    def prune_missing(self) -> int:
        gone = self.missing()
        for p in gone:
            self._books.pop(p, None)
            self._exists.pop(p, None)
        if gone:
            self._storage.schedule_save()
        return len(gone)

    # --- reading ---
    def __contains__(self, path: str) -> bool:
        return path in self._books

    def info(self, path: str) -> dict:
        return self._books[path]

    def title(self, path: str) -> str:
        return self._books[path].get("title", Path(path).stem)

    def count(self) -> int:
        return sum(1 for p in self._books if self._present(p))

    def entries(self, sort: int = 0, text: str = ""):
        q = text.strip().lower()
        books = [(p, i) for p, i in self._books.items()
                 if self._present(p) and q in i.get("title", Path(p).stem).lower()]
        if sort == SORT_TITLE:
            books.sort(key=lambda kv: kv[1].get("title", Path(kv[0]).stem).lower())
        elif sort == SORT_PROGRESS:
            books.sort(key=lambda kv: progress_fraction(kv[1]), reverse=True)
        else:
            books.sort(key=lambda kv: kv[1].get("last_opened", 0), reverse=True)
        return books

    def last_opened(self):
        recent = [(i.get("last_opened", 0), p) for p, i in self._books.items()
                  if i.get("last_opened", 0) > 0 and self._present(p)]
        return max(recent)[1] if recent else None

    # --- writing ---
    def register(self, path: str, pages: int = 0) -> str:
        """Add a book without opening the file (the page count is filled in afterwards)."""
        path = str(Path(path).resolve())
        if path not in self._books:
            self._books[path] = {"title": Path(path).stem, "page": 0,
                                 "pages": pages, "last_opened": 0.0}
            self._exists[path] = True
            self._storage.schedule_save()
        return path

    def set_pages(self, path: str, pages: int):
        if path in self._books and pages > 0 and self._books[path].get("pages") != pages:
            self._books[path]["pages"] = pages
            self._storage.schedule_save()

    def remove(self, path: str):
        self._books.pop(path, None)
        self._exists.pop(path, None)
        self._storage.schedule_save()

    def rename(self, path: str, title: str):
        self._books[path]["title"] = title
        self._storage.schedule_save()

    def reset_progress(self, path: str):
        self.set_page(path, 0)

    def set_page(self, path: str, page: int):
        if path in self._books:
            self._books[path]["page"] = page
            self._storage.schedule_save()

    def mark_opened(self, path: str, pages: int):
        info = self._books[path]
        info["pages"] = pages
        info["last_opened"] = time.time()
        self._storage.schedule_save()
