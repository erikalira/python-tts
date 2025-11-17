"""Start a minimal Flask server in a background thread and run the Discord bot.

This keeps the Discord bot running in the main thread (it uses asyncio.run)
and serves a lightweight HTTP endpoint on a different port so external tools
can check bot health or forward requests.

Run from project root or from `src/`:

    python src\run_with_flask.py

Environment variables:
  - DISCORD_BOT_PORT: port used by the bot's internal aiohttp server (default: 5000)
  - FLASK_PORT: port to expose the Flask health endpoint (default: 8080)
"""
import os
import threading

from flask import Flask


app = Flask(__name__)


@app.route("/")
def home():
    return "Bot online!"


def run_flask():
    port = int(os.getenv('FLASK_PORT', '8080'))
    # disable the reloader; run in threaded mode so it cooperates with background thread
    app.run(host="0.0.0.0", port=port, threaded=True, use_reloader=False)


if __name__ == '__main__':
    # start Flask in a background thread so the main thread can run the asyncio bot
    t = threading.Thread(target=run_flask, daemon=True)
    t.start()

    # import and start the existing discord bot
    # `discord_bot.run_bot()` blocks and runs the event loop inside asyncio.run
    try:
        from discord_bot import run_bot
    except Exception as e:
        print('Failed to import discord bot:', e)
        raise

    run_bot()
