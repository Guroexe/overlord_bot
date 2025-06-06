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
IKONA_TRAINING_VIDEO = "https://www.youtube.com/watch?v=GX_ZbWx0oYY"
OFFLINE_TRAINING_VIDEO = "https://www.youtube.com/watch?v=Kopx3whZquc"
ONLINE_TRAINING_VIDEO = "https://www.youtube.com/watch?v=10b_j5gBAg8"

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
        await update.message.reply_text(f"🎬 Обучающее видео: {FREE_TRAIN_VIDEO}")
        
        # Отправка описания
        description = (
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
        )
        await update.message.reply_text(description, parse_mode='Markdown')
        
        # Отправка GIF
        gif_path = os.path.join("static", "14.gif")
        try:
            with open(gif_path, "rb") as gif_file:
                await update.message.reply_animation(
                    animation=InputFile(gif_file),
                    caption=f"🚀 Начать генерацию! Используй COLAB: {COLAB_URL}"
                )
        except FileNotFoundError:
            logger.error(f"Файл {gif_path} не найден")
            await update.message.reply_text(f"🚀 Начать генерацию: {COLAB_URL}")
        
        # Кнопки при старте
        keyboard = [
            [
                InlineKeyboardButton("Пример промта", callback_data="show_prompt"),
                InlineKeyboardButton("ПОЛНАЯ ВЕРСИЯ OVERLORD INK AI PRO +", callback_data="pro_version")
            ],
            [
                InlineKeyboardButton("Обучение Тату IKONA", callback_data="ikona_training")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)
        
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
                    caption=prompt_data["prompt"]
                )
        except FileNotFoundError:
            logger.error(f"Файл {image_path} не найден")
            await query.message.reply_text(prompt_data["prompt"])
        
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
        await query.message.reply_text("Что дальше?", reply_markup=reply_markup)
        
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
            [InlineKeyboardButton("ПОЛНАЯ ВЕРСИЯ OVERLORD INK AI PRO +", callback_data="pro_version")],
            [InlineKeyboardButton("Обучение Тату IKONA", callback_data="ikona_training")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("**ГЛАВНОЕ МЕНЮ:**", reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Ошибка в main_menu: {str(e)}")

async def free_train(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Повторная отправка стартового сообщения"""
    try:
        query = update.callback_query
        await query.answer()
        
        await query.message.reply_text(f"🎬 Обучающее видео: {FREE_TRAIN_VIDEO}")
        
        description = (
            "🖌️ **OVERLORD AI INK (Free Train)**\n\n"
            "**Бесплатная версия** с 3 стилями генераций изображений...\n\n"
            "*(создатель - https://t.me/gurovlad)*"
        )
        await query.message.reply_text(description, parse_mode='Markdown')
        
        gif_path = os.path.join("static", "14.gif")
        try:
            with open(gif_path, "rb") as gif_file:
                await query.message.reply_animation(
                    animation=InputFile(gif_file),
                    caption=f"🚀 Начать генерацию! COLAB: {COLAB_URL}"
                )
        except FileNotFoundError:
            await query.message.reply_text(f"🚀 Начать генерацию: {COLAB_URL}")
        
        keyboard = [
            [
                InlineKeyboardButton("Пример промта", callback_data="show_prompt"),
                InlineKeyboardButton("ПОЛНАЯ ВЕРСИЯ OVERLORD INK AI PRO +", callback_data="pro_version")
            ],
            [
                InlineKeyboardButton("Обучение Тату IKONA", callback_data="ikona_training")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Выберите действие:", reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Ошибка в free_train: {str(e)}")

async def pro_version(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Информация о PRO версии"""
    try:
        query = update.callback_query
        await query.answer()
        
        # Отправка PRO видео
        await query.message.reply_text(f"🎬 PRO Обучение: {PRO_VERSION_VIDEO}")
        
        # Описание преимуществ PRO
        pro_features = (
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
                    caption="🔥 PRO версия открывает новые возможности генерации!",
                    reply_markup=reply_markup_pro
                )
        except FileNotFoundError:
            keyboard_pro = [
                [InlineKeyboardButton("🔥 Оформить PRO", url=TRIBUT_URL)]
            ]
            reply_markup_pro = InlineKeyboardMarkup(keyboard_pro)
            await query.message.reply_text(
                "🔥 PRO версия открывает новые возможности генерации!",
                reply_markup=reply_markup_pro
            )

        # Кнопки для возврата
        keyboard = [
            [InlineKeyboardButton("Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Выберите действие:", reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Ошибка в pro_version: {str(e)}")

async def ikona_training(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обучение Тату IKONA"""
    try:
        query = update.callback_query
        await query.answer()
        
        # Отправка видео
        await query.message.reply_text(f"🎬 Обучение IKONA: {IKONA_TRAINING_VIDEO}")
        
        # Описание обучения
        description = (
            "**ОБУЧЕНИЕ ТАТУ IKONA**\n\n"
            "Обучение создано для тех, кто хочет **сразу начать колоть СТИЛЬ** и быстро ворваться в индустрию и занять свое место!\n\n"
            "**ЧТО МЫ ПРЕДОСТАВЛЯЕМ:**\n\n"
            "🎯 Программу обучения с созданием **собственного стиля эскизов**\n"
            "🎯 Отточим до идеала **нанесение на кожу**\n"
            "🎯 Поможем **привлекать клиентов** уже во время обучения\n"
            "🎯 Развитие **социальных сетей**\n\n"
            "**ВЫБЕРИТЕ ПРОГРАММУ, КОТОРАЯ ВАМ БОЛЬШЕ ПОДХОДИТ:**"
        )
        await query.message.reply_text(description, parse_mode='Markdown')
        
        # Кнопки выбора программы
        keyboard = [
            [InlineKeyboardButton("Оффлайн обучение IKONA в Москве и Питере", callback_data="offline_training")],
            [InlineKeyboardButton("Онлайн обучение IKONA", callback_data="online_training")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Выберите формат обучения:", reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Ошибка в ikona_training: {str(e)}")

async def offline_training(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Оффлайн обучение IKONA"""
    try:
        query = update.callback_query
        await query.answer()
        
        # Отправка видео
        await query.message.reply_text(f"🎬 Оффлайн обучение: {OFFLINE_TRAINING_VIDEO}")
        
        # Описание оффлайн обучения
        description = (
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
        )
        await query.message.reply_text(description, parse_mode='Markdown')
        
        # Кнопки
        keyboard = [
            [InlineKeyboardButton("Записаться на Пробный Урок / Обучение", callback_data="contact_for_trial")],
            [InlineKeyboardButton("Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Выберите действие:", reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Ошибка в offline_training: {str(e)}")

async def online_training(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Онлайн обучение IKONA"""
    try:
        query = update.callback_query
        await query.answer()
        
        # Отправка видео
        await query.message.reply_text(f"🎬 Онлайн обучение: {ONLINE_TRAINING_VIDEO}")
        
        # Описание онлайн обучения
        description = (
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
        )
        await query.message.reply_text(description, parse_mode='Markdown')
        
        # Кнопки
        keyboard = [
            [InlineKeyboardButton("Подробнее / Записаться", callback_data="contact_for_details")],
            [InlineKeyboardButton("Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Выберите действие:", reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Ошибка в online_training: {str(e)}")

async def contact_for_trial(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Контакт для записи на пробный урок"""
    try:
        query = update.callback_query
        await query.answer()
        
        contact_text = (
            "**ЗАПИСЬ НА ПРОБНЫЙ УРОК / ОБУЧЕНИЕ**\n\n"
            "Для записи на пробный урок, обучение или получения подробной информации напишите с указанием вашего пожелания:\n\n"
            "👤 **@vladguro**\n\n"
            "**Ответим в ближайшее время!**"
        )
        await query.message.reply_text(contact_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Ошибка в contact_for_trial: {str(e)}")

async def contact_for_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Контакт для подробностей"""
    try:
        query = update.callback_query
        await query.answer()
        
        contact_text = (
            "**ПОДРОБНЕЕ / ЗАПИСАТЬСЯ**\n\n"
            "Для записи на обучение или получения подробной информации напишите с указанием вашего пожелания:\n\n"
            "👤 **@vladguro**\n\n"
            "**Ответим в ближайшее время!**"
        )
        await query.message.reply_text(contact_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Ошибка в contact_for_details: {str(e)}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка текстовых сообщений"""
    try:
        await update.message.reply_text("Пожалуйста, используйте кнопки меню")
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
