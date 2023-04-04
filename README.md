# Anime_Bot

## Телеграмм-бот для просмотра аниме-картинок (парсинг API)

### Описание

Возможности

- Запрашивает с API и присылает в чат картинки (по 5шт) и теги к ним
- Можно выбирать запрос по темам (тегам)
- Если попадается файл больше 5Мб - изменяет размер

### Технологии

Python 3.11.2

Python_telegram_bot 13.7

Pillow 9.5.0

### Как запустить проект в dev-режиме

Клонировать репозиторий и перейти в него в командной строке:

```bash
git clone https://github.com/sonikk666/anime_bot_lt.git

cd anime_bot_lt
```

Создать и активировать виртуальное окружение:

```bash
python3 -m venv env

source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```bash
python3 -m pip install --upgrade pip

pip install -r requirements.txt
```

- Создайте файл .env и наполните его по следующему шаблону:

```bash
TELEGRAM_CHAT_ID=0000000000  # сейчас стоит фильтр по user_id (установите свой)
TELEGRAM_TOKEN=token_for_bot  # токен вашего бота (установите свой)
```

Запустить проект:

```bash
python3 anime_bot_lt.py
```

### Автор

Никита Михайлов
