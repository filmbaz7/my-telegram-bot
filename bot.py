import os
import asyncio
import requests
from urllib.parse import urlparse, parse_qs, unquote
from bs4 import BeautifulSoup
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes

# اطلاعات شما:
TOKEN = '8029623606:AAEAEqoNkNq_B_oIPFhYFue0AjxK6vaX7fM'
WEBHOOK_URL = 'https://my-telegram-bot-l8ts.onrender.com'
PORT = int(os.environ.get('PORT', '8443'))

# شروع
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! برای دیدن لیست فیلم‌ها دستور /movies را بفرست.")

# استخراج فیلم‌ها از Digitoon
def get_movies():
    url = 'https://www.digitoon.tv/'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'lxml')

    movie_names = soup.find_all('div', class_='intl-home-2_name__Kt3Dz')
    movie_links = soup.find_all('a', class_='intl-home-2_card__c7h62')

    movies = []
    for i in range(min(len(movie_names), len(movie_links))):
        title = movie_names[i].text.strip()
        
        # لینک صفحه فیلم
        href = movie_links[i].get('href')
        link = f"https://www.digitoon.tv{href}" if href else '#'

        # عکس فیلم
        image_tag = movie_links[i].find('img')
        image = None
        if image_tag:
            src = image_tag.get('src') or ''
            parsed_url = urlparse(src)
            params = parse_qs(parsed_url.query)
            real_url = params.get('url', [None])[0]
            if real_url:
                image = unquote(real_url)
            else:
                image = src

        movies.append({
            'title': title,
            'link': link,
            'rating': 'نامشخص',
            'summary': 'توضیحی موجود نیست',
            'image': image
        })

        if len(movies) >= 20:
            break

    return movies

# فرمان /movies
async def movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    movies_list = get_movies()
    if not movies_list:
        await update.message.reply_text("متاسفانه فیلمی پیدا نشد.")
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

# ست کردن وبهوک
async def set_webhook(bot: Bot):
    await bot.set_webhook(url=WEBHOOK_URL)

# تابع اصلی
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
