from aiogram import Router, types

from menu import main_menu

router: Router = Router()


@router.message()
async def any_text(msg: types.Message):
    await main_menu.main_menu(msg)