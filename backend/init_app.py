"""
Application initialization script
"""
import sys
import os
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent))

def initialize_application():
    """Initialize application directories and files"""
    
    # Create necessary directories
    directories = [
        "data/uploads",
        "data/chroma_db",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory}")
    
    # Create .env if it doesn't exist
    if not os.path.exists(".env"):
        with open(".env.example", "r") as src:
            with open(".env", "w") as dst:
                dst.write(src.read())
        print("Created .env file from template")
    
    print("Application initialization complete!")


if __name__ == "__main__":
    initialize_application()
