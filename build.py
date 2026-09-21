#!/usr/bin/env python3
# =============================================================================
#  build.py — Universal Python App Builder
#  David Greenland / Jarvis — v1.0  2026-09-21
# =============================================================================
#
#  WHAT THIS DOES
#  --------------
#  Turns your Python script into a proper app that anyone can run —
#  no Python installation required on their machine.
#
#    macOS   →  dist/AppName.dmg        (double-click installer)
#    Windows →  dist/AppName/AppName.exe
#    Linux   →  dist/AppName-x86_64.AppImage  (single portable file)
#
#
#  HOW TO USE IT — STEP BY STEP
#  -----------------------------
#
#  STEP 1 — Copy this file into your project folder.
#            Your project folder is wherever your Python scripts live.
#            Example: if your app is at:
#              /Users/m4/Development/MyApp/main.py
#            then copy build.py to:
#              /Users/m4/Development/MyApp/build.py
#
#  STEP 2 — Edit the CONFIG section below. That's the only part you touch.
#            Every option has an explanation and example right next to it.
#
#  STEP 3 — Open Terminal, navigate to your project folder:
#              cd /Users/m4/Development/MyApp
#
#  STEP 4 — Run it:
#              python3 build.py
#
#            That's it. The output appears in a new "dist" folder
#            inside your project folder.
#
#
#  REQUIREMENTS
#  ------------
#  - Python 3.8 or newer (you already have this if your app runs)
#  - PyInstaller is installed AUTOMATICALLY if it's missing — you don't need
#    to install it yourself
#  - macOS DMG creation uses a Mac tool called "hdiutil" that is already
#    on every Mac — nothing extra to install
#  - Windows .exe: nothing extra needed
#  - Linux AppImage: needs "appimagetool" (optional — falls back to a folder
#    if it's not installed)
#
# =============================================================================


import os
import sys
import shutil
import subprocess
import textwrap

PLATFORM = sys.platform   # "darwin" = Mac, "win32" = Windows, "linux" = Linux


# =============================================================================
#  CONFIG — EDIT THIS SECTION FOR YOUR PROJECT
#  Everything else in this file is automatic. You only need to touch this.
# =============================================================================

# ------------------------------------------------------------------------------
# APP_NAME
# The name of your finished app / dmg / exe file.
# Use letters, numbers, spaces are OK.
# Whatever you put here is what shows up in the Finder / File Explorer.
#
# Examples:
#   APP_NAME = "DartVader"
#   APP_NAME = "Music Organizer"
#   APP_NAME = "My Budget Tool"
# ------------------------------------------------------------------------------
APP_NAME = "MyApp"


# ------------------------------------------------------------------------------
# ENTRY_POINT
# The Python file that starts your app — the one you run with "python3 <file>".
# Must be in the SAME FOLDER as this build.py file.
# Just the filename, not the full path.
#
# Examples:
#   ENTRY_POINT = "main.py"
#   ENTRY_POINT = "maingame.py"
#   ENTRY_POINT = "organize_music_gui.py"
#   ENTRY_POINT = "app.py"
# ------------------------------------------------------------------------------
ENTRY_POINT = "main.py"


# ------------------------------------------------------------------------------
# VERSION
# The version number of your app. Shown in the app's "About" info on Mac.
# Format: "major.minor.patch"  — just use "1.0.0" if you're not sure.
#
# Examples:
#   VERSION = "1.0.0"
#   VERSION = "2.1.3"
# ------------------------------------------------------------------------------
VERSION = "1.0.0"


# ------------------------------------------------------------------------------
# BUNDLE_ID  (macOS only — ignored on Windows and Linux)
# A unique identifier for your app in reverse-domain format.
# Apple uses this internally. Nobody sees it except the OS.
# Use: com.yourname.appname  (all lowercase, no spaces)
#
# Examples:
#   BUNDLE_ID = "com.greenland.dartvader"
#   BUNDLE_ID = "com.greenland.musicorganizer"
#   BUNDLE_ID = "com.greenland.mybudgettool"
# ------------------------------------------------------------------------------
BUNDLE_ID = "com.yourname.myapp"


