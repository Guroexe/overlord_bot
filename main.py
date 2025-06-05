import os
import json
from pathlib import Path
from typing import Dict

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputFile,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from flask import Flask, request
from telegram import Bot

# ------------------------------
# 1. Настройка переменных
# ------------------------------
# Токен берётся из переменной окружения TELEGRAM_TOKEN
TELEGRAM_TOKEN = os.environ.get("7972832759:AAEwXCLf7bXdYguvmx4cJvPCfnfWmslXVW8")
# Внешний URL вашего сервиса на Render (например, https://your-app.onrender.com)
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL")

if not TELEGRAM_TOKEN or not RENDER_EXTERNAL_URL:
    raise RuntimeError("Не задан TELEGRAM_TOKEN или RENDER_EXTERNAL_URL")  # :contentReference[oaicite:7]{index=7}

# Инициализируем Flask для приёма webhook-запросов
app = Flask(__name__)

# Путь к папке со статикой (картинками и гифками)
BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"

# Загрузка промтов из prompts.json
with open(BASE_DIR / "prompts.json", encoding="utf-8") as f:
    PROMPTS: Dict[str, str] = json.load(f)

# Словарь для хранения текущего индекса картинки для каждого пользователя
user_image_index: Dict[int, int] = {}  # ключ: user_id, значение: индекс в списке картинок (0-based) :contentReference[oaicite:8]{index=8}

# Список имён файлов с примерами картинок (фильтруем только PNG)
IMAGE_FILES = [fname for fname in sorted(os.listdir(STATIC_DIR)) if fname.endswith(".png")]

