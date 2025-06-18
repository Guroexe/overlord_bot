# -*- coding: utf-8 -*-
import logging
import json
import os
import asyncio
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputFile,
    InputMediaAnimation
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)
from telegram.error import RetryAfter, TimedOut, BadRequest
from dotenv import load_dotenv

# --- Инициализация ---
load_dotenv()

# Настройка логгирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Проверка токена
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    logger.error("Токен бота не найден!")
    raise ValueError("Требуется токен бота")

# --- Кэширование ресурсов ---
class MediaCache:
    def __init__(self):
        self.start_gif = None
        self.pro_gif = None
    
    async def load(self):
        try:
            with open(os.path.join("static", "14.gif"), "rb") as f:
                self.start_gif = InputMediaAnimation(f.read())
            with open(os.path.join("static", "9d.gif"), "rb") as f:
                self.pro_gif = InputMediaAnimation(f.read())
            logger.info("Медиафайлы загружены в кэш")
        except Exception as e:
            logger.error(f"Ошибка загрузки медиа: {e}")

media_cache = MediaCache()

# --- Конфигурация контента ---
RU_VIDEOS = {
    "free_train": "https://youtu.be/mxxbhZ8SxTU",
    "pro_version": "https://youtube.com/shorts/7hP9p5GnXWM?si=9Zq_pArWAZaisSKR",
    "ikona_training": "https://www.youtube.com/watch?v=GX_ZbWx0oYY",
    "offline_training": "https://www.youtube.com/watch?v=Kopx3whZquc",
    "online_training": "https://www.youtube.com/watch?v=10b_j5gBAg8"
}

EN_VIDEOS = {
    "free_train": "https://youtu.be/RcLS9A24Kss",
    "pro_version": "https://youtube.com/shorts/_I2o5jc76Ug?si=DxRgG60LuHmbiN2w",
    "ikona_training": "https://www.youtube.com/watch?v=GX_ZbWx0oYY",
    "offline_training": "https://www.youtube.com/watch?v=Kopx3whZquc",
    "online_training": "https://www.youtube.com/watch?v=10b_j5gBAg8"
}

COLAB_URL = "https://colab.research.google.com/drive/1lWfrS0Jh0B2B99IJ26aincVXylaoLuDq?usp=sharing"
TRIBUT_URL = "https://t.me/tribute/app?startapp=ep_8y0gVeOLXYRcOrfRtGTMLW8vu0C82z72WfxBEEtJz3ofJTky32"

