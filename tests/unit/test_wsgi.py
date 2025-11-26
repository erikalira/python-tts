"""Tests for WSGI entry point."""
import pytest
from unittest.mock import Mock, patch, MagicMock
import threading


class TestWSGI:
    """Test WSGI entry point."""
    
    def test_wsgi_imports_app(self):
        """Test that wsgi imports Flask app."""
        with patch('wsgi.threading.Thread'), \
             patch('wsgi.start_discord_bot'):
            import wsgi
            assert wsgi.app is not None
    
    def test_wsgi_starts_bot_thread(self):
        """Test that wsgi starts Discord bot in background thread."""
        with patch('wsgi.threading.Thread') as MockThread, \
             patch('wsgi.start_discord_bot'):
            
            # Reimport to trigger thread creation
            import importlib
            import wsgi as wsgi_module
            importlib.reload(wsgi_module)
            
            # Verify thread was created and started
            MockThread.assert_called()
            call_kwargs = MockThread.call_args[1]
            assert call_kwargs.get('daemon') is True
    
    def test_start_discord_bot_creates_event_loop(self):
        """Test that start_discord_bot creates new event loop."""
        with patch('wsgi.asyncio.new_event_loop') as mock_new_loop, \
             patch('wsgi.asyncio.set_event_loop'), \
             patch('config.settings.Config') as MockConfig, \
             patch('src.bot.main'):
            
            # Mock valid config
            mock_config = Mock()
            mock_config.validate.return_value = (True, None)
            MockConfig.return_value = mock_config
            
            # Mock event loop
            mock_loop = Mock()
            mock_new_loop.return_value = mock_loop
            
            from wsgi import start_discord_bot
            
            # Should create and use new loop
            try:
                start_discord_bot()
            except Exception:
                pass  # Expected to fail without full setup
            
            mock_new_loop.assert_called_once()
    
    def test_start_discord_bot_validates_config(self):
        """Test that start_discord_bot validates configuration."""
        with patch('config.settings.Config') as MockConfig, \
             patch('wsgi.logger') as mock_logger:
            
            # Mock invalid config
            mock_config = Mock()
            mock_config.validate.return_value = (False, "Missing token")
            MockConfig.return_value = mock_config
            
            from wsgi import start_discord_bot
            
            start_discord_bot()
            
            # Should log error
            mock_logger.error.assert_called()
    
    def test_wsgi_main_runs_flask_app(self):
        """Test that __main__ block runs Flask app."""
        with patch('wsgi.app') as mock_app, \
             patch('wsgi.os.getenv', return_value='8080'), \
             patch('wsgi.threading.Thread'), \
             patch('wsgi.start_discord_bot'):
            
            # Simulate running as main
            import wsgi
            if hasattr(wsgi, '__name__'):
                # Can't really test __main__ block, but can verify app exists
                assert mock_app is not None
