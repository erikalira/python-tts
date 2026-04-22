"""Main entry point for Discord bot with HTTP server.

This is the refactored version following SOLID principles and Clean Architecture.
Run with: python -m src.bot
"""
import asyncio
import logging

from src.bot_runtime.container import Container
from src.bot_runtime.settings import Config
from src.infrastructure.http.server import HTTPServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main entry point."""
    # Load configuration
    config = Config()
    
    # Validate configuration
    is_valid, error_msg = config.validate()
    if not is_valid:
        logger.error(f"Configuration error: {error_msg}")
        return
    
    # Create dependency injection container
    container = Container(config)
    await container.start()
    
    # Start HTTP server
    http_server = HTTPServer(
        speak_handler=container.speak_controller.handle,
        voice_context_handler=container.voice_context_controller.handle,
        port=config.http_port,
        host=config.http_host,
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