# Тексты для русской версии
RU_TEXTS = {
    "start": (
        "🖌️ **OVERLORD AI INK (Free Train)**\n\n"
        "**Бесплатная версия нейросети** для генерации изображений в стиле:\n"
        "• Sigilism\n"
        "• Tribal\n"
        "• Dark Tattoo\n\n"
        "Создавайте уникальные арты **без ограничений**!\n\n"
        "**КАК ИСПОЛЬЗОВАТЬ:**\n\n"
        "**1.** Введите текстовый промт на английском языке или используйте готовые примеры\n\n"
        "**2.** Настройте параметры генерации:\n"
        "   • Sampling method: **DPM++ 2M SDE**\n"
        "   • Steps: **20**\n"
        "   • Width: **720**\n"
        "   • Height: **980**\n"
        "   • CFG Scale: **4**\n\n"
        "**3.** Генерируйте изображения **бесплатно**!\n\n"
        "*(создатель - https://t.me/gurovlad)*"
    ),
    "pro_features": (
        "🔥 **OVERLORD AI INK PRO**\n"
        "**Полная версия с 30+ уникальными стилями!**\n\n"
        "**ОТЛИЧИЯ ОТ БЕСПЛАТНОЙ ВЕРСИИ:**\n\n"
        "✅ **30+ уникальных моделей** стилей\n"
        "✅ **Быстрые генерации** — в 4 раза быстрее\n"
        "✅ **Создание собственных стилей**\n"
        "✅ **Приоритетные обновления**\n"
        "✅ **Множество рабочих промтов**\n\n"
        "**ПОЛНЫЙ КОНТРОЛЬ НАД ГЕНЕРАЦИЕЙ!**\n\n"
        "*(создатель - https://t.me/gurovlad)*"
    ),
    "ikona_training": (
        "**ОБУЧЕНИЕ ТАТУ IKONA**\n\n"
        "Обучение создано для тех, кто хочет **сразу начать колоть СТИЛЬ** и быстро ворваться в индустрию и занять свое место!\n\n"
        "**ЧТО МЫ ПРЕДОСТАВЛЯЕМ:**\n\n"
        "🎯 Программу обучения с созданием **собственного стиля эскизов**\n"
        "🎯 Отточим до идеала **нанесение на кожу**\n"
        "🎯 Поможем **привлекать клиентов** уже во время обучения\n"
        "🎯 Развитие **социальных сетей**\n\n"
        "**ВЫБЕРИТЕ ПРОГРАММУ, КОТОРАЯ ВАМ БОЛЬШЕ ПОДХОДИТ:**"
    ),
    "offline_training": (
        "**ОФФЛАЙН ОБУЧЕНИЕ IKONA**\n"
        "**Москва и Санкт-Петербург**\n\n"
        "**ПРОГРАММА ОБУЧЕНИЯ:**\n\n"
        "👨‍🏫 Занятия с **действующим тату-мастером IKONA**\n"
        "🎯 Практика на **искусственной коже и живых людях**\n"
        "🤖 Создание **собственного стиля при помощи ИИ**\n"
        "💪 Идеальная техника **нанесения на коже**\n\n"
        "**УСЛОВИЯ:**\n\n"
        "⏱️ **Срок обучения:** 2 месяца\n"
        "💰 **Стоимость:** 99 000 рублей\n\n"
        "**БЕСПЛАТНЫЙ ПЕРВЫЙ УРОК!**\n\n"
        "Приходите на пробное занятие, где мы:\n"
        "• Подробно расскажем о программе\n"
        "• Дадим набить первую татуировку на искусственной коже\n"
        "• Вы попробуете себя в роли **Тату-Мастера**!"
    ),
    "online_training": (
        "**ОНЛАЙН ОБУЧЕНИЕ IKONA**\n\n"
        "**ПРОГРАММА СОСТОИТ ИЗ:**\n\n"
        "🤖 **Блок «Обучение ИИ»** — создание собственного стиля\n"
        "👨‍💻 **Онлайн уроки с преподавателем** — техника нанесения\n\n"
        "**КАК ПРОХОДИТ ОБУЧЕНИЕ:**\n\n"
        "📱 **Видеозвонки с преподавателем** — достаточно для правильной постановки руки и передачи важных знаний\n\n"
        "📦 **Профессиональная тату-машинка** — высылаем со всеми необходимыми компонентами для домашнего обучения\n\n"
        "🏢 **Поддержка в выборе салона** — поможем найти салон в вашем городе\n\n"
        "👥 **Поиск модели** — организуем полноценный сеанс под контролем преподавателя для вашей уверенности\n\n"
        "**УСЛОВИЯ:**\n\n"
        "⏱️ **Срок обучения:** 2 месяцев\n"
        "💰 **Стоимость:** 79 000 рублей"
    ),
    "contact_for_trial": (
        "**ЗАПИСЬ НА ПРОБНЫЙ УРОК / ОБУЧЕНИЕ**\n\n"
        "Для записи на пробный урок, обучение или получения подробной информации напишите с указанием вашего пожелания:\n\n"
        "👤 **@vladguro**\n\n"
        "**Ответим в ближайшее время!**"
    ),
    "contact_for_details": (
        "**ПОДРОБНЕЕ / ЗАПИСАТЬСЯ**\n\n"
        "Для записи на обучение или получения подробной информации напишите с указанием вашего пожелания:\n\n"
        "👤 **@vladguro**\n\n"
        "**Ответим в ближайшее время!**"
    ),
    "prompt_not_found": "⚠️ Примеры промтов временно недоступны",
    "file_not_found": "⚠️ Файл не найден",
    "error": "⚠️ Если не появились кнопки, нажмите /start",
    "choose_action": "Выберите действие:",
    "what_next": "Что дальше?",
    "main_menu": "**ГЛАВНОЕ МЕНЮ:**",
    "pro_caption": "🔥 PRO версия открывает новые возможности генерации!",
    "get_pro": "🔥 Оформить PRO",
    "back_to_main": "Главное меню",
    "more_examples": "Ещё пример",
    "prompt_example": "Пример промта",
    "full_version": "ПОЛНАЯ ВЕРСИЯ OVERLORD INK AI PRO +",
    "ikona_training_btn": "Обучение Тату IKONA",
    "free_train_btn": "OVERLORD AI INK (Free Train)",
    "offline_training_btn": "Оффлайн обучение IKONA в Москве и Питере",
    "online_training_btn": "Онлайн обучение IKONA",
    "trial_lesson": "Записаться на Пробный Урок / Обучение",
    "more_details": "Подробнее / Записаться",
    "use_buttons": "Пожалуйста, используйте кнопки меню",
    "training_video": "Видео обучения:",
    "start_generating": "Начните генерацию!"
}

