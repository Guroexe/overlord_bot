# -*- coding: utf-8 -*-
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
if not TOKEN:
    logger.error("Токен бота не найден в переменных окружения!")
    raise ValueError("Токен бота не найден")

# Видео для русской версии
RU_VIDEOS = {
    "free_train": "https://youtu.be/mxxbhZ8SxTU",
    "pro_version": "pro 420 ru.mp4",
    "ikona_training": "IKONA 420.mp4",
    "offline_training": "MARSHRUTNYI PLAN OBUCH 420.mp4",
    "online_training": "AI 420.mp4"
}

# Видео для английской версии
EN_VIDEOS = {
    "free_train": "https://youtu.be/RcLS9A24Kss",
    "pro_version": "420 pro en.mp4",
    "ikona_training": "IKONA 420.mp4",
    "offline_training": "MARSHRUTNYI PLAN OBUCH 420.mp4",
    "online_training": "AI 420.mp4"
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
        "🔗 [Оформить PRO версию](https://t.me/tribute/app?startapp=ep_8y0gVeOLXYRcOrfRtGTMLW8vu0C82z72WfxBEEtJz3ofJTky32)\n\n"
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
        "⏱️ **Срок обучения:** 2 месяца\n"
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
    "error": "⚠️ Если не появились кнопки, нажмите /start ",
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
    "use_buttons": "Пожалуйста, используйте кнопки меню"
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
        "🔗 [Get PRO version](https://t.me/tribute/app?startapp=ep_8y0gVeOLXYRcOrfRtGTMLW8vu0C82z72WfxBEEtJz3ofJTky32)\n\n"
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
    "use_buttons": "Please use menu buttons"
}

# Загрузка промтов
try:
    with open("prompts.json", "r", encoding="utf-8") as f:
        PROMPTS = json.load(f)
    logger.info(f"Успешно загружено {len(PROMPTS)} промтов")
except Exception as e:
    logger.error(f"Ошибка загрузки prompts.json: {str(e)}")
    PROMPTS = []

