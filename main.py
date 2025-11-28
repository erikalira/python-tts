"""Main entry point for the Discord bot with Flask health check server.

This runs both the Discord bot and a Flask server for keep-alive monitoring.
"""
import os
import threading
import asyncio
import logging
from flask import Flask

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Simple Flask app for health checks
app = Flask(__name__)

@app.route('/')
def home():
    return {"status": "online", "bot": "Discord TTS Bot"}, 200

@app.route('/health')
def health():
    return {"status": "healthy"}, 200


def run_flask():
    """Run Flask server in a separate thread."""
    port = int(os.getenv('PORT', '10000'))
    logger.info(f"Starting Flask health check server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)


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
    
    # Start Discord bot
    try:
        asyncio.run(container.discord_client.start(config.discord_token))
    except KeyboardInterrupt:
        logger.info('Bot shutting down...')
    except Exception as e:
        logger.error(f'Bot error: {e}', exc_info=True)


if __name__ == '__main__':
    # Start Flask in background thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info("Flask health check server started")
    
    # Run Discord bot in main thread
    run_discord_bot()
