#!/usr/bin/env python3
"""
Build script for creating Windows .exe for AI Photo Editor Pro
Run this on a Windows machine with Python and PyInstaller installed
"""

import os
import sys
import subprocess
from pathlib import Path

def build_exe():
    """Build the Windows executable using PyInstaller"""
    
    print("=" * 60)
    print("AI Photo Editor Pro - Windows .exe Builder")
    print("=" * 60)
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"✓ PyInstaller found: {PyInstaller.__version__}")
    except ImportError:
        print("✗ PyInstaller not found. Install with: pip install pyinstaller")
        sys.exit(1)
    
    # Check if spec file exists
    spec_file = Path("photo_editor.spec")
    if not spec_file.exists():
        print(f"✗ Spec file not found: {spec_file}")
        sys.exit(1)
    
    print(f"✓ Spec file found: {spec_file}")
    
    # Run PyInstaller
    print("\n" + "=" * 60)
    print("Building executable...")
    print("=" * 60 + "\n")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "PyInstaller", str(spec_file)],
            check=True
        )
        
        print("\n" + "=" * 60)
        print("✓ Build successful!")
        print("=" * 60)
        
        exe_path = Path("dist/AIPhotoEditorPro/AIPhotoEditorPro.exe")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"\n✓ Executable created: {exe_path}")
            print(f"  Size: {size_mb:.2f} MB")
            print(f"\nYou can now distribute this executable!")
        else:
            print(f"\n⚠ Executable not found at expected location")
            print(f"Check dist/ directory for output")
            
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Build failed with error code: {e.returncode}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_exe()
