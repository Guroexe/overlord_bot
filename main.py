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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка команды /start"""
    user = update.effective_user
    context.user_data["prompt_index"] = 0
    
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
    except:
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
    
    current_index = context.user_data.get("prompt_index", 0)
    prompt_data = PROMPTS[current_index % len(PROMPTS)]
    
    try:
        with open(os.path.join("static", prompt_data["image"]), "rb") as photo_file:
            await query.message.reply_photo(
                photo=InputFile(photo_file),
                caption=prompt_data["prompt"],
                parse_mode='HTML'
            )
    except:
        await query.message.reply_text(prompt_data["prompt"], parse_mode='HTML')
    
    context.user_data["prompt_index"] = (current_index + 1) % len(PROMPTS)
    
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
    except:
        await query.message.reply_text(f"<b>🚀 Начать генерацию:</b>\n{COLAB_URL}", parse_mode='HTML')
    
    keyboard = [
        [InlineKeyboardButton("Пример промта", callback_data="show_prompt")],
        [InlineKeyboardButton("OVERLORD AI INK PRO", callback_data="pro_version")],
        [InlineKeyboardButton("Обучение Тату IKONA", callback_data="tattoo_training")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Выберите действие:", reply_markup=reply_markup)

async def pro_version(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Информация о PRO версии"""
    query = update.callback_query
    await query.answer()
    
    await query.message.reply_text(f"<b>🎬 PRO Обучение:</b>\n{PRO_VERSION_VIDEO}", parse_mode='HTML')
    
    pro_features = (
        "<b>🔥 OVERLORD AI INK PRO - Полная Версия с 30+ уникальными стилями!</b>\n\n"
        "<b>Отличия от бесплатной версии:</b>\n"
        "• 30+ уникальных моделей стилей\n"
        "• Быстрые генерации (в 4 раза быстрее)\n"
        "• Создание собственных стилей\n\n"
        f"Создатель: {CREATOR_CHANNEL}"
    )
    await query.message.reply_text(pro_features, parse_mode='HTML')

    try:
        with open(os.path.join("static", "9d.gif"), "rb") as pro_gif_file:
            keyboard_pro = [[InlineKeyboardButton("🔥 Оформить PRO", url=TRIBUT_URL)]]
            await query.message.reply_animation(
                animation=InputFile(pro_gif_file),
                caption="<b>🔥 PRO версия открывает новые возможности генерации!</b>",
                parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup(keyboard_pro)
            )
    except:
        keyboard_pro = [[InlineKeyboardButton("🔥 Оформить PRO", url=TRIBUT_URL)]]
        await query.message.reply_text(
            "<b>🔥 PRO версия открывает новые возможности генерации!</b>",
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(keyboard_pro)
        )

    keyboard = [[InlineKeyboardButton("Главное меню", callback_data="main_menu")]]
    await query.message.reply_text("Выберите действие:", reply_markup=InlineKeyboardMarkup(keyboard))

async def tattoo_training(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обучение Тату IKONA"""
    query = update.callback_query
    await query.answer()
    
    await query.message.reply_text(f"<b>🎬 Обучение Тату IKONA:</b>\n{TATTOO_TRAINING_VIDEO}", parse_mode='HTML')
    
    description = (
        "<b>Обучение Икона</b>\n\n"
        "Создана для тех, кто хочет сразу начать колоть СТИЛЬ и быстро ворваться в индустрию.\n\n"
        "<b>Выбери программу, которая тебе больше подходит!</b>"
    )
    await query.message.reply_text(description, parse_mode='HTML')
    
    keyboard = [
        [InlineKeyboardButton("Оффлайн обучение IKONA в Москве и Питере", callback_data="offline_training")],
        [InlineKeyboardButton("Онлайн обучение IKONA", callback_data="online_training")],
        [InlineKeyboardButton("Главное меню", callback_data="main_menu")]
    ]
    await query.message.reply_text("Выберите формат обучения:", reply_markup=InlineKeyboardMarkup(keyboard))

async def offline_training(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Оффлайн обучение IKONA"""
    query = update.callback_query
    await query.answer()
    
    await query.message.reply_text(f"<b>🎬 Оффлайн обучение:</b>\n{OFFLINE_TRAINING_VIDEO}", parse_mode='HTML')
    
    description = (
        "<b>Оффлайн обучение IKONA в Москве и Питере</b>\n\n"
        "<b>Программа включает:</b>\n"
        "• Занятия на искусственной коже и на людях\n"
        "• Создание собственного стиля при помощи ИИ\n\n"
        "<b>Детали:</b>\n"
        "• Срок обучения: 2 месяца\n"
        "• Стоимость: 99 000₽\n\n"
        "<b>Приходи на Бесплатный Первый Урок!</b>"
    )
    await query.message.reply_text(description, parse_mode='HTML')
    
    keyboard = [
        [InlineKeyboardButton("Записаться на Пробный Урок / Обучение", callback_data="sign_up")],
        [InlineKeyboardButton("Главное меню", callback_data="main_menu")]
    ]
    await query.message.reply_text("Выберите действие:", reply_markup=InlineKeyboardMarkup(keyboard))

async def online_training(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Онлайн обучение IKONA"""
    query = update.callback_query
    await query.answer()
    
    await query.message.reply_text(f"<b>🎬 Онлайн обучение:</b>\n{ONLINE_TRAINING_VIDEO}", parse_mode='HTML')
    
    description = (
        "<b>Онлайн Обучение IKONA</b>\n\n"
        "<b>Программа состоит из:</b>\n"
        "1. Обучение работе с ИИ\n"
        "2. Онлайн уроки по нанесению тату\n\n"
        "<b>Дополнительно:</b>\n"
        "• Профессиональная тату машинка\n"
        "• Помощь с поиском салона и модели\n\n"
        "<b>Детали:</b>\n"
        "• Срок обучения: 2 месяца\n"
        "• Стоимость: 79 000₽"
    )
    await query.message.reply_text(description, parse_mode='HTML')
    
    keyboard = [
        [InlineKeyboardButton("Подробнее / Записаться", callback_data="sign_up")],
        [InlineKeyboardButton("Главное меню", callback_data="main_menu")]
    ]
    await query.message.reply_text("Выберите действие:", reply_markup=InlineKeyboardMarkup(keyboard))

async def sign_up(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Запись на обучение"""
    query = update.callback_query
    await query.answer()
    
    message = (
        "<b>Запись на обучение</b>\n\n"
        "Для записи на пробный урок или обучения:\n\n"
        "Напишите сюда: @vladguro\n\n"
        "Мы свяжемся с вами в ближайшее время!"
    )
    await query.message.reply_text(message, parse_mode='HTML')
    
    keyboard = [[InlineKeyboardButton("Главное меню", callback_data="main_menu")]]
    await query.message.reply_text("Выберите действие:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка текстовых сообщений"""
    await update.message.reply_text("Пожалуйста, используйте кнопки меню")

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
