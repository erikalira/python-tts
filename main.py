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

async def start_discord_bot_with_retry(client, token, max_retries: int = 5):
    """Start Discord bot with exponential backoff retry logic.
    
    Handles Discord rate limiting (429 errors) by retrying with exponential backoff.
    This prevents cascading failures during container restarts.
    
    Args:
        client: Discord client instance
        token: Bot token
        max_retries: Maximum number of retry attempts
    """
    for attempt in range(max_retries):
        try:
            logger.info(f"Discord bot login attempt {attempt + 1}/{max_retries}...")
            await client.start(token)
            return  # Success
        except Exception as e:
            error_str = str(e).lower()
            
            # Check if it's a rate limit error
            if "429" in str(e) or "rate limit" in error_str:
                if attempt < max_retries - 1:
                    wait_time = min(2 ** attempt, 300)  # Exponential backoff, max 5 minutes
                    logger.warning(
                        f"Rate limited by Discord. Retrying in {wait_time}s... "
                        f"(attempt {attempt + 1}/{max_retries})"
                    )
                    await asyncio.sleep(wait_time)
                    continue
            
            # For other errors, log and re-raise
            logger.error(f'Bot error: {e}', exc_info=True)
            raise
    
    raise RuntimeError(f"Failed to start Discord bot after {max_retries} attempts")


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
    
    # Retry configuration with exponential backoff
    max_retries = 2
    base_wait_time = 30  # Start with 30 seconds
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Discord bot connection attempt {attempt + 1}/{max_retries}")
            asyncio.run(container.discord_client.start(config.discord_token))
            break  # Success
        except HTTPException as e:
            if e.status == 429:  # Rate limit error
                if attempt < max_retries - 1:
                    wait_time = base_wait_time * (2 ** attempt)  # Exponential backoff
                    logger.warning(
                        f"Rate limited (429) by Discord. "
                        f"Waiting {wait_time} seconds before retry... "
                        f"(Attempt {attempt + 1}/{max_retries})"
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(
                        f"Max retries reached. Discord is still rate limiting. "
                        f"Please check your token and try again later."
                    )
                    return
            else:
                logger.error(f"HTTP error {e.status}: {e}", exc_info=True)
                return
        except KeyboardInterrupt:
            logger.info('Bot shutting down...')
            break
        except Exception as e:
            logger.error(f'Unexpected bot error: {e}', exc_info=True)
            return


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
