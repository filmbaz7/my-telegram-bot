import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = '8029623606:AAEAEqoNkNq_B_oIPFhYFue0AjxK6vaX7fM'
WEBHOOK_URL = f'https://my-telegram-bot-l8ts.onrender.com/webhook/{TOKEN}'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! برای دیدن لیست فیلم‌ها دستور /movies رو بزن.")

def get_movies():
    url = 'https://www.digitoon.tv/'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'lxml')

    movies = []
    for item in soup.select('div.card-media'):
        title = item.get('title') or 'بدون عنوان'
        link_tag = item.find('a')
        link = 'https://www.digitoon.tv' + link_tag['href'] if link_tag else '#'
        image_tag = item.find('img')
        image = image_tag['src'] if image_tag else None

        movies.append({
            'title': title.strip(),
            'link': link,
            'rating': 'نامشخص',
            'summary': 'توضیح موجود نیست',
            'image': image
        })

        if len(movies) >= 10:
            break

    return movies

async def movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    movie_list = get_movies()
    if not movie_list:
        await update.message.reply_text("فیلمی پیدا نشد!")
        return

    for movie in movie_list:
        msg = f"🎬 *{movie['title']}*\n⭐ امتیاز: {movie['rating']}\n📖 {movie['summary']}\n🔗 [مشاهده فیلم]({movie['link']})"
        if movie['image']:
            await update.message.reply_photo(photo=movie['image'], caption=msg, parse_mode='Markdown')
        else:
            await update.message.reply_text(msg, parse_mode='Markdown')

async def set_webhook(app: Application):
    await app.bot.set_webhook(WEBHOOK_URL)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('movies', movies))

    # ثبت وب‌هوک در هنگام بالا آمدن
    app.post_init = set_webhook

    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),
        webhook_url=WEBHOOK_URL,
    )

if __name__ == '__main__':
    main()
