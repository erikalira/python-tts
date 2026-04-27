"""Tests for bot entry point."""
import logging
import pytest
from unittest.mock import Mock, AsyncMock, patch


@pytest.mark.asyncio
class TestBot:
    """Test bot.py entry point."""
    
    async def test_main_creates_container(self):
        """Test that main creates and initializes container."""
        with patch('src.bot.Container') as MockContainer, \
             patch('src.bot.Config') as MockConfig, \
             patch('src.bot.HTTPServer') as MockHTTPServer:
            
            # Mock config validation
            mock_config = Mock()
            mock_config.validate.return_value = (True, None)
            mock_config.http_port = 10000
            mock_config.http_host = "127.0.0.1"
            mock_config.http_cors_allowed_origins = ()
            mock_config.http_max_body_bytes = 4096
            MockConfig.return_value = mock_config
            
            # Mock HTTP server
            mock_http_server = Mock()
            mock_http_server.start = AsyncMock()
            MockHTTPServer.return_value = mock_http_server
            
            # Mock container
            mock_container = Mock()
            mock_container.speak_controller = Mock()
            mock_container.voice_context_controller = Mock()
            mock_container.otel_runtime = Mock()
            mock_container.runtime_telemetry = Mock()
            mock_container.readiness_payload = AsyncMock(return_value={"status": "ready", "dependencies": []})
            mock_container.speak_controller.handle = AsyncMock()
            mock_container.voice_context_controller.handle = AsyncMock()
            mock_container.shutdown = AsyncMock()
            mock_container.discord_client = Mock()
            # Make start raise an exception to stop the bot from running
            mock_container.discord_client.start = AsyncMock(
                side_effect=KeyboardInterrupt("Test interrupt")
            )
            mock_container.discord_client.close = AsyncMock()
            MockContainer.return_value = mock_container
            
            # Import and run
            from src.bot import main
            
            # Should handle KeyboardInterrupt gracefully
            try:
                await main()
            except KeyboardInterrupt:
                pass
            
            # Verify container was created
            MockContainer.assert_called_once()
            MockHTTPServer.assert_called_once_with(
                speak_handler=mock_container.speak_controller.handle,
                voice_context_handler=mock_container.voice_context_controller.handle,
                port=10000,
                host="127.0.0.1",
                observability_snapshot_provider=mock_container.runtime_telemetry.snapshot_payload,
                readiness_provider=mock_container.readiness_payload,
                otel_runtime=mock_container.otel_runtime,
                cors_allowed_origins=(),
                max_request_body_bytes=4096,
            )
            # Verify HTTP server was started
            mock_http_server.start.assert_called_once()
            mock_container.shutdown.assert_awaited_once()
            mock_container.discord_client.close.assert_awaited_once()
    
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

    def test_configure_logging_uses_warning_for_library_loggers_at_info(self):
        """Test noisy library loggers are reduced at INFO without hiding errors."""
        from src.bot import _configure_logging

        discord_logger = logging.getLogger("discord")
        aiohttp_access_logger = logging.getLogger("aiohttp.access")
        original_discord_level = discord_logger.level
        original_aiohttp_level = aiohttp_access_logger.level

        try:
            _configure_logging("INFO")

            assert discord_logger.level == logging.WARNING
            assert aiohttp_access_logger.level == logging.WARNING
        finally:
            discord_logger.setLevel(original_discord_level)
            aiohttp_access_logger.setLevel(original_aiohttp_level)

    def test_configure_logging_respects_error_for_library_loggers(self):
        """Test library loggers honor ERROR when configured above INFO."""
        from src.bot import _configure_logging

        discord_logger = logging.getLogger("discord")
        aiohttp_access_logger = logging.getLogger("aiohttp.access")
        original_discord_level = discord_logger.level
        original_aiohttp_level = aiohttp_access_logger.level

        try:
            _configure_logging("ERROR")

            assert discord_logger.level == logging.ERROR
            assert aiohttp_access_logger.level == logging.ERROR
        finally:
            discord_logger.setLevel(original_discord_level)
            aiohttp_access_logger.setLevel(original_aiohttp_level)
