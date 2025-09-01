# main.py
from fastapi import FastAPI, Request
import requests
import os

TOKEN = os.getenv("BOT_TOKEN", "8437051202:AAFExzUTY9OfCE7MPGb6bkEHBhLjrMmhRuw")
API_URL = f"https://api.telegram.org/bot{TOKEN}"

app = FastAPI()

@app.get("/")
def home():
    return {"status": "ok"}

@app.post("/webhook/")
async def webhook(req: Request):
    data = await req.json()
    print(">>> دریافت شد:", data)  # لاگ برای تست

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text.lower() == "news":
            msg = "📰 این یه تست موفقیت‌آمیزه!\nربات پیام رو گرفت."
            requests.post(f"{API_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": msg
            })

    return {"ok": True}
