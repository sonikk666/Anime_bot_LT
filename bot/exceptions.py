"""Мои исключения."""


class Error(Exception):
    """Мой общий класс ошибок."""

    pass


class ErrorApi(Error):
    """Общая ошибка ответа API."""

    pass


class MyErrorSendMessage(Error):
    """Ошибка при отправке сообщения."""

    pass


class StatusCodeError(Error):
    """Ошибка при запросе к основному API.

    Статус не 200.
    """

    pass
