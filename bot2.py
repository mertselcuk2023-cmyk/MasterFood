from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    CallbackQueryHandler, MessageHandler, filters
)
import os
import json

TOKEN = os.environ.get('TOKEN')
ADMIN_CHAT_ID = -5254029215  # замените на ваш ID группы

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

async def receive_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = update.message.web_app_data.data
    order = json.loads(data)

    lines = ["Новый заказ:\n"]
    total = 0
    for item in order.get('order', []):
        name = item.get('name')
        qty = item.get('quantity')
        price = item.get('price')
        sum_price = price * qty
        total += sum_price
        lines.append(f"{name} — {qty} шт. — {price} ₽/шт — Итого: {sum_price} ₽")

    user = update.effective_user
    lines.append(f"\nПользователь: {user.full_name} (@{user.username}), ID: {user.id}")
    lines.append(f"\nОбщая сумма заказа: {total} ₽")

    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text="\n".join(lines))
    await update.message.reply_text("Спасибо! Ваш заказ получен и обрабатывается.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, receive_order))

    print("Бот запущен...")
    app.run_polling()
