"""Main entry point for Discord bot with HTTP server.

This is the refactored version following SOLID principles and Clean Architecture.
Run with: python -m src.bot
"""
import asyncio
import logging

from src.bot_runtime.container import Container
from src.bot_runtime.settings import Config
from src.infrastructure.http.server import HTTPServer

logger = logging.getLogger(__name__)


def _configure_logging(log_level_name: str) -> None:
    level = logging.getLevelNamesMapping().get(log_level_name.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        force=True,
    )

    if level == logging.INFO:
        library_level = logging.WARNING
    elif level > logging.INFO:
        library_level = level
    else:
        return

    logging.getLogger("discord").setLevel(library_level)
    logging.getLogger("aiohttp.access").setLevel(library_level)


async def main():
    """Main entry point."""
    # Load configuration
    config = Config()
    _configure_logging(config.log_level)
    
    # Validate configuration
    is_valid, error_msg = config.validate()
    if not is_valid:
        logger.error(f"Configuration error: {error_msg}")
        return
    
    # Create dependency injection container
    container = Container(config)
    
    # Start HTTP server
    http_server = HTTPServer(
        speak_handler=container.speak_controller.handle,
        voice_context_handler=container.voice_context_controller.handle,
        port=config.http_port,
        host=config.http_host,
        observability_snapshot_provider=container.runtime_telemetry.snapshot_payload,
        readiness_provider=container.readiness_payload,
        otel_runtime=container.otel_runtime,
    )
    await http_server.start()
    
    # Start Discord bot
    try:
        if config.discord_token is None:
            logger.error("Discord token is not configured")
            return
        await container.discord_client.start(config.discord_token)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Error running bot: {e}", exc_info=True)
    finally:
        try:
            await http_server.stop()
        except Exception as e:
            logger.error(f"Error stopping HTTP server: {e}")
        try:
            await container.shutdown()
        except Exception as e:
            logger.error(f"Error stopping queue worker: {e}")
        try:
            await container.discord_client.close()
        except Exception as e:
            logger.error(f"Error closing Discord client: {e}")


def run():
    """Run the bot."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutdown complete")


if __name__ == '__main__':
    run()