async def send_video_from_static(message, context: ContextTypes.DEFAULT_TYPE, video_key: str, caption: str = None) -> None:
    """Отправка видео из папки static или YouTube ссылки"""
    try:
        lang = context.user_data.get("lang", "ru")
        videos = RU_VIDEOS if lang == "ru" else EN_VIDEOS
        video_content = videos[video_key]
        
        # Если это YouTube ссылка
        if video_key == "free_train":
            await message.reply_text(video_content)
            return
            
        video_path = os.path.join("static", video_content)
        
        cached_file_id = context.user_data["file_id_cache"].get(video_path)

        if cached_file_id:
            logger.info(f"Отправка видео из кэша: {video_path}")
            message = await message.reply_video(
                video=cached_file_id,
                caption=caption,
                parse_mode='Markdown' if caption else None
            )
        else:
            try:
                logger.info(f"Отправка видео с диска: {video_path}")
                with open(video_path, "rb") as video_file:
                    message = await message.reply_video(
                        video=InputFile(video_file),
                        caption=caption,
                        parse_mode='Markdown' if caption else None
                    )
                # Сохраняем file_id в кэш
                if message.video and message.video.file_id:
                    context.user_data["file_id_cache"][video_path] = message.video.file_id
                    logger.info(f"Сохранен file_id для {video_path}: {message.video.file_id}")
            except FileNotFoundError:
                logger.error(f"Файл {video_path} не найден")
                if caption:
                    await message.reply_text(caption, parse_mode='Markdown')
            except Exception as e:
                logger.error(f"Ошибка при отправке видео {video_path}: {str(e)}")
                if caption:
                    await message.reply_text(caption, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Ошибка в send_video_from_static: {str(e)}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка команды /start"""
    try:
        user = update.effective_user
        logger.info(f"Новый пользователь: {user.id} {user.username}")
        
        # Инициализация состояния пользователя
        context.user_data["prompt_index"] = 0
        # Инициализация кэша file_id для текущего пользователя
        if "file_id_cache" not in context.user_data:
            context.user_data["file_id_cache"] = {}
        
        # Кнопки выбора языка
        keyboard = [
            [
                InlineKeyboardButton("🇷🇺 Русский", callback_data="set_lang_ru"),
                InlineKeyboardButton("🇺🇸 English", callback_data="set_lang_en")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Please select language / Пожалуйста, выберите язык:", reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Ошибка в команде /start: {str(e)}")
        await update.message.reply_text("⚠️ Произошла ошибка. Попробуйте позже.")

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE, lang: str) -> None:
    """Установка языка и показ главного меню"""
    try:
        query = update.callback_query
        await query.answer()
        
        # Сохраняем выбранный язык
        context.user_data["lang"] = lang
        texts = RU_TEXTS if lang == "ru" else EN_TEXTS
        
        # Отправка YouTube видео обучения
        await send_video_from_static(query.message, context, "free_train")
        
        # Комбинированный текст для GIF-сообщения
        full_caption_text = (
            f"{texts['start']}\n\n"
            f"🚀 {'Начните генерацию! Используйте COLAB:' if lang == 'ru' else 'Start generating! Use COLAB:'} {COLAB_URL}"
        )

        # Отправка GIF с объединенным текстом в качестве подписи
        gif_path = os.path.join("static", "14.gif")
        cached_file_id = context.user_data["file_id_cache"].get(gif_path)

        if cached_file_id:
            logger.info(f"Отправка GIF из кэша: {gif_path}")
            message = await query.message.reply_animation(
                animation=cached_file_id,
                caption=full_caption_text,
                parse_mode='Markdown'
            )
        else:
            try:
                logger.info(f"Отправка GIF с диска: {gif_path}")
                with open(gif_path, "rb") as gif_file:
                    message = await query.message.reply_animation(
                        animation=InputFile(gif_file),
                        caption=full_caption_text,
                        parse_mode='Markdown'
                    )
                # Сохраняем file_id в кэш
                if message.animation and message.animation.file_id:
                    context.user_data["file_id_cache"][gif_path] = message.animation.file_id
                    logger.info(f"Сохранен file_id для {gif_path}: {message.animation.file_id}")
            except FileNotFoundError:
                logger.error(f"Файл {gif_path} не найден")
                await query.message.reply_text(full_caption_text, parse_mode='Markdown')
            except Exception as e:
                logger.error(f"Ошибка при отправке GIF {gif_path}: {str(e)}")
                await query.message.reply_text(full_caption_text, parse_mode='Markdown')
        
        # Кнопки при старте
        keyboard = [
            [
                InlineKeyboardButton(texts["prompt_example"], callback_data="show_prompt"),
                InlineKeyboardButton(texts["full_version"], callback_data="pro_version")
            ],
            [
                InlineKeyboardButton(texts["ikona_training_btn"], callback_data="ikona_training")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(texts["choose_action"], reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Ошибка в set_language: {str(e)}")
        if update.callback_query:
            await update.callback_query.message.reply_text("⚠️ Произошла ошибка. Попробуйте позже.")
        else:
            await update.message.reply_text("⚠️ Произошла ошибка. Попробуйте позже.")

async def set_lang_ru(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Установка русского языка"""
    await set_language(update, context, "ru")

async def set_lang_en(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Установка английского языка"""
    await set_language(update, context, "en")

async def show_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показ примера промта с изображением"""
    try:
        query = update.callback_query
        await query.answer()
        
        lang = context.user_data.get("lang", "ru")
        texts = RU_TEXTS if lang == "ru" else EN_TEXTS
        
        if not PROMPTS:
            await query.message.reply_text(texts["prompt_not_found"])
            return
            
        # Получение текущего индекса
        current_index = context.user_data.get("prompt_index", 0)
        prompt_data = PROMPTS[current_index]
        
        # Отправка изображения
        image_path = os.path.join("static", prompt_data["image"])
        cached_file_id = context.user_data["file_id_cache"].get(image_path)

        if cached_file_id:
            logger.info(f"Отправка фото из кэша: {image_path}")
            message = await query.message.reply_photo(
                photo=cached_file_id,
                caption=prompt_data["prompt"]
            )
        else:
            try:
                logger.info(f"Отправка фото с диска: {image_path}")
                with open(image_path, "rb") as photo_file:
                    message = await query.message.reply_photo(
                        photo=InputFile(photo_file),
                        caption=prompt_data["prompt"]
                    )
                # Сохраняем file_id в кэш
                if message.photo and message.photo[-1].file_id:
                    context.user_data["file_id_cache"][image_path] = message.photo[-1].file_id
                    logger.info(f"Сохранен file_id для {image_path}: {message.photo[-1].file_id}")
            except FileNotFoundError:
                logger.error(f"Файл {image_path} не найден")
                await query.message.reply_text(prompt_data["prompt"])
            except Exception as e:
                logger.error(f"Ошибка при отправке фото {image_path}: {str(e)}")
                await query.message.reply_text(prompt_data["prompt"])
        
        # Обновление индекса
        next_index = (current_index + 1) % len(PROMPTS)
        context.user_data["prompt_index"] = next_index
        
        # Кнопки для продолжения
        keyboard = [
            [
                InlineKeyboardButton(texts["more_examples"], callback_data="show_prompt"),
                InlineKeyboardButton(texts["back_to_main"], callback_data="main_menu")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(texts["what_next"], reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Ошибка в show_prompt: {str(e)}")
        await query.message.reply_text("⚠️ Не удалось загрузить пример")

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показ главного меню"""
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
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(texts["main_menu"], reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Ошибка в main_menu: {str(e)}")

async def free_train(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Повторная отправка стартового сообщения"""
    try:
        query = update.callback_query
        await query.answer()
        
        lang = context.user_data.get("lang", "ru")
        texts = RU_TEXTS if lang == "ru" else EN_TEXTS
        
        # Отправка YouTube видео обучения
        await send_video_from_static(query.message, context, "free_train")
        
        # Комбинированный текст для GIF-сообщения
        full_caption_text = (
            f"{texts['start']}\n\n"
            f"🚀 {'Начните генерацию! Используйте COLAB:' if lang == 'ru' else 'Start generating! Use COLAB:'} {COLAB_URL}"
        )
        
        gif_path = os.path.join("static", "14.gif")
        cached_file_id = context.user_data["file_id_cache"].get(gif_path)

        if cached_file_id:
            logger.info(f"Отправка GIF из кэша: {gif_path}")
            message = await query.message.reply_animation(
                animation=cached_file_id,
                caption=full_caption_text,
                parse_mode='Markdown'
            )
        else:
            try:
                logger.info(f"Отправка GIF с диска: {gif_path}")
                with open(gif_path, "rb") as gif_file:
                    message = await query.message.reply_animation(
                        animation=InputFile(gif_file),
                        caption=full_caption_text,
                        parse_mode='Markdown'
                    )
                # Сохраняем file_id в кэш
                if message.animation and message.animation.file_id:
                    context.user_data["file_id_cache"][gif_path] = message.animation.file_id
                    logger.info(f"Сохранен file_id для {gif_path}: {message.animation.file_id}")
            except FileNotFoundError:
                logger.error(f"Файл {gif_path} не найден")
                await query.message.reply_text(full_caption_text, parse_mode='Markdown')
            except Exception as e:
                logger.error(f"Ошибка при отправке GIF {gif_path}: {str(e)}")
                await query.message.reply_text(full_caption_text, parse_mode='Markdown')
        
        keyboard = [
            [
                InlineKeyboardButton(texts["prompt_example"], callback_data="show_prompt"),
                InlineKeyboardButton(texts["full_version"], callback_data="pro_version")
            ],
            [
                InlineKeyboardButton(texts["ikona_training_btn"], callback_data="ikona_training")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(texts["choose_action"], reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Ошибка в free_train: {str(e)}")

async def pro_version(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Информация о PRO версии"""
    try:
        query = update.callback_query
        await query.answer()
        
        lang = context.user_data.get("lang", "ru")
        texts = RU_TEXTS if lang == "ru" else EN_TEXTS
        
        # Комбинированный текст для видео-сообщения
        pro_caption_text = texts["pro_features"]

        # Отправляем видео с текстом
        await send_video_from_static(query.message, context, "pro_version", pro_caption_text)
        
        # Кнопки для возврата
        keyboard = [
            [InlineKeyboardButton(texts["back_to_main"], callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(texts["choose_action"], reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Ошибка в pro_version: {str(e)}")

async def ikona_training(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обучение Тату IKONA"""
    try:
        query = update.callback_query
        await query.answer()
        
        lang = context.user_data.get("lang", "ru")
        texts = RU_TEXTS if lang == "ru" else EN_TEXTS
        
        # Отправка видео
        await send_video_from_static(query.message, context, "ikona_training")
        
        # Описание обучения
        await query.message.reply_text(texts["ikona_training"], parse_mode='Markdown')
        
        # Кнопки выбора программы
        keyboard = [
            [InlineKeyboardButton(texts["offline_training_btn"], callback_data="offline_training")],
            [InlineKeyboardButton(texts["online_training_btn"], callback_data="online_training")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        menu_text = "Выберите формат обучения:" if lang == "ru" else "Choose training format:"
        await query.message.reply_text(menu_text, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Ошибка в ikona_training: {str(e)}")

async def offline_training(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Оффлайн обучение IKONA"""
    try:
        query = update.callback_query
        await query.answer()
        
        lang = context.user_data.get("lang", "ru")
        texts = RU_TEXTS if lang == "ru" else EN_TEXTS
        
        # Отправка видео
        await send_video_from_static(query.message, context, "offline_training")
        
        # Описание оффлайн обучения
        await query.message.reply_text(texts["offline_training"], parse_mode='Markdown')
        
        # Кнопки
        keyboard = [
            [InlineKeyboardButton(texts["trial_lesson"], callback_data="contact_for_trial")],
            [InlineKeyboardButton(texts["back_to_main"], callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(texts["choose_action"], reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Ошибка в offline_training: {str(e)}")

async def online_training(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Онлайн обучение IKONA"""
    try:
        query = update.callback_query
        await query.answer()
        
        lang = context.user_data.get("lang", "ru")
        texts = RU_TEXTS if lang == "ru" else EN_TEXTS
        
        # Отправка видео
        await send_video_from_static(query.message, context, "online_training")
        
        # Описание онлайн обучения
        await query.message.reply_text(texts["online_training"], parse_mode='Markdown')
        
        # Кнопки
        keyboard = [
            [InlineKeyboardButton(texts["more_details"], callback_data="contact_for_details")],
            [InlineKeyboardButton(texts["back_to_main"], callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(texts["choose_action"], reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Ошибка в online_training: {str(e)}")

async def contact_for_trial(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Контакт для записи на пробный урок"""
    try:
        query = update.callback_query
        await query.answer()
        
        lang = context.user_data.get("lang", "ru")
        texts = RU_TEXTS if lang == "ru" else EN_TEXTS
        
        await query.message.reply_text(texts["contact_for_trial"], parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Ошибка в contact_for_trial: {str(e)}")

async def contact_for_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Контакт для подробностей"""
    try:
        query = update.callback_query
        await query.answer()
        
        lang = context.user_data.get("lang", "ru")
        texts = RU_TEXTS if lang == "ru" else EN_TEXTS
        
        await query.message.reply_text(texts["contact_for_details"], parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Ошибка в contact_for_details: {str(e)}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка текстовых сообщений"""
    try:
        lang = context.user_data.get("lang", "ru")
        texts = RU_TEXTS if lang == "ru" else EN_TEXTS
        await update.message.reply_text(texts["use_buttons"])
    except Exception as e:
        logger.error(f"Ошибка в handle_text: {str(e)}")

def main() -> None:
    """Запуск бота"""
    try:
        application = Application.builder().token(TOKEN).build()
        
        # Обработчики команд
        application.add_handler(CommandHandler("start", start))
        
        # Обработчики callback-запросов
        application.add_handler(CallbackQueryHandler(set_lang_ru, pattern="^set_lang_ru$"))
        application.add_handler(CallbackQueryHandler(set_lang_en, pattern="^set_lang_en$"))
        application.add_handler(CallbackQueryHandler(show_prompt, pattern="^show_prompt$"))
        application.add_handler(CallbackQueryHandler(main_menu, pattern="^main_menu$"))
        application.add_handler(CallbackQueryHandler(free_train, pattern="^free_train$"))
        application.add_handler(CallbackQueryHandler(pro_version, pattern="^pro_version$"))
        application.add_handler(CallbackQueryHandler(ikona_training, pattern="^ikona_training$"))
        application.add_handler(CallbackQueryHandler(offline_training, pattern="^offline_training$"))
        application.add_handler(CallbackQueryHandler(online_training, pattern="^online_training$"))
        application.add_handler(CallbackQueryHandler(contact_for_trial, pattern="^contact_for_trial$"))
        application.add_handler(CallbackQueryHandler(contact_for_details, pattern="^contact_for_details$"))
        
        # Обработчик текстовых сообщений
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
        
        logger.info("Бот запускается...")
        application.run_polling()
        
    except Exception as e:
        logger.critical(f"Ошибка запуска бота: {str(e)}")

if __name__ == "__main__":
    main()
