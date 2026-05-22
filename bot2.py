from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    CallbackQueryHandler
)

import os
TOKEN = os.environ.get('TOKEN')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🍽 Открыть меню", web_app=WebAppInfo(url="https://mertselcuk2023-cmyk.github.io/MasterFood/menu.html"))],
        [InlineKeyboardButton("🚚 Доставка и оплата", callback_data="Доставка и оплата")],
        [InlineKeyboardButton("🤝 Реферальная программа", callback_data="Реферальная программа")],
        [InlineKeyboardButton("🍲 Предложить блюдо", callback_data="Предложить блюдо")],
        [InlineKeyboardButton("💰 Баланс", callback_data="Баланс")],
        [InlineKeyboardButton("⚙️ Настройки", callback_data="Настройки")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    welcome_text = "👋 Добро пожаловать в MasterFood!"
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if data == "Доставка и оплата":
        text = "Информация о доставке и оплате."
    elif data == "Реферальная программа":
        text = "Информация о реферальной программе."
    elif data == "Предложить блюдо":
        text = "Вы можете предложить блюдо, отправив его название и описание."
    elif data == "Баланс":
        text = "Ваш текущий баланс: 0 ₽."
    elif data == "Настройки":
        text = "Настройки пока недоступны."
    else:
        text = "Неизвестная команда."

    await query.edit_message_text(text=text)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Бот запущен...")
    app.run_polling()
