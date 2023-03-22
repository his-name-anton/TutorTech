from pprint import pprint

from aiogram import types
from aiogram.fsm.context import FSMContext
from keyboards.main_keyboards import create_kb
from menu.states import States
from menu.other import main_dict


class KbButtons:
    CMD_MENU = {
        'main_menu': 'Меню'
    }
    MAIN_MENU = {
        'select_new_course': 'Новый курс',
        'solve_test': 'Решать тест'
    }
    CONTINUE_TRAINING = {
        'continue_training': 'Продолжить обучение'
    }
    BACK_MAIN_MENU = {
        'back_main_menu': '⬅️ Назад'
    }

    CREATE_COURSE_PROGRAM = {
        'running_course': '✅Создать курс'
    }


async def main_menu(msg: types.Message, state: FSMContext):
    main_menu_msg = await msg.answer('Меню 👋',
                                     reply_markup=create_kb({**KbButtons.CONTINUE_TRAINING, **KbButtons.MAIN_MENU}, )
                                     )
    await state.update_data(main_menu_msg=main_menu_msg)


async def back_main_menu(cb: types.CallbackQuery, state: FSMContext):
    await state.clear()
    main_menu_msg = await cb.message.edit_text('Меню 👋',
                                               reply_markup=create_kb(
                                                   {**KbButtons.CONTINUE_TRAINING, **KbButtons.MAIN_MENU}, )
                                               )
    await state.update_data(main_menu_msg=main_menu_msg)


async def select_new_course(cb: types.CallbackQuery, state: FSMContext):
    await state.set_state(States.wait_theme_from_user)

    # data
    main_dict[cb.from_user.id] = {}
    main_dict[cb.from_user.id]["new_course"] = {}
    main_dict[cb.from_user.id]["new_course"]["edit_msg"] = cb.message
    pprint(main_dict)

    await state.update_data(main_msg_id=cb.message.message_id)
    await cb.message.edit_text('Напишите тему',
                               reply_markup=create_kb(KbButtons.BACK_MAIN_MENU))


async def continue_training(cb: types.CallbackQuery, state: FSMContext):
    await cb.message.edit_text('Продолжаем обучение',
                               reply_markup=create_kb(KbButtons.BACK_MAIN_MENU))


async def solve_test(cb: types.CallbackQuery, state: FSMContext):
    await cb.message.edit_text('Решаем тесты',
                               reply_markup=create_kb(KbButtons.BACK_MAIN_MENU))
