# PyInstaller-Helper

**Turn any Python script into a proper installable app — one file, one command.**

No packaging knowledge required. Copy `build.py` into your project, fill in 8 values at the top, run it. You get a distributable app that runs on any machine without Python installed.

| Platform | Output |
|----------|--------|
| macOS    | `dist/AppName.dmg` — double-click installer, drag to Applications |
| Windows  | `dist/AppName/AppName.exe` — zip the folder and send it |
| Linux    | `dist/AppName-x86_64.AppImage` — single portable file |

---

## Quick Start

```bash
# 1. Copy build.py into your project folder
cp build.py /path/to/your/project/

# 2. Edit the CONFIG section at the top of build.py (see below)

# 3. Run it
cd /path/to/your/project
python3 build.py
```

Your output file appears in `dist/` when it's done. That's it.

---

## What File Goes Where

Your project folder should look like this **before** you run the build:

```
YourProject/
    your_main_script.py     ← the script you normally run with "python3"
    build.py                ← copied from this repo  ← YOU ADD THIS
    icon.icns               ← optional, macOS app icon
    icon.ico                ← optional, Windows app icon
    assets/                 ← any images, sounds, fonts your app uses
    config.json             ← any data files your app reads at runtime
```

**Rule:** `build.py` must live in the same folder as your entry script. Not in a subfolder. Same level.

After the build runs, you'll also have:

```
YourProject/
    dist/
        AppName.dmg         ← macOS: this is what you send people
        AppName.app         ← macOS: the raw app bundle (the .dmg wraps this)
    build/                  ← working files, safe to delete
```

---

## The CONFIG Section — Every Option Explained

Open `build.py`. Near the top is the CONFIG block. This is the **only part you need to edit.** Everything below it is automatic.

```python
# ── CONFIG — edit this section for your project ──────────────────
APP_NAME    = "MyApp"
ENTRY_POINT = "main.py"
VERSION     = "1.0.0"
BUNDLE_ID   = "com.yourname.myapp"
WINDOWED    = True
ICON_MAC    = None
ICON_WIN    = None
EXTRA_DATA  = []
HIDDEN_IMPORTS = []
EXCLUDES    = []
# ─────────────────────────────────────────────────────────────────
```

### `APP_NAME`

The name of your finished app. This is what shows up in Finder / File Explorer / the Dock.

```python
APP_NAME = "DartVader"
APP_NAME = "Music Organizer"
APP_NAME = "Budget Tracker"
APP_NAME = "My Photo Tool"   # spaces are fine
```

---

### `ENTRY_POINT`

The Python file that starts your app — the one you normally run with `python3 <file>`. Must be in the same folder as `build.py`.

```python
ENTRY_POINT = "main.py"
ENTRY_POINT = "maingame.py"
ENTRY_POINT = "app.py"
ENTRY_POINT = "organize_music_gui.py"
```

---

### `VERSION`

Your app's version number, shown in macOS "Get Info". Use `"1.0.0"` if you're just starting out.

```python
VERSION = "1.0.0"
VERSION = "2.3.1"
```

---

### `BUNDLE_ID`

A unique identifier for your app on macOS. **macOS only** — Windows and Linux ignore this.

Format: `com.yourname.appname` — all lowercase, dots between sections, no spaces or special characters.

```python
BUNDLE_ID = "com.greenland.dartvader"
BUNDLE_ID = "com.greenland.musicorganizer"
BUNDLE_ID = "com.smith.budgettracker"
```

---

### `WINDOWED`

Controls whether a terminal/console window appears when the app runs.

```python
WINDOWED = True    # GUI app — opens as a normal window, no terminal behind it
                   # ← use this for tkinter, PyQt5, wxPython, or any windowed app

WINDOWED = False   # CLI tool — a terminal window appears so users can see output
                   # ← use this for scripts that print results to the console
```

**When in doubt: if your app has a window, use `True`.**

---

### `ICON_MAC` and `ICON_WIN`

Your app icon. Set to `None` to use the default Python icon.

```python
ICON_MAC = "icon.icns"    # macOS — .icns format, put file in project folder
ICON_WIN = "icon.ico"     # Windows — .ico format, put file in project folder
ICON_MAC = None           # no custom icon — Python's default icon will be used
```

#### Icon Format Quick Reference

Each platform requires a **different file format**. You cannot use the same file for all platforms. You need to convert your image into the right format for each OS.

| Platform | Required Format | Extension | Minimum Source Size | Where to Put It |
|----------|----------------|-----------|--------------------|--------------:|
| macOS    | Apple Icon Image | `.icns` | 512×512 px PNG | Project folder (same level as `build.py`) |
| Windows  | Windows Icon | `.ico` | 256×256 px PNG | Project folder (same level as `build.py`) |
| Linux    | PNG image | `.png` | 256×256 px | Not used by `build.py` directly — set automatically |

> **Key rule:** You cannot hand PyInstaller a `.png` or `.jpg` and expect it to become an icon. You must convert it first.

#### Creating a .icns for macOS

Open Terminal and run this one command (your source PNG should be at least 512×512 pixels):

```bash
sips -s format icns your-image.png --out icon.icns
```

