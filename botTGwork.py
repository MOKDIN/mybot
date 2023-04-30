import asyncio
from typing import Optional
import openai
import logging
import markups as nav
from aiogram import Bot, Dispatcher, types
from config import OPENAI_API_KEY, TELEGRAM_BOT_TOKEN
from io import BytesIO
import aiohttp
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.handler import SkipHandler
from html import escape
import hashlib
import time
from aiohttp import web
from aiogram.types import ContentTypes
import pytesseract
from PIL import Image, ImageEnhance
from aiogram.types import InputFile
import os
from pydub import AudioSegment
import speech_recognition as sr

# Set up the OpenAI API key
openai.api_key = OPENAI_API_KEY
DEEP_AI_API_KEY = "c8005234-5bfa-46f5-a62d-3437f6c5fb01"

# Set up the Telegram bot
bot = Bot(token=TELEGRAM_BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)
CHANNEL_ID = "-1001867967990"
NOTSUB_MESSAGE = "Для доступа к функционалу бота подпишитесь на канал!"


def check_sub_channel(chat_member):
    print(chat_member['status'])
    if chat_member['status'] != 'left':
        return True
    else:
        return False













@dp.message_handler(content_types=['voice'])
async def handle_voice(message: types.Message):
    voice_file = await bot.download_file_by_id(message.voice.file_id)
    ogg_file_path = f"voice_{message.voice.file_id}.ogg"
    wav_file_path = f"voice_{message.voice.file_id}.wav"

    with open(ogg_file_path, 'wb') as f:
        f.write(voice_file.read())

    convert_ogg_to_wav(ogg_file_path, wav_file_path)

    recognized_text = transcribe_audio(wav_file_path)

    # Получить ответ от GPT-3.5-turbo API
    gpt_response = await ai(recognized_text, message.from_user.id)

    await message.reply(gpt_response)

    # Удалить файлы после использования
    os.remove(ogg_file_path)
    os.remove(wav_file_path)


def transcribe_audio(file_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio, language='ru-RU')
        return text
    except sr.UnknownValueError:
        return "Не удалось распознать аудио"
    except sr.RequestError as e:
        return f"Ошибка сервиса распознавания речи: {e}"


@dp.message_handler(content_types=['voice'])
async def handle_voice(message: types.Message):
    voice_file = await bot.download_file_by_id(message.voice.file_id)
    file_path = f"voice_{message.voice.file_id}.ogg"

    with open(file_path, 'wb') as f:
        f.write(voice_file.read())

    # Здесь вам нужно будет преобразовать файл OGG в поддерживаемый формат, например, WAV.

    recognized_text = transcribe_audio(file_path)
    await message.reply(recognized_text)


from pydub import AudioSegment


def convert_ogg_to_wav(ogg_file_path, wav_file_path):
    audio = AudioSegment.from_ogg(ogg_file_path)
    audio.export(wav_file_path, format="wav")


def preprocess_image(image):
    # Изменить размер изображения
    image = image.resize((image.width * 2, image.height * 2), Image.BICUBIC)

    # Увеличить контраст
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2)

    # Повысить яркость
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(1.2)

    return image


def recognize_text(image_data):
    with Image.open(BytesIO(image_data)) as image:
        image = preprocess_image(image)
        recognized_text = pytesseract.image_to_string(image, lang='rus')
    return recognized_text


@dp.message_handler(content_types=types.ContentType.PHOTO)
async def handle_photos(message: types.Message):
    image_file_id = message.photo[-1].file_id
    image_file = await bot.download_file_by_id(image_file_id)

    recognized_text = recognize_text(image_file.read())
    await bot.send_message(message.chat.id, recognized_text)





# Обработчик команды /group
@dp.message_handler(commands=['channel'])
async def group(message: types.Message):
    # Создаем ссылку на группу и отправляем ее пользователю
    group_link = f"https://t.me/postonbottg"
    await message.reply(f"Переход на канал: {group_link}")




