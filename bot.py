import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = '8029623606:AAEAEqoNkNq_B_oIPFhYFue0AjxK6vaX7fM'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! برای دیدن لیست فیلم‌ها دستور /movies را ارسال کن.")

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

        if len(movies) >= 20:
            break

    return movies

async def movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    movies_list = get_movies()
    if not movies_list:
        await update.message.reply_text("متاسفانه نتونستم فیلمی پیدا کنم!")
        return

    for movie in movies_list:
        title = movie['title']
        url = movie['link']
        rating = movie['rating']
        summary = movie['summary']
        image_url = movie['image']

        message = f"🎬 *{title}*\n⭐ امتیاز: {rating}\n\n📖 خلاصه:\n{summary}\n\n🔗 [مشاهده فیلم]({url})"

        if image_url:
            await update.message.reply_photo(photo=image_url, caption=message, parse_mode='Markdown')
        else:
            await update.message.reply_text(message, parse_mode='Markdown')

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('movies', movies))

    PORT = int(os.environ.get('PORT', 8443))
    WEBHOOK_URL = 'https://my-telegram-bot-l8ts.onrender.com/webhook'

    app.run_webhook(
        host='0.0.0.0',
        port=PORT,
        webhook_url=WEBHOOK_URL
    )

if __name__ == '__main__':
    main()
