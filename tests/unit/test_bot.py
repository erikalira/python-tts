"""Tests for bot entry point."""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock


@pytest.mark.asyncio
class TestBot:
    """Test bot.py entry point."""
    
    async def test_main_creates_container(self):
        """Test that main creates and initializes container."""
        with patch('src.bot.Container') as MockContainer, \
             patch('src.bot.Config') as MockConfig:
            
            # Mock config validation
            mock_config = Mock()
            mock_config.validate.return_value = (True, None)
            MockConfig.return_value = mock_config
            
            # Mock container
            mock_container = Mock()
            mock_container.http_server = Mock()
            mock_container.http_server.start = AsyncMock()
            mock_container.discord_client = Mock()
            mock_container.discord_client.start = AsyncMock()
            MockContainer.return_value = mock_container
            
            # Import and run
            from src.bot import main
            
            # Should not raise exception
            try:
                await main()
            except Exception:
                pass  # Bot will try to start, just testing initialization
            
            # Verify container was created
            MockContainer.assert_called_once()
    
    async def test_main_validates_config(self):
        """Test that main validates configuration."""
        with patch('src.bot.Container'), \
             patch('src.bot.Config') as MockConfig, \
             patch('src.bot.logger') as mock_logger:
            
            # Mock invalid config
            mock_config = Mock()
            mock_config.validate.return_value = (False, "Missing DISCORD_TOKEN")
            MockConfig.return_value = mock_config
            
            from src.bot import main
            
            # Should log error and return without starting
            await main()
            
            # Verify error was logged
            mock_logger.error.assert_called()


class TestBotModule:
    """Test bot module execution."""
    
    def test_bot_can_be_imported(self):
        """Test that bot module can be imported."""
        from src import bot
        assert hasattr(bot, 'main')
    
    def test_bot_has_main_function(self):
        """Test that bot has async main function."""
        from src.bot import main
        import asyncio
        assert asyncio.iscoroutinefunction(main)
