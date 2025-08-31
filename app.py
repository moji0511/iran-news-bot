from flask import Flask, request
import sys

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

@app.route("/webhook/", methods=["POST"])
def webhook():
    update = request.get_json()
    print(">>> Update received:", update, file=sys.stdout, flush=True)
    return {"ok": True}
