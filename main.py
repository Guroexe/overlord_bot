import logging
import json
import os
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputFile
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Настройка логгирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Константы
TOKEN = os.getenv("TOKEN")
FREE_TRAIN_VIDEO = "https://www.youtube.com/watch?v=10b_j5gBAg8"
PRO_VERSION_VIDEO = "https://www.youtube.com/watch?v=QKLOb6f5L-k"
COLAB_URL = "https://colab.research.google.com/drive/1lWfrS0Jh0B2B99IJ26aincVXylaoLuDq?usp=sharing"
TRIBUT_URL = "https://t.me/tribute/app?startapp=ep_8y0gVeOLXYRcOrfRtGTMLW8vu0C82z72WfxBEEtJz3ofJTky32"
TATTOO_TRAINING_VIDEO = "https://www.youtube.com/watch?v=GX_ZbWx0oYY"
OFFLINE_TRAINING_VIDEO = "https://www.youtube.com/watch?v=Kopx3whZquc"
ONLINE_TRAINING_VIDEO = "https://www.youtube.com/watch?v=10b_j5gBAg8"
CREATOR_CHANNEL = "https://t.me/gurovlad"

# Загрузка промтов
with open("prompts.json", "r", encoding="utf-8") as f:
    PROMPTS = json.load(f)

# Глобальный словарь для хранения состояний пользователей
user_states = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка команды /start"""
    user = update.effective_user
    user_states[user.id] = {"prompt_index": 0}
    
    await update.message.reply_text(f"<b>🎬 Обучающее видео:</b>\n{FREE_TRAIN_VIDEO}", parse_mode='HTML')
    
    description = (
        "<b>🖌️ OVERLORD AI INK (Free Train)</b>\n\n"
        "Бесплатная версия нейросети для генерации изображений в стиле sigilism, tribal, dark tattoo.\n\n"
        "<b>Как использовать:</b>\n"
        "1. Введите текстовый промт на английском\n"
        "2. Настройте параметры (Sampling method - DPM++ 2M SDE, Steps - 20)\n"
        "3. Генерируйте изображения бесплатно!\n\n"
        f"Создатель: {CREATOR_CHANNEL}"
    )
    await update.message.reply_text(description, parse_mode='HTML')
    
    try:
        with open(os.path.join("static", "14.gif"), "rb") as gif_file:
            await update.message.reply_animation(
                animation=InputFile(gif_file),
                caption=f"<b>🚀 Начать генерацию!</b>\nИспользуй COLAB: {COLAB_URL}",
                parse_mode='HTML'
            )
    except Exception as e:
        logger.error(f"Error sending gif: {e}")
        await update.message.reply_text(f"<b>🚀 Начать генерацию:</b>\n{COLAB_URL}", parse_mode='HTML')
    
    keyboard = [
        [InlineKeyboardButton("Пример промта", callback_data="show_prompt")],
        [InlineKeyboardButton("OVERLORD AI INK PRO", callback_data="pro_version")],
        [InlineKeyboardButton("Обучение Тату IKONA", callback_data="tattoo_training")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)

async def show_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показ примера промта с изображением"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_state = user_states.get(user_id, {"prompt_index": 0})
    current_index = user_state["prompt_index"]
    
    # Получение текущего промта
    prompt_data = PROMPTS[current_index]
    image_path = os.path.join("static", prompt_data["image"])
    prompt_text = prompt_data["prompt"]
    
    # Отправка изображения
    try:
        with open(image_path, "rb") as photo_file:
            await query.message.reply_photo(
                photo=InputFile(photo_file),
                caption=prompt_text,
                parse_mode='HTML'
            )
    except Exception as e:
        logger.error(f"Error sending photo: {e}")
        await query.message.reply_text(
            f"Пример промта:\n{prompt_text}\n\n(Изображение недоступно)",
            parse_mode='HTML'
        )
    
    # Обновление индекса (циклически)
    next_index = (current_index + 1) % len(PROMPTS)
    user_states[user_id] = {"prompt_index": next_index}
    
    keyboard = [
        [InlineKeyboardButton("Ещё пример", callback_data="show_prompt")],
        [InlineKeyboardButton("Главное меню", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Что дальше?", reply_markup=reply_markup)

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показ главного меню"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("OVERLORD AI INK (Free Train)", callback_data="free_train")],
        [InlineKeyboardButton("OVERLORD AI INK PRO", callback_data="pro_version")],
        [InlineKeyboardButton("Обучение Тату IKONA", callback_data="tattoo_training")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("<b>Главное меню:</b>", reply_markup=reply_markup, parse_mode='HTML')

async def free_train(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Повторная отправка стартового сообщения"""
    query = update.callback_query
    await query.answer()
    
    await query.message.reply_text(f"<b>🎬 Обучающее видео:</b>\n{FREE_TRAIN_VIDEO}", parse_mode='HTML')
    
    description = (
        "<b>🖌️ OVERLORD AI INK (Free Train)</b>\n\n"
        "Бесплатная версия с 3 стилями генераций изображений.\n\n"
        f"Создатель: {CREATOR_CHANNEL}"
    )
    await query.message.reply_text(description, parse_mode='HTML')
    
    try:
        with open(os.path.join("static", "14.gif"), "rb") as gif_file:
            await query.message.reply_animation(
                animation=InputFile(gif_file),
                caption=f"<b>🚀 Начать генерацию!</b>\nCOLAB: {COLAB_URL}",
                parse_mode='HTML'
            )
    except Exception as e:
        logger.error(f"Error sending gif: {e}")
        await query.message.reply_text(f"<b>🚀 Начать генерацию:</b>\n{COLAB_URL}", parse_mode='HTML')
    
    keyboard = [
        [InlineKeyboardButton("Пример промта", callback_data="show_prompt")],
        [InlineKeyboardButton("OVERLORD AI INK PRO", callback_data="pro_version")],
        [InlineKeyboardButton("Обучение Тату IKONA", callback_data="tattoo_training")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Выберите действие:", reply_markup=reply_markup)

# Остальные функции (pro_version, tattoo_training, offline_training, online_training, sign_up) остаются без изменений
# ...

def main() -> None:
    """Запуск бота"""
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(show_prompt, pattern="^show_prompt$"))
    application.add_handler(CallbackQueryHandler(main_menu, pattern="^main_menu$"))
    application.add_handler(CallbackQueryHandler(free_train, pattern="^free_train$"))
    application.add_handler(CallbackQueryHandler(pro_version, pattern="^pro_version$"))
    application.add_handler(CallbackQueryHandler(tattoo_training, pattern="^tattoo_training$"))
    application.add_handler(CallbackQueryHandler(offline_training, pattern="^offline_training$"))
    application.add_handler(CallbackQueryHandler(online_training, pattern="^online_training$"))
    application.add_handler(CallbackQueryHandler(sign_up, pattern="^sign_up$"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    application.run_polling()

if __name__ == "__main__":
    main()
