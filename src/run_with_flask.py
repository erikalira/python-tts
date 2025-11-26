"""Start a minimal Flask server in a background thread and run the Discord bot.

This keeps the Discord bot running in the main thread (it uses asyncio.run)
and serves a lightweight HTTP endpoint on a different port so external tools
can check bot health or forward requests.

Run from project root or from `src/`:

    python src/run_with_flask.py

Environment variables:
  - DISCORD_BOT_PORT: port used by the bot's internal aiohttp server (default: 5000)
  - FLASK_PORT: port to expose the Flask health endpoint (default: 8080)
"""
import os
import threading

from flask import Flask, jsonify

try:
    from src.__version__ import __version__, __author__, __description__
except ImportError:
    __version__ = "unknown"
    __author__ = "unknown"
    __description__ = "unknown"


app = Flask(__name__)


@app.route("/")
def home():
    return "Bot online!"


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


def run_flask():
    # Prefer the service PORT env var (Render provides $PORT). Fallback to FLASK_PORT or 8080.
    port = int(os.getenv('PORT', os.getenv('FLASK_PORT', '8080')))
    # In production, Gunicorn will handle the app. This is only for development.
    # Use debug=False and disable reloader for production-like behavior
    app.run(host="0.0.0.0", port=port, threaded=True, use_reloader=False, debug=False)


if __name__ == '__main__':
    # start Flask in a background thread so the main thread can run the asyncio bot
    t = threading.Thread(target=run_flask, daemon=True)
    t.start()

    # import and start the existing discord bot
    # Use an explicit package import so imports work both when running the module
    # directly and when executed via runpy from the project root.
    try:
        from src.discord_bot import run_bot
    except Exception as e:
        print('Failed to import discord bot:', e)
        raise

    run_bot()
