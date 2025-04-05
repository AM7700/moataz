
import random
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

TOKEN = "7826190251:AAGDwIOgvqKWJ550MVmnj0kEpDtc9AEJZmU"

conn = sqlite3.connect("players.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS players (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    height INTEGER DEFAULT 0,
    money INTEGER DEFAULT 0
)
""")
conn.commit()

def register_player(user_id: int, username: str):
    cursor.execute("INSERT OR IGNORE INTO players (user_id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()

def climb(user_id: int):
    events = [
        ("وجدت عملة ذهبية!", 5, 10),
        ("قفزت قفزة عالية!", 10, 0),
        ("رياح قوية أعادتك للخلف!", -5, -5),
        ("وقعت في فخ!", -10, -10),
        ("ارتفعت بشكل طبيعي.", 3, 2)
    ]
    event = random.choice(events)
    cursor.execute("UPDATE players SET height = height + ?, money = money + ? WHERE user_id = ?", (event[1], event[2], user_id))
    conn.commit()
    return event

def get_stats(user_id: int):
    cursor.execute("SELECT height, money FROM players WHERE user_id = ?", (user_id,))
    return cursor.fetchone()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    register_player(user.id, user.username or "بدون اسم")
    keyboard = [[InlineKeyboardButton("⬆️ اصعد", callback_data="climb")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"أهلاً {user.first_name}! مستعد تبدأ الصعود؟", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    register_player(user.id, user.username or "بدون اسم")
    event = climb(user.id)
    height, money = get_stats(user.id)
    text = f"{event[0]}\n\nالارتفاع الحالي: {height} متر\nالرصيد: {money} عملة"
    await query.answer()
    await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬆️ اصعد", callback_data="climb")]]))

async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
