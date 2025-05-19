import requests
from bs4 import BeautifulSoup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

TOKEN = '8029623606:AAEAEqoNkNq_B_oIPFhYFue0AjxK6vaX7fM'

BASE_URL = "https://www.uptvs.com/category/moviesz"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! برای دیدن لیست فیلم‌ها دستور /movies را بفرستید."
    )

def fetch_movies():
    try:
        response = requests.get(BASE_URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        movies = []

        items = soup.select(".item")
        for item in items[:10]:  # فقط 10 فیلم اول
            title = item.select_one(".name").text.strip()
            link = item.select_one("a").get("href")
            img = item.select_one("img").get("src")
            movies.append({
                "title": title,
                "link": link,
                "img": img
            })
        return movies
    except Exception as e:
        print(f"Error fetching movies: {e}")
        return []

async def movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    movies = fetch_movies()
    if not movies:
        await update.message.reply_text("متأسفانه نتوانستم فیلمی پیدا کنم.")
        return

    keyboard = []
    for movie in movies:
        keyboard.append([InlineKeyboardButton(movie['title'], url=movie['link'])])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_photo(
        photo=movies[0]['img'],
        caption="فیلم‌های جدید:\nلطفا روی عنوان فیلم مورد نظر کلیک کنید تا به صفحه آن بروید.",
        reply_markup=reply_markup
    )

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("movies", movies))

    print("ربات در حال اجراست...")
    app.run_polling()