# Тексты для английской версии
EN_TEXTS = {
    "start": (
        "🖌️ **OVERLORD AI INK (Free Trial)**\n\n"
        "**Free version of neural network** for generating images in styles:\n"
        "• Sigilism\n"
        "• Tribal\n"
        "• Dark Tattoo\n\n"
        "Create unique artworks **without limitations**!\n\n"
        "**HOW TO USE:**\n\n"
        "**1.** Enter text prompt in English or use ready examples\n\n"
        "**2.** Configure generation parameters:\n"
        "   • Sampling method: **DPM++ 2M SDE**\n"
        "   • Steps: **20**\n"
        "   • Width: **720**\n"
        "   • Height: **980**\n"
        "   • CFG Scale: **4**\n\n"
        "**3.** Generate images **for free**!\n\n"
        "*(creator - https://t.me/gurovlad)*"
    ),
    "pro_features": (
        "🔥 **OVERLORD AI INK PRO**\n"
        "**Full version with 30+ unique styles!**\n\n"
        "**DIFFERENCES FROM FREE VERSION:**\n\n"
        "✅ **30+ unique style** models\n"
        "✅ **Faster generation** — 4 times faster\n"
        "✅ **Create your own styles**\n"
        "✅ **Priority updates**\n"
        "✅ **Many working prompts**\n\n"
        "**FULL CONTROL OVER GENERATION!**\n\n"
        "*(creator - https://t.me/gurovlad)*"
    ),
    "ikona_training": (
        "**IKONA TATTOO TRAINING**\n\n"
        "The training is created for those who want to **start tattooing STYLE right away** and quickly break into the industry and take their place!\n\n"
        "**WHAT WE PROVIDE:**\n\n"
        "🎯 Training program with creation of **your own sketch style**\n"
        "🎯 Perfecting **skin application** technique\n"
        "🎯 Help **attracting clients** already during training\n"
        "🎯 Development of **social networks**\n\n"
        "**CHOOSE THE PROGRAM THAT SUITS YOU BEST:**"
    ),
    "offline_training": (
        "**OFFLINE IKONA TRAINING**\n"
        "**Moscow and St. Petersburg**\n\n"
        "**TRAINING PROGRAM:**\n\n"
        "👨‍🏫 Classes with **current IKONA tattoo master**\n"
        "🎯 Practice on **artificial skin and live people**\n"
        "🤖 Creating **your own style using AI**\n"
        "💪 Perfect **skin application** technique\n\n"
        "**CONDITIONS:**\n\n"
        "⏱️ **Training duration:** 2 months\n"
        "💰 **Price:** 99,000 rubles\n\n"
        "**FREE FIRST LESSON!**\n\n"
        "Come to a trial lesson where we will:\n"
        "• Tell you in detail about the program\n"
        "• Let you make your first tattoo on artificial skin\n"
        "• You will try yourself as a **Tattoo Master**!"
    ),
    "online_training": (
        "**ONLINE IKONA TRAINING**\n\n"
        "**THE PROGRAM CONSISTS OF:**\n\n"
        "🤖 **AI Training block** — creating your own style\n"
        "👨‍💻 **Online lessons with teacher** — application technique\n\n"
        "**HOW THE TRAINING GOES:**\n\n"
        "📱 **Video calls with teacher** — enough for correct hand positioning and transfer of important knowledge\n\n"
        "📦 **Professional tattoo machine** — we send with all necessary components for home training\n\n"
        "🏢 **Support in choosing a salon** — we will help you find a salon in your city\n\n"
        "👥 **Model search** — we will organize a full session under the supervision of a teacher for your confidence\n\n"
        "**CONDITIONS:**\n\n"
        "⏱️ **Training duration:** 2 months\n"
        "💰 **Price:** 79,000 rubles"
    ),
    "contact_for_trial": (
        "**SIGN UP FOR A TRIAL LESSON / TRAINING**\n\n"
        "To sign up for a trial lesson, training or to get more information, write indicating your request:\n\n"
        "👤 **@vladguro**\n\n"
        "**We will reply as soon as possible!**"
    ),
    "contact_for_details": (
        "**MORE DETAILS / SIGN UP**\n\n"
        "To sign up for training or to get more information, write indicating your request:\n\n"
        "👤 **@vladguro**\n\n"
        "**We will reply as soon as possible!**"
    ),
    "prompt_not_found": "⚠️ Prompt examples temporarily unavailable",
    "file_not_found": "⚠️ File not found",
    "error": "⚠️ If the buttons do not appear, press /start",
    "choose_action": "Choose action:",
    "what_next": "What's next?",
    "main_menu": "**MAIN MENU:**",
    "pro_caption": "🔥 PRO version opens new generation possibilities!",
    "get_pro": "🔥 Get PRO",
    "back_to_main": "Main menu",
    "more_examples": "More examples",
    "prompt_example": "Prompt example",
    "full_version": "FULL VERSION OVERLORD INK AI PRO +",
    "ikona_training_btn": "IKONA Tattoo Training",
    "free_train_btn": "OVERLORD AI INK (Free Trial)",
    "offline_training_btn": "Offline IKONA training in Moscow and St. Petersburg",
    "online_training_btn": "Online IKONA training",
    "trial_lesson": "Sign up for Trial Lesson / Training",
    "more_details": "More details / Sign up",
    "use_buttons": "Please use menu buttons",
    "training_video": "Training video:",
    "start_generating": "Start generating!"
}

