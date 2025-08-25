import telebot
import os
import requests
from bs4 import BeautifulSoup

TOKEN = os.getenv("BOT_TOKEN", "PASTE_YOUR_TOKEN_HERE")
bot = telebot.TeleBot(TOKEN)

# --- دستور start ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "سلام 👋 من ربات خبر مجی هستم. دستور 'news' رو بفرست تا آخرین اخبار ایران رو بیاری برات.")

# --- تابع گرفتن خبر از BBC ---
def fetch_bbc():
    url = "https://www.bbc.com/persian/topics/cnq68n4291gt"
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    titles = [a.get_text() for a in soup.find_all("a") if a.get_text()]
    return titles[:3]

# --- تابع گرفتن خبر از DW ---
def fetch_dw():
    url = "https://www.dw.com/fa-ir/%D8%A7%DB%8C%D8%B1%D8%A7%D9%86/s-10607"
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    titles = [h.get_text() for h in soup.find_all("a") if h.get_text()]
    return titles[:3]

# --- دستور news ---
@bot.message_handler(func=lambda message: message.text.lower() == "news")
def send_news(message):
    try:
        news = []

        # BBC
        try:
            news += fetch_bbc()
        except:
            pass

        # DW
        try:
            news += fetch_dw()
        except:
            pass

        if news:
            text = "\n\n".join([f"📰 {t}" for t in news[:10]])
            bot.reply_to(message, f"📌 آخرین خبرهای ایران:\n\n{text}")
        else:
            bot.reply_to(message, "⚠️ خبری پیدا نشد. بعداً امتحان کن.")

    except Exception as e:
        bot.reply_to(message, f"❌ خطا: {e}")

# --- اکو کردن بقیه پیام‌ها ---
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    if message.text.lower() != "news":
        bot.reply_to(message, f"پیام گرفتم: {message.text}")

print("Bot is running...")
bot.polling()
