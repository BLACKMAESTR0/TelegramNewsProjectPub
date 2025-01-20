from aiogram.types import Update
from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Dict, Any, Awaitable

import app.database.request as rq


class HelloMiddleware(BaseMiddleware):
    async def __call__(self,
                       handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
                       event: Update,
                       data: Dict[str, Any]) -> Any:

        tg_id = None

        if event.message:  # Если это сообщение
            tg_id = event.message.from_user.id
        elif event.callback_query:  # Если это callback_query
            tg_id = event.callback_query.from_user.id
        elif event.inline_query:  # Если это inline_query
            tg_id = event.inline_query.from_user.id
        elif event.my_chat_member:  # Если это обновление чата
            tg_id = event.my_chat_member.from_user.id
        elif event.chat_member:  # Если это обновление участника чата
            tg_id = event.chat_member.from_user.id
        elif event.pre_checkout_query:  # Если это запрос на предоплату
            tg_id = event.pre_checkout_query.from_user.id

        user = await rq.get_profile(tg_id)
        if not user:
            await rq.set_info(tg_id=tg_id)
        await rq.set_active(tg_id)
        return await handler(event, data)
