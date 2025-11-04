# @Study:ST-016 @Study:ST-017 @Study:ST-018
#!/usr/bin/env python3
"""
Test configuration and fixtures for Modamoda Invisible Mannequin
"""

import pytest
from pathlib import Path

@pytest.fixture(scope="session")
def project_root():
    """Get the project root directory"""
    return Path(__file__).parent.parent

@pytest.fixture(scope="session")
def test_data_dir(project_root):
    """Get test data directory"""
    test_data = project_root / "tests" / "test_data"
    test_data.mkdir(exist_ok=True)
    return test_data

# TODO: Add FastAPI test client fixture when backend is fully implemented
# @pytest.fixture
# def client():
#     """FastAPI test client"""
#     from fastapi.testclient import TestClient
#     from src.backend.main import app
#     return TestClient(app)

@pytest.fixture
def governance_monitor():
    """Governance monitor for testing"""
    from scripts.governance_monitor import GovernanceMonitor
    return GovernanceMonitor()