# ------------------------------------------------------------------------------
# WINDOWED
# True  = the app opens as a normal window with no terminal/console behind it.
#         Use this for GUI apps (tkinter, PyQt5, etc.)
# False = a terminal/console window appears when the app runs.
#         Use this if your app prints output to the terminal that the user needs to see.
#
# Examples:
#   WINDOWED = True   ← most desktop apps with a GUI
#   WINDOWED = False  ← command-line tools that print to the terminal
# ------------------------------------------------------------------------------
WINDOWED = True


# ------------------------------------------------------------------------------
# ICON_MAC
# The app icon shown in the macOS Dock and Finder.
# Must be a .icns file in the SAME FOLDER as build.py.
# Set to None if you don't have an icon — the app will use a default Python icon.
#
# How to make a .icns from a PNG:
#   1. Open Terminal
#   2. Run: sips -s format icns yourimage.png --out icon.icns
#   (your PNG should be at least 512x512 pixels for best results)
#
# Examples:
#   ICON_MAC = "icon.icns"     ← file is at MyApp/icon.icns
#   ICON_MAC = "dart.icns"     ← DartVader uses this
#   ICON_MAC = None            ← no icon, use default
# ------------------------------------------------------------------------------
ICON_MAC = None


# ------------------------------------------------------------------------------
# ICON_WIN
# The app icon shown in Windows File Explorer and the taskbar.
# Must be a .ico file in the SAME FOLDER as build.py.
# Set to None if you don't have one.
#
# How to convert a PNG to .ico (free online tool):
#   https://www.favicon.io/favicon-converter/
#   or use GIMP: File → Export As → name it icon.ico
#
# Examples:
#   ICON_WIN = "icon.ico"
#   ICON_WIN = None
# ------------------------------------------------------------------------------
ICON_WIN = None


# ------------------------------------------------------------------------------
# EXTRA_DATA
# Extra files or folders your app needs to run — images, sounds, databases,
# config files, etc.
#
# PyInstaller bundles your Python code automatically, but it does NOT
# automatically include non-Python files. If your app reads any file at
# runtime (images, JSON, audio, SQLite DB, etc.), you must list it here.
#
# FORMAT:  each entry is a pair:  ("where it is NOW",  "where to put it IN THE APP")
#          Written as:  ("source", "destination")
#
# THE SOURCE is the path to the file/folder RELATIVE TO your project folder.
# THE DESTINATION is the folder name INSIDE the app bundle.
#   - Use "." (a single dot) to put the file in the app's root folder.
#   - Use the same name as the source folder to keep it tidy.
#
# If you have no extra files, leave this as an empty list:  EXTRA_DATA = []
#
# Examples:
#
#   EXTRA_DATA = [
#       ("images/",          "images"),     # bundle the whole "images" folder
#       ("sounds/",          "sounds"),     # bundle the whole "sounds" folder
#       ("data.json",        "."),          # bundle data.json into the app root
#       ("config.ini",       "."),          # bundle config.ini into the app root
#       ("database.sqlite",  "."),          # bundle a SQLite database file
#       ("style.qss",        "."),          # DartVader uses this (Qt stylesheet)
#       ("UI/",              "UI"),         # DartVader UI folder
#       ("voice_models/",    "voice_models"), # DartVader voice models folder
#   ]
#
# WHAT IF I DON'T KNOW WHAT TO ADD?
#   Run the built app and see what errors or crashes appear.
#   A "file not found" error almost always means something is missing from here.
#   The missing filename tells you exactly what to add.
# ------------------------------------------------------------------------------
EXTRA_DATA = []


# ------------------------------------------------------------------------------
# HIDDEN_IMPORTS
# Python packages/modules that PyInstaller fails to detect automatically.
#
# PyInstaller scans your code to find what packages to include.
# But some packages load their components dynamically (at runtime) in a way
# that PyInstaller can't see. The app then crashes on launch with an
# "ImportError" or "ModuleNotFoundError".
#
# If you leave this as an empty list and the app works, great — leave it empty.
# Only add things here if the built app crashes with an import error.
#
# HOW TO KNOW WHAT TO ADD:
#   1. Build the app with this empty.
#   2. Run the built app (not from the terminal — double-click it).
#   3. If it crashes, look for "ModuleNotFoundError: No module named 'something'".
#   4. Add that 'something' to this list.
#
# Examples:
#   HIDDEN_IMPORTS = ["screeninfo", "vosk", "sounddevice._sounddevice"]
#   HIDDEN_IMPORTS = ["PIL._tkinter_finder"]
#   HIDDEN_IMPORTS = []   ← start with this; add only if needed
# ------------------------------------------------------------------------------
HIDDEN_IMPORTS = []


