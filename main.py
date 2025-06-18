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

# Видео для русской версии (теперь с возможностью хранения file_id)
# Изначально будут ссылки, но после первой отправки бота будут сохранены file_id
RU_VIDEOS = {
    "free_train": {"url": "https://youtu.be/mxxbhZ8SxTU", "file_id": None},
    "pro_version": {"url": "https://youtube.com/shorts/7hP9p5GnXWM?si=9Zq_pArWAZaisSKR", "file_id": None},
    "ikona_training": {"url": "https://www.youtube.com/watch?v=GX_ZbWx0oYY", "file_id": None},
    "offline_training": {"url": "https://www.youtube.com/watch?v=Kopx3whZquc", "file_id": None},
    "online_training": {"url": "https://www.youtube.com/watch?v=10b_j5gBAg8", "file_id": None}
}

# Видео для английской версии
EN_VIDEOS = {
    "free_train": {"url": "https://youtu.be/RcLS9A24Kss", "file_id": None},
    "pro_version": {"url": "https://youtube.com/shorts/_I2o5jc76Ug?si=DxRgG60LuHmbiN2w", "file_id": None},
    "ikona_training": {"url": "https://www.youtube.com/watch?v=GX_ZbWx0oYY", "file_id": None},
    "offline_training": {"url": "https://www.youtube.com/watch?v=Kopx3whZquc", "file_id": None},
    "online_training": {"url": "https://www.youtube.com/watch?v=10b_j5gBAg8", "file_id": None}
}

COLAB_URL = "https://colab.research.google.com/drive/1lWfrS0Jh0B2B99IJ26aincVXylaoLuDq?usp=sharing"
TRIBUT_URL = "https://t.me/tribute/app?startapp=ep_8y0gVeOLXYRcOrfRtGTMLW8vu0C82z72WfxBEEtJz3ofJTky32"

