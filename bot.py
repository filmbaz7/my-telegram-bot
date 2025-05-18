import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = '8029623606:AAEAEqoNkNq_B_oIPFhYFue0AjxK6vaX7fM'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! برای دیدن لیست فیلم‌ها دستور /movies را ارسال کن.")

def get_movies():
    url = 'https://yts.mx/api/v2/list_movies.json?limit=20'  # 20 فیلم اول
    response = requests.get(url)
    data = response.json()

    movies = []
    if data['status'] == 'ok' and data['data']['movie_count'] > 0:
        for movie in data['data']['movies']:
            movies.append({
                'title': movie['title'],
                'link': movie['url'],
                'rating': movie.get('rating', 'ندارد'),
                'summary': movie.get('summary', 'بدون توضیح'),
                'image': movie.get('large_cover_image', None)
            })
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

    app.run_polling()

if __name__ == '__main__':
    main()
