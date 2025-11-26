"""Flask server entry point (for production with Gunicorn).

This keeps compatibility with the existing wsgi.py and run_with_flask.py
while using the new architecture.
"""
import os
import threading
from flask import Flask, jsonify
from src.__version__ import __version__, __author__, __description__

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
