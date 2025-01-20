from aiogram.types import Update
from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from app.states import Register
import app.keyboards as kb
import app.database.request as rq


class CheckUserMiddleware(BaseMiddleware):
    async def __call__(self,
                       handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
                       event: Update,
                       data: Dict[str, Any]) -> Any:
        fsm_context: FSMContext = data.get("state")
        state = await fsm_context.get_state() if fsm_context else None

        if state == Register.name.state and event.message:
            return await handler(event, data)


        if state == Register.categories.state and event.callback_query:
            return await handler(event, data)

        if event.callback_query:
            callback: CallbackQuery = event.callback_query
            tg_id = callback.from_user.id

            user = await rq.get_profile(tg_id)
            isRegistred = user and user.name
            if not isRegistred:
                if callback.data == "start_reg":
                    return await handler(event, data)
                if fsm_context:
                    await fsm_context.clear()
                await callback.message.answer(
                    text='Добро пожаловать\\! \nЭто новостной бот *ExtremeNews*, адаптирующийся к вашим '
                         'предпочтениям\\.'
                         '\nДля начала \\- *пройдите регистрацию*\\.', reply_markup=kb.register_keyboard,
                    parse_mode="MarkdownV2")
                return
        else:
            tg_id = event.message.from_user.id

            user = await rq.get_profile(tg_id)
            isRegistred = user and user.name
            if not isRegistred:
                await event.message.answer(
                    text='Добро пожаловать\\! \nЭто новостной бот *ExtremeNews*, адаптирующийся к вашим '
                         'предпочтениям\\.'
                         '\nДля начала \\- *пройдите регистрацию*\\.', reply_markup=kb.register_keyboard,
                    parse_mode="MarkdownV2")
                if fsm_context:
                    await fsm_context.clear()
                return

        return await handler(event, data)