# ------------------------------
# 2. Хендлер /start
# ------------------------------
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    При старте бот отправляет:
    1) Ссылку на видео YouTube
    2) Текстовое описание OVERLORD AI INK (Free Train)
    3) GIF с ссылкой на Google Colab
    4) Inline-кнопку 'пример промта'
    """
    chat_id = update.effective_chat.id

    # 2.1. Отправляем YouTube ссылку
    youtube_link = "https://www.youtube.com/watch?v=J4qY9DYE184"
    await context.bot.send_message(chat_id=chat_id,
                                   text=f"🔗 Смотрите видео:\n{youtube_link}")  # :contentReference[oaicite:9]{index=9}

    # 2.2. Отправляем текстовое описание Free Train
    free_train_text = (
        "OVERLORD AI INK (Free Train)\n\n"
        "Это бесплатная версия бота для обучения ваших моделей в Stable Diffusion. "
        "Здесь вы можете генерировать изображения на основе заранее заданных LoRA, "
        "а также изменять параметры вашей модели. Для работы с ботом достаточно "
        "открыть меню 'пример промта' и следовать инструкциям ниже.\n"
    )
    await context.bot.send_message(chat_id=chat_id, text=free_train_text)  # :contentReference[oaicite:10]{index=10}

    # 2.3. Отправляем GIF (14.gif) вместе со ссылкой на Google Colab
    # Пример ссылки на Colab (замените на реальную ссылку, если есть)
    colab_link = "https://colab.research.google.com/your_colab_link"
    gif_path = STATIC_DIR / "14.gif"
    if gif_path.exists():
        await context.bot.send_animation(chat_id=chat_id,
                                         animation=InputFile(gif_path),
                                         caption=f"💻 Запустите Colab: {colab_link}")  # :contentReference[oaicite:11]{index=11}
    else:
        await context.bot.send_message(chat_id=chat_id,
                                       text="⚠️ GIF не найден.")  # :contentReference[oaicite:12]{index=12}

    # 2.4. Отправляем кнопку 'пример промта' и 'главное меню'
    keyboard = [
        [InlineKeyboardButton("📷 Пример промта", callback_data="show_prompt")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=chat_id,
                                   text="Выберите действие:",
                                   reply_markup=reply_markup)  # :contentReference[oaicite:13]{index=13}

    # Инициализируем индекс картинок для пользователя
    user_image_index[chat_id] = 0  # :contentReference[oaicite:14]{index=14}

# ------------------------------
# 3. Обработчик callback-запросов
# ------------------------------
async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработка нажатий на Inline-кнопки.
    Возможные callback_data:
    - 'show_prompt'         : показать очередной пример промта
    - 'main_menu'           : вернуться в главное меню (Free Train)
    - 'menu_free'           : показать Free Train (аналог /start)
    - 'menu_pro'            : показать PRO-версию и подписки
    - 'sub_month' / 'sub_forever' : подписки через Tribut
    """
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id
    data = query.data

    # 3.1. Нажатие 'show_prompt' — показать картинку+промт
    if data == "show_prompt":
        # Получаем текущий индекс для пользователя
        idx = user_image_index.get(chat_id, 0)
        filename = IMAGE_FILES[idx]
        prompt_text = PROMPTS.get(filename, "Описание отсутствует")
        image_path = STATIC_DIR / filename

        # Отправляем картинку и текст промта
        if image_path.exists():
            await context.bot.send_photo(chat_id=chat_id,
                                         photo=InputFile(image_path),
                                         caption=f"💡 Пример промта для {filename}:\n{prompt_text}")  # :contentReference[oaicite:15]{index=15}
        else:
            await context.bot.send_message(chat_id=chat_id,
                                           text=f"⚠️ Файл {filename} не найден.")  # :contentReference[oaicite:16]{index=16}

        # Обновляем индекс (переходим к следующему, если конец — возвращаемся к 0)
        next_idx = (idx + 1) % len(IMAGE_FILES)
        user_image_index[chat_id] = next_idx  # :contentReference[oaicite:17]{index=17}

        # Снова показываем кнопки: Пример промта и Главное меню
        keyboard = [
            [InlineKeyboardButton("📷 Пример промта", callback_data="show_prompt")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=chat_id,
                                       text="Что дальше?",
                                       reply_markup=reply_markup)  # :contentReference[oaicite:18]{index=18}

    # 3.2. Нажатие 'main_menu' — показать заново Free Train (аналог /start)
    elif data == "main_menu" or data == "menu_free":
        # Вызываем логику из start_command
        # Здесь проще напрямую вызвать команду start
        await start_command(update, context)  # :contentReference[oaicite:19]{index=19}

    # 3.3. Нажатие 'menu_pro' — показать PRO-версию и информацию о подписках
    elif data == "menu_pro":
        pro_text = (
            "💼 Полная Версия OVERLORD AI INK PRO\n\n"
            "В PRO-версии доступны:\n"
            "• Расширенный набор моделей Stable Diffusion\n"
            "• Возможность подключения сторонних LoRA и кастомных стилей\n"
            "• Регулярные обновления и новые функции\n\n"
            "Вы можете оформить подписку через Tribut:"
        )
        await context.bot.send_message(chat_id=chat_id, text=pro_text)  # :contentReference[oaicite:20]{index=20}

        # Кнопки подписки через Tribut
        tribut_link = "https://t.me/TributeBot?start=overlord_ai_ink"  # пример ссылки
        keyboard = [
            [InlineKeyboardButton("1 месяц – 2990₽", url=tribut_link + "_month")],
            [InlineKeyboardButton("Навсегда – 11990₽", url=tribut_link + "_forever")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=chat_id,
                                       text="Выберите подписку:",
                                       reply_markup=reply_markup)  # :contentReference[oaicite:21]{index=21}

    # 3.4. Обработка возможных callback’ов для подписок (к примеру, можем отправить подтверждение)
    elif data in ("sub_month", "sub_forever"):
        if data == "sub_month":
            await context.bot.send_message(chat_id=chat_id,
                                           text="Вы выбрали подписку 1 месяц – 2990₽.\nПерейдите по ссылке выше для оплаты.")  # :contentReference[oaicite:22]{index=22}
        else:
            await context.bot.send_message(chat_id=chat_id,
                                           text="Вы выбрали подписку навсегда – 11990₽.\nПерейдите по ссылке выше для оплаты.")  # :contentReference[oaicite:23]{index=23}

    else:
        # На всякий случай
        await context.bot.send_message(chat_id=chat_id,
                                       text="❓ Неизвестное действие. Пожалуйста, выберите опцию.")  # :contentReference[oaicite:24]{index=24}

# ------------------------------
# 4. Функция для установки webhook (вызывается при старте)
# ------------------------------
async def set_webhook(app_context):
    """
    При запуске приложения устанавливаем webhook Telegram на адрес RENDER_EXTERNAL_URL/webhook
    """
    bot = Bot(token=TELEGRAM_TOKEN)
    webhook_url = f"{RENDER_EXTERNAL_URL}/webhook"
    # Устанавливаем webhook
    await bot.set_webhook(webhook_url)  # :contentReference[oaicite:25]{index=25}

# ------------------------------
# 5. Flask-приложение для обработки webhook-запросов
# ------------------------------
@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    """
    Приходящий запрос из Telegram (update) присылается сюда в формате JSON.
    Мы преобразуем его в Update и передаём в dispatcher.
    """
    from telegram import Update
    from telegram.ext import Dispatcher

    # Создаём ApplicationBuilder для обработки update внутри Flask (синхронно)
    application = app.config["bot_app"]

    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), application.bot)
        application.update_queue.put(update)
        return "OK", 200
    else:
        return "Hello, this is OVERLORD AI INK bot!", 200

# ------------------------------
# 6. Точка входа при запуске на Render
# ------------------------------
if __name__ == "__main__":
    # Создаём приложение (Application) для python-telegram-bot с запуском webhook
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Сохраняем Application в конфиг Flask, чтобы можно было достучаться в webhook()
    app.config["bot_app"] = application

    # Регистрируем хендлеры
    application.add_handler(CommandHandler("start", start_command))  # :contentReference[oaicite:26]{index=26}
    application.add_handler(CallbackQueryHandler(callback_query_handler))  # :contentReference[oaicite:27]{index=27}

    # Устанавливаем webhook при старте
    # Обратите внимание: для установки webhook требуется asyncio-цикл,
    # поэтому мы используем run_once в корутине.
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", "8443")),
        webhook_url=f"{RENDER_EXTERNAL_URL}/webhook",
    )  # :contentReference[oaicite:28]{index=28}
