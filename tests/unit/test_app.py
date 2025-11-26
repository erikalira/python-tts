"""Tests for Flask app factory."""
import pytest
from unittest.mock import Mock, patch


class TestFlaskApp:
    """Test Flask app creation."""
    
    def test_app_is_created(self):
        """Test that Flask app is created."""
        from src.app import app
        assert app is not None
        assert hasattr(app, 'route')
    
    def test_app_has_health_endpoint(self):
        """Test that app has /health endpoint."""
        from src.app import app
        
        client = app.test_client()
        response = client.get('/health')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
    
    def test_app_name(self):
        """Test that app has correct name."""
        from src.app import app
        assert app.name == 'src.app'
    
    def test_app_has_json_support(self):
        """Test that app supports JSON responses."""
        from src.app import app
        
        client = app.test_client()
        response = client.get('/health')
        
        assert response.content_type == 'application/json'
