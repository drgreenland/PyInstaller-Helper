# PyInstaller-Helper — Comprehensive Help Guide

This is the deep-dive companion to the README. It covers how PyInstaller actually works, every error you're likely to hit, platform-specific gotchas, and advanced config for complex apps.

---

## Table of Contents

1. [How PyInstaller Works](#how-pyinstaller-works)
2. [Understanding the Build Output](#understanding-the-build-output)
3. [The Most Common Errors — and How to Fix Them](#the-most-common-errors)
4. [EXTRA_DATA — The Complete Guide](#extra_data--the-complete-guide)
5. [HIDDEN_IMPORTS — The Complete Guide](#hidden_imports--the-complete-guide)
6. [EXCLUDES — When and Why](#excludes--when-and-why)
7. [Icons — Everything You Need to Know](#icons--everything-you-need-to-know)
8. [macOS-Specific Notes](#macos-specific-notes)
9. [Windows-Specific Notes](#windows-specific-notes)
10. [Linux-Specific Notes](#linux-specific-notes)
11. [Common Python Packages — Known Issues](#common-python-packages--known-issues)
12. [Virtual Environments (venv / uv / conda)](#virtual-environments)
13. [Making the Built App Read/Write Files Correctly](#making-the-built-app-readwrite-files-correctly)
14. [Reducing Output Size](#reducing-output-size)
15. [Rebuilding After Code Changes](#rebuilding-after-code-changes)
16. [Advanced: Adding a Second .spec Entry](#advanced-adding-extra-binaries)
17. [FAQ](#faq)

---

## How PyInstaller Works

Understanding this makes everything else make sense.

When you run your Python script normally (`python3 main.py`), Python reads your `.py` file and executes it. Your packages (tkinter, PyQt5, etc.) are sitting in your Python installation.

**The person you send your app to doesn't have Python.** They can't run `.py` files.

PyInstaller solves this by:

1. **Scanning your code** to find every `import` statement
2. **Copying those packages** from your Python installation into a `dist/` folder
3. **Copying the Python interpreter itself** into that folder
4. **Wrapping it all** into an executable that boots Python internally and runs your script

The result is a self-contained folder (or `.app` / `.exe`) that runs on any machine — Python not required.

### What PyInstaller does NOT do automatically

- Include non-Python files (images, sounds, JSON, databases) — you must list these in `EXTRA_DATA`
- Detect dynamically-imported modules (things imported with `importlib` or inside `__init__` files) — you must list these in `HIDDEN_IMPORTS`
- Sign or notarise the app — you must do this separately if needed (see macOS notes)

---

## Understanding the Build Output

After a successful build, your project folder contains:

```
YourProject/
    dist/
        AppName.app          ← macOS: the raw app bundle
        AppName.dmg          ← macOS: the distributable installer (send this)
        AppName/             ← Windows/Linux: folder containing everything
            AppName.exe      ← Windows: the executable
            AppName          ← Linux: the executable
            _internal/       ← Python + all bundled packages (don't touch)
    build/
        AppName/             ← PyInstaller working files — safe to delete
```

**What to send people:**
- **macOS:** the `.dmg` file only
- **Windows:** zip the entire `dist/AppName/` folder and send the zip
- **Linux:** the `.AppImage` file (or zip the `dist/AppName/` folder if AppImage wasn't created)

**The `build/` folder** is just working files. You can delete it anytime. It gets cleaned automatically next time you run `build.py`.

---

## The Most Common Errors

### ❌ `Entry point 'main.py' not found`

```
ERROR: Entry point 'main.py' not found.
       Make sure build.py and main.py are in the same folder.
       Current folder: /Users/you/Desktop
```

**Cause:** `build.py` is in a different folder from your script, OR your ENTRY_POINT name is wrong.

**Fix:**
1. Run `ls` in Terminal to see what files are in your current folder
2. Make sure both `build.py` AND your entry script are listed
3. Make sure `ENTRY_POINT` in the CONFIG matches the actual filename exactly (including capitalisation)

---

### ❌ `FileNotFoundError` when running the built app

```
FileNotFoundError: [Errno 2] No such file or directory: 'config.json'
```

**Cause:** Your app tries to read a file that isn't bundled.

**Fix:** Add the missing file to `EXTRA_DATA` in the CONFIG:

```python
EXTRA_DATA = [
    ("config.json", "."),    # add this
]
```

Then rebuild.

**Important note on file paths inside built apps — see the [file paths section below](#making-the-built-app-readwrite-files-correctly).**

---

### ❌ `ModuleNotFoundError` when running the built app

```
ModuleNotFoundError: No module named 'screeninfo'
```

**Cause:** PyInstaller missed a module your app needs.

**Fix:** Add the module name to `HIDDEN_IMPORTS`:

```python
HIDDEN_IMPORTS = ["screeninfo"]
```

Then rebuild.

---

### ❌ App window appears but is completely blank / white

**Cause (macOS):** On macOS 26 (and some earlier versions), complex views presented inside a `.sheet()` render blank. This is an iOS/macOS rendering bug, not a PyInstaller issue.

**Cause (general):** Your app loads a UI file from disk (e.g. a `.ui` or `.qml` file) that wasn't bundled.

**Fix (UI files missing):** Add the UI files folder to `EXTRA_DATA`:
```python
EXTRA_DATA = [
    ("UI/", "UI"),     # if your .ui files are in a folder called UI/
]
```

---

### ❌ `PyInstaller: command not found` or `No module named PyInstaller`

**Cause:** PyInstaller isn't installed, and the auto-install failed.

**Fix:**
```bash
pip3 install pyinstaller
```

If that fails because you're in a venv:
```bash
source venv/bin/activate     # activate your venv first
pip install pyinstaller
python3 build.py
```

---

### ❌ `UPX is not available`

```
WARNING: upx is not available.
```

This is a WARNING, not an error. UPX is a compression tool that makes the output smaller. It's optional. The build still succeeds without it.

**To install UPX (optional):**
```bash
brew install upx    # macOS
```

---

### ❌ Build fails with `RecursionError`

Some packages (particularly large scientific ones like scipy) trigger PyInstaller's recursion limit.

**Fix:** Add this to the top of `build.py` (above the CONFIG section):
```python
import sys
sys.setrecursionlimit(5000)
```

---

### ❌ macOS: "The application cannot be opened" or "App is damaged"

**Cause:** The app isn't code-signed. macOS Gatekeeper blocks unsigned apps from unknown developers.

**Quick fix for personal use:**
1. Right-click (Control-click) the app
2. Select "Open"
3. Click "Open" in the dialog
4. The app will open. This only needs to be done once — macOS remembers.

**Alternative fix:**
```bash
xattr -cr /Applications/YourApp.app
```

**Proper fix (for distributing to others):** You need an Apple Developer account and code signing. See the [macOS section](#macos-specific-notes).

---

### ❌ Windows: "Windows protected your PC" (SmartScreen)

**Cause:** The `.exe` isn't code-signed. Windows SmartScreen warns about unsigned executables from unknown publishers.

**Quick fix:** Click "More info" → "Run anyway".

**Proper fix:** Purchase a code signing certificate. See the [Windows section](#windows-specific-notes).

---

### ❌ Build seems stuck / nothing happening for 5+ minutes

PyInstaller is not stuck. Building takes time — especially the first time, and especially on large apps with many dependencies. It can take:

- Simple tkinter app: 30–60 seconds
- Medium app with a few packages: 1–3 minutes
- Large app with PyQt5, numpy, pandas: 3–8 minutes
- App with a large voice model or ML library: 5–15 minutes

Leave it running. The terminal will eventually show "BUILD COMPLETE".

If it has been genuinely stuck for over 15 minutes with zero output, press Ctrl+C and try again.

---

## EXTRA_DATA — The Complete Guide

### The source path

The source path is **relative to your project folder** (where `build.py` lives).

```python
# If your project is at /Users/m4/Development/MyApp/ and build.py is there too:

EXTRA_DATA = [
    ("images/", "images"),        # bundles /Users/m4/Development/MyApp/images/
    ("config.json", "."),         # bundles /Users/m4/Development/MyApp/config.json
]
```

Use forward slashes `/` even on Windows.

### The destination path

The destination is where the file ends up **inside the app bundle**.

- `"."` — puts the file in the app's root directory (same level as the executable)
- `"images"` — puts files inside an `images/` folder inside the app
- `"data/models"` — creates a nested path `data/models/` inside the app

### Folders vs files

```python
EXTRA_DATA = [
    # Entire folder — include everything inside:
    ("images/",   "images"),    # trailing slash = folder

    # Single file — put it in the app root:
    ("logo.png",  "."),         # no trailing slash = file

    # Single file — put it in a subfolder:
    ("logo.png",  "images"),    # logo.png → images/logo.png inside the app
]
```

### Nested folders

If your voice model or other data is in a nested path:

```python
EXTRA_DATA = [
    # The whole nested path is preserved:
    ("voice_models/small-en-us/", "voice_models/small-en-us"),
]
```

### How your code refers to these files

See [Making the Built App Read/Write Files Correctly](#making-the-built-app-readwrite-files-correctly) — this is the most important section if you're having file-not-found issues.

---

## HIDDEN_IMPORTS — The Complete Guide

### Why modules go missing

PyInstaller detects imports by statically reading your source code. It finds:

```python
import tkinter          # ✓ detected
from PyQt5 import QtGui  # ✓ detected
```

But it MISSES imports that happen dynamically:

```python
importlib.import_module("somepackage")    # ✗ not detected
__import__("somepackage")                 # ✗ not detected
```

Many packages use dynamic imports internally (even if your code doesn't). PyInstaller ships "hooks" that handle known packages — but hooks don't exist for every package.

### How to find what's missing

1. Build the app with `HIDDEN_IMPORTS = []`
2. Open the built app by double-clicking it (not from Terminal — that bypasses the issue)
3. If it crashes, the error message shows the missing module:
   ```
   ModuleNotFoundError: No module named 'vosk'
   ```
4. Add `"vosk"` to `HIDDEN_IMPORTS` and rebuild

### Submodules

Sometimes you need the full dotted path:

```python
HIDDEN_IMPORTS = [
    "sounddevice._sounddevice",   # not just "sounddevice"
    "word2number.w2n",             # not just "word2number"
    "screeninfo.enumerators",      # not just "screeninfo"
]
```

---

## EXCLUDES — When and Why

### What to exclude

Only exclude packages that your app **genuinely does not use**.

```python
EXCLUDES = [
    "tkinter",      # if your app uses PyQt5 or wx — not tkinter
    "PIL",          # if your app doesn't do image processing
    "Pillow",       # same as PIL
    "numpy",        # if your app doesn't do number crunching
    "pandas",       # if your app doesn't process data tables
    "matplotlib",   # if your app doesn't make charts
    "scipy",        # if your app doesn't do scientific computing
    "email",        # if your app doesn't send email
    "html",         # if your app doesn't parse HTML
    "http",         # if your app doesn't make HTTP requests
    "unittest",     # test framework — never needed in production app
]
```

### Never exclude

```python
# DON'T exclude these — PyInstaller needs them:
"os", "sys", "pathlib", "json", "re", "io",
"collections", "functools", "threading", "subprocess"
```

### When NOT to use EXCLUDES

If your app crashes after adding something to EXCLUDES, remove it. Some packages are pulled in as transitive dependencies (packages that other packages need) — even if you don't use them directly.

---

## Icons — Everything You Need to Know

### macOS (.icns)

**Creating .icns from any image:**

The simplest method uses `sips`, which is built into every Mac:

```bash
# Source image should be 512×512 or larger PNG
sips -s format icns your-image.png --out icon.icns
```

For better quality with all icon sizes:

```bash
# Create an iconset folder with all required sizes
mkdir icon.iconset
sips -z 16 16     your-image.png --out icon.iconset/icon_16x16.png
sips -z 32 32     your-image.png --out icon.iconset/icon_16x16@2x.png
sips -z 32 32     your-image.png --out icon.iconset/icon_32x32.png
sips -z 64 64     your-image.png --out icon.iconset/icon_32x32@2x.png
sips -z 128 128   your-image.png --out icon.iconset/icon_128x128.png
sips -z 256 256   your-image.png --out icon.iconset/icon_128x128@2x.png
sips -z 256 256   your-image.png --out icon.iconset/icon_256x256.png
sips -z 512 512   your-image.png --out icon.iconset/icon_256x256@2x.png
sips -z 512 512   your-image.png --out icon.iconset/icon_512x512.png
sips -z 1024 1024 your-image.png --out icon.iconset/icon_512x512@2x.png
iconutil -c icns icon.iconset
# Result: icon.icns
```

### Windows (.ico)

**Creating .ico from any image:**

- **Free online:** https://www.favicon.io/favicon-converter/ — upload your PNG, download the `.ico`
- **GIMP:** File → Export As → name it `icon.ico` → Save
- **ImageMagick (command line):**
  ```bash
  magick convert your-image.png -resize 256x256 icon.ico
  ```

### Linux

Linux AppImages don't have an icon file built in the same way. The icon appears in the file manager based on the `.desktop` entry. `build.py` sets this automatically using the app name.

---

## macOS-Specific Notes

### The "App is damaged" problem

Unsigned apps from unknown developers are blocked by Gatekeeper. For personal use:

```bash
# Remove quarantine attribute (run in Terminal after copying to Applications):
xattr -cr "/Applications/YourApp.app"
```

Or: right-click → Open → Open.

### Code signing (for distributing to others)

If you want to distribute your app publicly without the Gatekeeper warning, you need:

1. **Apple Developer account** ($99/year at developer.apple.com)
2. **Developer ID certificate** issued by Apple
3. Sign the app after building:
   ```bash
   codesign --deep --force --sign "Developer ID Application: Your Name (XXXXXXXX)" "dist/AppName.app"
   ```
4. **Notarize** with Apple:
   ```bash
   xcrun notarytool submit dist/AppName.dmg --apple-id your@email.com --team-id XXXXXXXX --password app-specific-password --wait
   xcrun stapler staple dist/AppName.dmg
   ```

This is only needed for public distribution. For personal use or sharing with known people, just use `xattr -cr`.

### Full Disk Access (macOS)

If your app reads files from protected locations (Desktop, Documents, Downloads, external drives, `~/Music`), macOS may silently block it without any error message — the app just appears to do nothing.

**Fix:** The user must grant Full Disk Access:
1. System Settings → Privacy & Security → Full Disk Access
2. Click `+` → find and select your `.app`
3. Toggle it on

Document this requirement for your users.

### High-DPI / Retina display

`build.py` automatically adds `NSHighResolutionCapable: True` to the app's `Info.plist`. Your app will render at full Retina resolution without any extra work.

### macOS app won't launch at all (no error shown)

```bash
# Run from Terminal to see the actual error:
open -a "dist/AppName.app" --stdout /tmp/applog.txt --stderr /tmp/applog.txt
cat /tmp/applog.txt
```

---

## Windows-Specific Notes

### Output location

On Windows, PyInstaller in `--onedir` mode (what `build.py` uses) creates:

```
dist/
    AppName/
        AppName.exe      ← the executable
        _internal/       ← everything else (Python, packages, data)
```

**You must distribute the entire `AppName/` folder, not just the `.exe`.** The `.exe` will crash if it can't find the `_internal/` folder next to it.

To distribute: zip the `dist/AppName/` folder. The recipient unzips and double-clicks `AppName.exe`.

### Windows Defender / SmartScreen warning

Unsigned executables show a blue "Windows protected your PC" warning. The user clicks "More info" → "Run anyway".

For public distribution, you need a code signing certificate from a Certificate Authority like DigiCert or Sectigo (typically $200–400/year). For personal/small-group use, the "Run anyway" workaround is fine.

### Windows-specific hidden imports

Some packages need extra help on Windows:

```python
HIDDEN_IMPORTS = [
    "win32api",          # if you use win32 APIs
    "win32con",          # Windows constants
    "winreg",            # Registry access
    "pywintypes",        # PyWin32 types
]
```

### Path separators on Windows

PyInstaller accepts forward slashes in `EXTRA_DATA` source paths even on Windows. Use `/` not `\\`.

---

## Linux-Specific Notes

### AppImage

An AppImage is a single executable file that runs on most Linux distributions without installation. The user just makes it executable and runs it:

```bash
chmod +x AppName-x86_64.AppImage
./AppName-x86_64.AppImage
```

### Getting appimagetool

`build.py` uses `appimagetool` to create the AppImage. If it's not installed, you get a folder bundle instead.

```bash
# Download from https://github.com/AppImage/AppImageKit/releases
wget -O appimagetool https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool
sudo mv appimagetool /usr/local/bin/
```

### Linux and display servers

If your app uses a GUI and crashes on Linux with:
```
qt.qpa.xcb: could not connect to display
```

The machine may not have a display. Run with:
```bash
DISPLAY=:0 ./AppName
```

Or install a virtual display: `xvfb-run ./AppName`

### Shared libraries on Linux

Linux ELF binaries link to system libraries. If you build on Ubuntu 22 and run on Ubuntu 18, some libraries may be missing.

**Best practice:** build on the oldest Linux version you want to support (typically Ubuntu 20.04 LTS).

---

## Common Python Packages — Known Issues

### tkinter

Usually works out of the box. If tkinter UI looks ugly on macOS, add:
```python
HIDDEN_IMPORTS = ["tkinter", "tkinter.ttk", "tkinter.messagebox"]
```

On Linux, tkinter may need to be installed separately:
```bash
sudo apt-get install python3-tk
```

### PyQt5 / PyQt6

PyQt5 usually works well. If you get blank windows on macOS 26, see the `fullScreenCover` workaround in `HELP.md` (this is an OS bug, not PyInstaller).

```python
HIDDEN_IMPORTS = [
    "PyQt5",
    "PyQt5.QtCore",
    "PyQt5.QtGui",
    "PyQt5.QtWidgets",
    "PyQt5.uic",
]
```

If you use `.ui` files:
```python
EXTRA_DATA = [
    ("ui_files/", "ui_files"),
]
```

### Pillow / PIL

Usually detected automatically. If not:
```python
HIDDEN_IMPORTS = ["PIL", "PIL.Image", "PIL.ImageTk"]
```

### pandas / numpy / scipy

These work but produce **large output** (100–300MB). To reduce size, use `EXCLUDES` to remove what you're not using.

If you get recursion errors:
```python
# Add at the top of build.py, before the CONFIG:
import sys
sys.setrecursionlimit(5000)
```

### requests / httpx

Usually auto-detected. If SSL errors occur in the built app:
```python
HIDDEN_IMPORTS = ["requests", "urllib3", "certifi"]
```

### mutagen (audio metadata)

Works out of the box. No special config needed.

### vosk (offline speech recognition)

Needs hidden imports AND you must bundle the model files:

```python
HIDDEN_IMPORTS = ["vosk"]
EXTRA_DATA = [
    ("voice_models/vosk-model-small-en-us-0.15", "voice_models/vosk-model-small-en-us-0.15"),
]
```

### sounddevice / pyaudio

```python
HIDDEN_IMPORTS = ["sounddevice", "sounddevice._sounddevice"]
```

On macOS, the built app also needs microphone permission. Add to `build.py`'s `info_plist` in the `write_spec()` function:
```python
'NSMicrophoneUsageDescription': 'This app uses the microphone for voice input.',
```

### sqlalchemy

```python
HIDDEN_IMPORTS = ["sqlalchemy.dialects.sqlite"]
# add other dialects if you use them (postgresql, mysql, etc.)
```

### cryptography / PyNaCl / Ed25519

```python
HIDDEN_IMPORTS = ["cryptography", "cryptography.hazmat.primitives"]
```

---

## Virtual Environments

### Standard venv

```bash
# Activate your venv first, then build:
source venv/bin/activate
python3 build.py
```

PyInstaller will use the packages from the active venv.

### uv

```bash
# Option 1: activate the uv venv
source .venv/bin/activate
python3 build.py

# Option 2: run via uv
uv run python build.py
```

### conda

```bash
conda activate my-environment
python build.py
```

### Why this matters

If you run `python3 build.py` without activating your venv, PyInstaller uses the system Python and won't find the packages your app needs. The build may succeed but the app will crash with `ModuleNotFoundError` immediately.

**Always activate your environment before building.**

---

## Making the Built App Read/Write Files Correctly

This is one of the most common sources of confusion.

### The problem

When your app runs normally (from your dev machine), `open("data.json")` works because Python looks for `data.json` in the current working directory — which is your project folder.

When your app runs as a built `.app` or `.exe`, the current working directory might be somewhere completely different (`/`, or the Desktop, or the user's home folder). `open("data.json")` then fails to find the file.

### The fix — use `sys._MEIPASS` for read-only data

PyInstaller extracts bundled data files to a temporary folder at runtime. The path to that folder is available as `sys._MEIPASS`.

Add this helper function to your Python code (your `main.py` or wherever you load data files):

```python
import sys
import os

def resource_path(relative_path):
    """
    Get the correct path to a bundled resource file.
    Works both when running from source and when running as a built app.
    """
    if hasattr(sys, '_MEIPASS'):
        # Running as a built app — files are extracted here
        return os.path.join(sys._MEIPASS, relative_path)
    else:
        # Running from source — use the normal path
        return os.path.join(os.path.dirname(__file__), relative_path)
```

Then use it wherever you load files:

```python
# BEFORE (works in dev, breaks in built app):
with open("config.json") as f:
    config = json.load(f)

# AFTER (works everywhere):
with open(resource_path("config.json")) as f:
    config = json.load(f)
```

```python
# BEFORE:
image = Image.open("images/logo.png")

# AFTER:
image = Image.open(resource_path("images/logo.png"))
```

### Writing files — don't write into the bundle

The app bundle is read-only. If your app writes files (saves settings, logs, databases), **never write relative to `_MEIPASS`**.

Instead, write to the user's home directory or a platform-appropriate folder:

```python
import os

def user_data_path(filename):
    """
    Get a writable path in the user's home directory for app data.
    Creates the folder if it doesn't exist.
    """
    folder = os.path.join(os.path.expanduser("~"), ".myappname")
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, filename)

# Usage:
settings_file = user_data_path("settings.json")
log_file = user_data_path("app.log")
database = user_data_path("data.sqlite")
```

This creates a hidden folder `~/.myappname/` in the user's home directory where your app stores its writable data.

---

## Reducing Output Size

PyInstaller bundles Python + all packages, so output is often 50–300MB. This is normal. Here's how to reduce it:

### 1. Use EXCLUDES

List packages you don't need:
```python
EXCLUDES = ["tkinter", "PIL", "Pillow", "numpy", "pandas", "matplotlib"]
```

### 2. Use a clean virtual environment

If you build from your main Python installation, PyInstaller may pick up every package you've ever installed. Use a venv with only what your app needs:

```bash
python3 -m venv build-venv
source build-venv/bin/activate
pip install mutagen pyinstaller      # only what your app needs
python3 build.py
```

### 3. UPX compression

UPX compresses the output binaries. `build.py` already passes `upx=True` — you just need UPX installed:

```bash
brew install upx    # macOS
```

Typically reduces output by 20–40%.

### 4. --onefile mode (advanced)

`build.py` uses `--onedir` (a folder) because it's more reliable, especially with large data files. `--onefile` produces a single executable but startup is slower (it unzips to a temp folder every time).

To switch to onefile, you would need to modify `build.py`'s `write_spec()` function to use `EXE(..., a.scripts, a.binaries, a.datas, ...)` (merged into the exe) instead of the `COLLECT()` approach. This is an advanced modification.

---

## Rebuilding After Code Changes

Every time you change your Python code and want a fresh build:

```bash
cd /path/to/your/project
python3 build.py
```

`build.py` always cleans `build/` and `dist/` first, then rebuilds from scratch. You always get a fresh output.

**Tip:** If the build is slow, the most time-consuming part is the first build (PyInstaller analyses everything). Subsequent builds are faster because the OS caches disk reads.

---

## Advanced: Adding Extra Binaries

Some packages include compiled `.so` / `.dylib` / `.dll` files that PyInstaller doesn't detect automatically. The `vosk` package is an example — it includes `libvosk.dyld` with a non-standard extension.

To add these, you would edit `build.py`'s `write_spec()` function to add entries to `binaries`:

```python
# In dartvader.spec (this is the format pyinstaller uses):
binaries=[
    ('virt/lib/python3.9/site-packages/vosk/libvosk.dyld', 'vosk'),
],
```

For the `build.py` approach, you'd add a `EXTRA_BINARIES` config option and include it in the spec generation. This is only needed for unusual packages — most common packages work without it.

---

## FAQ

**Q: Do I need to re-copy build.py to every project?**

Yes — copy it into each project folder and edit the CONFIG section for that project. The CONFIG section is the whole point: it's what makes `build.py` know the name, entry point, and data files for that specific project.

**Q: Can I build a Mac app on Windows (or vice versa)?**

No. PyInstaller can only build for the platform you're running on. To build a `.dmg` you need a Mac. To build a `.exe` you need Windows. There's no cross-compilation.

**Q: Can I use this for a web app (Flask, FastAPI, Django)?**

Technically yes, but web apps are usually deployed to a server rather than distributed as desktop apps. PyInstaller bundles the Python server — the user would still need to open a browser and go to `localhost:5000`. It works, but it's unusual.

**Q: The output is 200MB — is that normal?**

Yes. PyInstaller bundles the Python interpreter plus all packages. A minimal tkinter app is ~20–30MB. A PyQt5 app is ~60–100MB. An app with numpy/pandas can be 200–400MB. This is unavoidable — it's the cost of not requiring Python to be installed.

**Q: Can the recipient just double-click the .dmg?**

Yes. On Mac, they double-click the `.dmg`, a virtual drive mounts, they drag the `.app` to their Applications folder, eject the drive, and run the app from Applications. They never need to see the Terminal.

**Q: My app has multiple Python files. Do I list them all in build.py?**

No — only `ENTRY_POINT`. PyInstaller follows all the `import` statements in your code automatically, starting from the entry point. As long as your other `.py` files are imported somewhere in your code chain, they'll be included automatically.

**Q: What if my app needs to update itself or download new data?**

The app bundle is read-only. Write any downloaded or updated data to a user data directory (`~/.yourapp/` or similar). See the [file paths section](#making-the-built-app-readwrite-files-correctly).

**Q: Can I include a README or licence file with the app?**

Yes — add them to `EXTRA_DATA`:
```python
EXTRA_DATA = [
    ("README.txt", "."),
    ("LICENCE.txt", "."),
]
```
They'll be bundled inside the `.app`. On Windows they'll be in the `dist/AppName/` folder.

**Q: The app works on my machine but not on someone else's Mac. Why?**

The most common reasons:
1. They're on an older macOS version that your app doesn't support — check the minimum deployment target
2. They need to grant Full Disk Access or another privacy permission
3. Gatekeeper is blocking the unsigned app — see [macOS notes](#macos-specific-notes)
4. They're on Apple Silicon (M1/M2/M3) and you built on Intel (or vice versa) — rebuild on the same architecture, or build a universal binary

**Q: How do I make a universal binary that runs on both Intel and Apple Silicon Macs?**

This requires building with `--target-arch universal2`, which needs both architectures' Python. The easiest approach is to build on an Apple Silicon Mac (which can run Intel code via Rosetta for testing) and pass `target_arch='universal2'` in the EXE section of the spec. This is an advanced topic beyond the scope of `build.py`'s defaults.

---

*David Greenland / Jarvis — 2026-09-21*
*For bugs or improvements: https://github.com/drgreenland/PyInstaller-Helper*
