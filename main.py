from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import json

PROMPT_IMAGES = ["1.png", "2.png", "3.png", "4.png"]
PROMPTS = json.load(open("prompts.json"))
user_prompt_index = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_prompt_index[chat_id] = 0

    await update.message.reply_text("🔗 Видео: https://www.youtube.com/watch?v=J4qY9DYE184")
    await update.message.reply_text("🧠 OVERLORD AI INK (Free Train):\nЗдесь ты можешь попробовать использовать Stable Diffusion бесплатно...\nИнструкция по применению ниже 👇")

    await context.bot.send_animation(chat_id=chat_id,
        animation="https://huggingface.co/guroexe/overlord_bot/resolve/main/14.gif",
        caption="🔥 Запуск через Google Colab: [жми сюда](https://colab.research.google.com/drive/1vR5xxZ...)", parse_mode='Markdown'
    )

    keyboard = [
        [InlineKeyboardButton("Пример промта", callback_data="example")],
        [InlineKeyboardButton("Главное меню", callback_data="menu")],
        [InlineKeyboardButton("Полная версия OVERLORD AI INK PRO", callback_data="pro")]
    ]
    await update.message.reply_text("Выбери действие:", reply_markup=InlineKeyboardMarkup(keyboard))

async def show_example(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.message.chat.id
    await query.answer()

    index = user_prompt_index.get(chat_id, 0)
    img = PROMPT_IMAGES[index]
    prompt_text = PROMPTS[img]

    url = f"https://huggingface.co/guroexe/overlord_bot/resolve/main/{img}"
    await context.bot.send_photo(chat_id=chat_id, photo=url, caption=prompt_text)

    user_prompt_index[chat_id] = (index + 1) % len(PROMPT_IMAGES)

    keyboard = [
        [InlineKeyboardButton("Пример промта", callback_data="example")],
        [InlineKeyboardButton("Главное меню", callback_data="menu")]
    ]
    await context.bot.send_message(chat_id=chat_id, text="Хочешь ещё?", reply_markup=InlineKeyboardMarkup(keyboard))

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("OVERLORD AI INK (Free Train)", callback_data="start")],
        [InlineKeyboardButton("Полная версия OVERLORD AI INK PRO", callback_data="pro")]
    ]
    await query.message.reply_text("Главное меню", reply_markup=InlineKeyboardMarkup(keyboard))

async def show_pro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "⚙️ Разница с PRO версией:\n— доступ к множеству моделей\n— кастомизация стиля через Lora\n— обновления и приватный доступ\n\nПодписка через Tribut:"
    )

    keyboard = [
        [InlineKeyboardButton("Подписка на 1 месяц — 2990₽", url="https://t.me/tribut_link_1")],
        [InlineKeyboardButton("Навсегда — 11990₽", url="https://t.me/tribut_link_2")]
    ]
    await query.message.reply_text("Выбери подписку:", reply_markup=InlineKeyboardMarkup(keyboard))

def main():
    app = ApplicationBuilder().token("7972832759:AAEwXCLf7bXdYguvmx4cJvPCfnfWmslXVW8").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(show_example, pattern="^example$"))
    app.add_handler(CallbackQueryHandler(show_menu, pattern="^menu$"))
    app.add_handler(CallbackQueryHandler(start, pattern="^start$"))
    app.add_handler(CallbackQueryHandler(show_pro, pattern="^pro$"))
    app.run_polling()

if __name__ == "__main__":
    main()
