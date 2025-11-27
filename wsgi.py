"""WSGI entry point for production deployment with Gunicorn.

This file is used by Gunicorn to run the Flask app in production.
The Discord bot runs in a background thread while Flask serves HTTP requests.

Usage:
    gunicorn --bind 0.0.0.0:$PORT wsgi:app
"""
import os
import threading
import asyncio
import logging

# Import the Flask app
from src.app import app, set_container

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def start_discord_bot():
    """Start the Discord bot with its own event loop in a background thread."""
    try:
        logger.info("Starting Discord bot thread...")
        from config.settings import Config
        from config.container import Container
        
        config = Config()
        is_valid, error_msg = config.validate()
        if not is_valid:
            logger.error(f'Configuration error: {error_msg}')
            return
        
        # Create dependency injection container
        container = Container(config)
        
        # Set container for Flask app to use
        set_container(container)
        logger.info("Container initialized and set for Flask app")
        
        # Create a new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        logger.info("Discord bot event loop created, starting bot...")
        
        # Start Discord bot (without HTTP server since Flask handles HTTP)
        try:
            loop.run_until_complete(container.discord_client.start(config.discord_token))
        except Exception as e:
            logger.error(f"Error running Discord bot: {e}", exc_info=True)
            
    except KeyboardInterrupt:
        logger.info('Discord bot shutting down')
    except Exception as e:
        logger.error(f'Failed to start Discord bot: {e}', exc_info=True)


# Start Discord bot in a background thread when the WSGI app loads
logger.info("Initializing Discord bot thread...")
bot_thread = threading.Thread(target=start_discord_bot, daemon=True)
bot_thread.start()
logger.info("Discord bot thread started")


if __name__ == '__main__':
    # This is only for local testing. In production, Gunicorn imports the `app` object.
    port = int(os.getenv('PORT', '8080'))
    app.run(host='0.0.0.0', port=port)
