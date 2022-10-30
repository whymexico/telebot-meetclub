import asyncio
import inline as markups

from aiogram import types, Dispatcher
from aiogram.dispatcher import DEFAULT_RATE_LIMIT
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import Throttled

from main import dp, logger


class anti_bot(StatesGroup):
    in_process = State()
    in_process_2 = State()
    banned = State()

class ThrottlingMiddleware(BaseMiddleware):
    """
    Стандартный middleware для предотвращение спама через throttling
    """

    def __init__(self, limit: int = DEFAULT_RATE_LIMIT, key_prefix: str = 'antiflood_'):
        self.rate_limit = limit
        self.prefix = key_prefix
        super(ThrottlingMiddleware, self).__init__()

    # noinspection PyUnusedLocal
    async def on_process_message(self, message: types.Message, data: dict):
        handler = current_handler.get()
        dispatcher = Dispatcher.get_current()
        if handler:
            limit = getattr(handler, 'throttling_rate_limit', self.rate_limit)
            key = getattr(handler, 'throttling_key', f"{self.prefix}_{handler.__name__}")
        else:
            limit = self.rate_limit
            key = f"{self.prefix}_message"
        try:
            await dispatcher.throttle(key, rate=limit)
        except Throttled as t:
            await self.message_throttled(message, t)
            raise CancelHandler()

    async def message_throttled(self, message: types.Message, throttled: Throttled):
        '''
        '''

        await message.delete()

        handler = current_handler.get()
        limit = getattr(handler, 'throttling_rate_limit', self.rate_limit)
        delta = throttled.rate - throttled.delta
        logger.debug(f'@{message.from_user.username}:{message.from_user.id} спамит командой {message.text}')

        if throttled.exceeded_count <= 4:
            await message.answer(f'❗ *Пожалуйста, не используйте команды так часто*\n\n _Вы сможете снова использовать команду через_ *{limit} сек.*', parse_mode='Markdown')

        else:
            state = dp.current_state(chat=message.chat.id, user=message.from_user.id)
            await state.set_state(anti_bot.in_process)

            generated_tuple = markups.generate_confirm_markup(message.from_user.id)
            markup = generated_tuple[0]
            subject = generated_tuple[1]
            await message.answer(f'❗ *Пройдите проверку, чтобы подтвердить, что вы не робот*\n\n_Найдите_ *{subject}* _на панели ниже!_', parse_mode='Markdown', reply_markup=markup)

        await asyncio.sleep(delta)


def rate_limit(limit: int = None, key: str = None):
    """
    Decorator for configuring rate limit and key in different functions.
    """

    def decorator(func):
        setattr(func, 'throttling_rate_limit', limit)
        if key:
            setattr(func, 'throttling_key', key)
        return func

    return decorator
