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
TOKEN = os.getenv("TOKEN", "7972832759:AAGLOsFkxn_elDVNKsM2hk7Vt1qpoQawE2o")
YOUTUBE_URL = "https://www.youtube.com/watch?v=J4qY9DYE184"
COLAB_URL = "https://colab.research.google.com/drive/your-colab-link"
TRIBUT_URL = "https://t.me/your_tribut_channel"

# Загрузка промтов
with open("prompts.json", "r", encoding="utf-8") as f:
    PROMPTS = json.load(f)

# Глобальные переменные для состояний пользователей
user_states = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка команды /start"""
    user_id = update.effective_user.id
    user_states[user_id] = {"prompt_index": 0}
    
    # Отправка YouTube видео
    await update.message.reply_text(f"🎬 Обучающее видео: {YOUTUBE_URL}")
    
    # Отправка описания
    description = (
        "🖌️ OVERLORD AI INK (Free Train)\n\n"
        "Это бесплатная версия нейросети для генерации изображений в стиле аниме и манга. "
        "Используйте Stable Diffusion для создания уникальных артов без ограничений!\n\n"
        "Как использовать:\n"
        "1. Введите текстовый промт на английском\n"
        "2. Настройте параметры (стиль, детализацию)\n"
        "3. Генерируйте изображения бесплатно!"
    )
    await update.message.reply_text(description)
    
    # Отправка GIF
    gif_path = os.path.join("static", "14.gif")
    with open(gif_path, "rb") as gif_file:
        await update.message.reply_animation(
            animation=InputFile(gif_file),
            caption=f"🚀 Начать генерацию: {COLAB_URL}"
        )
    
    # Кнопка "Пример промта"
    keyboard = [
        [InlineKeyboardButton("Пример промта", callback_data="show_prompt")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Попробуйте готовые промты:", reply_markup=reply_markup)

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
    with open(image_path, "rb") as photo_file:
        await query.message.reply_photo(
            photo=InputFile(photo_file),
            caption=prompt_text
        )
    
    # Обновление индекса (циклически)
    next_index = (current_index + 1) % len(PROMPTS)
    user_states[user_id] = {"prompt_index": next_index}
    
    # Кнопки для продолжения
    keyboard = [
        [
            InlineKeyboardButton("Ещё пример", callback_data="show_prompt"),
            InlineKeyboardButton("Главное меню", callback_data="main_menu")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Что дальше?", reply_markup=reply_markup)

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показ главного меню"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("OVERLORD AI INK (Free Train)", callback_data="free_train")],
        [InlineKeyboardButton("Полная Версия OVERLORD AI INK PRO", callback_data="pro_version")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Главное меню:", reply_markup=reply_markup)

async def free_train(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Повторная отправка стартового сообщения"""
    query = update.callback_query
    await query.answer()
    
    # Повторяем логику команды /start
    await query.message.reply_text(f"🎬 Обучающее видео: {YOUTUBE_URL}")
    
    description = (
        "🖌️ OVERLORD AI INK (Free Train)\n\n"
        "Бесплатная версия с базовыми функциями генерации изображений..."
    )
    await query.message.reply_text(description)
    
    gif_path = os.path.join("static", "14.gif")
    with open(gif_path, "rb") as gif_file:
        await query.message.reply_animation(
            animation=InputFile(gif_file),
            caption=f"🚀 Начать генерацию: {COLAB_URL}"
        )
    
    keyboard = [[InlineKeyboardButton("Пример промта", callback_data="show_prompt")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Попробуйте готовые промты:", reply_markup=reply_markup)

async def pro_version(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Информация о PRO версии"""
    query = update.callback_query
    await query.answer()
    
    # Описание преимуществ PRO
    pro_features = (
        "🔥 OVERLORD AI INK PRO - Премиум версия\n\n"
        "Отличия от бесплатной версии:\n"
        "✅ 20+ эксклюзивных моделей стилей\n"
        "✅ Поддержка LoRA-адаптеров\n"
        "✅ Создание собственных стилей\n"
        "✅ Приоритетные обновления\n"
        "✅ Экспорт в 4K разрешении\n\n"
        "Полный контроль над генерацией!"
    )
    await query.message.reply_text(pro_features)
    
    # Подписки через Tribut
    subscriptions = (
        "💎 Выберите подписку:\n\n"
        "1 месяц - 2990₽\n"
        "Навсегда - 11990₽\n\n"
        f"Оформить: {TRIBUT_URL}"
    )
    await query.message.reply_text(subscriptions)

def main() -> None:
    """Запуск бота"""
    application = Application.builder().token(TOKEN).build()
    
    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    
    # Обработчики callback-запросов
    application.add_handler(CallbackQueryHandler(show_prompt, pattern="^show_prompt$"))
    application.add_handler(CallbackQueryHandler(main_menu, pattern="^main_menu$"))
    application.add_handler(CallbackQueryHandler(free_train, pattern="^free_train$"))
    application.add_handler(CallbackQueryHandler(pro_version, pattern="^pro_version$"))
    
    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()
