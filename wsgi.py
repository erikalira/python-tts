"""WSGI entry point for production deployment with Gunicorn.

This file is used by Gunicorn to run the Flask app in production.
The Discord bot runs in a background thread while Flask serves HTTP requests.

Usage:
    gunicorn --bind 0.0.0.0:$PORT wsgi:app
"""
import os
import threading

# Import the Flask app
from src.run_with_flask import app


def start_discord_bot():
    """Start the Discord bot in the main thread."""
    try:
        from src.discord_bot import run_bot
        run_bot()
    except Exception as e:
        print(f'Failed to start Discord bot: {e}')


# Start Discord bot in a background thread when the WSGI app loads
bot_thread = threading.Thread(target=start_discord_bot, daemon=True)
bot_thread.start()


if __name__ == '__main__':
    # This is only for local testing. In production, Gunicorn imports the `app` object.
    port = int(os.getenv('PORT', '8080'))
    app.run(host='0.0.0.0', port=port)