# Define the help command handler
@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    help_text = "Привет! Я бот OpenAI и я работаю на модели 3.5 Turbo. Вот что я могу сделать:\n\n" \
                "/start - Начать диалог со мной\n" \
                "/help - Показать эту справку\n" \
                "/weather - Получение прогноза погоды\n" \
                "/news - Получение последних новостей\n" \
                "/translate - переводчик\n" \
                "/define - Определение слова и его значения\n" \
                "/joke - Получение случайной шутки\n" \
                "/fact - Получение случайного факта\n" \
                "/quote - Получение случайной цитаты\n" \
                "/music - Получение песни по названию\n" \
                "/movie - Получение информации о фильме\n\n" \
                "Это только некоторые из команд, которые я могу обрабатывать через телеграм бота. " \
                "Если у вас есть другие запросы, пожалуйста, сообщите мне, и я постараюсь помочь вам."

    await bot.send_message(chat_id=message.chat.id, text=help_text)





# Define the clear command handler
@dp.message_handler(commands=['clear'])
async def clear_context(message: types.Message):
    # Clear the previous context
    openai.api_key = None

    # Send a message to confirm context clear
    await bot.send_message(chat_id=message.chat.id, text="Previous context cleared.")




@dp.callback_query_handler(lambda call: call.data == 'pay_subscription')
async def process_callback_button1(call: types.CallbackQuery):
    await bot.answer_callback_query(call.id)
    await send_invoice(call.message.chat.id)


async def send_invoice(chat_id):
    title = "Премиум подписка на 1 месяц"
    description = "Получите доступ к расширенным возможностям бота: 150 запросов в день и 50 изображений в месяц."
    payload = "subscription_payload"
    provider_token = "390540012:LIVE:33861"
    start_parameter = "subscription"
    currency = "RUB"
    price = 100 * 100  # Умножьте на 100, чтобы конвертировать в копейки
    prices = [types.LabeledPrice(label=title, amount=price)]

    await bot.send_invoice(
        chat_id=chat_id,
        title=title,
        description=description,
        payload=payload,
        provider_token=provider_token,
        start_parameter=start_parameter,
        currency=currency,
        prices=prices,
    )






@dp.message_handler(commands=['premium'])
async def premium_command(message: types.Message):
    text = "Бот позволяет ежедневно бесплатно отправлять до 50 запросов к Open AI для генерации текстов и создавать 3 изображений в месяц. Такой лимит обеспечивает скорость и качество работы.\n\nНужно больше? Подключите премиум-подписку на месяц за 450 руб.\n\nПремиум-подписка включает:\n✅ до 100 текстовых запросов ежедневно;\n✅ до 50 запросов на создание картинок в месяц;\n✅ нет паузы между запросами;\n✅ поддержание высокой скорости работы, даже в период повышенной нагрузки;\n✅ более 50 встроенных текстовых шаблонов (скоро)"
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    button1 = types.InlineKeyboardButton(text="Канал подписки", url="https://t.me/postonbottg")
    button2 = types.InlineKeyboardButton(text="Оплатить подписку", callback_data="pay_subscription")
    button3 = types.InlineKeyboardButton(text="Связаться с поддержкой", url="https://t.me/nikitinno")
    keyboard.add(button1, button2, button3)
    await bot.send_message(chat_id=message.chat.id, text=text, reply_markup=keyboard)


@dp.pre_checkout_query_handler(lambda query: True)
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message_handler(content_types=ContentTypes.SUCCESSFUL_PAYMENT)
async def process_successful_payment(message: types.Message):
    # Здесь вы можете обновить статус подписки пользователя в вашей базе данных
    await bot.send_message(chat_id=message.chat.id, text="Спасибо за оплату! Ваша подписка активирована.")





@dp.message_handler(commands=['profile'])
async def profile_command(message: types.Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    subscription_type = "Стандартная"
    subscription_limit = "Вопросов за сегодня: 0/20\nКартинок за месяц: 1/5"
    if check_sub_channel(await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)):
        subscription_type = "Премиум"
        subscription_limit = "Вопросов за сегодня: 0/100\nКартинок за месяц: 1/50"
    await bot.send_message(chat_id=chat_id,
                           text=f"Тип подписки: {subscription_type} ✔️\n{subscription_limit}\nНужно больше? Подключите премиум-подписку на месяц за 450 руб.\n\nПремиум-подписка включает:\n✅ до 100 запросов к боту ежедневно;\n✅ до 50 запросов на создание картинок в месяц;\n✅ нет паузы между запросами;\n✅ голосовые сообщения;\n✅ поддержание высокой скорости работы, даже в период повышенной нагрузки.\n\nЧтобы подключить, перейдите в раздел /premium")








