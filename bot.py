import os
import asyncio
import requests
from bs4 import BeautifulSoup
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = '8029623606:AAEAEqoNkNq_B_oIPFhYFue0AjxK6vaX7fM'
WEBHOOK_URL = 'https://my-telegram-bot-l8ts.onrender.com'  # آدرس رندر شما

PORT = int(os.environ.get('PORT', '8443'))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! برای دیدن لیست فیلم‌ها دستور /movies را ارسال کن.")

def get_movies():
    url = 'https://upmedia.movie/iran-movies'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    movies = []
    # هر فیلم داخل div با کلاس movie-item هست
    for item in soup.select('div.movie-item'):
        title_tag = item.select_one('h3.movie-title')
        title = title_tag.text.strip() if title_tag else 'بدون عنوان'

        link_tag = item.select_one('a')
        link = link_tag['href'] if link_tag else '#'
        if link and not link.startswith('http'):
            link = 'https://upmedia.movie' + link

        image_tag = item.select_one('img')
        image = image_tag['src'] if image_tag else None
        if image and image.startswith('/'):
            image = 'https://upmedia.movie' + image

        summary_tag = item.select_one('div.movie-desc')
        summary = summary_tag.text.strip() if summary_tag else 'بدون توضیح'

        rating_tag = item.select_one('span.rating')
        rating = rating_tag.text.strip() if rating_tag else 'نامشخص'

        movies.append({
            'title': title,
            'link': link,
            'image': image,
            'summary': summary,
            'rating': rating
        })

        if len(movies) >= 20:
            break

    return movies

async def movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    movies_list = get_movies()
    if not movies_list:
        await update.message.reply_text("متاسفانه فیلمی پیدا نکردم!")
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
