from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, ConversationHandler,
    MessageHandler, filters, ContextTypes
)
import os

TOKEN = os.environ.get('TOKEN')
ADMIN_CHAT_ID = -5254029215  # Ваш ID группы для заказов

# Состояния разговора
(
    SELECTING_DISH,
    CONFIRMING_QUANTITY,
    ENTERING_ADDRESS,
    ENTERING_TIME,
    ENTERING_PAYMENT
) = range(5)

menu = [
    {'name': 'Салат Цезарь', 'description': 'Классический салат с курицей', 'price': 350},
    {'name': 'Стейк из говядины', 'description': 'Сочный стейк средней прожарки', 'price': 1200},
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Добро пожаловать! Введите /menu чтобы увидеть меню.")

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for i, dish in enumerate(menu):
        keyboard.append([InlineKeyboardButton(f"Заказать {dish['name']} ({dish['price']} ₽)", callback_data=str(i))])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Меню:", reply_markup=reply_markup)
    return SELECTING_DISH

async def select_dish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    dish_id = int(query.data)
    context.user_data['dish_id'] = dish_id
    dish = menu[dish_id]
    await query.edit_message_text(text=f"Вы выбрали: {dish['name']}. Сколько штук вы хотите заказать?")
    return CONFIRMING_QUANTITY

async def quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        qty = int(update.message.text)
        if qty <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите корректное положительное число.")
        return CONFIRMING_QUANTITY
    context.user_data['quantity'] = qty
    await update.message.reply_text("Введите адрес доставки:")
    return ENTERING_ADDRESS

async def address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['address'] = update.message.text
    await update.message.reply_text("Введите желаемое время доставки (например, 13:30):")
    return ENTERING_TIME

async def delivery_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['delivery_time'] = update.message.text
    await update.message.reply_text("Введите способ оплаты (наличные, карта, онлайн):")
    return ENTERING_PAYMENT

async def payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['payment'] = update.message.text
    dish_id = context.user_data['dish_id']
    dish = menu[dish_id]
    qty = context.user_data['quantity']
    address = context.user_data['address']
    time = context.user_data['delivery_time']
    payment = context.user_data['payment']
    user = update.effective_user

    order_text = (
        f"Новый заказ!\n"
        f"Пользователь: {user.full_name} (@{user.username}, id: {user.id})\n"
        f"Блюдо: {dish['name']}\n"
        f"Количество: {qty}\n"
        f"Адрес доставки: {address}\n"
        f"Время доставки: {time}\n"
        f"Оплата: {payment}\n"
        f"Итог: {dish['price'] * qty} ₽"
    )

    # Отправляем заказ в группу администраторов
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=order_text)

    # Подтверждаем пользователю
    await update.message.reply_text("Ваш заказ принят! Спасибо!")

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Заказ отменён.")
    return ConversationHandler.END

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('menu', menu_command)],
        states={
            SELECTING_DISH: [CallbackQueryHandler(select_dish)],
            CONFIRMING_QUANTITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, quantity)],
            ENTERING_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, address)],
            ENTERING_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, delivery_time)],
            ENTERING_PAYMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, payment)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)

    print("Бот запущен...")
    application.run_polling()
