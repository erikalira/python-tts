"""Flask HTTP server used for keep-alive and HTTP endpoints.

This app is used together with the Discord bot. The DI container
is injected by `main.py` via `set_container`.
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

# Global variable to store the container (set by main.py)
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
        # Always use the Discord client's loop set in the container
        future = asyncio.run_coroutine_threadsafe(
            _container.speak_use_case.execute(tts_request),
            _container.discord_client.loop
        )
        # Increased timeout to 2 minutes to handle Discord connection issues
        result = future.result(timeout=120)
        
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
    # Bind to 0.0.0.0 in containers; default port 10000 or $PORT
    port = int(os.getenv('PORT', os.getenv('FLASK_PORT', '10000')))
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    app.run(host=host, port=port, threaded=True, use_reloader=False, debug=False)


if __name__ == '__main__':
    # Start Flask in background thread
    t = threading.Thread(target=run_flask, daemon=True)
    t.start()
    
    # Start Discord bot
    from src.bot import run
    run()
