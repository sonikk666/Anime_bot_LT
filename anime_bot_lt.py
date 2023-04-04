"""Код Телеграм бота.

Запрашивает картинки с АПИ и присылает в чат.
Имеет две версии FULL и LITE.
Для полной версии нужно иметь файл full_version.py.
"""

import logging
import os
import sys
import time

import requests
from dotenv import load_dotenv
from PIL import Image
from telegram import Message, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

from exceptions import Error

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


def version_bot():
    """Определяет версию работы  бота: full или lite.

    Проверяя наличие файла full_version.py.
    Импортирует константы, в зависимости от версии.
    """
    if os.path.isfile('full_version.py') and os.getenv('FULL'):
        FULL = True
        from full_version import URLS_FULL, BUTTON_FULL, BOT_COMMANDS_FULL
    else:
        FULL = False
        from lt_version import URLS_LITE, BUTTON_LITE, BOT_COMMANDS_LITE

    URLS = URLS_FULL if FULL else URLS_LITE
    BUTTON_KEYS = BUTTON_FULL if FULL else BUTTON_LITE
    BOT_COMMANDS = BOT_COMMANDS_FULL if FULL else BOT_COMMANDS_LITE

    return URLS, BUTTON_KEYS, BOT_COMMANDS


def get_logger():
    """Задаёт параметры логирования."""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    streamHandler = logging.StreamHandler(stream=sys.stdout)
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s - %(name)s'
    )
    logger.addHandler(streamHandler)
    streamHandler.setFormatter(formatter)
    return logger


def say_hi(update, context):
    """Приветствие бота."""
    chat = update.effective_chat
    if chat.id == int(TELEGRAM_CHAT_ID):
        context.bot.send_message(chat_id=chat.id, text='Привет, я АнимеБот!')
    else:
        context.bot.send_message(
            chat_id=chat.id, text='Извините, у Вас нет доступа!'
        )


def length_count(random_image):
    """Расчёт размера файла в запросе."""
    header = requests.head(random_image)
    content_length = header.headers.get('content-length')
    length_mb = int(content_length) / 1024 / 1024
    length = round(length_mb, 1)
    return length


def get_new_image(url):
    """Получает новую картинку."""
    while True:
        try:
            response = requests.get(url).json()
            random_waifu = response.get('images')[0].get('url')

            tags = response.get('images')[0].get('tags')
            tag_list = []
            for tag in tags:
                tag_name = tag.get('name')
                tag_list.append(tag_name)
            text = (', #'.join(tag_list))
            text = f'#{text}'

            tuple = (random_waifu, text.upper())
            return tuple

        except Error as error:
            logger.debug(f'{error}')


def new_image(update, context):
    """Отправляет картинку в чат."""
    counter = 0
    try:
        while counter < 5:
            try:
                chat = update.effective_chat
                url = URLS.get(update.message.text)[0]
                name = URLS.get(update.message.text)[1]
                image_tuple = get_new_image(url)
                image_photo = image_tuple[0]
                image_tag = image_tuple[1]

                text = f'{name} №{counter+1} {image_tag}'

                if length_count(image_photo) < 5:
                    context.bot.send_photo(chat.id, image_photo, text)
                else:
                    logger.debug(f'Попался большой файл {image_photo}')
                    url = image_photo
                    path = os.path.join('media', 'anime.jpg')

                    request = requests.get(url)

                    with open(path, 'wb') as file:
                        file.write(request.content)

                    image = Image.open(path)
                    rgb_im = image.convert('RGB')
                    rgb_im.save(os.path.join('media', 'anime_RGB.jpg'))

                    photo = open(os.path.join(
                        os.path.join('media', 'anime_RGB.jpg')
                    ), 'rb')
                    text_2 = text + ' <resize>'
                    context.bot.send_photo(chat.id, photo, text_2)
                    os.remove(os.path.join('media', 'anime.jpg'))

                time.sleep(0.2)
                counter = counter + 1

            except Exception as error:
                logger.error(f'Вложенная ошибка {error}')
    except Exception as error:
        logger.error(f'Ошибка в new_image {error}')
        logger.info(f'{counter}')


def wake_up(update, context):
    """Старт бота."""
    chat = update.effective_chat
    name = update.message.chat.first_name
    button = ReplyKeyboardMarkup([
        ['/new_waifu', ],
    ], resize_keyboard=True)

    context.bot.send_message(
        chat_id=chat.id,
        text='Привет, {}. Посмотри, что я нашёл.'.format(name),
        reply_markup=button
    )
    url = URLS.get('/new_waifu')[0]
    context.bot.send_photo(chat.id, get_new_image(url)[0])


def clear_history(update, context):
    """Очищает историю сообщений и выходит из tags_mode."""
    chat = update.effective_chat
    button = ReplyKeyboardMarkup([
        ['/new_waifu'],
    ], resize_keyboard=True)
    context.bot.send_message(
        chat_id=chat.id,
        text='You have cleared the history.',
        reply_markup=button
    )

    new_message_id = update.message.message_id
    print(new_message_id)
    while new_message_id > 1:
        try:
            context.bot.delete_message(
                chat_id=update.message.chat_id, message_id=new_message_id
            )
        except Exception as error:
            print(f'Message_id does not exist: {new_message_id} - {error}')
            break
        new_message_id -= 1


def tags_mode(update, context):
    """Выводит на экран бота дополнительные кнопки запросов."""
    chat = update.effective_chat
    button = ReplyKeyboardMarkup(BUTTON_KEYS, resize_keyboard=True)
    context.bot.send_message(
        chat_id=chat.id,
        text='tags_mode activated.',
        reply_markup=button
    )


def main():
    """Главная работа бота."""
    try:
        updater = Updater(token=TELEGRAM_TOKEN)
        updater.dispatcher.add_handler(CommandHandler(
            command='start', callback=wake_up,
            filters=Filters.user(user_id=int(TELEGRAM_CHAT_ID))
        ))
        updater.dispatcher.add_handler(CommandHandler(
            'tags_mode', tags_mode,
            Filters.user(user_id=int(TELEGRAM_CHAT_ID))
        ))
        updater.dispatcher.add_handler(CommandHandler(
            LIST, new_image,
            Filters.user(user_id=int(TELEGRAM_CHAT_ID))
        ))
        updater.dispatcher.add_handler(CommandHandler(
            'clear_history', clear_history,
            Filters.user(user_id=int(TELEGRAM_CHAT_ID))
        ))
        updater.dispatcher.add_handler(MessageHandler(
            Filters.text, say_hi,
            Filters.user(user_id=int(TELEGRAM_CHAT_ID))
        ))

        updater.start_polling()
        updater.idle()

    except Exception as error:
        print(f'Сбой в работе программы: {error}')


if __name__ == '__main__':
    logger = get_logger()
    URLS, BUTTON_KEYS, LIST = version_bot()
    try:
        logger.info('Запуск программы')
        main()
    except KeyboardInterrupt:
        logger.info('Выход из программы с клавиатуры')
        sys.exit('Выход из программы с клавиатуры')
