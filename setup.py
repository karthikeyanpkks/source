import os
import sys
import subprocess
import urllib.request
import zipfile
import shutil

# Define installation paths
TESSERACT_URL = "https://github.com/tesseract-ocr/tesseract/releases/download/5.5.0/tesseract-ocr-w64-setup-5.5.0.20241111.exe"
TESSERACT_INSTALL_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POPLER_URL = "https://github.com/oschwartz10612/poppler-windows/releases/download/v23.11.0-0/Release-23.11.0-0.zip"
POPLER_INSTALL_PATH = r"C:\poppler"
TEMP_ZIP = "poppler.zip"

def run_command(command, admin=False):
    """Run a shell command with optional admin privileges."""
    try:
        if admin:
            command = f'powershell Start-Process cmd -ArgumentList "/c {command}" -Verb RunAs'
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running command: {command}\n{e}")

def install_tesseract():
    """Download and install Tesseract OCR with error handling."""
    try:
        print("🚀 Downloading and installing Tesseract OCR...")
        tess_installer = "tesseract_installer.exe"
        urllib.request.urlretrieve(TESSERACT_URL, tess_installer)
        run_command(f"{tess_installer} /SILENT")
        os.remove(tess_installer)  # Clean up installer
        print("✅ Tesseract installed successfully!")
    except Exception as e:
        print(f"❌ Error installing Tesseract: {e}")

def install_poppler():
    """Download and extract Poppler with error handling."""
    try:
        print("🚀 Downloading and installing Poppler...")
        urllib.request.urlretrieve(POPLER_URL, TEMP_ZIP)
        
        # Extract to desired path
        with zipfile.ZipFile(TEMP_ZIP, "r") as zip_ref:
            zip_ref.extractall(POPLER_INSTALL_PATH)
        
        # Remove temp file
        os.remove(TEMP_ZIP)
        
        # Find actual extracted folder and move contents up
        extracted_folder = next(os.scandir(POPLER_INSTALL_PATH)).path
        for item in os.listdir(extracted_folder):
            shutil.move(os.path.join(extracted_folder, item), POPLER_INSTALL_PATH)
        shutil.rmtree(extracted_folder)

        print(f"✅ Poppler installed at {POPLER_INSTALL_PATH}")
    except Exception as e:
        print(f"❌ Error installing Poppler: {e}")

def add_to_path():
    """Add Tesseract and Poppler to system PATH with error handling."""
    try:
        print("🔧 Adding Tesseract and Poppler to system PATH...")
        paths = [r"C:\Program Files\Tesseract-OCR", POPLER_INSTALL_PATH + r"\bin"]
        for path in paths:
            run_command(f'setx PATH "%PATH%;{path}"', admin=True)
        print("✅ PATH updated successfully! Restart your terminal.")
    except Exception as e:
        print(f"❌ Error updating PATH: {e}")

def install_python_dependencies():
    """Upgrade pip and install required Python packages with error handling."""
    try:
        print("🚀 Installing Python dependencies...")
        run_command(f"{sys.executable} -m pip install --upgrade pip setuptools wheel")
        run_command(f"{sys.executable} -m pip install -r requirements.txt")
        print("✅ Python dependencies installed!")
    except Exception as e:
        print(f"❌ Error installing Python dependencies: {e}")

def set_tesseract_path():
    """Ensure pytesseract knows where Tesseract is installed."""
    try:
        print(f"🔹 Setting Tesseract path in Python: {TESSERACT_INSTALL_PATH}")
        with open(os.path.expanduser("~/.pytesseract"), "w") as f:
            f.write(TESSERACT_INSTALL_PATH)
        print("✅ Tesseract path set successfully!")
    except Exception as e:
        print(f"❌ Error setting Tesseract path: {e}")

if __name__ == "__main__":
    try:
        install_tesseract()
        install_poppler()
        add_to_path()
        install_python_dependencies()
        set_tesseract_path()
        print("\n🎉 Setup completed successfully! Restart your terminal to apply changes.")
    except Exception as e:
        print(f"\n❌ Critical Error: {e}")
