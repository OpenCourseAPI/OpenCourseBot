"""
Server extension for the bot, with utilities to keep repl.it bots alive.

NOTE: repl.it still shuts the server down at a certain time each day
      basically, you will need an external service to ping the server
"""

import threading
import logging
import json
import requests

from os import getenv
from flask import Flask, request, jsonify, current_app
from discord.ext import tasks

log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)

PORT = getenv("SERVER_PORT", 3000)
enable_keepalive = getenv("ENABLE_KEEPALIVE", False)
server = None
app = Flask(__name__, static_url_path="", static_folder="../static")

app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0


@app.route("/")
def homepage():
    return current_app.send_static_file("index.html")


def include_in_filter(query):
    def check(option):
        words = query.lower().split()
        label = f"{option['Campus'].lower()} {option['Major'].lower()}"

        return all([word in label for word in words])

    return check


@app.route("/api/stats/search")
def search_stats():
    query = request.args.get("q")

    with open("data/allData.json") as f:
        allData = json.load(f)

    options = []

    for campus, campus_data in allData.items():
        for major_info in campus_data.values():
            major_info["Major"] = major_info["Major"].title()
            major_info["Campus"] = campus
            options.append(major_info)
            # data = {}
            # data['campus'] = campus
            # data['major'] = major
            # data['info'] = major_info
            # options.append(data)

    if not query:
        return jsonify(options)

    return jsonify(list(filter(include_in_filter(query), options)))


@app.route("/shutdown")
def shutdown():
    if request.remote_addr == "127.0.0.1":
        print("[server] shutting down")
        func = request.environ.get("werkzeug.server.shutdown")
        func()
        return "Ok!"

    return "Hmm...", 401


def start_server():
    app.run(host="0.0.0.0", port=PORT, debug=False)


def fetch_on_thread():
    print("[keepalive] Doing keepalive fetch")
    requests.get("https://ASSISTant.davidtso.repl.co")


@tasks.loop(seconds=45)
async def keepalive_loop():
    threading.Thread(target=fetch_on_thread).start()


def setup(bot):
    global server

    if server:
        print("[server] WARNING! server already exists")

    if enable_keepalive:
        keepalive_loop.start()

    server = threading.Thread(target=start_server)
    server.start()


def teardown(bot):
    global server

    if enable_keepalive:
        keepalive_loop.cancel()

    if server:
        print("[server] Tearing down server")
        requests.get(f"http://127.0.0.1:{PORT}/shutdown")
        server.join()
        server.close()
        server = None