That creates `icon.icns` in the same folder. Then set `ICON_MAC = "icon.icns"` in the CONFIG.

#### Creating a .ico for Windows

- **Easiest (free online):** Go to https://www.favicon.io/favicon-converter/ — upload your PNG, download the `.ico` file
- **GIMP:** File → Export As → name the file `icon.ico` → click Export → Save
- **On Mac with ImageMagick installed:** `magick convert your-image.png -resize 256x256 icon.ico`

Then set `ICON_WIN = "icon.ico"` in the CONFIG.

#### Common icon mistakes

- Setting `ICON_MAC = "icon.png"` — **won't work.** Must be `.icns`
- Setting `ICON_WIN = "icon.icns"` — **won't work on Windows.** Must be `.ico`
- Putting the icon file in a subfolder — `build.py` looks in the same folder as itself
- Using a tiny source image (under 256×256) — the icon will look blurry; use 512×512 or larger
- Icon shows correctly in `dist/` but not after installing — macOS caches icons; see HELP.md for the fix

---

### `EXTRA_DATA`

Extra files or folders your app needs at runtime — images, sounds, fonts, databases, config files, etc.

**PyInstaller bundles your Python code automatically. But any file your app *reads at runtime* must be listed here, or the built app won't find it.**

If your app has no data files, leave this empty:
```python
EXTRA_DATA = []
```

Otherwise, list each file or folder as a pair: `("where it is now", "where to put it inside the app")`.

```python
EXTRA_DATA = [
    # Format: ("source path",  "destination inside app")
    #
    # A WHOLE FOLDER — include everything inside it:
    ("images/",       "images"),        # your images/ folder → bundled as images/
    ("sounds/",       "sounds"),        # your sounds/ folder → bundled as sounds/
    ("assets/",       "assets"),        # your assets/ folder → bundled as assets/
    ("UI/",           "UI"),            # PyQt UI files
    ("fonts/",        "fonts"),         # custom fonts
    ("voice_models/", "voice_models"),  # large model folder (DartVader example)
    #
    # A SINGLE FILE — use "." as the destination to put it in the app root:
    ("config.json",     "."),           # → app finds it at the root level
    ("database.sqlite", "."),           # → SQLite database
    ("settings.ini",    "."),           # → settings file
    ("style.qss",       "."),           # → Qt stylesheet
    ("data.json",       "."),           # → any JSON data file
]
```

**How to know what to add:**

1. Build the app (even with `EXTRA_DATA = []`)
2. Double-click the built app
3. If it crashes with a `FileNotFoundError: [Errno 2] No such file or directory: 'something.json'`, add `"something.json"` to `EXTRA_DATA`
4. Rebuild

---

### `HIDDEN_IMPORTS`

Python modules PyInstaller fails to detect automatically.

PyInstaller scans your imports to figure out what to bundle. But some packages load their internals dynamically in ways PyInstaller can't see. The built app then crashes on launch with a `ModuleNotFoundError`.

**Start with this empty and only add things if the built app crashes:**

```python
HIDDEN_IMPORTS = []    # ← start here

# Only add if you see "ModuleNotFoundError: No module named 'X'" when running the built app:
HIDDEN_IMPORTS = ["screeninfo"]
HIDDEN_IMPORTS = ["screeninfo", "vosk", "sounddevice._sounddevice"]
```

Common packages that sometimes need to be listed here:
- `screeninfo` — multi-monitor detection
- `vosk` — offline speech recognition
- `sounddevice` or `sounddevice._sounddevice` — audio input/output
- `word2number.w2n` — number parsing
- `PIL._tkinter_finder` — if using Pillow with tkinter

---

### `EXCLUDES`

Packages to deliberately leave out to make the built app smaller.

**Safe to leave empty — it's always fine to include too much:**

```python
EXCLUDES = []    # ← safe default, use this if unsure
```

Only add packages your app genuinely doesn't use:

```python
EXCLUDES = ["tkinter"]                 # if your app uses PyQt5 or wx instead
EXCLUDES = ["PIL", "Pillow"]           # if your app doesn't process images
EXCLUDES = ["tkinter", "PIL", "Pillow"]  # DartVader — doesn't need either
```

---

## Full Worked Examples

### Example 1 — Minimal GUI app

Project layout:
```
BudgetApp/
    main.py
    build.py
```

`build.py` CONFIG:
```python
APP_NAME       = "Budget Tracker"
ENTRY_POINT    = "main.py"
VERSION        = "1.0.0"
BUNDLE_ID      = "com.yourname.budgettracker"
WINDOWED       = True
ICON_MAC       = None
ICON_WIN       = None
EXTRA_DATA     = []
HIDDEN_IMPORTS = []
EXCLUDES       = []
```

Result: `dist/Budget Tracker.dmg`

---

### Example 2 — App with images and a config file

Project layout:
```
PhotoTool/
    main.py
    config.json
    images/
        logo.png
        background.png
    icon.icns
    build.py
```

