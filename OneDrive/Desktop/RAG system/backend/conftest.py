"""
Testing configuration and fixtures
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def sample_pdf_path(tmp_path):
    """Create a sample PDF file for testing"""
    # This would be a simple PDF in real tests
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_bytes(b"PDF sample content")
    return pdf_path


@pytest.mark.asyncio
async def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
