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
from telegram import (
    InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
)
from telegram.ext import (
    CallbackQueryHandler, CommandHandler, Filters, MessageHandler, Updater
)

from exceptions import Error
from full_version import BUTTON_FULL
from lt_version import BOT_COMMANDS_LITE, BUTTON_LITE, URLS_LITE

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TELEGRAM_GROUP_CHAT_ID = os.getenv('TELEGRAM_GROUP_CHAT_ID')

# Путь для конвертирования изображений
now_time = time.time()
FILE_PATH: str = os.path.join('media', 'anime.jpg')
FILE_PATH_RGB: str = os.path.join('media', f'anime_RGB_{now_time}.jpg')
folder: str = os.path.join('media')
full = False


def version_bot() -> tuple:
    """Определяет версию работы  бота: full или lite.

    Проверяя наличие файла full_version.py.
    Импортирует константы, в зависимости от версии.
    """
    if os.path.isfile('full_version.py') and os.getenv('FULL'):
        full = True
        from full_version import BOT_COMMANDS_FULL, BUTTON_FULL, URLS_FULL
    else:
        full = False

    urls = URLS_FULL | URLS_LITE if full else URLS_LITE
    button_keys = BUTTON_FULL + BUTTON_LITE if full else BUTTON_LITE
    bot_commands = (
        BOT_COMMANDS_FULL + BOT_COMMANDS_LITE
        if full else BOT_COMMANDS_LITE
    )

    return urls, button_keys, bot_commands, full


def get_logger():
    """Задаёт параметры логирования."""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    streamhandler = logging.StreamHandler(stream=sys.stdout)
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s - %(name)s'
    )
    logger.addHandler(streamhandler)
    streamhandler.setFormatter(formatter)
    return logger


def say_hi(update, context):
    """Приветствие бота.

    Ответ бота на любое сообщение.
    """
    chat = update.effective_chat
    context.bot.send_message(chat_id=chat.id, text='Привет, я АнимеБот!')


def get_new_image(url: str) -> dict:
    """Получает новую картинку."""
    params = (
        'byte_size',
        'height',
        'url',
        'width',
    )
    while True:
        try:
            response = requests.get(url).json()
            full_info = response.get('images')[0]

            image_info = {
                key: full_info[key] for key in full_info if key in params
            }

            tag_list = ['#'+x['name'] for x in full_info['tags']]
            image_info['tags'] = ', '.join(tag_list).upper()

            # logger.info(image_info)

            return image_info

        except Error as error:
            logger.debug(f'{error}')


def convert_image(url_image):
    """Конвертирует изображение в RGB формат.

    Сначала сохраняет его в папку, потом конвертирует
    и удаляет оригинал.
    """
    request = requests.get(url_image)

    if not os.path.isdir(folder):
        os.makedirs(folder)

    with open(FILE_PATH, 'wb') as file:
        file.write(request.content)

    image = Image.open(FILE_PATH)
    rgb_im = image.convert('RGB')
    rgb_im.save(FILE_PATH_RGB)

    # photo = open(FILE_PATH_RGB, 'rb')
    os.remove(os.path.join(FILE_PATH))

    return open(FILE_PATH_RGB, 'rb')


def create_image_info(
        image_info: dict, name_image: str, counter: int = 1
) -> tuple:
    """Формирует текстовое сообщение - информацию о картинке."""
    width = image_info.get('width')
    height = image_info.get('height')
    byte_size = image_info['byte_size']
    tags_image = image_info.get('tags')

    mb_size = round(byte_size / 1024 / 1024, 1)

    mini_text = f'{name_image} №{counter}'
    text = (
        # f'{name_image} №{counter}'
        f'{tags_image}'
        f'\n({width}x{height} pix, {mb_size} Mb)'
    )

    return text, mini_text


def send_image(update, context) -> None:
    """Отправляет картинку в чат."""
    counter = 1
    try:
        while counter <= 5:
            try:
                chat = update.effective_chat

                url, name = URLS.get(update.message.text)

                image_info = get_new_image(url)
                text, mini_text = create_image_info(image_info, name, counter)

                url_image = image_info.get('url')
                button1 = InlineKeyboardButton('Info', callback_data=text)
                button2 = InlineKeyboardButton(
                    'Download', callback_data=url_image
                )
                markup = InlineKeyboardMarkup([[button1, button2]])

                # Если изображение больше 5 Мб, конвертируем его в RGB
                if image_info['byte_size'] < 5*1024*1024:
                    context.bot.send_photo(
                        chat.id, url_image, mini_text, reply_markup=markup
                    )
                else:
                    logger.debug(f'Попался большой файл {url_image}')
                    image_in_folder = convert_image(url_image)

                    context.bot.send_photo(
                        chat.id, image_in_folder,
                        caption=f'{mini_text} <resize>', reply_markup=markup
                    )
                    image_in_folder.close()

                    os.remove(FILE_PATH_RGB)

                time.sleep(0.2)
                counter = counter + 1

            except Exception as error:
                logger.error(f'Вложенная ошибка - {error} - для {url_image}')
    except Exception as error:
        logger.error(f'Ошибка в new_image {error}')
        logger.info(f'{counter}')


