"""
Environment setup script for HR Inbox Scanner
"""
import os
import sys
import subprocess
import pkg_resources
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    
    print(f"✅ Python version: {sys.version}")
    return True

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    
    requirements = [
        'imaplib2==3.6',
        'PyPDF2==3.0.1',
        'python-docx==0.8.11',
        'openpyxl==3.1.2',
        'pandas==2.0.3',
        'email-validator==2.0.0',
        'python-dotenv==1.0.0',
        'nltk==3.8.1',
        'regex==2023.8.8',
        'beautifulsoup4==4.12.2'
    ]
    
    for requirement in requirements:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', requirement])
            print(f"✅ Installed: {requirement}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install: {requirement}")
            print(f"Error: {e}")
            return False
    
    return True

def download_nltk_data():
    """Download required NLTK data"""
    print("📚 Downloading NLTK data...")
    
    try:
        import nltk
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        print("✅ NLTK data downloaded successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to download NLTK data: {e}")
        return False

def create_directory_structure():
    """Create required directory structure"""
    print("📁 Creating directory structure...")
    
    directories = [
        'src',
        'config', 
        'data',
        'data/processed_emails',
        'tests'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {directory}")
    
    # Create __init__.py files
    init_files = [
        'src/__init__.py',
        'config/__init__.py'
    ]
    
    for init_file in init_files:
        Path(init_file).touch()
        print(f"✅ Created: {init_file}")
    
    return True

def create_env_file():
    """Create sample .env file"""
    env_content = """# HR Inbox Scanner Environment Variables
# Email Configuration (Optional - you can also enter these when running the script)

# HR_EMAIL_ADDRESS=your-hr-email@company.com
# HR_EMAIL_PASSWORD=your-app-password-here

# For Gmail: Use App Password from https://myaccount.google.com/apppasswords
# For Outlook: Use your regular password or app password if 2FA is enabled
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file template")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def run_setup():
    """Run complete setup process"""
    print("🚀 HR Inbox Scanner - Environment Setup")
    print("="*50)
    
    steps = [
        ("Checking Python version", check_python_version),
        ("Installing requirements", install_requirements),
        ("Downloading NLTK data", download_nltk_data),
        ("Creating directory structure", create_directory_structure),
        ("Creating environment file", create_env_file)
    ]
    
    for step_name, step_function in steps:
        print(f"\n{step_name}...")
        if not step_function():
            print(f"❌ Setup failed at: {step_name}")
            return False
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Add your email credentials to .env file (optional)")
    print("2. Run: python main.py")
    
    return True

if __name__ == "__main__":
    run_setup()