# Загрузка промтов
try:
    with open("prompts.json", "r", encoding="utf-8") as f:
        PROMPTS = json.load(f)
    logger.info(f"Успешно загружено {len(PROMPTS)} промтов")
except Exception as e:
    logger.error(f"Ошибка загрузки prompts.json: {str(e)}")
    PROMPTS = []

# --- Утилиты ---
async def safe_delete_message(chat_id: int, message_id: int, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.delete_message(chat_id, message_id)
    except Exception as e:
        logger.warning(f"Не удалось удалить сообщение: {e}")

async def send_with_retry(chat_id, content, context, retry_count=3):
    for attempt in range(retry_count):
        try:
            if isinstance(content, str):
                return await context.bot.send_message(chat_id, content)
            elif isinstance(content, dict):
                return await context.bot.send_animation(chat_id, **content)
        except RetryAfter as e:
            wait_time = e.retry_after + 1
            logger.warning(f"Rate limited. Waiting {wait_time} sec (attempt {attempt + 1})")
            await asyncio.sleep(wait_time)
        except Exception as e:
            logger.error(f"Ошибка отправки: {e}")
            await asyncio.sleep(2)
    return None

# --- Обработчики ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /start"""
    try:
        user = update.effective_user
        logger.info(f"Новый пользователь: {user.id} {user.username}")
        
        context.user_data.clear()
        context.user_data["prompt_index"] = 0
        
        keyboard = [
            [
                InlineKeyboardButton("🇷🇺 Русский", callback_data="set_lang_ru"),
                InlineKeyboardButton("🇺🇸 English", callback_data="set_lang_en")
            ]
        ]
        
        await update.message.reply_text(
            "Please select language / Пожалуйста, выберите язык:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    except Exception as e:
        logger.error(f"Ошибка в /start: {e}")
        await error_handler(update, context)

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE, lang: str):
    """Установка языка"""
    try:
        query = update.callback_query
        await query.answer()
        
        context.user_data["lang"] = lang
        texts = RU_TEXTS if lang == "ru" else EN_TEXTS
        videos = RU_VIDEOS if lang == "ru" else EN_VIDEOS
        
        # Комбинированное сообщение
        message = await query.message.reply_text(
            f"🎬 {texts.get('training_video', 'Видео обучения:')} {videos['free_train']}\n\n"
            f"{texts['start']}\n\n"
            f"🚀 {texts.get('start_generating', 'Начните генерацию:')} {COLAB_URL}",
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
        
        # Сохраняем ID для возможного удаления
        context.user_data["last_msg_id"] = message.message_id
        
        # Кнопки
        keyboard = [
            [
                InlineKeyboardButton(texts["prompt_example"], callback_data="show_prompt"),
                InlineKeyboardButton(texts["full_version"], callback_data="pro_version")
            ],
            [
                InlineKeyboardButton(texts["ikona_training_btn"], callback_data="ikona_training")
            ]
        ]
        
        await query.message.reply_text(
            texts["choose_action"],
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    except Exception as e:
        logger.error(f"Ошибка установки языка: {e}")
        await error_handler(update, context)

async def show_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показ примера промта"""
    try:
        query = update.callback_query
        await query.answer()
        
        lang = context.user_data.get("lang", "ru")
        texts = RU_TEXTS if lang == "ru" else EN_TEXTS
        
        if not PROMPTS:
            await query.message.reply_text(texts["prompt_not_found"])
            return
            
        current_index = context.user_data.get("prompt_index", 0)
        prompt_data = PROMPTS[current_index]
        
        # Отправка промта
        await query.message.reply_text(
            prompt_data["prompt"],
            parse_mode='Markdown'
        )
        
        # Обновление индекса
        context.user_data["prompt_index"] = (current_index + 1) % len(PROMPTS)
        
        # Кнопки
        keyboard = [
            [
                InlineKeyboardButton(texts["more_examples"], callback_data="show_prompt"),
                InlineKeyboardButton(texts["back_to_main"], callback_data="main_menu")
            ]
        ]
        
        await query.message.reply_text(
            texts["what_next"],
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    except Exception as e:
        logger.error(f"Ошибка показа промта: {e}")
        await error_handler(update, context)

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главное меню"""
    try:
        query = update.callback_query
        await query.answer()
        
        lang = context.user_data.get("lang", "ru")
        texts = RU_TEXTS if lang == "ru" else EN_TEXTS
        
        keyboard = [
            [InlineKeyboardButton(texts["free_train_btn"], callback_data="free_train")],
            [InlineKeyboardButton(texts["full_version"], callback_data="pro_version")],
            [InlineKeyboardButton(texts["ikona_training_btn"], callback_data="ikona_training")]
        ]
        
        await query.message.reply_text(
            texts["main_menu"],
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка главного меню: {e}")
        await error_handler(update, context)

async def free_train(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Бесплатная версия"""
    try:
        query = update.callback_query
        await query.answer()
        
        lang = context.user_data.get("lang", "ru")
        texts = RU_TEXTS if lang == "ru" else EN_TEXTS
        videos = RU_VIDEOS if lang == "ru" else EN_VIDEOS
        
        # Комбинированное сообщение
        await query.message.reply_text(
            f"🎬 {texts.get('training_video', 'Видео обучения:')} {videos['free_train']}\n\n"
            f"{texts['start']}\n\n"
            f"🚀 {texts.get('start_generating', 'Начните генерацию:')} {COLAB_URL}",
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
        
        # Кнопки
        keyboard = [
            [
                InlineKeyboardButton(texts["prompt_example"], callback_data="show_prompt"),
                InlineKeyboardButton(texts["full_version"], callback_data="pro_version")
            ],
            [
                InlineKeyboardButton(texts["ikona_training_btn"], callback_data="ikona_training")
            ]
        ]
        
        await query.message.reply_text(
            texts["choose_action"],
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    except Exception as e:
        logger.error(f"Ошибка free_train: {e}")
        await error_handler(update, context)

async def pro_version(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """PRO версия"""
    try:
        query = update.callback_query
        await query.answer()
        
        lang = context.user_data.get("lang", "ru")
        texts = RU_TEXTS if lang == "ru" else EN_TEXTS
        videos = RU_VIDEOS if lang == "ru" else EN_VIDEOS
        
        # Комбинированное сообщение
        await query.message.reply_text(
            f"🎬 PRO обучение: {videos['pro_version']}\n\n"
            f"{texts['pro_features']}",
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
        
        # Кнопка для PRO
        keyboard = [
            [InlineKeyboardButton(texts["get_pro"], url=TRIBUT_URL)],
            [InlineKeyboardButton(texts["back_to_main"], callback_data="main_menu")]
        ]
        
        if media_cache.pro_gif:
            await query.message.reply_animation(
                animation=media_cache.pro_gif,
                caption=texts["pro_caption"],
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await query.message.reply_text(
                texts["pro_caption"],
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        
    except Exception as e:
        logger.error(f"Ошибка pro_version: {e}")
        await error_handler(update, context)

async def ikona_training(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обучение IKONA"""
    try:
        query = update.callback_query
        await query.answer()
        
        lang = context.user_data.get("lang", "ru")
        texts = RU_TEXTS if lang == "ru" else EN_TEXTS
        videos = RU_VIDEOS if lang == "ru" else EN_VIDEOS
        
        # Комбинированное сообщение
        await query.message.reply_text(
            f"🎬 {texts.get('training_video', 'Видео обучения:')} {videos['ikona_training']}\n\n"
            f"{texts['ikona_training']}",
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
        
        # Кнопки выбора обучения
        keyboard = [
            [InlineKeyboardButton(texts["offline_training_btn"], callback_data="offline_training")],
            [InlineKeyboardButton(texts["online_training_btn"], callback_data="online_training")],
            [InlineKeyboardButton(texts["back_to_main"], callback_data="main_menu")]
        ]
        
        await query.message.reply_text(
            texts["choose_action"],
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    except Exception as e:
        logger.error(f"Ошибка ikona_training: {e}")
        await error_handler(update, context)

async def offline_training(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Оффлайн обучение"""
    try:
        query = update.callback_query
        await query.answer()
        
        lang = context.user_data.get("lang", "ru")
        texts = RU_TEXTS if lang == "ru" else EN_TEXTS
        videos = RU_VIDEOS if lang == "ru" else EN_VIDEOS
        
        # Комбинированное сообщение
        await query.message.reply_text(
            f"🎬 Оффлайн обучение: {videos['offline_training']}\n\n"
            f"{texts['offline_training']}",
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
        
        # Кнопки
        keyboard = [
            [InlineKeyboardButton(texts["trial_lesson"], callback_data="contact_for_trial")],
            [InlineKeyboardButton(texts["back_to_main"], callback_data="main_menu")]
        ]
        
        await query.message.reply_text(
            texts["choose_action"],
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    except Exception as e:
        logger.error(f"Ошибка offline_training: {e}")
        await error_handler(update, context)

async def online_training(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Онлайн обучение"""
    try:
        query = update.callback_query
        await query.answer()
        
        lang = context.user_data.get("lang", "ru")
        texts = RU_TEXTS if lang == "ru" else EN_TEXTS
        videos = RU_VIDEOS if lang == "ru" else EN_VIDEOS
        
        # Комбинированное сообщение
        await query.message.reply_text(
            f"🎬 Онлайн обучение: {videos['online_training']}\n\n"
            f"{texts['online_training']}",
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
        
        # Кнопки
        keyboard = [
            [InlineKeyboardButton(texts["more_details"], callback_data="contact_for_details")],
            [InlineKeyboardButton(texts["back_to_main"], callback_data="main_menu")]
        ]
        
        await query.message.reply_text(
            texts["choose_action"],
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    except Exception as e:
        logger.error(f"Ошибка online_training: {e}")
        await error_handler(update, context)

async def contact_for_trial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Контакт для пробного урока"""
    try:
        query = update.callback_query
        await query.answer()
        
        lang = context.user_data.get("lang", "ru")
        texts = RU_TEXTS if lang == "ru" else EN_TEXTS
        
        await query.message.reply_text(
            texts["contact_for_trial"],
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка contact_for_trial: {e}")
        await error_handler(update, context)

async def contact_for_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Контакт для подробностей"""
    try:
        query = update.callback_query
        await query.answer()
        
        lang = context.user_data.get("lang", "ru")
        texts = RU_TEXTS if lang == "ru" else EN_TEXTS
        
        await query.message.reply_text(
            texts["contact_for_details"],
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка contact_for_details: {e}")
        await error_handler(update, context)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений"""
    try:
        lang = context.user_data.get("lang", "ru")
        texts = RU_TEXTS if lang == "ru" else EN_TEXTS
        
        await update.message.reply_text(
            texts["use_buttons"],
            reply_markup=InlineKeyboardMarkup(
                [InlineKeyboardButton(texts["back_to_main"], callback_data="main_menu")]
            )
        )
        
    except Exception as e:
        logger.error(f"Ошибка handle_text: {e}")
        await error_handler(update, context)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Глобальный обработчик ошибок"""
    error = context.error
    logger.error(msg="Exception occurred:", exc_info=error)
    
    if update and isinstance(update, Update):
        message = update.effective_message
        if message:
            try:
                lang = context.user_data.get("lang", "ru") if hasattr(context, 'user_data') else "ru"
                text = RU_TEXTS["error"] if lang == "ru" else EN_TEXTS["error"]
                await message.reply_text(text)
            except Exception as e:
                logger.error(f"Не удалось отправить сообщение об ошибке: {e}")

# --- Основная функция ---
async def main():
    """Запуск бота"""
    try:
        # Загрузка кэша
        await media_cache.load()
        
        # Создание приложения
        app = Application.builder().token(TOKEN).build()
        
        # Обработчики команд
        app.add_handler(CommandHandler("start", start))
        
        # Обработчики callback
        app.add_handler(CallbackQueryHandler(set_lang_ru, pattern="^set_lang_ru$"))
        app.add_handler(CallbackQueryHandler(set_lang_en, pattern="^set_lang_en$"))
        app.add_handler(CallbackQueryHandler(show_prompt, pattern="^show_prompt$"))
        app.add_handler(CallbackQueryHandler(main_menu, pattern="^main_menu$"))
        app.add_handler(CallbackQueryHandler(free_train, pattern="^free_train$"))
        app.add_handler(CallbackQueryHandler(pro_version, pattern="^pro_version$"))
        app.add_handler(CallbackQueryHandler(ikona_training, pattern="^ikona_training$"))
        app.add_handler(CallbackQueryHandler(offline_training, pattern="^offline_training$"))
        app.add_handler(CallbackQueryHandler(online_training, pattern="^online_training$"))
        app.add_handler(CallbackQueryHandler(contact_for_trial, pattern="^contact_for_trial$"))
        app.add_handler(CallbackQueryHandler(contact_for_details, pattern="^contact_for_details$"))
        
        # Обработчик текстовых сообщений
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
        
        # Обработчик ошибок
        app.add_error_handler(error_handler)
        
        # Запуск
        logger.info("Бот запущен в режиме polling...")
        await app.run_polling()
        
    except Exception as e:
        logger.critical(f"Фатальная ошибка: {e}")
    finally:
        logger.info("Бот остановлен")

if __name__ == "__main__":
    asyncio.run(main())
