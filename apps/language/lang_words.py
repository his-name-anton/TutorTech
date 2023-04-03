
from aiogram import Router, types
from aiogram.fsm.context import FSMContext

from menu.states import States

router = Router()

DEFAULT_LEVEL = 3


@router.callback_query(lambda c: 'select_lang' in c.data)
async def init_topic_for_words(cb: types.CallbackQuery, state: FSMContext):
    await state.set_state(States.wait_topic_for_words)
    await cb.message.edit_text('Напишите тему, в которой вы хотите пополнить словарный запас')


@router.message(States.wait_topic_for_words)
async def first_pack_words(msg: types.Message, state: FSMContext):
    topic = msg.text
    level = DEFAULT_LEVEL

