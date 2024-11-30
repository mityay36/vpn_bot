import logging
from functools import wraps

from aiogram.types import CallbackQuery, Message

logger = logging.getLogger(__name__)


class UserContextFilter(logging.Filter):
    def filter(self, record):
        record.chat_id = getattr(record, 'chat_id', 'UnknownChatID')
        record.username = getattr(record, 'username', 'UnknownUser')
        return True


def log_user_activity(handler):
    @wraps(handler)
    async def wrapper(event, *args, **kwargs):
        if isinstance(event, Message):
            chat_id = event.chat.id
            username = event.from_user.username or "NoUsername"
        elif isinstance(event, CallbackQuery):
            chat_id = event.message.chat.id
            username = event.from_user.username or "NoUsername"
        else:
            logger.warning("Unknown event type for logging")
            return await handler(event, *args, **kwargs)

        logger.info(
            "Handling update",
            extra={'chat_id': chat_id, 'username': username}
        )

        return await handler(event, *args, **kwargs)
    return wrapper
