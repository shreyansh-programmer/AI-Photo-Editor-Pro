# Building Windows .exe for AI Photo Editor Pro

## Overview

The Linux executable has been created successfully. To build a Windows .exe file, you have several options:

## Option 1: Build on Windows Machine (Recommended)

### Prerequisites
- Windows 10/11
- Python 3.11+
- PyInstaller

### Steps

1. **Clone the repository** on your Windows machine:
```bash
git clone https://github.com/shreyansh-programmer/AI-Photo-Editor-Pro.git
cd AI-Photo-Editor-Pro
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
pip install pyinstaller
```

3. **Build the executable**:
```bash
pyinstaller photo_editor.spec
```

4. **Find the executable**:
The .exe file will be located at: `dist/AIPhotoEditorPro/AIPhotoEditorPro.exe`

## Option 2: Using Wine on Linux (Alternative)

If you want to build the Windows executable on Linux using Wine:

```bash
# Install Wine and dependencies
sudo apt-get install wine wine32 wine64

# Build with PyInstaller (will create Windows executable)
pyinstaller --onefile --windowed --icon=icon.ico main.py
```

## Option 3: Cross-Compilation with Docker

Use a Docker container with Windows build environment:

```bash
docker run -v $(pwd):/src cdrx/pyinstaller-windows pyinstaller /src/photo_editor.spec
```

## PyInstaller Spec File

The `photo_editor.spec` file is configured with:

```python
# Key settings:
- One-file executable (--onefile)
- Windowed mode (--windowed) - no console window
- Hidden imports for PyQt6, OpenCV, NumPy
- Icon and metadata
```

## Distribution

Once built, you can distribute the .exe file:

1. **Standalone**: Users can run the .exe directly without Python installed
2. **Installer**: Use NSIS or Inno Setup to create an installer
3. **GitHub Releases**: Upload to GitHub releases for easy downloading

## Troubleshooting

### Missing DLL errors
- Ensure all dependencies are installed
- Check that _internal folder is included with the executable

### Icon not showing
- Verify icon.ico file exists in the project root
- Update the spec file with correct icon path

### Application won't start
- Run from command line to see error messages
- Check that all dependencies are properly bundled

## Recommended Distribution Method

1. Build on Windows machine using PyInstaller
2. Create an installer using Inno Setup or NSIS
3. Upload to GitHub Releases
4. Link from the website

This ensures maximum compatibility and professional presentation.

---

## Quick Start for Windows Users

Once the .exe is built and distributed:

1. Download `AIPhotoEditorPro.exe`
2. Double-click to run
3. No installation required (portable executable)

---

## Current Status

- ✅ Linux executable created: `/dist/AIPhotoEditorPro/AIPhotoEditorPro`
- ⏳ Windows .exe: Requires build on Windows machine or Docker
- 🌐 Website: Live at https://aiphotoedito-mpgx9xam.manus.space
