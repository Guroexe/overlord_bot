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

FREE_TRAIN_VIDEO = "https://www.youtube.com/watch?v=10b_j5gBAg8"
PRO_VERSION_VIDEO = "https://www.youtube.com/watch?v=QKLOb6f5L-k"
COLAB_URL = "https://colab.research.google.com/drive/1lWfrS0Jh0B2B99IJ26aincVXylaoLuDq?usp=sharing"
TRIBUT_URL = "https://t.me/tribute/app?startapp=ep_8y0gVeOLXYRcOrfRtGTMLW8vu0C82z72WfxBEEtJz3ofJTky32"

# Новые константы для IKONA
IKONA_MAIN_VIDEO = "https://www.youtube.com/watch?v=GX_ZbWx0oYY"
IKONA_OFFLINE_VIDEO = "https://www.youtube.com/watch?v=Kopx3whZquc"
IKONA_ONLINE_VIDEO = "https://www.youtube.com/watch?v=10b_j5gBAg8"

# Загрузка промтов
try:
    with open("prompts.json", "r", encoding="utf-8") as f:
        PROMPTS = json.load(f)
    logger.info(f"Успешно загружено {len(PROMPTS)} промтов")
except Exception as e:
    logger.error(f"Ошибка загрузки prompts.json: {str(e)}")
    PROMPTS = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка команды /start"""
    try:
        user = update.effective_user
        logger.info(f"Новый пользователь: {user.id} {user.username}")
        
        # Инициализация состояния пользователя
        context.user_data["prompt_index"] = 0
        
        # Отправка YouTube видео
        await update.message.reply_text(f"🎬 **Обучающее видео:** {FREE_TRAIN_VIDEO}", parse_mode='Markdown')
        
        # Отправка описания
        description = (
            "🖌️ **OVERLORD AI INK (Free Train)**\n\n"
            "Это бесплатная версия нейросети для генерации изображений в стиле sigilism, tribal, dark tattoo. "
            "Используйте OVERLORD INK AI для создания уникальных артов без ограничений!\n\n"
            "**Как использовать:**\n"
            "1. Введите текстовый промт на английском. Или используйте промт из примеров подсказок\n"
            "2. Настройте параметры. Sampling method - DPM++ 2M SDE. Steps - 20. Width - 720. Height - 980. CFG Scale - 4\n"
            "3. Генерируйте изображения бесплатно!\n\n"
            "*создатель - https://t.me/gurovlad*"
        )
        await update.message.reply_text(description, parse_mode='Markdown')
        
        # Отправка GIF
        gif_path = os.path.join("static", "14.gif")
        try:
            with open(gif_path, "rb") as gif_file:
                await update.message.reply_animation(
                    animation=InputFile(gif_file),
                    caption=f"🚀 **Начать генерацию!** Используй COLAB: {COLAB_URL}",
                    parse_mode='Markdown'
                )
        except FileNotFoundError:
            logger.error(f"Файл {gif_path} не найден")
            await update.message.reply_text(f"🚀 **Начать генерацию:** {COLAB_URL}", parse_mode='Markdown')
        
        # Кнопки при старте
        keyboard = [
            [
                InlineKeyboardButton("Пример промта", callback_data="show_prompt"),
                InlineKeyboardButton("OVERLORD AI INK PRO", callback_data="pro_version")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("**Выберите действие:**", reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Ошибка в команде /start: {str(e)}")
        await update.message.reply_text("⚠️ Произошла ошибка. Попробуйте позже.")

async def show_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показ примера промта с изображением"""
    try:
        query = update.callback_query
        await query.answer()
        
        if not PROMPTS:
            await query.message.reply_text("⚠️ Примеры промтов временно недоступны")
            return
            
        # Получение текущего индекса
        current_index = context.user_data.get("prompt_index", 0)
        prompt_data = PROMPTS[current_index]
        
        # Отправка изображения
        image_path = os.path.join("static", prompt_data["image"])
        try:
            with open(image_path, "rb") as photo_file:
                await query.message.reply_photo(
                    photo=InputFile(photo_file),
                    caption=f"**Пример промта:**\n\n`{prompt_data['prompt']}`",
                    parse_mode='Markdown'
                )
        except FileNotFoundError:
            logger.error(f"Файл {image_path} не найден")
            await query.message.reply_text(f"**Пример промта:**\n\n`{prompt_data['prompt']}`", parse_mode='Markdown')
        
        # Обновление индекса
        next_index = (current_index + 1) % len(PROMPTS)
        context.user_data["prompt_index"] = next_index
        
        # Кнопки для продолжения
        keyboard = [
            [
                InlineKeyboardButton("Ещё пример", callback_data="show_prompt"),
                InlineKeyboardButton("Главное меню", callback_data="main_menu")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("**Что дальше?**", reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Ошибка в show_prompt: {str(e)}")
        await query.message.reply_text("⚠️ Не удалось загрузить пример")

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показ главного меню"""
    try:
        query = update.callback_query
        await query.answer()
        
        keyboard = [
            [InlineKeyboardButton("OVERLORD AI INK (Free Train)", callback_data="free_train")],
            [InlineKeyboardButton("Полная Версия OVERLORD AI INK PRO", callback_data="pro_version")],
            [InlineKeyboardButton("Обучение Тату IKONA", callback_data="ikona_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("**ГЛАВНОЕ МЕНЮ**", reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Ошибка в main_menu: {str(e)}")

async def free_train(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Повторная отправка стартового сообщения"""
    try:
        query = update.callback_query
        await query.answer()
        
        await query.message.reply_text(f"🎬 **Обучающее видео:** {FREE_TRAIN_VIDEO}", parse_mode='Markdown')
        
        description = (
            "🖌️ **OVERLORD AI INK (Free Train)**\n\n"
            "Бесплатная версия с 3 стилями генераций изображений в стиле sigilism, tribal, dark tattoo. "
            "Используйте OVERLORD INK AI для создания уникальных артов без ограничений!\n\n"
            "**Как использовать:**\n"
            "1. Введите текстовый промт на английском\n"
            "2. Настройте параметры генерации\n"
            "3. Создавайте уникальные изображения бесплатно!\n\n"
            "*создатель - https://t.me/gurovlad*"
        )
        await query.message.reply_text(description, parse_mode='Markdown')
        
        gif_path = os.path.join("static", "14.gif")
        try:
            with open(gif_path, "rb") as gif_file:
                await query.message.reply_animation(
                    animation=InputFile(gif_file),
                    caption=f"🚀 **Начать генерацию!** COLAB: {COLAB_URL}",
                    parse_mode='Markdown'
                )
        except FileNotFoundError:
            await query.message.reply_text(f"🚀 **Начать генерацию:** {COLAB_URL}", parse_mode='Markdown')
        
        keyboard = [
            [
                InlineKeyboardButton("Пример промта", callback_data="show_prompt"),
                InlineKeyboardButton("OVERLORD AI INK PRO", callback_data="pro_version")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("**Выберите действие:**", reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Ошибка в free_train: {str(e)}")

async def pro_version(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Информация о PRO версии"""
    try:
        query = update.callback_query
        await query.answer()
        
        # Отправка PRO видео
        await query.message.reply_text(f"🎬 **PRO Обучение:** {PRO_VERSION_VIDEO}", parse_mode='Markdown')
        
        # Описание преимуществ PRO
        pro_features = (
            "🔥 **OVERLORD AI INK PRO** - **Полная Версия с 30+ уникальными стилями!**\n\n"
            "**Отличия от бесплатной версии:**\n"
            "✅ 30+ уникальных моделей стилей\n"
            "✅ Быстрые генерации. В 4 раза быстрее\n"
            "✅ Создание собственных стилей\n"
            "✅ Приоритетные обновления\n"
            "✅ Множество рабочих промтов\n\n"
            "**Полный контроль над генерацией!**\n\n"
            "*создатель - https://t.me/gurovlad*"
        )
        await query.message.reply_text(pro_features, parse_mode='Markdown')

        # Отправка PRO GIF с инлайн-кнопкой
        pro_gif_path = os.path.join("static", "9d.gif")
        try:
            with open(pro_gif_path, "rb") as pro_gif_file:
                keyboard_pro = [
                    [InlineKeyboardButton("🔥 Оформить PRO", url=TRIBUT_URL)]
                ]
                reply_markup_pro = InlineKeyboardMarkup(keyboard_pro)
                
                await query.message.reply_animation(
                    animation=InputFile(pro_gif_file),
                    caption="🔥 **PRO версия открывает новые возможности генерации!**",
                    reply_markup=reply_markup_pro,
                    parse_mode='Markdown'
                )
        except FileNotFoundError:
            keyboard_pro = [
                [InlineKeyboardButton("🔥 Оформить PRO", url=TRIBUT_URL)]
            ]
            reply_markup_pro = InlineKeyboardMarkup(keyboard_pro)
            await query.message.reply_text(
                "🔥 **PRO версия открывает новые возможности генерации!**",
                reply_markup=reply_markup_pro,
                parse_mode='Markdown'
            )

        # Кнопки для возврата
        keyboard = [
            [InlineKeyboardButton("Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("**Выберите действие:**", reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Ошибка в pro_version: {str(e)}")

async def ikona_main(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Главная страница обучения IKONA"""
    try:
        query = update.callback_query
        await query.answer()
        
        # Отправка видео
        await query.message.reply_text(f"🎬 **Обучение Тату IKONA:** {IKONA_MAIN_VIDEO}", parse_mode='Markdown')
        
        # Основной текст
        ikona_text = (
            "🎨 **ОБУЧЕНИЕ ТАТУ IKONA**\n\n"
            "Обучения Икона создана для тех, кто хочет сразу начать колоть **СТИЛЬ** и быстро ворваться в индустрию и занять свое место!\n\n"
            "Мы предоставляем программу обучения в которой мы создадим собственный стиль эскизов для татуировок и оточим до идеала нанесение его на кожу!\n\n"
            "Это позволяет нашим ученикам уже во время обучения начинать привлекать клиентов и быстро развивать свои соц.сети с чем мы тоже поможем!\n\n"
            "**Выбери программу которая тебе больше подходит!**"
        )
        await query.message.reply_text(ikona_text, parse_mode='Markdown')
        
        # Кнопки выбора программы
        keyboard = [
            [InlineKeyboardButton("Оффлайн обучение IKONA в Москве и Питере", callback_data="ikona_offline")],
            [InlineKeyboardButton("Онлайн обучение IKONA", callback_data="ikona_online")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("**Выберите формат обучения:**", reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Ошибка в ikona_main: {str(e)}")

async def ikona_offline(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Информация об оффлайн обучении IKONA"""
    try:
        query = update.callback_query
        await query.answer()
        
        # Отправка видео
        await query.message.reply_text(f"🎬 **Оффлайн обучение IKONA:** {IKONA_OFFLINE_VIDEO}", parse_mode='Markdown')
        
        # Описание программы
        offline_text = (
            "🏢 **ОФФЛАЙН ОБУЧЕНИЕ IKONA В МОСКВЕ И ПИТЕРЕ**\n\n"
            "Программа обучения с учителем IKONA действующим тату-мастером включает в себя занятия на искусственной коже и на людях.\n\n"
            "**Что вы получите:**\n"
            "• Создадим собственный стиль при помощи ИИ\n"
            "• Научим его идеально набивать на коже\n"
            "• Практика на искусственной коже и живых моделях\n"
            "• Индивидуальный подход от действующего мастера\n\n"
            "**Срок обучения:** 2 месяца\n"
            "**Стоимость:** 99 000 рублей\n\n"
            "**Приходи на Бесплатный Первый Урок**, где мы подробно все расскажем и дадим набить первую татуировку на искусственной коже! Попробуешь себя в роли Тату-Мастера!"
        )
        await query.message.reply_text(offline_text, parse_mode='Markdown')
        
        # Кнопки
        keyboard = [
            [InlineKeyboardButton("Записаться на Пробный Урок / Обучение", callback_data="ikona_contact")],
            [InlineKeyboardButton("Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("**Выберите действие:**", reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Ошибка в ikona_offline: {str(e)}")

async def ikona_online(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Информация об онлайн обучении IKONA"""
    try:
        query = update.callback_query
        await query.answer()
        
        # Отправка видео
        await query.message.reply_text(f"🎬 **Онлайн обучение IKONA:** {IKONA_ONLINE_VIDEO}", parse_mode='Markdown')
        
        # Описание программы
        online_text = (
            "💻 **ОНЛАЙН ОБУЧЕНИЕ IKONA**\n\n"
            "Программа состоит из блока **Обучение ИИ** и **Онлайн Уроки с Преподавателем**.\n\n"
            "**Что включает программа:**\n"
            "• Обучение ИИ ведется онлайн с преподавателем и онлайн уроками для создания собственного стиля тату\n"
            "• Онлайн уроки по нанесению тату проводятся через видеозвонки\n"
            "• Профессиональная тату машинка со всеми компонентами для домашнего обучения\n"
            "• Помощь в выборе салона в вашем городе\n"
            "• Поиск модели для полноценного сеанса под контролем преподавателя\n\n"
            "**Срок обучения:** 2 месяца\n"
            "**Стоимость:** 79 000 рублей\n\n"
            "Этого достаточно чтобы правильно поставить руку и передать все важные знания!"
        )
        await query.message.reply_text(online_text, parse_mode='Markdown')
        
        # Кнопки
        keyboard = [
            [InlineKeyboardButton("Подробнее / Записаться", callback_data="ikona_contact")],
            [InlineKeyboardButton("Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("**Выберите действие:**", reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Ошибка в ikona_online: {str(e)}")

async def ikona_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Контактная информация для записи на обучение IKONA"""
    try:
        query = update.callback_query
        await query.answer()
        
        contact_text = (
            "📞 **ЗАПИСЬ НА ОБУЧЕНИЕ**\n\n"
            "Для записи на пробный урок / Записаться на обучение / Подробнее об Обучении напишите сюда с выбранным вами пожеланием:\n\n"
            "**@vladguro**\n\n"
            "Вам ответят в ближайшее время!"
        )
        await query.message.reply_text(contact_text, parse_mode='Markdown')
        
        # Кнопка возврата
        keyboard = [
            [InlineKeyboardButton("Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("**Выберите действие:**", reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Ошибка в ikona_contact: {str(e)}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка текстовых сообщений"""
    try:
        await update.message.reply_text("**Пожалуйста, используйте кнопки меню**", parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Ошибка в handle_text: {str(e)}")

def main() -> None:
    """Запуск бота"""
    try:
        application = Application.builder().token(TOKEN).build()
        
        # Обработчики команд
        application.add_handler(CommandHandler("start", start))
        
        # Обработчики callback-запросов
        application.add_handler(CallbackQueryHandler(show_prompt, pattern="^show_prompt$"))
        application.add_handler(CallbackQueryHandler(main_menu, pattern="^main_menu$"))
        application.add_handler(CallbackQueryHandler(free_train, pattern="^free_train$"))
        application.add_handler(CallbackQueryHandler(pro_version, pattern="^pro_version$"))
        application.add_handler(CallbackQueryHandler(ikona_main, pattern="^ikona_main$"))
        application.add_handler(CallbackQueryHandler(ikona_offline, pattern="^ikona_offline$"))
        application.add_handler(CallbackQueryHandler(ikona_online, pattern="^ikona_online$"))
        application.add_handler(CallbackQueryHandler(ikona_contact, pattern="^ikona_contact$"))
        
        # Обработчик текстовых сообщений
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
        
        logger.info("Бот запускается...")
        application.run_polling()
        
    except Exception as e:
        logger.critical(f"Ошибка запуска бота: {str(e)}")

if __name__ == "__main__":
    main()