`build.py` CONFIG:
```python
APP_NAME       = "Photo Tool"
ENTRY_POINT    = "main.py"
VERSION        = "1.0.0"
BUNDLE_ID      = "com.yourname.phototool"
WINDOWED       = True
ICON_MAC       = "icon.icns"
ICON_WIN       = None
EXTRA_DATA     = [
    ("images/",     "images"),
    ("config.json", "."),
]
HIDDEN_IMPORTS = []
EXCLUDES       = []
```

---

### Example 3 — DartVader (complex PyQt5 app with voice recognition)

Project layout:
```
Darts/
    maingame.py
    dart.icns
    style.qss
    playerfile.txt
    GameData.json
    DartStats.db
    UI/
    DartImages/
    voice_models/
        vosk-model-small-en-us-0.15/
    build.py
```

`build.py` CONFIG:
```python
APP_NAME       = "DartVader"
ENTRY_POINT    = "maingame.py"
VERSION        = "2.0.0"
BUNDLE_ID      = "com.greenland.dartvader"
WINDOWED       = True
ICON_MAC       = "dart.icns"
ICON_WIN       = None
EXTRA_DATA     = [
    ("UI/",                                       "UI"),
    ("DartImages/",                               "DartImages"),
    ("dart.icns",                                 "."),
    ("style.qss",                                 "."),
    ("playerfile.txt",                            "."),
    ("GameData.json",                             "."),
    ("DartStats.db",                              "."),
    ("voice_models/vosk-model-small-en-us-0.15",  "voice_models/vosk-model-small-en-us-0.15"),
]
HIDDEN_IMPORTS = [
    "screeninfo",
    "screeninfo.enumerators",
    "PyQt5",
    "vosk",
    "sounddevice",
    "sounddevice._sounddevice",
    "word2number",
    "word2number.w2n",
]
EXCLUDES       = ["PIL", "Pillow", "tkinter"]
```

---

### Example 4 — MusicUpdater (simple tkinter + mutagen utility)

```python
APP_NAME       = "Music Organizer"
ENTRY_POINT    = "organize_music_gui.py"
VERSION        = "1.2.0"
BUNDLE_ID      = "com.greenland.musicorganizer"
WINDOWED       = True
ICON_MAC       = None
ICON_WIN       = None
EXTRA_DATA     = []
HIDDEN_IMPORTS = []
EXCLUDES       = []
```

---

## Requirements

- **Python 3.8+** — if your app runs, you have this
- **PyInstaller** — installed automatically when you first run `build.py`
- **macOS DMG creation** — uses `hdiutil`, built into every Mac. Nothing to install.
- **Windows EXE** — no extra tools needed. PyInstaller handles everything.
- **Linux AppImage** — requires `appimagetool` on your PATH (optional). If not installed, you get a folder bundle instead. Get it from [AppImageKit releases](https://github.com/AppImage/AppImageKit/releases).

---

## Running in a Virtual Environment

If your project uses a virtual environment (venv), **activate it before running the build**. This ensures PyInstaller picks up the packages installed in your venv, not the system Python.

```bash
# If using venv:
source venv/bin/activate
python3 build.py

# If using uv:
uv run python build.py
```

---

## Troubleshooting

For detailed troubleshooting — crash logs, platform-specific issues, common package problems, advanced config — see [HELP.md](HELP.md).

**Quick reference:**

| Problem | Fix |
|---------|-----|
| `Entry point 'main.py' not found` | `build.py` and your entry script must be in the same folder |
| App crashes with `FileNotFoundError` | Add the missing file to `EXTRA_DATA` |
| App crashes with `ModuleNotFoundError` | Add the missing module to `HIDDEN_IMPORTS` |
| `PyInstaller not found` | Run `pip3 install pyinstaller` then try again |
| macOS: "App is damaged" | Right-click → Open → Open (bypasses Gatekeeper, one-time only) |
| Build looks stuck | It's not stuck — PyInstaller takes 1–3 minutes. Wait for it. |
| Output is 200MB+ | This is normal. PyInstaller bundles Python + all packages. |

---

## Files in This Repo

| File | Purpose |
|------|---------|
| `build.py` | **The file you copy into your project.** Edit the CONFIG at the top. |
| `README.md` | This guide — usage, config reference, worked examples |
| `HELP.md` | Deep-dive troubleshooting, advanced topics, platform-specific notes |

---

## How It Works (the short version)

`build.py` does four things:

1. **Generates a PyInstaller `.spec` file** on the fly from your CONFIG values. The `.spec` is PyInstaller's instruction file — normally you'd have to write this by hand. `build.py` writes it for you and deletes it after the build.

2. **Runs PyInstaller**, which analyses your Python code, finds all its dependencies, and bundles everything into a standalone folder containing your app + Python interpreter + all packages.

3. **Wraps the output** for your platform:
   - macOS: runs `hdiutil` to compress the `.app` bundle into a `.dmg` installer
   - Windows: the `.exe` is already in `dist/` — nothing extra needed
   - Linux: runs `appimagetool` to create a single `.AppImage` file (or leaves the folder bundle if `appimagetool` isn't installed)

4. **Prints a clear BUILD COMPLETE message** with the exact path to your output file.

---

*Made with PyInstaller. Wrapper by David Greenland / Jarvis, 2026.*
