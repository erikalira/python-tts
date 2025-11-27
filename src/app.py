"""Flask server entry point (for production with Gunicorn).

This keeps compatibility with the existing wsgi.py and run_with_flask.py
while using the new architecture.
"""
import os
import threading
import asyncio
import logging
from flask import Flask, jsonify, request
from src.__version__ import __version__, __author__, __description__

# Configure logging
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global variable to store the container (will be set by wsgi.py)
_container = None


def set_container(container):
    """Set the dependency injection container."""
    global _container
    _container = container


@app.route("/")
def home():
    return "Bot online!"


@app.route("/health")
def health():
    """Health check endpoint for Docker/Render."""
    return jsonify({"status": "healthy"})


@app.route("/version")
def version():
    return jsonify({
        "version": __version__,
        "author": __author__,
        "description": __description__
    })


@app.route("/about")
def about():
    return jsonify({
        "name": "TTS Hotkey Windows",
        "version": __version__,
        "author": __author__,
        "description": __description__,
        "status": "online"
    })


@app.route("/speak", methods=['POST'])
def speak():
    """Handle /speak endpoint for TTS hotkey integration.
    
    This endpoint allows the Windows hotkey script to send text to the Discord bot.
    """
    if not _container:
        logger.error("[SPEAK] Container not initialized")
        return jsonify({"error": "Bot not initialized"}), 503
    
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({"error": "Missing 'text' field"}), 400
        
        from src.core.entities import TTSRequest
        
        # Create TTS request
        tts_request = TTSRequest(
            text=data.get('text', ''),
            channel_id=_parse_int(data.get('channel_id')),
            guild_id=_parse_int(data.get('guild_id')),
            member_id=_parse_int(data.get('member_id') or data.get('user_id'))
        )
        
        # Execute use case in the Discord bot's event loop
        # We need to run this asynchronously in the bot's loop
        loop = None
        for thread in threading.enumerate():
            if hasattr(thread, '_loop'):
                loop = thread._loop
                break
        
        # If we can't find the bot's loop, create a task in a new way
        if not loop:
            # Get the current event loop from the bot thread
            future = asyncio.run_coroutine_threadsafe(
                _container.speak_use_case.execute(tts_request),
                _container.discord_client.loop
            )
            # Wait for result with timeout
            result = future.result(timeout=30)
        else:
            future = asyncio.run_coroutine_threadsafe(
                _container.speak_use_case.execute(tts_request),
                loop
            )
            result = future.result(timeout=30)
        
        if result["success"]:
            return jsonify({"message": result["message"]}), 200
        else:
            return jsonify({"error": result["message"]}), 400
            
    except asyncio.TimeoutError:
        logger.error("[SPEAK] Timeout executing TTS request")
        return jsonify({"error": "Request timeout"}), 504
    except Exception as e:
        logger.error(f"[SPEAK] Error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


def _parse_int(value):
    """Safely parse integer from value."""
    if value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def run_flask():
    """Run Flask server (used in threading mode)."""
    port = int(os.getenv('PORT', os.getenv('FLASK_PORT', '8080')))
    app.run(host="0.0.0.0", port=port, threaded=True, use_reloader=False, debug=False)


if __name__ == '__main__':
    # Start Flask in background thread
    t = threading.Thread(target=run_flask, daemon=True)
    t.start()
    
    # Start Discord bot
    from src.bot import run
    run()
