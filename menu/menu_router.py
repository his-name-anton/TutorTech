from pprint import pprint

from aiogram import Router, types
from aiogram.fsm.context import FSMContext

from menu import main_menu, new_course
from menu.main_menu import KbButtons

router: Router = Router()
names_func_buttons = list(
    item
    for d in vars(KbButtons).values()
    if isinstance(d, dict)
    for item in d.keys()
)


@router.callback_query(lambda c: c.data in names_func_buttons)
async def process_callback_button(cb: types.CallbackQuery, state: FSMContext):
    data = cb.data
    func = {**vars(main_menu), **vars(new_course)}.get(data)
    await func(cb, state)


@router.message()
async def any_text(msg: types.Message, state: FSMContext):
    await main_menu.main_menu(msg, state)