# Define the start command handler
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if message.chat.type == 'private':
        if check_sub_channel(await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=message.from_user.id)):
            welcome_message = """Привет! 

Этот бот открывает вам доступ к продуктам, таким как ChatGPT для создания текста и DeepAi для генерации изображений.

⚡️ Бот использует ту же модель, что и сайт ChatGPT: gpt-3.5-turbo.

Чатбот умеет:
1. Писать и редактировать тексты
2. Переводить с любого языка на любой
3. Писать и редактировать код
4. Отвечать на вопросы
5. Генерация изображений.

Вы можете общаться с ботом, как с живым собеседником, задавая вопросы на любом языке. Обратите внимание, что иногда бот придумывает факты, а также обладает ограниченными знаниями о событиях после 2021 года.

✉️ Чтобы получить текстовый ответ, просто напишите в чат ваш вопрос.

🌅 Чтобы сгенерировать изображение, начните свой запрос с /generate_image, а затем введите текст. Например: /generate_image зеленое дерево на фоне заката.Запросы для генерации изображений лучше воспринимает на английском языке.

🚀 Помните, что ботом вместе с вами пользуются ещё много людей, он может отвечать с задержкой. Чтобы ускорить ответы, вы можете подписаться на /premium.     v.1.10"""
            await bot.send_message(chat_id=message.chat.id, text=welcome_message, reply_markup=nav.profileKeyboard)
        else:
            await bot.send_message(message.from_user.id, NOTSUB_MESSAGE, reply_markup=nav.checkSubMenu)





@dp.message_handler()
async def bot_message(message: types.Message):
    dp.register_message_handler(bot_message)
    if message.chat.type == 'private':
        if message.text == "СТАРТ":
            await bot.send_message(message.from_user.id, """Привет! 

Этот бот открывает вам доступ к продуктам, таким как ChatGPT для создания текста и DeepAi для генерации изображений.

⚡️ Бот использует ту же модель, что и сайт ChatGPT: gpt-3.5-turbo.

Чатбот умеет:
1. Писать и редактировать тексты
2. Переводить с любого языка на любой
3. Писать и редактировать код
4. Отвечать на вопросы
5. Генерация изображений.

Вы можете общаться с ботом, как с живым собеседником, задавая вопросы на любом языке. Обратите внимание, что иногда бот придумывает факты, а также обладает ограниченными знаниями о событиях после 2021 года.

✉️ Чтобы получить текстовый ответ, просто напишите в чат ваш вопрос.

🌅 Чтобы сгенерировать изображение, начните свой запрос с /generate_image, а затем введите текст. Например: /generate_image зеленое дерево на фоне заката.Запросы для генерации изображений лучше воспринимает на английском языке.

🚀 Помните, что ботом вместе с вами пользуются ещё много людей, он может отвечать с задержкой. Чтобы ускорить ответы, вы можете подписаться на /premium.     v.1.10""")
        elif message.text.startswith('/generate_image'):
            prompt = message.text[len('/generate_image'):].strip()
            if not prompt:
                await message.reply("Пожалуйста, введите описание изображения после команды.")
            else:
                image_data = await generate_image(prompt)
                if image_data:
                    await bot.send_photo(chat_id=message.chat.id, photo=image_data)
                else:
                    await message.reply("Извините, не удалось сгенерировать изображение.")
        elif check_sub_channel(await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=message.from_user.id)):
            # Use the ai function to generate a response
            ai_message = await ai(message.text, message.chat.id)

            # Send the AI's message to the user
            if ai_message:
                await bot.send_message(chat_id=message.chat.id, text=ai_message)
        else:
            await bot.send_message(message.from_user.id, NOTSUB_MESSAGE, reply_markup=nav.checkSubMenu)