def send_message(
        update, context, text_message: str, start: bool = False
) -> None:
    """Отправка сообщения в чат."""
    chat = update.effective_chat

    button = ReplyKeyboardMarkup([
        ['/new_waifu'],
    ], resize_keyboard=True)

    context.bot.send_message(
        chat_id=chat.id,
        text=text_message,
        reply_markup=button
    )

    # Если вызов из функции Start_bot, то отправить изображение
    # и отрисовать кнопку
    if start:
        url = URLS.get('/new_waifu')[0]
        image = get_new_image(url)['url']
        button2 = InlineKeyboardButton('Download', callback_data=image)
        markup = InlineKeyboardMarkup([[button2]])
        context.bot.send_photo(chat.id, image, reply_markup=markup)
        # Отправить фото в чат группы
        context.bot.send_photo(
            chat_id=TELEGRAM_GROUP_CHAT_ID, photo=image, reply_markup=markup
        )


def start_bot(update, context):
    """Старт бота."""
    name = update.message.chat.first_name
    text = 'Привет, {}. Посмотри, что я нашёл.'.format(name)
    send_message(update, context, text, start=True)


def clear_history(update, context):
    """Очищает историю сообщений и выходит из tags_mode."""
    text = 'You have cleared the history.'
    send_message(update, context, text)

    new_message_id = update.message.message_id

    while new_message_id > 1:
        try:
            context.bot.delete_message(
                chat_id=update.message.chat_id, message_id=new_message_id
            )
        except Exception as error:
            logger.info(
                f'Message_id does not exist: {new_message_id} - {error}'
            )
            break
        new_message_id -= 1


def tags_mode(update, context) -> None:
    """Выводит на экран бота дополнительные кнопки запросов."""
    chat = update.effective_chat
    button = ReplyKeyboardMarkup(BUTTON_LITE, resize_keyboard=True)
    context.bot.send_message(
        chat_id=chat.id,
        text='tags_mode activated.',
        reply_markup=button
    )


def button(update, context) -> None:
    """Кнопки."""
    query = update.callback_query

    data = query.data

    chat = update.effective_chat
    message = update.effective_message

    query.answer()

    if 'pix' in data:
        context.bot.edit_message_caption(
            chat_id=chat.id,
            message_id=message.message_id,
            caption=data,
            # reply_markup=markup
            # reply_markup=button
        )
    elif 'http' in data:
        context.bot.send_document(chat.id, data)


def full_version_on(update, context) -> None:
    """Включение кнопок полной версии."""
    chat = update.effective_chat
    if chat.id == int(TELEGRAM_CHAT_ID):
        button = ReplyKeyboardMarkup(BUTTON_FULL, resize_keyboard=True)
        context.bot.send_message(
            chat_id=chat.id,
            text='full_mode activated.',
            reply_markup=button
        )
    else:
        context.bot.send_message(
            chat_id=chat.id, text='Извините, у Вас нет доступа!'
        )


def main():
    """Главная работа бота."""
    # Словарь для команд бота
    commands = {
        'start': start_bot,
        'tags_mode': tags_mode,
        'clear_history': clear_history,
        LIST: send_image,
    }
    if full:
        commands['paid'] = full_version_on

    try:
        updater = Updater(token=TELEGRAM_TOKEN)
        app = updater.dispatcher

        # Загружаем список команд из словаря
        for key, value in commands.items():
            app.add_handler(CommandHandler(
                command=key, callback=value,
            ))
        app.add_handler(MessageHandler(
            Filters.text, say_hi,
            Filters.user(user_id=int(TELEGRAM_CHAT_ID))
        ))
        app.add_handler(CallbackQueryHandler(button))

        updater.start_polling()
        updater.idle()

    except Exception as error:
        logger.error(f'Сбой в работе программы: {error}')


if __name__ == '__main__':
    logger = get_logger()
    URLS, BUTTON_KEYS, LIST, full = version_bot()
    try:
        logger.info('Запуск программы')
        main()
    except KeyboardInterrupt:
        logger.info('Выход из программы с клавиатуры')
        sys.exit('Выход из программы с клавиатуры')