# Тексты для русской версии
RU_TEXTS = {
    "start": (
        "🖌️ **OVERLORD AI INK (Free Train)**\n\n"
        "**Бесплатная версия нейросети** для генерации изображений в стиле:\n"
        "* Sigilism\n"
        "* Tribal\
        "* Dark Tattoo\n\n"
        "Создавайте уникальные арты **без ограничений**!\n\n"
        "**КАК ИСПОЛЬЗОВАТЬ:**\n\n"
        "**1.** Введите текстовый промт на английском языке или используйте готовые примеры\n\n"
        "**2.** Настройте параметры генерации:\n"
        "   - Sampling method: **DPM++ 2M SDE**\n"
        "   - Steps: **20**\n"
        "   - Width: **720**\n"
        "   - Height: **980**\n"
        "   - CFG Scale: **4**\n\n"
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
        "- Sigilism\n"
        "- Tribal\n"
        "- Dark Tattoo\n\n"
        "Create unique artworks **without limitations**!\n\n"
        "**HOW TO USE:**\n\n"
        "**1.** Enter text prompt in English or use ready examples\n\n"
        "**2.** Configure generation parameters:\n"
        "   - Sampling method: **DPM++ 2M SDE**\n"
        "   - Steps: **20**\n"
        "   - Width: **720**\n"
        "   - Height: **980**\n"
        "   - CFG Scale: **4**\n\n"
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

# Добавляем file_id для гифок
# Это будет храниться в памяти бота и позволит избежать повторной загрузки
GIF_FILE_IDS = {
    "14.gif": None,
    "9d.gif": None,
}

async def send_media_with_file_id(message, media_type: str, file_path: str, caption: str = None, reply_markup=None) -> str:
    """
    Отправляет медиафайл, используя file_id из глобального словаря GIF_FILE_IDS, если он доступен,
    иначе отправляет файл с диска и сохраняет file_id.
    Возвращает file_id отправленного файла или None в случае ошибки.
    """
    file_name = os.path.basename(file_path)
    current_file_id = GIF_FILE_IDS.get(file_name)

    if current_file_id:
        try:
            if media_type == "animation":
                sent_message = await message.reply_animation(animation=current_file_id, caption=caption, reply_markup=reply_markup)
            elif media_type == "photo":
                sent_message = await message.reply_photo(photo=current_file_id, caption=caption, reply_markup=reply_markup)
            logger.info(f"Медиафайл {file_name} отправлен по file_id: {current_file_id}")
            return current_file_id
        except Exception as e:
            logger.warning(f"Ошибка при отправке медиа {file_name} по file_id ({current_file_id}): {e}. Попытка отправить с диска.")
            GIF_FILE_IDS[file_name] = None # Сбрасываем file_id, если он недействителен

    full_file_path = os.path.join("static", file_path)
    if not os.path.exists(full_file_path):
        logger.error(f"Файл {full_file_path} не найден.")
        await message.reply_text(f"⚠️ Файл не найден: {caption}" if caption else "⚠️ Файл не найден.")
        return None

    try:
        with open(full_file_path, "rb") as file_to_send:
            if media_type == "animation":
                sent_message = await message.reply_animation(animation=InputFile(file_to_send), caption=caption, reply_markup=reply_markup)
                new_file_id = sent_message.animation.file_id
            elif media_type == "photo":
                sent_message = await message.reply_photo(photo=InputFile(file_to_send), caption=caption, reply_markup=reply_markup)
                new_file_id = sent_message.photo[-1].file_id # Берем наибольшую версию фото
            
            GIF_FILE_IDS[file_name] = new_file_id
            logger.info(f"Медиафайл {file_name} отправлен с диска и сохранен file_id: {new_file_id}")
            return new_file_id
    except Exception as e:
        logger.error(f"Ошибка при отправке медиафайла {full_file_path}: {e}")
        await message.reply_text(f"⚠️ Ошибка при отправке медиа. {caption}" if caption else "⚠️ Ошибка при отправке медиа.")
        return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка команды /start"""
    try:
        user = update.effective_user
        logger.info(f"Новый пользователь: {user.id} {user.username}")
        
        # Инициализация состояния пользователя
        context.user_data["prompt_index"] = 0
        
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
        videos = RU_VIDEOS if lang == "ru" else EN_VIDEOS
        
        # Отправка YouTube видео (отдельно)
        video_text = "🎬 Видео обучения:" if lang == "ru" else "🎬 Training video:"
        await query.message.reply_text(f"{video_text} {videos['free_train']['url']}")
        
        # Объединяем вступительный текст и Colab URL в одну подпись для GIF
        gif_path = "14.gif"
        caption_text = f"{texts['start']}\n\n🚀 {'Начните генерацию! Используйте COLAB:' if lang == 'ru' else 'Start generating! Use COLAB:'} {COLAB_URL}"

        # Отправка GIF с объединенным текстом
        await send_media_with_file_id(
            query.message,
            "animation",
            gif_path,
            caption=caption_text,
            # No reply_markup here, will send main menu buttons separately
        )
        
        # Кнопки при старте - отправляем отдельным сообщением после GIF
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
        # Отправляем сообщение об ошибке только один раз
        await query.message.reply_text("⚠️ Произошла ошибка при загрузке. Пожалуйста, попробуйте еще раз, нажав /start.")


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
        
        # Отправляем фото
        await send_media_with_file_id(
            query.message,
            "photo",
            prompt_data["image"], # Имя файла, например "image1.jpg"
            caption=prompt_data["prompt"]
        )
        
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
        videos = RU_VIDEOS if lang == "ru" else EN_VIDEOS
        
        # Отправка YouTube видео (отдельно)
        video_text = "🎬 Видео обучения:" if lang == "ru" else "🎬 Training video:"
        await query.message.reply_text(f"{video_text} {videos['free_train']['url']}")
        
        # Объединяем вступительный текст и Colab URL в одну подпись для GIF
        gif_path = "14.gif"
        caption_text = f"{texts['start']}\n\n🚀 {'Начните генерацию! Используйте COLAB:' if lang == 'ru' else 'Start generating! Use COLAB:'} {COLAB_URL}"

        # Отправка GIF с объединенным текстом
        await send_media_with_file_id(
            query.message,
            "animation",
            gif_path,
            caption=caption_text,
            # No reply_markup here, will send main menu buttons separately
        )
        
        # Кнопки - отправляем отдельным сообщением после GIF
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
        videos = RU_VIDEOS if lang == "ru" else EN_VIDEOS
        
        # Отправка PRO видео
        video_text = "🎬 PRO обучение:" if lang == "ru" else "🎬 PRO Training:"
        await query.message.reply_text(f"{video_text} {videos['pro_version']['url']}")
        
        # Описание преимуществ PRO в подписи GIF
        pro_gif_path = "9d.gif"
        
        # Кнопки для PRO версии встроены в GIF
        keyboard_pro = [
            [InlineKeyboardButton(texts["get_pro"], url=TRIBUT_URL)]
        ]
        reply_markup_pro = InlineKeyboardMarkup(keyboard_pro)
        
        await send_media_with_file_id(
            query.message,
            "animation",
            pro_gif_path,
            caption=f"{texts['pro_features']}\n\n{texts['pro_caption']}", # Объединяем текст
            reply_markup=reply_markup_pro
        )

        # Кнопки для возврата - отправляем отдельным сообщением
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
        videos = RU_VIDEOS if lang == "ru" else EN_VIDEOS
        
        # Отправка видео
        video_text = "🎬 Обучение IKONA:" if lang == "ru" else "🎬 IKONA Training:"
        await query.message.reply_text(f"{video_text} {videos['ikona_training']['url']}")
        
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
        videos = RU_VIDEOS if lang == "ru" else EN_VIDEOS
        
        # Отправка видео
        video_text = "🎬 Оффлайн обучение:" if lang == "ru" else "🎬 Offline training:"
        await query.message.reply_text(f"{video_text} {videos['offline_training']['url']}")
        
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
        videos = RU_VIDEOS if lang == "ru" else EN_VIDEOS
        
        # Отправка видео
        video_text = "🎬 Онлайн обучение:" if lang == "ru" else "🎬 Online training:"
        await query.message.reply_text(f"{video_text} {videos['online_training']['url']}")
        
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