@dp.callback_query_handler(text="subchanneldone")
async def subchanneldone(call: types.CallbackQuery):
    await bot.delete_message(call.from_user.id, call.message.message_id)
    if check_sub_channel(await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=call.from_user.id)):
        await bot.send_message(call.from_user.id,
                               text="Добро пожаловать в чат с ботом GPT 3.5 Turbo! Я очень рад приветствовать вас здесь и помочь вам в любых вопросах и задачах.",
                               reply_markup=nav.profileKeyboard)
    else:
        await bot.send_message(call.from_user.id, NOTSUB_MESSAGE, reply_markup=nav.checkSubMenu)


# Глобальный словарь для хранения истории сообщений
user_message_histories = {}

# Максимальное количество хранящихся сообщений для каждого пользователя
max_messages_per_user = 10


async def ai(prompt, user_id):
    try:
        if user_id not in user_message_histories:
            user_message_histories[user_id] = [
                {"role": "system", "content": 'Тебя зовут OpenAiBot и ты лучший персональный помошник!'}]

        user_message_histories[user_id].append({"role": "user", "content": prompt})

        # Удаление старых сообщений, если количество сообщений превышает максимальное значение
        if len(user_message_histories[user_id]) > max_messages_per_user:
            user_message_histories[user_id].pop(1)
            user_message_histories[user_id].pop(1)

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=user_message_histories[user_id]
        )

        bot_response = completion.choices[0].message.content
        bot_response = escape(bot_response)
        user_message_histories[user_id].append({"role": "assistant", "content": bot_response})

        return bot_response
    except Exception as e:
        logging.error(f"Error in ai function: {e}")
        return None, None


from aiogram.dispatcher.handler import SkipHandler  # Import SkipHandler at the top of your script


@dp.message_handler(commands=['image', 'generate', '/generate_image'], state='*')
async def generate_image_command(message: types.Message):
    if check_sub_channel(await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=message.from_user.id)):
        # Пользователь является подписчиком, выполняем команду `\image generate`
        await generate_image_command(message)
    else:
        # Пользователь не является подписчиком, отправляем сообщение о недоступности команды
        await bot.send_message(message.chat.id, "Для использования данной команды необходимо подписаться на канал.")
    print("generate_image_command called")
    prompt = message.get_args()
    if not prompt:
        await message.reply("Пожалуйста, введите описание изображения после команды.")
        return

    print(f"Called generate_image with prompt: {prompt}")
    image_data = await generate_image(prompt, grid_size="1", width="512", height="512")

    if image_data:
        await bot.send_photo(chat_id=message.chat.id, photo=image_data)
    else:
        await message.reply("Извините, не удалось сгенерировать изображение.")
    raise SkipHandler


async def generate_image(prompt: str, grid_size: str = "1", width: str = "512", height: str = "512") -> Optional[
    BytesIO]:
    async with aiohttp.ClientSession() as session:
        async with session.post(
                "https://api.deepai.org/api/text2img",
                data={
                    "text": prompt,
                    "grid_size": grid_size,
                    "width": width,
                    "height": height,
                },
                headers={"api-key": DEEP_AI_API_KEY},
        ) as response:

            if response.status == 200:
                json_response = await response.json()
                image_url = json_response["output_url"]

                async with session.get(image_url) as image_response:
                    if image_response.status == 200:
                        image_data = BytesIO(await image_response.read())
                        image_data.name = "generated_image.png"
                        return image_data
                    else:
                        print(f"Error getting image: {image_response.status}")
            else:
                print(f"Error generating image: {response.status}")
    return None


dp.register_message_handler(generate_image_command, commands=['generate_image'])


@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def echo(message: types.Message):
    # Get the user's message
    user_message = message.text

    # Use the ai function to generate a response
    ai_message = await ai(user_message, message.chat.id)

    # Send the AI's message to the user
    if ai_message:
        await bot.send_message(chat_id=message.chat.id, text=ai_message)


async def main():
    while True:
        try:
            await dp.start_polling()
        except Exception as e:
            logging.error(f"Error occurred: {e}")
            logging.info("Restarting bot in 5 seconds...")
            await asyncio.sleep(5)


if __name__ == '__main__':
    asyncio.run(main())
