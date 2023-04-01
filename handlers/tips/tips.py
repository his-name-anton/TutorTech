
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Text

router = Router()


@router.callback_query(Text(['tips_topic_code']))
async def tips_topic_code(cb: types.CallbackQuery, state: FSMContext):
    pass
