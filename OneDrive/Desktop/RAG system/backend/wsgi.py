"""
WSGI entry point for production deployment
"""
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.main import app

# For gunicorn/uwsgi
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "wsgi:app",
        host="0.0.0.0",
        port=8000,
        workers=4
    )
