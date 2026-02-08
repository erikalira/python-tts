"""Main entry point for the Discord bot with keep-alive HTTP server.

Runs the Discord bot and the Flask app defined in `src.app`.
"""
import threading
import asyncio
import logging
import time
from src.app import run_flask, set_container

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def start_discord_bot_with_retry(client, token):
    """Start Discord bot.
    
    Discord.py clients cannot be reused after a failed connection attempt.
    If connection fails, the entire container will be recreated by Render's auto-restart.
    
    Args:
        client: Discord client instance
        token: Bot token
    """
    try:
        logger.info("Starting Discord bot...")
        await client.start(token)
    except Exception as e:
        logger.error(f'Bot failed to start: {e}', exc_info=True)
        raise


def run_discord_bot():
    """Run the Discord bot with exponential backoff retry strategy."""
    logger.info("Initializing Discord bot...")
    
    from config.settings import Config
    from config.container import Container
    from discord.errors import HTTPException
    
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
    
    if config.discord_token is None:
        logger.error("Discord token is not set")
        return
    
    # Use async retry logic within single event loop
    try:
        asyncio.run(start_discord_bot_with_retry(container.discord_client, config.discord_token))
    except KeyboardInterrupt:
        logger.info('Bot shutting down...')
    except Exception as e:
        logger.error(f'Failed to start Discord bot: {e}', exc_info=True)


if __name__ == '__main__':
    # Start Flask in background thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info("Flask server started")
    
    # Load config to check if Discord bot is enabled
    from config.settings import Config
    config = Config()
    
    if config.discord_enabled:
        # Run Discord bot in main thread
        run_discord_bot()
    else:
        logger.info("Discord bot is disabled (DISCORD_ENABLED=false)")
        logger.info("Flask API endpoints are available")
        # Keep Flask running
        try:
            flask_thread.join()
        except KeyboardInterrupt:
            logger.info("Shutting down...")