# ------------------------------------------------------------------------------
# EXCLUDES
# Packages to deliberately leave OUT of the app bundle to reduce file size.
#
# If your app doesn't use tkinter, Pillow, PyQt5, or other large libraries,
# listing them here can shrink the output significantly.
# Only list things your app genuinely does NOT use.
#
# If you're not sure, leave this empty — it's always safe to leave it empty.
#
# Examples:
#   EXCLUDES = ["tkinter", "PIL", "Pillow"]   ← DartVader doesn't use these
#   EXCLUDES = []                              ← safe default
# ------------------------------------------------------------------------------
EXCLUDES = []


# =============================================================================
#  END OF CONFIG — do not edit below this line
# =============================================================================


def ensure_pyinstaller():
    """Install PyInstaller automatically if it's not already installed."""
    try:
        import PyInstaller  # noqa: F401
        print("==> PyInstaller is installed.")
    except ImportError:
        print("==> PyInstaller not found — installing it now (one-time, takes ~30 seconds)...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("==> PyInstaller installed successfully.")


def clean():
    """Remove previous build output so we always get a fresh build."""
    print("==> Removing previous build/dist folders (if any)")
    for d in ("build", "dist"):
        if os.path.exists(d):
            shutil.rmtree(d)


def _icon_path():
    """Return the right icon path for this platform, or None."""
    icon = ICON_MAC if PLATFORM == "darwin" else ICON_WIN
    if icon and os.path.exists(icon):
        return icon
    if icon:
        print(f"    Warning: icon file '{icon}' not found — building without icon.")
    return None


def write_spec():
    """
    Generate a PyInstaller .spec file on the fly based on the CONFIG above.
    The .spec file is a Python script that tells PyInstaller exactly what to bundle.
    We create it automatically so you never have to touch it.
    """
    datas_lines = "\n".join(f"        ('{s}', '{d}')," for s, d in EXTRA_DATA)
    hidden_str  = ", ".join(f"'{m}'" for m in HIDDEN_IMPORTS)
    excludes_str = ", ".join(f"'{m}'" for m in EXCLUDES)
    icon        = _icon_path()
    icon_str    = f"'{icon}'" if icon else "None"

    spec = textwrap.dedent(f"""\
        # Auto-generated by build.py — do not edit.
        a = Analysis(
            ['{ENTRY_POINT}'],
            pathex=['.'],
            binaries=[],
            datas=[
        {datas_lines}
            ],
            hiddenimports=[{hidden_str}],
            hookspath=[],
            runtime_hooks=[],
            excludes=[{excludes_str}],
            noarchive=False,
        )
        pyz = PYZ(a.pure)

        exe = EXE(
            pyz,
            a.scripts,
            [],
            exclude_binaries=True,
            name='{APP_NAME}',
            debug=False,
            strip=False,
            upx=True,
            console={str(not WINDOWED)},
            icon={icon_str},
        )
        coll = COLLECT(
            exe,
            a.binaries,
            a.datas,
            strip=False,
            upx=True,
            name='{APP_NAME}',
        )
    """)

    if PLATFORM == "darwin":
        spec += textwrap.dedent(f"""\
            app = BUNDLE(
                coll,
                name='{APP_NAME}.app',
                icon={icon_str},
                bundle_identifier='{BUNDLE_ID}',
                info_plist={{
                    'CFBundleShortVersionString': '{VERSION}',
                    'NSHighResolutionCapable': 'True',
                }},
            )
        """)

    spec_path = f"_build_{APP_NAME}.spec"
    with open(spec_path, "w") as f:
        f.write(spec)
    return spec_path


def run_pyinstaller(spec_path):
    print("==> Running PyInstaller — this may take 1–3 minutes, please wait...")
    subprocess.check_call(
        [sys.executable, "-m", "PyInstaller", "--clean", "-y", spec_path]
    )
    print("==> PyInstaller finished.")


def make_dmg():
    """Wrap the .app into a .dmg using macOS built-in hdiutil."""
    app_path = f"dist/{APP_NAME}.app"
    dmg_path = f"dist/{APP_NAME}.dmg"
    print(f"==> Creating DMG installer: {dmg_path}")
    subprocess.check_call([
        "hdiutil", "create",
        "-volname", APP_NAME,
        "-srcfolder", app_path,
        "-ov",
        "-format", "UDZO",
        dmg_path,
    ])


def make_appimage():
    """Package the Linux folder bundle into an AppImage if appimagetool is available."""
    src     = f"dist/{APP_NAME}"
    app_dir = f"dist/{APP_NAME}.AppDir"
    bin_dir = os.path.join(app_dir, "usr/bin")
    os.makedirs(bin_dir, exist_ok=True)

    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(bin_dir, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)

    desktop_content = textwrap.dedent(f"""\
        [Desktop Entry]
        Name={APP_NAME}
        Exec={APP_NAME}
        Icon={APP_NAME.lower()}
        Type=Application
        Categories=Utility;
    """)
    with open(os.path.join(app_dir, f"{APP_NAME}.desktop"), "w") as f:
        f.write(desktop_content)

    if shutil.which("appimagetool"):
        out = f"dist/{APP_NAME}-x86_64.AppImage"
        subprocess.check_call(["appimagetool", app_dir, out])
        return out
    else:
        return None


def print_summary(output_path):
    """Print a clear success message showing exactly where the output file is."""
    print()
    print("=" * 60)
    print("  BUILD COMPLETE")
    print("=" * 60)
    print(f"  App name : {APP_NAME}")
    print(f"  Version  : {VERSION}")
    print(f"  Platform : {PLATFORM}")
    print(f"  Output   : {os.path.abspath(output_path)}")
    print("=" * 60)
    print()

    if PLATFORM == "darwin":
        print("  To distribute: send the .dmg file to anyone with a Mac.")
        print("  They double-click it and drag the app to their Applications folder.")
    elif PLATFORM == "win32":
        print("  To distribute: zip the entire dist/<AppName>/ folder and send it.")
        print("  The recipient unzips it and double-clicks the .exe inside.")
    else:
        print("  To distribute: send the .AppImage file.")
        print("  The recipient makes it executable (chmod +x) and double-clicks it.")
    print()


def main():
    print()
    print("=" * 60)
    print(f"  build.py — {APP_NAME} v{VERSION}")
    if PLATFORM == "darwin":
        print("  Building for: macOS  →  .app  →  .dmg")
    elif PLATFORM == "win32":
        print("  Building for: Windows  →  .exe")
    else:
        print("  Building for: Linux  →  .AppImage")
    print("=" * 60)
    print()

    # Sanity checks before doing any work
    if not os.path.exists(ENTRY_POINT):
        print(f"ERROR: Entry point '{ENTRY_POINT}' not found.")
        print(f"       Make sure build.py and {ENTRY_POINT} are in the same folder.")
        print(f"       Current folder: {os.getcwd()}")
        sys.exit(1)

    ensure_pyinstaller()
    clean()

    spec_path = write_spec()
    try:
        run_pyinstaller(spec_path)
    finally:
        if os.path.exists(spec_path):
            os.remove(spec_path)

    # Platform-specific packaging
    if PLATFORM == "darwin":
        make_dmg()
        output = f"dist/{APP_NAME}.dmg"
    elif PLATFORM == "win32":
        output = f"dist/{APP_NAME}/{APP_NAME}.exe"
        if not os.path.exists(output):
            print(f"\nWARNING: Expected .exe at '{output}' but it wasn't found.")
            print("Check the PyInstaller output above for errors.")
            sys.exit(1)
    else:
        result = make_appimage()
        if result:
            output = result
        else:
            output = f"dist/{APP_NAME}/"
            print()
            print("NOTE: appimagetool was not found on PATH.")
            print("      Your app is built as a folder bundle instead.")
            print("      To get a single .AppImage file, install appimagetool:")
            print("      https://github.com/AppImage/AppImageKit/releases")

    print_summary(output)


if __name__ == "__main__":
    main()
