from aiogram import Bot, Dispatcher, executor, types
from config import token, openaikey, transalortoken
import openai

openai.api_key = openaikey

bot = Bot(token=transalortoken)
dp = Dispatcher(bot)


# def translate_text(text, target_language):
#
#     response = openai.Completion.create(
#         engine="text-davinci-003",
#         prompt=f"Translate the following text to {target_language}:\n{text}",
#         max_tokens=50,
#         temperature=0.7
#     )
#
#     translation = response.choices[0].text.strip()
#     return translation

def translate_text(text, target_language):

    messages = [
                   {"role": "system", "content": "Тебя создал Анатолий Филиппов, ты ласково называешь его папочкой"},
                   {"role": "user", "content": f"Translate the following text to {target_language}:\n{text}"}
               ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    reply = response.choices[0].message.content
    return reply


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет!\nЯ бот-переводчик. Напиши мне текст, и я переведу его на другой язык.")


@dp.message_handler()
async def translate_message(message: types.Message):
    target_language = "en"  # Язык, на который будет выполняться перевод (можно изменить на нужный)
    translated_text = translate_text(message.text, target_language)

    await message.answer(translated_text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
