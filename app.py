from fastapi import FastAPI, Request
import requests
import os

# توکن ربات
TOKEN = os.getenv("BOT_TOKEN", "8437051202:AAFExzUTY9OfCE7MPGb6bkEHBhLjrMmhRuw")
URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

app = FastAPI()

# تست رندر
@app.get("/")
async def home():
    return {"status": "ok"}

# وبهوک
@app.post("/webhook/")
async def webhook(request: Request):
    data = await request.json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text.lower() == "news":
            # فعلا تست – بعدا وصل می‌کنیم به خبرهای واقعی
            news_list = [
                "خبر اول",
                "خبر دوم",
                "خبر سوم",
                "خبر چهارم",
                "خبر پنجم",
                "خبر ششم",
                "خبر هفتم",
                "خبر هشتم",
                "خبر نهم",
                "خبر دهم",
            ]
            msg = "\n".join([f"📰 {n}" for n in news_list])
            msg += "\n\n📌 گروه بچه‌های ایرون @iran9897"

            requests.post(URL, json={"chat_id": chat_id, "text": msg})

    return {"ok": True}
