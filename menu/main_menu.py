from aiogram import types
from keyboards.main_keyboards import make_inline_menu_board


class MainMenuButtons:
    CMD_MENU = {
        'main_menu': 'Меню'
    }

    MAIN_MENU = {
        'select_new_course': 'Новый курс',
        'tasks': 'Задачки'
    }


async def main_menu(msg: types.Message):
    await msg.answer('Меню 👋', reply_markup=make_inline_menu_board(MainMenuButtons.MAIN_MENU))