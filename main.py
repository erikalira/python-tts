"""Main entry point for the Discord bot with keep-alive HTTP server.

Runs the Discord bot and the Flask app defined in `src.app`.
"""
import threading
import asyncio
import logging
from src.app import run_flask, set_container

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_discord_bot():
    """Run the Discord bot."""
    logger.info("Initializing Discord bot...")
    
    from config.settings import Config
    from config.container import Container
    
    config = Config()
    is_valid, error_msg = config.validate()
    if not is_valid:
        logger.error(f'Configuration error: {error_msg}')
        return
    
    # Create dependency injection container
    container = Container(config)
    logger.info("Container initialized")
    # Make container available to Flask endpoints (e.g., /speak)
    set_container(container)
    
    # Start Discord bot
    try:
        if config.discord_token is None:
            logger.error("Discord token is not set")
            return
        asyncio.run(container.discord_client.start(config.discord_token))
    except KeyboardInterrupt:
        logger.info('Bot shutting down...')
    except Exception as e:
        logger.error(f'Bot error: {e}', exc_info=True)


if __name__ == '__main__':
    # Start Flask in background thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info("Flask server started")
    
    # Run Discord bot in main thread
    run_discord_bot()
