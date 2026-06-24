# AI Photo Editor Pro - Distribution Guide

## 📦 Available Executables

### Current Status

| Platform | Status | Location | Size |
|----------|--------|----------|------|
| **Windows (.exe)** | ⏳ Build on Windows | See instructions below | ~150-200 MB |
| **Linux** | ✅ Ready | `/dist/AIPhotoEditorPro/` | 5.7 MB |
| **macOS** | ⏳ Build on macOS | Requires macOS machine | ~150-200 MB |

---

## 🪟 Building Windows .exe

### Option A: Build on Windows Machine (Recommended)

#### Prerequisites
- Windows 10/11 (64-bit recommended)
- Python 3.11 or later
- Git

#### Steps

1. **Clone the repository**:
```bash
git clone https://github.com/shreyansh-programmer/AI-Photo-Editor-Pro.git
cd AI-Photo-Editor-Pro
```

2. **Install Python dependencies**:
```bash
pip install -r requirements.txt
pip install pyinstaller
```

3. **Run the build script**:
```bash
python build_windows_exe.py
```

4. **Find your executable**:
```
dist/AIPhotoEditorPro/AIPhotoEditorPro.exe
```

The executable is now ready to distribute! Users can run it directly without installing Python.

---

### Option B: Using Docker (Cross-Platform)

If you want to build Windows executable from Linux/Mac:

```bash
# Build Docker image with Windows build environment
docker build -t pyinstaller-windows -f Dockerfile.windows .

# Run build
docker run -v $(pwd):/src pyinstaller-windows python build_windows_exe.py
```

---

## 📥 Distribution Methods

### Method 1: GitHub Releases (Recommended)

1. Build the .exe on Windows
2. Go to GitHub repository → Releases → Create new release
3. Upload `AIPhotoEditorPro.exe`
4. Add release notes and download link

### Method 2: Direct Download Link

Host the .exe on a cloud service:
- Google Drive
- Dropbox
- AWS S3
- Azure Blob Storage

### Method 3: Create an Installer

Use Inno Setup or NSIS to create a professional installer:

```bash
# Example with Inno Setup (Windows)
# Create AIPhotoEditorPro.iss installer script
# Then compile with: iscc AIPhotoEditorPro.iss
```

---

## 🚀 Installation for End Users

### For Windows Users

1. **Download** `AIPhotoEditorPro.exe` from the website or GitHub
2. **Run** the executable (no installation needed)
3. **First launch** may take a few seconds as Python libraries load
4. **Enjoy** editing photos with AI!

### For Linux Users

1. **Download** the Linux executable from releases
2. **Make executable**: `chmod +x AIPhotoEditorPro`
3. **Run**: `./AIPhotoEditorPro`

---

## 📋 System Requirements

### Windows
- Windows 10 or later (64-bit)
- 4 GB RAM minimum (8 GB recommended)
- 2 GB free disk space
- GPU recommended for faster processing

### Linux
- Ubuntu 20.04 or later (or equivalent)
- 4 GB RAM minimum
- 2 GB free disk space
- GPU support for CUDA acceleration

### macOS
- macOS 10.14 or later
- 4 GB RAM minimum
- 2 GB free disk space

---

## 🔧 Troubleshooting

### Windows Defender Warning

If Windows Defender flags the executable:
1. This is normal for unsigned executables
2. Click "More info" → "Run anyway"
3. Consider code signing for production releases

### Missing Dependencies

If you get "DLL not found" errors:
1. Ensure the `_internal` folder is in the same directory as the .exe
2. Don't move or delete the `_internal` folder
3. The entire `dist/AIPhotoEditorPro/` folder must stay together

### Application Won't Start

Try running from command line to see error messages:
```bash
AIPhotoEditorPro.exe --verbose
```

---

## 📊 File Structure After Build

```
dist/AIPhotoEditorPro/
├── AIPhotoEditorPro.exe          # Main executable
└── _internal/                     # Required libraries
    ├── Python runtime
    ├── PyQt6 libraries
    ├── OpenCV libraries
    └── Other dependencies
```

**Important**: Keep the entire folder structure intact. Don't separate the .exe from the _internal folder.

---

## 🔐 Code Signing (Optional)

For production releases, sign the executable:

```bash
# Using signtool (Windows)
signtool sign /f certificate.pfx /p password AIPhotoEditorPro.exe
```

This removes security warnings and builds user trust.

---

## 📈 Release Checklist

- [ ] Test executable on clean Windows machine
- [ ] Verify all features work correctly
- [ ] Check file size and performance
- [ ] Create GitHub release
- [ ] Upload executable and documentation
- [ ] Test download link
- [ ] Update website with download link
- [ ] Announce release on social media

---

## 🌐 Website Integration

Update your website with download links:

```html
<a href="https://github.com/shreyansh-programmer/AI-Photo-Editor-Pro/releases/download/v1.0.0/AIPhotoEditorPro.exe">
  Download for Windows
</a>
```

---

## 📞 Support

For issues with building or distributing:

1. Check the BUILD_WINDOWS_EXE.md file
2. Review PyInstaller documentation: https://pyinstaller.org/
3. Open an issue on GitHub
4. Contact the development team

---

## 📝 Version Management

When releasing new versions:

1. Update version in `main.py`:
```python
APP_VERSION = "1.0.1"
```

2. Rebuild executable with new version
3. Create new GitHub release with version tag
4. Update website download links

---

**Last Updated**: June 24, 2026
**Current Version**: 1.0.0
**Next Release**: TBD
