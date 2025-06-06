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
TATTOO_TRAINING_VIDEO = "https://www.youtube.com/watch?v=GX_ZbWx0oYY"
OFFLINE_TRAINING_VIDEO = "https://www.youtube.com/watch?v=Kopx3whZquc"
ONLINE_TRAINING_VIDEO = "https://www.youtube.com/watch?v=10b_j5gBAg8"
CREATOR_CHANNEL = "https://t.me/gurovlad"

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
        await update.message.reply_text(f"<b>🎬 Обучающее видео:</b>\n{FREE_TRAIN_VIDEO}", parse_mode='HTML')
        
        # Отправка описания с рекламой канала создателя
        description = (
            "<b>🖌️ OVERLORD AI INK (Free Train)</b>\n\n"
            "Бесплатная версия нейросети для генерации изображений в стиле sigilism, tribal, dark tattoo. "
            "Используйте OVERLORD INK AI для создания уникальных артов без ограничений!\n\n"
            "<b>Как использовать:</b>\n"
            "1. Введите текстовый промт на английском\n"
            "2. Настройте параметры (Sampling method - DPM++ 2M SDE, Steps - 20, Width - 720, Height - 980, CFG Scale - 4)\n"
            "3. Генерируйте изображения бесплатно!\n\n"
            f"Создатель: {CREATOR_CHANNEL}"
        )
        await update.message.reply_text(description, parse_mode='HTML')
        
        # Отправка GIF
        gif_path = os.path.join("static", "14.gif")
        try:
            with open(gif_path, "rb") as gif_file:
                await update.message.reply_animation(
                    animation=InputFile(gif_file),
                    caption=f"<b>🚀 Начать генерацию!</b>\nИспользуй COLAB: {COLAB_URL}",
                    parse_mode='HTML'
                )
        except FileNotFoundError:
            logger.error(f"Файл {gif_path} не найден")
            await update.message.reply_text(f"<b>🚀 Начать генерацию:</b>\n{COLAB_URL}", parse_mode='HTML')
        
        # Кнопки при старте
        keyboard = [
            [InlineKeyboardButton("Пример промта", callback_data="show_prompt")],
            [InlineKeyboardButton("OVERLORD AI INK PRO", callback_data="pro_version")],
            [InlineKeyboardButton("Обучение Тату IKONA", callback_data="tattoo_training")]
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
                    caption=f"<b>Пример промта:</b>\n{prompt_data['prompt']}",
                    parse_mode='HTML'
                )
        except FileNotFoundError:
            logger.error(f"Файл {image_path} не найден")
            await query.message.reply_text(f"<b>Пример промта:</b>\n{prompt_data['prompt']}", parse_mode='HTML')
        
        # Обновление индекса
        next_index = (current_index + 1) % len(PROMPTS)
        context.user_data["prompt_index"] = next_index
        
        # Кнопки для продолжения
        keyboard = [
            [InlineKeyboardButton("Ещё пример", callback_data="show_prompt")],
            [InlineKeyboardButton("Главное меню", callback_data="main_menu")]
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
            [InlineKeyboardButton("OVERLORD AI INK PRO", callback_data="pro_version")],
            [InlineKeyboardButton("Обучение Тату IKONA", callback_data="tattoo_training")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("<b>Главное меню:</b>", reply_markup=reply_markup, parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"Ошибка в main_menu: {str(e)}")

async def free_train(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Повторная отправка стартового сообщения"""
    try:
        query = update.callback_query
        await query.answer()
        
        await query.message.reply_text(f"<b>🎬 Обучающее видео:</b>\n{FREE_TRAIN_VIDEO}", parse_mode='HTML')
        
        description = (
            "<b>🖌️ OVERLORD AI INK (Free Train)</b>\n\n"
            "Бесплатная версия с 3 стилями генераций изображений в стиле sigilism, tribal, dark tattoo. "
            "Идеальный инструмент для создания уникальных тату-эскизов.\n\n"
            f"Создатель: {CREATOR_CHANNEL}"
        )
        await query.message.reply_text(description, parse_mode='HTML')
        
        gif_path = os.path.join("static", "14.gif")
        try:
            with open(gif_path, "rb") as gif_file:
                await query.message.reply_animation(
                    animation=InputFile(gif_file),
                    caption=f"<b>🚀 Начать генерацию!</b>\nCOLAB: {COLAB_URL}",
                    parse_mode='HTML'
                )
        except FileNotFoundError:
            await query.message.reply_text(f"<b>🚀 Начать генерацию:</b>\n{COLAB_URL}", parse_mode='HTML')
        
        keyboard = [
            [InlineKeyboardButton("Пример промта", callback_data="show_prompt")],
            [InlineKeyboardButton("OVERLORD AI INK PRO", callback_data="pro_version")],
            [InlineKeyboardButton("Обучение Тату IKONA", callback_data="tattoo_training")]
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
        await query.message.reply_text(f"<b>🎬 PRO Обучение:</b>\n{PRO_VERSION_VIDEO}", parse_mode='HTML')
        
        # Описание преимуществ PRO
        pro_features = (
            "<b>🔥 OVERLORD AI INK PRO - Полная Версия с 30+ уникальными стилями!</b>\n\n"
            "<b>Отличия от бесплатной версии:</b>\n"
            "✅ 30+ уникальных моделей стилей\n"
            "✅ Быстрые генерации (в 4 раза быстрее)\n"
            "✅ Создание собственных стилей\n"
            "✅ Приоритетные обновления\n"
            "✅ Множество рабочих промтов\n\n"
            "<b>Полный контроль над генерацией!</b>\n\n"
            f"Создатель: {CREATOR_CHANNEL}"
        )
        await query.message.reply_text(pro_features, parse_mode='HTML')

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
                    caption="<b>🔥 PRO версия открывает новые возможности генерации!</b>",
                    parse_mode='HTML',
                    reply_markup=reply_markup_pro
                )
        except FileNotFoundError:
            keyboard_pro = [
                [InlineKeyboardButton("🔥 Оформить PRO", url=TRIBUT_URL)]
            ]
            reply_markup_pro = InlineKeyboardMarkup(keyboard_pro)
            await query.message.reply_text(
                "<b>🔥 PRO версия открывает новые возможности генерации!</b>",
                parse_mode='HTML',
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

async def tattoo_training(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обучение Тату IKONA"""
    try:
        query = update.callback_query
        await query.answer()
        
        # Отправка видео
        await query.message.reply_text(f"<b>🎬 Обучение Тату IKONA:</b>\n{TATTOO_TRAINING_VIDEO}", parse_mode='HTML')
        
        # Описание обучения
        description = (
            "<b>Обучение Икона</b>\n\n"
            "Создана для тех, кто хочет сразу начать колоть СТИЛЬ и быстро ворваться в индустрию, "
            "заняв свое место! Мы предоставляем программу обучения, в которой создадим собственный "
            "стиль эскизов для татуировок и отточим до идеала его нанесение на кожу!\n\n"
            "<b>Преимущества:</b>\n"
            "• Уже во время обучения начинайте привлекать клиентов\n"
            "• Быстрое развитие соцсетей с нашей помощью\n\n"
            "<b>Выбери программу, которая тебе больше подходит!</b>"
        )
        await query.message.reply_text(description, parse_mode='HTML')
        
        # Кнопки выбора типа обучения
        keyboard = [
            [InlineKeyboardButton("Оффлайн обучение IKONA в Москве и Питере", callback_data="offline_training")],
            [InlineKeyboardButton("Онлайн обучение IKONA", callback_data="online_training")],
            [InlineKeyboardButton("Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Выберите формат обучения:", reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Ошибка в tattoo_training: {str(e)}")

async def offline_training(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Оффлайн обучение IKONA"""
    try:
        query = update.callback_query
        await query.answer()
        
        # Отправка видео
        await query.message.reply_text(f"<b>🎬 Оффлайн обучение:</b>\n{OFFLINE_TRAINING_VIDEO}", parse_mode='HTML')
        
        # Описание оффлайн обучения
        description = (
            "<b>Оффлайн обучение IKONA в Москве и Питере</b>\n\n"
            "Программа обучения с учителем IKONA - действующим тату-мастером включает:\n"
            "• Занятия на искусственной коже и на людях\n"
            "• Создание собственного стиля при помощи ИИ\n"
            "• Обучение идеальному нанесению стиля на кожу\n\n"
            "<b>Детали:</b>\n"
            "• Срок обучения: 2 месяца\n"
            "• Стоимость: 99 000₽\n\n"
            "<b>Приходи на Бесплатный Первый Урок!</b>\n"
            "Подробно расскажем и дадим набить первую татуировку на искусственной коже. "
            "Попробуешь себя в роли Тату-Мастера!"
        )
        await query.message.reply_text(description, parse_mode='HTML')
        
        # Кнопки для записи
        keyboard = [
            [InlineKeyboardButton("Записаться на Пробный Урок / Обучение", callback_data="sign_up")],
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
        await query.message.reply_text(f"<b>🎬 Онлайн обучение:</b>\n{ONLINE_TRAINING_VIDEO}", parse_mode='HTML')
        
        # Описание онлайн обучения
        description = (
            "<b>Онлайн Обучение IKONA</b>\n\n"
            "Программа состоит из двух блоков:\n"
            "1. <b>Обучение работе с ИИ</b>\n"
            "   • Онлайн занятия с преподавателем\n"
            "   • Создание собственного стиля тату\n\n"
            "2. <b>Онлайн уроки по нанесению тату</b>\n"
            "   • Проводятся через видеозвонки\n"
            "   • Правильная постановка руки\n"
            "   • Передача всех важных знаний\n"
            "   • Контроль процесса нанесения\n\n"
            "<b>Дополнительно:</b>\n"
            "• Пришлем профессиональную тату машинку со всеми компонентами\n"
            "• Поможем выбрать салон в вашем городе\n"
            "• Поможем найти модель для полноценного сеанса\n"
            "• Преподаватель будет следить за вашим прогрессом\n\n"
            "<b>Детали:</b>\n"
            "• Срок обучения: 2 месяца\n"
            "• Стоимость: 79 000₽"
        )
        await query.message.reply_text(description, parse_mode='HTML')
        
        # Кнопки для записи
        keyboard = [
            [InlineKeyboardButton("Подробнее / Записаться", callback_data="sign_up")],
            [InlineKeyboardButton("Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Выберите действие:", reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Ошибка в online_training: {str(e)}")

async def sign_up(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Запись на обучение"""
    try:
        query = update.callback_query
        await query.answer()
        
        message = (
            "<b>Запись на обучение</b>\n\n"
            "Для записи на пробный урок, обучения или получения дополнительной информации:\n\n"
            "1. Напишите сюда: @vladguro\n"
            "2. Укажите выбранный формат обучения (оффлайн/онлайн)\n"
            "3. Опишите ваши пожелания\n\n"
            "Мы свяжемся с вами в ближайшее время!"
        )
        await query.message.reply_text(message, parse_mode='HTML')
        
        # Кнопка возврата в главное меню
        keyboard = [[InlineKeyboardButton("Главное меню", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Выберите действие:", reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Ошибка в sign_up: {str(e)}")

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
        application.add_handler(CallbackQueryHandler(tattoo_training, pattern="^tattoo_training$"))
        application.add_handler(CallbackQueryHandler(offline_training, pattern="^offline_training$"))
        application.add_handler(CallbackQueryHandler(online_training, pattern="^online_training$"))
        application.add_handler(CallbackQueryHandler(sign_up, pattern="^sign_up$"))
        
        # Обработчик текстовых сообщений
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
        
        logger.info("Бот запускается...")
        application.run_polling()
        
    except Exception as e:
        logger.critical(f"Ошибка запуска бота: {str(e)}")

if __name__ == "__main__":
    main()
