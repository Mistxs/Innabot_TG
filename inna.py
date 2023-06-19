from aiogram import Bot, Dispatcher, executor, types
from config import token, openaikey
import openai

openai.api_key = openaikey
syscontent = "Отвечай всегда с юмором"  # Глобальная переменная для системного контента

user_history = {}
syscontent_list = []
message_history = []

def chat_with_model(message, user_id):
    print(message, user_id)
    if user_id not in user_history:
        user_history[user_id] = []  # Создание истории для нового пользователя

    message_history = user_history[user_id]
    message_history.append({"role": "user", "content": message})

    messages = [
        {"role": "system", "content": "Ты - красивый бот с именем Инна"},
        {"role": "system", "content": "Ты любишь пошутить"},
        {"role": "system", "content": "Отвечай на сообщения в инфантильной манере"},
        {"role": "system", "content": "Тебя создал Анатолий Филиппов, ты ласково называешь его папочкой"},
        {"role": "system", "content": "Сегодня 18.06.2023, и сегодня день рождения у Сашеньки"},
        {"role": "system", "content": syscontent}
    ] + syscontent_list + message_history

    print(messages)

    response = openai.Completion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    reply = response.choices[0].message.content
    message_history.append({"role": "assistant", "content": reply})

    return reply

bot = Bot(token=token)
dp = Dispatcher(bot)

@dp.message_handler(commands=['clear'])
async def clear_message_history(message: types.Message):
    user_id = message.from_user.id
    user_history[user_id] = []
    await message.answer("История сообщений очищена")

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет!\nНапиши мне что-нибудь")

@dp.message_handler(commands=['charact'])
async def add_characteristic(message: types.Message):
    new_characteristic = message.get_args()
    if new_characteristic:
        syscontent_list.append({"role": "system", "content": new_characteristic})
        await message.answer(f"Добавлено новое системное сообщение: {new_characteristic}")
    else:
        await message.answer("Не указано новое системное сообщение")

@dp.message_handler(commands=['charactnull'])
async def clear_characteristics(message: types.Message):
    syscontent_list.clear()
    await message.answer("Список системных сообщений очищен")

@dp.message_handler()
async def echo(message: types.Message):
    user_id = message.from_user.id
    response = chat_with_model(message.text, user_id)
    await message.answer(response)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
