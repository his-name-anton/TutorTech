from aiogram import types
from aiogram.fsm.context import FSMContext
from keyboards.main_keyboards import create_kb
from menu.states import States
from redis_cash.other import main_dict
from redis_cash.redis_client import QuizRedis


class KbButtons:
    CMD_MENU = {
        'main_menu': 'Меню'
    }
    MAIN_MENU = {
        'select_new_course': 'Новый курс',
        'solve_quizzes': 'Решать квизы',
        'languages_select_lang': 'Изучать языки',
        'init_tips': 'Tips',
    }
    BACK_MAIN_MENU = {
        'back_main_menu': '⬅️ Назад'
    }

    CREATE_COURSE_PROGRAM = {
        'running_course': '✅Создать курс'
    }


async def main_menu(msg: types.Message, state: FSMContext):
    main_menu_msg = await msg.answer('Меню 👋',
                                     reply_markup=create_kb(KbButtons.MAIN_MENU)
                                     )
    await state.update_data(main_menu_msg=main_menu_msg)


async def back_main_menu(cb: types.CallbackQuery, state: FSMContext, addit_text=''):
    await state.clear()
    main_menu_msg = await cb.message.edit_text(f'{addit_text}\n\nМеню 👋',
                                               reply_markup=create_kb(  KbButtons.MAIN_MENU)
                                               )
    await state.update_data(main_menu_msg=main_menu_msg)


async def select_new_course(cb: types.CallbackQuery, state: FSMContext):
    await state.set_state(States.wait_theme_from_user)
    await state.update_data(main_msg_id=cb.message.message_id)
    await cb.message.edit_text('Напишите тему',
                               reply_markup=create_kb(KbButtons.BACK_MAIN_MENU))


async def continue_training(cb: types.CallbackQuery, state: FSMContext):
    await cb.message.edit_text('Кнопка в разработке',
                               reply_markup=create_kb(KbButtons.BACK_MAIN_MENU))


async def init_tips(cb: types.CallbackQuery, state: FSMContext):
    await cb.message.edit_text('Выберите',
                               reply_markup=create_kb(
                                   {'tips_topic_code': 'Програмирование',
                                    'tips_any_topic': 'Другая тема',
                                    **KbButtons.BACK_MAIN_MENU}
                                    )
                               )


async def solve_quizzes(cb: types.CallbackQuery, state: FSMContext):
    data = QuizRedis(cb.from_user.id)
    await state.set_state(States.wait_topic_for_quizzes)

    data.remove_user_data()
    data.init_counter()
    data.set_message(data.MAIN_MSG, cb.message)

    await cb.message.edit_text('Отлично! Давайте порешаем квизы 🤓\n\n'
                               'Напишите тему, а я составлю для вас квизы',
                               reply_markup=create_kb(KbButtons.BACK_MAIN_MENU))


async def languages_select_lang(cb: types.CallbackQuery, state: FSMContext):
    await cb.message.edit_text('Выберите какой язык будете изучать',
                               reply_markup=create_kb({
                                   'select_lang_eng': 'Английский',
                                   'select_lang_fr': 'Французский',
                                   'select_lang_grm': 'Немецкий',
                                   'select_lang_chi': 'Китайский',
                                   'select_lang_jap': 'Японский',
                                   **KbButtons.BACK_MAIN_MENU
                               }))