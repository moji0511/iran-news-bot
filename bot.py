import telebot
import os

# 8437051202:AAEonwByisCkzIuPRzQ7d2B0FTp_LyXWF0w
TOKEN = os.getenv("BOT_TOKEN", "PASTE_YOUR_TOKEN_HERE")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "سلام 👋 من ربات آماده‌ام!")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, f"پیام گرفتم: {message.text}")

print("Bot is running...")
bot.polling()
