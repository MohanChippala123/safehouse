#!/usr/bin/env python3
"""Setup script for SafeHouse development environment."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def print_header(text: str) -> None:
    """Print a section header."""
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}\n")

def check_python_version() -> bool:
    """Check if Python 3.12+ is installed."""
    if sys.version_info < (3, 12):
        print(f"ERROR: Python 3.12+ required (found {sys.version})")
        return False
    print(f"✓ Python {sys.version.split()[0]} detected")
    return True

def check_exiftool() -> bool:
    """Check if exiftool is installed."""
    if shutil.which("exiftool"):
        print("✓ exiftool is installed")
        return True
    print("⚠ exiftool not found. Install with:")
    print("  Windows: choco install exiftool")
    print("  macOS: brew install exiftool")
    print("  Linux: apt-get install libimage-exiftool-perl")
    return False

def create_venv() -> bool:
    """Create virtual environment."""
    venv_path = Path("venv")
    if venv_path.exists():
        print("✓ Virtual environment already exists")
        return True

    print("Creating virtual environment...")
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✓ Virtual environment created")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to create virtual environment: {e}")
        return False

def install_dependencies() -> bool:
    """Install Python dependencies."""
    print("Installing dependencies...")
    pip_path = Path("venv") / ("Scripts" if sys.platform == "win32" else "bin") / "pip"

    try:
        subprocess.run(
            [str(pip_path), "install", "-r", "requirements.txt"],
            check=True,
            capture_output=False
        )
        print("✓ Dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to install dependencies: {e}")
        return False

def create_env_file() -> bool:
    """Create .env file from .env.example."""
    env_path = Path(".env")
    env_example_path = Path(".env.example")

    if env_path.exists():
        print("✓ .env file already exists")
        return True

    if env_example_path.exists():
        print("Creating .env from .env.example...")
        try:
            env_path.write_text(env_example_path.read_text())
            print("✓ .env file created")
            print("  ⚠ Remember to add your API keys!")
            return True
        except IOError as e:
            print(f"ERROR: Failed to create .env: {e}")
            return False
    else:
        print("WARNING: .env.example not found")
        return False

def main() -> None:
    """Run setup."""
    print_header("SafeHouse Setup")

    # Check Python version
    print("Checking Python version...")
    if not check_python_version():
        sys.exit(1)

    # Check exiftool
    print("\nChecking exiftool...")
    exiftool_ok = check_exiftool()

    # Create virtual environment
    print_header("Setting up Python Environment")
    if not create_venv():
        sys.exit(1)

    # Install dependencies
    print_header("Installing Dependencies")
    if not install_dependencies():
        sys.exit(1)

    # Create .env file
    print_header("Configuring Environment")
    create_env_file()

    # Final instructions
    print_header("Setup Complete!")

    venv_activate = "venv\\Scripts\\activate" if sys.platform == "win32" else "source venv/bin/activate"

    print("Next steps:")
    print(f"1. Activate virtual environment:")
    print(f"   {venv_activate}")
    print()
    print("2. Configure API keys in .env:")
    print("   - VT_API_KEY from virustotal.com")
    print("   - URLSCAN_KEY from urlscan.io")
    print("   - GROQ_KEY from console.groq.com")
    print()
    print("3. Run the application:")
    print("   python app.py")
    print()
    print("4. Visit http://localhost:5000")

    if not exiftool_ok:
        print()
        print("⚠ ExifTool is required for metadata extraction")
        print("  Install it before running the application")

    print()

if __name__ == "__main__":
    main()
