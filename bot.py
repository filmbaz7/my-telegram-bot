import os
import asyncio
import requests
from bs4 import BeautifulSoup
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = '8029623606:AAEAEqoNkNq_B_oIPFhYFue0AjxK6vaX7fM'
WEBHOOK_URL = 'https://my-telegram-bot-l8ts.onrender.com'
PORT = int(os.environ.get('PORT', '8443'))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! برای دیدن لیست فیلم‌ها دستور /movies را بفرست.")

def get_movies():
    url = 'https://uptvs.com/category/moviesz'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    movies = []
    for item in soup.select('div.post-item', limit=20):
        title_tag = item.select_one('h2.title')
        image_tag = item.select_one('img')
        link_tag = item.select_one('a')

        title = title_tag.get_text(strip=True) if title_tag else 'بدون عنوان'
        image = image_tag['src'] if image_tag and 'src' in image_tag.attrs else None
        link = link_tag['href'] if link_tag and 'href' in link_tag.attrs else '#'

        movies.append({
            'title': title,
            'link': link,
            'image': image,
            'rating': 'نامشخص',
            'summary': 'خلاصه‌ای موجود نیست'
        })

    return movies

async def movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    movies_list = get_movies()
    if not movies_list:
        await update.message.reply_text("متاسفانه نتونستم فیلمی پیدا کنم!")
        return

    for movie in movies_list:
        message = f"🎬 *{movie['title']}*\n⭐ امتیاز: {movie['rating']}\n\n📖 خلاصه:\n{movie['summary']}\n\n🔗 [مشاهده فیلم]({movie['link']})"
        if movie['image']:
            await update.message.reply_photo(photo=movie['image'], caption=message, parse_mode='Markdown')
        else:
            await update.message.reply_text(message, parse_mode='Markdown')

async def set_webhook(bot: Bot):
    await bot.set_webhook(url=WEBHOOK_URL)

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('movies', movies))

    bot = Bot(token=TOKEN)
    asyncio.get_event_loop().run_until_complete(set_webhook(bot))

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL,
    )

if __name__ == '__main__':
    main()
