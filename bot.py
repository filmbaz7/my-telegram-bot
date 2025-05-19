import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from aiohttp import web

TOKEN = '8029623606:AAEAEqoNkNq_B_oIPFhYFue0AjxK6vaX7fM'
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"https://my-telegram-bot-l8ts.onrender.com{WEBHOOK_PATH}"

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

async def handle(request):
    data = await request.json()
    await application.update_queue.put(Update.de_json(data, application.bot))
    return web.Response()

async def on_startup(app):
    await application.bot.set_webhook(url=WEBHOOK_URL)

application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler('start', start))
application.add_handler(CommandHandler('movies', movies))

app = web.Application()
app.router.add_post(WEBHOOK_PATH, handle)
app.on_startup.append(on_startup)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    web.run_app(app, port=port)
