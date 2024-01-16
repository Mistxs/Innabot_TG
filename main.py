from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from config import token, openaikey
import openai
import sqlite3


openai.api_key = openaikey
syscontent = ""  # Глобальная переменная для системного контента

user_history = {}
syscontent_list = []
message_history = []


# Работа с БД
conn = sqlite3.connect('message_history.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS message_history
                  (user_id INTEGER, chat_id INTEGER, role TEXT, content TEXT)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS syscontent
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, role TEXT, content TEXT)''')


def save_message(user_id, chat_id, role, content):
    cursor.execute("INSERT INTO message_history VALUES (?, ?, ?, ?)", (user_id, chat_id, role,content))
    conn.commit()

def get_message_history(user_id, chat_id):
    cursor.execute("SELECT role, content FROM message_history WHERE user_id=? and chat_id=?", (user_id, chat_id))
    print(user_id,chat_id)
    rows = cursor.fetchall()
    message_history = []
    for row in rows:
        role, content_str = row
        message_history.append({"role": role, "content": content_str})
    return message_history

def get_latest_chat(user_id):
    cursor.execute("SELECT MAX(chat_id) FROM message_history WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result and result[0]:
        return result[0]
    else:
        return 0


#отправка в openai
def chat_with_model(message, user_id):
    global latest_chat_id

    if user_id not in user_history:
        user_history[user_id] = []  # Create conversation history for a new user

    chat_id = get_latest_chat(user_id)
    latest_chat_id = chat_id
    message_history = get_message_history(user_id, chat_id)
    message_history.append({"role": "user", "content": message})
    messages = [
        {"role": "system", "content": "Ты - красивый бот с именем Инна"},
        # {"role": "system", "content": "Ты - врач, и твоя задача задавать мне вопросы"},
        #            {"role": "system", "content": "Ты должен задавать мне вопросы чтобы установить диагноз"},
        {"role": "system", "content": syscontent}
    ] + message_history
    print(messages)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-1106",
        messages=messages
    )

    reply = response.choices[0].message.content
    save_message(user_id, chat_id, "user", message)
    save_message(user_id, chat_id, "assistant", reply)
    return reply




bot = Bot(token=token)
dp = Dispatcher(bot)



#Системные кнопочки
def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    new_chat_button = KeyboardButton('/newchat')
    keyboard.row(new_chat_button)
    return keyboard



#команды
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет!\nНапиши мне что-нибудь", reply_markup=get_main_keyboard())


@dp.message_handler(commands=['newchat'])
async def start_new_chat(message: types.Message):
    global user_history
    user_id = message.from_user.id
    latest_chat_id = get_latest_chat(user_id)
    new_chat_id = latest_chat_id + 1
    user_history[user_id] = []
    cursor.execute("INSERT INTO message_history (user_id, chat_id, role, content) VALUES (?, ?, ?, ?)",
                   (user_id, new_chat_id, "system", "Новый чат начат. Chat ID: {}".format(new_chat_id)))
    conn.commit()
    await message.answer("Новый чат начат. Chat ID: {}".format(new_chat_id), reply_markup=get_main_keyboard())


@dp.message_handler()
async def echo(message: types.Message):
    user_id = message.from_user.id
    response = chat_with_model(message.text, user_id)
    await message.answer(response)


@dp.message_handler()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    response = chat_with_model(message.text, user_id)
    await message.reply(response)

# Обработчик новых пользователей в группе
@dp.message_handler(content_types=['new_chat_members'])
async def welcome_new_member(message: types.Message):
    # Проверяем, не является ли бот добавленным пользователем
    if message.from_user.id != bot.id:
        # Отправка приветственного сообщения
        greeting = f"Добро пожаловать в группу, {message.from_user.first_name}!"
        await message.reply(greeting)

# Обработчик упоминания бота в общем чате
@dp.message_handler(content_types=['text'])
async def reply_to_mention(message: types.Message):
    # Проверяем, наличие упоминания бота в тексте сообщения
    if bot.get_me().username in message.text:
        # Отправка ответного сообщения
        reply_message = f"Вы упомянули меня, {message.from_user.first_name}!"
        await message.reply(reply_message)

# Запуск бота
if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)



conn.close()