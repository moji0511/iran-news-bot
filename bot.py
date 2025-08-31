import os
import json
import logging
from flask import Flask, request, jsonify
import requests
from scraper import get_latest_iran_headlines

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_API = "https://api.telegram.org/bot"
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "hook")  # مثلا یک رشته تصادفی امن

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set. Please set it as an environment variable.")

app = Flask(__name__)


def telegram_send_message(chat_id: int, text: str, parse_mode: str = None):
    url = f"{TELEGRAM_API}{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    if parse_mode:
        payload["parse_mode"] = parse_mode
    try:
        r = requests.post(url, json=payload, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logger.exception("sendMessage failed: %s", e)
        return None


def set_webhook(base_url: str):
    # مسیر وب‌هوک: https://<render-app>/<webhook>/<WEBHOOK_SECRET>
    webhook_url = f"{base_url.rstrip('/')}/webhook/{WEBHOOK_SECRET}"
    url = f"{TELEGRAM_API}{BOT_TOKEN}/setWebhook"
    try:
        r = requests.post(url, json={"url": webhook_url}, timeout=15)
        r.raise_for_status()
        logger.info("Webhook set to %s | result=%s", webhook_url, r.text)
    except Exception as e:
        logger.exception("setWebhook failed: %s", e)


@app.route("/")
def health():
    return {"ok": True, "service": "iran-news-bot"}


@app.route(f"/webhook/<secret>", methods=["POST"])
def webhook(secret):
    if secret != WEBHOOK_SECRET:
        return jsonify({"ok": False, "error": "forbidden"}), 403

    update = request.get_json(force=True, silent=True) or {}
    message = update.get("message") or update.get("edited_message")
    if not message:
        return jsonify({"ok": True})

    chat = message.get("chat", {})
    chat_id = chat.get("id")
    text = (message.get("text") or "").strip()

    # تریگر: کلمه news یا دستور /news
    lowered = text.lower()
    is_news_trigger = ("news" in lowered) or lowered.startswith("/news")

    if is_news_trigger and chat_id:
        try:
            titles = get_latest_iran_headlines(limit=10)
            if not titles:
                raise RuntimeError("no titles")

            lines = ["\uD83D\uDCCC آخرین خبرهای ایران:"]
            for i, t in enumerate(titles, 1):
                # فقط تیتر، بدون لینک
                clean = t.replace("\n", " ").strip()
                lines.append(f"{i}. {clean}")
            lines.append("")
            lines.append("گروه بچه‌های ایرون @iran9897")

            telegram_send_message(chat_id, "\n".join(lines))
        except Exception:
            logger.exception("failed to fetch headlines")
            telegram_send_message(chat_id, "متاسفم، الان نتونستم خبرها رو بیارم. چند دقیقه دیگه دوباره امتحان کن.")

    return jsonify({"ok": True})


if __name__ == "__main__":
    # روی Render می‌تونیم از RENDER_EXTERNAL_URL استفاده کنیم برای ست کردن وب‌هوک
    base_url = os.getenv("RENDER_EXTERNAL_URL")
    if base_url:
        set_webhook(base_url)
    port = int(os.getenv("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
