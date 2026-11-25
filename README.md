<p align="center">
  <img src="assets/banner.svg" alt="PyFolio" width="480">
</p>

# PyFolio

A lightweight desktop PDF reader and library manager, built with Python, PySide6 (Qt) and PyMuPDF.

## Features

- **Library** – add PDFs, see covers and reading progress, search, and sort by recent, title or progress. Adding books is instant: page counts and covers are generated in the background.
- **Reader** – single or double-page view, fit to page / width / custom zoom, right-to-left mode, click-zone and mouse-wheel page turning, optional page shadow.
- **Table of contents** – dockable outline panel (toggle with `T`).
- **Light and dark themes.**
- **Resume where you left off** – reading position is saved per book, and the last book can be reopened at launch.
- **Clean export** – save a copy of a PDF without JavaScript, attachments or automatic actions (`Ctrl+E`).
- **Password-protected PDFs** are supported.
- **Resilient storage** – an unreadable `data.json` is set aside rather than overwritten, and out-of-range settings fall back to safe defaults.

## Requirements

- Python 3
- [PySide6](https://pypi.org/project/PySide6/)
- [PyMuPDF](https://pypi.org/project/PyMuPDF/)
- [platformdirs](https://pypi.org/project/platformdirs/)

## Installation

```bash
git clone https://github.com/Clem256/PyFolio
cd PyFolio
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```bash
python run.py                    # or: python -m pyfolio
python run.py path/to/book.pdf   # open a PDF directly
```

### Keyboard shortcuts

| Shortcut | Action |
| --- | --- |
| `Ctrl` + `+` / `Ctrl` + `-` | Zoom in / out |
| `T` | Toggle the table of contents |
| `Ctrl` + `E` | Export a cleaned copy of the current PDF |
| `Ctrl` + `,` | Open settings |
| `←` / `→`, `PgUp` / `PgDown`, `Backspace` / `Space` | Previous / next page (arrows are swapped in right-to-left mode) |

## Data and configuration

PyFolio stores its library, settings and cached covers in your system's per-user data directory (via `platformdirs`). To use another location — for a portable install or for tests — set the `PYFOLIO_DATA_DIR` environment variable:

```bash
PYFOLIO_DATA_DIR=./data python run.py
```

## Project structure

```
pyfolio/
├── app.py            # application entry point
├── config.py         # paths, defaults and allowed value ranges
├── core/             # UI-independent logic
│   ├── library.py    #   book entries, progress, search
│   ├── pdf_tools.py  #   PyMuPDF access, covers, clean export
│   ├── reader_state.py
│   ├── settings.py
│   └── storage.py    #   JSON persistence
└── ui/               # Qt interface
    ├── main_window.py
    ├── library_page.py
    ├── reader_page.py
    ├── settings_dialog.py
    └── ...
```

## Notes

PyMuPDF is not thread-safe, so every access to it goes through a single re-entrant lock and background work (page counts, covers) runs on one worker thread.
