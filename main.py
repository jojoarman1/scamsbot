import sqlite3
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, InputMediaPhoto
from aiogram.dispatcher.filters import Command
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from localization import get_translation

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Токен вашего бота
API_TOKEN = '7535068571:AAE43ounQIYIFfH3XP0784DguusvmPx1ApQ'

# ID администратора
ADMIN_IDS = [735291377, 5429082466]  # Замените на ваши ID

# Глобальная переменная для хранения ID сообщений бота
bot_message_ids = []

# Создаем объект бота и диспетчера с хранилищем состояния
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

# Создаем подключение к базе данных SQLite
conn = sqlite3.connect('scam_bot_users.db')
cursor = conn.cursor()

# Создаем таблицу для хранения пользователей
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT
)
''')

conn.commit()


# Состояния для FSM
class AdminState(StatesGroup):
    waiting_for_message = State()


# Проверка, является ли пользователь администратором
def is_admin(user_id):
    return user_id in ADMIN_IDS


@dp.message_handler(commands=['scam'])
async def scam_command(message: types.Message):
    logging.info(f"Received /scam command from user: {message.from_user.id}")
    await delete_previous_bot_messages(message.chat.id)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await send_message(message)


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    logging.info(f"Received /start command from user: {message.from_user.id}")
    await delete_previous_bot_messages(message.chat.id)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await send_message(message)


# Удаление всех предыдущих сообщений бота
async def delete_previous_bot_messages(chat_id):
    global bot_message_ids  # Используем глобальную переменную
    for message_id in bot_message_ids:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception as e:
            logging.warning(f"Не удалось удалить сообщение: {e}")
    bot_message_ids = []  # Очищаем список после удаления сообщений


# Добавление вызова с username
def initialize_db():
    with sqlite3.connect('scam_bot_users.db') as conn:
        cursor = conn.cursor()
        # Удаляем таблицу, если она существует, для пересоздания с новой структурой
        cursor.execute('DROP TABLE IF EXISTS users')
        # Создаем таблицу для хранения пользователей с новой колонкой
        cursor.execute('''
        CREATE TABLE users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            language TEXT
        )
        ''')
        conn.commit()


initialize_db()


# Функция для добавления пользователя в базу данных
async def add_user(user_id, username, language='en'):
    with sqlite3.connect('scam_bot_users.db') as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO users (user_id, username, language) VALUES (?, ?, ?)',
                       (user_id, username if username else "No username", language))
        conn.commit()
        logging.info(f"Added/Updated user: ID={user_id}, Username={username}, Language={language}")


# Добавление вызова с username
async def send_message(message: types.Message):
    global bot_message_ids

    # Получаем язык пользователя из базы данных
    user_id = message.from_user.id
    with sqlite3.connect('scam_bot_users.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT language FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        language = row[0] if row else 'en'

    await add_user(user_id, message.from_user.username, language)
    logging.info(f"User ID: {user_id}, Language retrieved: {language}")

    # Удаляем сообщение пользователя
    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except Exception as e:
        if "message to delete not found" in str(e).lower():
            logging.warning(f"Сообщение пользователя не найдено для удаления: {e}")
        else:
            logging.error(f"Ошибка при удалении сообщения пользователя: {e}")

    # Создаем кнопки
    webapp_button = InlineKeyboardButton(
        text="SCAM$",
        web_app=WebAppInfo(url="https://chachacode.github.io/SCAMSOON/")
    )
    url_button = InlineKeyboardButton(
        text="Join SCAM$ community",
        url="t.me/scamcoin_en"
    )
    markup = InlineKeyboardMarkup().add(webapp_button, url_button)

    # Отправляем сообщение с изображением и кнопками
    with open('start.png', 'rb') as photo:
        caption = get_translation(language, 'welcome_message')
        logging.info(f"Caption to send: {caption}")
        sent_message = await bot.send_photo(
            chat_id=message.chat.id,
            photo=photo,
            caption=caption,
            reply_markup=markup
        )
        bot_message_ids.append(sent_message.message_id)


# Обработчик команды /scam1337 для администратора
@dp.message_handler(Command('scam1337'), state='*')
async def scam1337_command(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("У вас нет прав для использования этой команды.")
        return

    # Удаляем все предыдущие сообщения бота
    await delete_previous_bot_messages(message.chat.id)

    # Удаляем команду от пользователя
    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except Exception as e:
        logging.warning(f"Не удалось удалить сообщение пользователя: {e}")

    # Создаем инлайн-кнопки
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("Отправить сообщение", callback_data='send_post'),
        InlineKeyboardButton("Пользователи SCAM$", callback_data='scam_users'),
        InlineKeyboardButton("Закрыть", callback_data='close')
    )

    # Отправляем сообщение с фото и кнопками
    with open('adminpannel.png', 'rb') as photo:  # Замените на путь к вашему файлу
        sent_message = await bot.send_photo(
            chat_id=message.chat.id,
            photo=photo,
            caption="Добро пожаловать в Администрацию бота SCAM$",
            reply_markup=markup
        )

    # Сохраняем ID отправленного сообщения
    bot_message_ids.append(sent_message.message_id)


# Обработчик нажатия на инлайн-кнопки
@dp.callback_query_handler(lambda c: c.data)
async def process_callback_button(callback_query: types.CallbackQuery):
    if callback_query.data == 'send_post':
        await bot.send_message(callback_query.message.chat.id, "Функция 'Отправить пост' пока не реализована.")
    elif callback_query.data == 'scam_users':
        with sqlite3.connect('scam_bot_users.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT user_id, username FROM users')
            rows = cursor.fetchall()

            # Формируем список пользователей
            user_list = "\n".join([f"@{row[1]} , *ID:* {row[0]}" for row in rows])

        # Создаем кнопки для возврата в админпанель
        back_button = InlineKeyboardButton("Назад", callback_data='back_to_admin')
        markup = InlineKeyboardMarkup().add(back_button)

        # Редактируем старое сообщение, добавляя изображение и список пользователей
        with open('users.png', 'rb') as photo:  # Замените на путь к вашему файлу
            await bot.edit_message_media(
                media=InputMediaPhoto(photo, caption=f"*Пользователи SCAM$:*\n{user_list}", parse_mode='MarkdownV2'),
                chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.message_id,
                reply_markup=markup
            )

    elif callback_query.data == 'back_to_admin':
        # Возврат в админпанель
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("Отправить пост", callback_data='send_post'),
            InlineKeyboardButton("Пользователи SCAM$", callback_data='scam_users'),
            InlineKeyboardButton("Закрыть", callback_data='close')
        )

        # Редактируем старое сообщение, возвращаясь к админпанели
        with open('adminpannel.png', 'rb') as photo:  # Замените на путь к вашему файлу
            await bot.edit_message_media(
                media=InputMediaPhoto(photo, caption="Добро пожаловать в Администрацию бота SCAM$"),
                chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.message_id,
                reply_markup=markup
            )

    elif callback_query.data == 'close':
        await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)

    # Подтверждение обработки колбэка
    await bot.answer_callback_query(callback_query.id)


# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
