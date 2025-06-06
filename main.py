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
FREE_TRAIN_VIDEO = "https://www.youtube.com/watch?v=10b_j5gBAg8"
PRO_VERSION_VIDEO = "https://www.youtube.com/watch?v=QKLOb6f5L-k"
COLAB_URL = "https://colab.research.google.com/drive/1lWfrS0Jh0B2B99IJ26aincVXylaoLuDq?usp=sharing"
TRIBUT_URL = "https://t.me/tribute/app?startapp=ep_8y0gVeOLXYRcOrfRtGTMLW8vu0C82z72WfxBEEtJz3ofJTky32"

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
    await update.message.reply_text(f"ОБУЧАЮЩЕЕ ВИДЕО: {FREE_TRAIN_VIDEO}")

    # Описание без кнопок
    description = (
        "OVERLORD AI INK (FREE TRAIN)\n\n"
        "ЭТО БЕСПЛАТНАЯ ВЕРСИЯ НЕЙРОСЕТИ ДЛЯ ГЕНЕРАЦИИ ИЗОБРАЖЕНИЙ В СТИЛЕ SIGILISM, TRIBAL, DARK TATTOO. "
        "ИСПОЛЬЗУЙТЕ OVERLORD INK AI ДЛЯ СОЗДАНИЯ УНИКАЛЬНЫХ АРТОВ БЕЗ ОГРАНИЧЕНИЙ!\n\n"
        "КАК ИСПОЛЬЗОВАТЬ:\n"
        "1. ВВЕДИТЕ ТЕКСТОВЫЙ ПРОМТ НА АНГЛИЙСКОМ ИЛИ ИСПОЛЬЗУЙТЕ ПРОМТ ИЗ ПРИМЕРОВ ПОДСКАЗОК\n"
        "2. НАСТРОЙТЕ ПАРАМЕТРЫ: SAMPLING METHOD - DPM++ 2M SDE, STEPS - 20, WIDTH - 720, HEIGHT - 980, CFG SCALE - 4\n"
        "3. ГЕНЕРИРУЙТЕ ИЗОБРАЖЕНИЯ БЕСПЛАТНО!"
    )
    await update.message.reply_text(description)

    # Отправка гифки с подписью и кнопками (одно сообщение)
    gif_path = os.path.join("static", "14.gif")
    keyboard = [
        [
            InlineKeyboardButton("ПРИМЕР ПРОМТА", callback_data="show_prompt"),
            InlineKeyboardButton("OVERLORD AI INK PRO", callback_data="pro_version")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    with open(gif_path, "rb") as gif_file:
        await update.message.reply_animation(
            animation=InputFile(gif_file),
            caption=f"НАЧАТЬ ГЕНЕРАЦИЮ ИСПОЛЬЗУЙ COLAB: {COLAB_URL}",
            reply_markup=reply_markup
        )

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
            InlineKeyboardButton("ЕЩЁ ПРИМЕР", callback_data="show_prompt"),
            InlineKeyboardButton("ГЛАВНОЕ МЕНЮ", callback_data="main_menu")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("ЧТО ДАЛЬШЕ?", reply_markup=reply_markup)

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показ главного меню"""
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("OVERLORD AI INK (FREE TRAIN)", callback_data="free_train")],
        [InlineKeyboardButton("ПОЛНАЯ ВЕРСИЯ OVERLORD AI INK PRO", callback_data="pro_version")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("ГЛАВНОЕ МЕНЮ:", reply_markup=reply_markup)

async def free_train(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Повторная отправка стартового сообщения"""
    query = update.callback_query
    await query.answer()

    await query.message.reply_text(f"ОБУЧАЮЩЕЕ ВИДЕО: {FREE_TRAIN_VIDEO}")

    description = (
        "OVERLORD AI INK (FREE TRAIN)\n\n"
        "БЕСПЛАТНАЯ ВЕРСИЯ С 3 СТИЛЯМИ ГЕНЕРАЦИЙ ИЗОБРАЖЕНИЙ..."
    )
    await query.message.reply_text(description)

    gif_path = os.path.join("static", "14.gif")
    with open(gif_path, "rb") as gif_file:
        await query.message.reply_animation(
            animation=InputFile(gif_file),
            caption=f"НАЧАТЬ ГЕНЕРАЦИЮ! COLAB: {COLAB_URL}"
        )

    keyboard = [
        [
            InlineKeyboardButton("ПРИМЕР ПРОМТА", callback_data="show_prompt"),
            InlineKeyboardButton("OVERLORD AI INK PRO", callback_data="pro_version")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("ВЫБЕРИТЕ ДЕЙСТВИЕ:", reply_markup=reply_markup)

async def pro_version(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Информация о PRO версии"""
    query = update.callback_query
    await query.answer()

    # Отправка PRO видео
    await query.message.reply_text(f"PRO ОБУЧЕНИЕ: {PRO_VERSION_VIDEO}")

    # Описание преимуществ PRO
    pro_features = (
        "OVERLORD AI INK PRO - ПОЛНАЯ ВЕРСИЯ С 30+ УНИКАЛЬНЫМИ СТИЛЯМИ!\n\n"
        "ОТЛИЧИЯ ОТ БЕСПЛАТНОЙ ВЕРСИИ:\n"
        "30+ УНИКАЛЬНЫХ МОДЕЛЕЙ СТИЛЕЙ\n"
        "БЫСТРЫЕ ГЕНЕРАЦИИ. В 4 РАЗА БЫСТРЕЕ\n"
        "СОЗДАНИЕ СОБСТВЕННЫХ СТИЛЕЙ\n"
        "ПРИОРИТЕТНЫЕ ОБНОВЛЕНИЯ\n"
        "МНОЖЕСТВО РАБОЧИХ ПРОМТОВ\n\n"
        "ПОЛНЫЙ КОНТРОЛЬ НАД ГЕНЕРАЦИЕЙ!"
    )
    await query.message.reply_text(pro_features)

    # Отправка PRO GIF с инлайн-кнопкой
    pro_gif_path = os.path.join("static", "9d.gif")
    with open(pro_gif_path, "rb") as pro_gif_file:
        keyboard_pro = [
            [InlineKeyboardButton("ОФОРМИТЬ PRO", url=TRIBUT_URL)]
        ]
        reply_markup_pro = InlineKeyboardMarkup(keyboard_pro)

        await query.message.reply_animation(
            animation=InputFile(pro_gif_file),
            caption="PRO ВЕРСИЯ ОТКРЫВАЕТ НОВЫЕ ВОЗМОЖНОСТИ ГЕНЕРАЦИИ!",
            reply_markup=reply_markup_pro
        )

    # Кнопки для возврата
    keyboard = [
        [InlineKeyboardButton("ГЛАВНОЕ МЕНЮ", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("ВЫБЕРИТЕ ДЕЙСТВИЕ:", reply_markup=reply_markup)

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
