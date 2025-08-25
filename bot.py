import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import feedparser

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# 📌 اینجا توکن رباتت رو بذار
BOT_TOKEN = "8437051202:AAEonwByisCkzIuPRzQ7d2B0FTp_LyXWF0w"

# منابع خبری (RSS)
NEWS_SOURCES = {
    "BBC": "https://www.bbc.com/persian/index.xml",
    "DW": "https://rss.dw.com/rdf/rss-farsi-news",
    "رادیو فردا": "https://www.radiofarda.com/api/zyoeo",
    "VOA": "https://ir.voanews.com/api/zm$ome",
    "Euronews": "https://fa.euronews.com/rss?level=theme&name=news"
}

# تابع گرفتن خبرها
def get_latest_news():
    news_items = []
    for source, url in NEWS_SOURCES.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:2]:  # از هر منبع ۲ خبر
                news_items.append(f"📰 [{source}] {entry.title}")
        except Exception as e:
            news_items.append(f"⚠️ خطا در دریافت خبر از {source}")
    return news_items[:10]

# دستور /news
async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    news_items = get_latest_news()
    if news_items:
        message = "📌 آخرین خبرهای ایران:\n\n" + "\n".join(news_items)
    else:
        message = "❌ نتونستم خبر جدید پیدا کنم."
    await update.message.reply_text(message)

# ران اصلی
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("news", news))
    app.run_polling()

if __name__ == "__main__":
    main()
