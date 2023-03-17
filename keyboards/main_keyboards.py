from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def make_inline_menu_board(items: dict[str: str], long_f=False) -> InlineKeyboardBuilder:
    if long_f:
        board = InlineKeyboardBuilder()
        for key, value in items.items():
            board.row(InlineKeyboardButton(
                text=value[0],
                callback_data=key
            ))
    else:
        buttons = []
        row = []
        for key, value in items.items():
            row.append(InlineKeyboardButton(
                text=value,
                callback_data=key
            ))
            if len(row) == 2:
                buttons.append(row)
                row = []
        if len(row) == 1:
            buttons.append(row)
        board = InlineKeyboardBuilder(buttons)
    return board.as_markup()