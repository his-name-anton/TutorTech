import asyncio
from pprint import pprint
from aiogram import types, Router
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from bs4 import BeautifulSoup

from handlers.quizzes.assistants import text_after_answer, save_quizzes_data_in_db, update_current_quiz
from keyboards.main_keyboards import create_kb
from menu.other import main_dict
from menu.states import States
from gpt.gpt_quizz import generate_q_list
from menu.new_course import wait_msg
from menu.main_menu import back_main_menu
from database.dbw import db, Tables


router: Router = Router()


async def create_pack_quizzes(chat_id: int,
                              is_first: bool = True,
                              is_background=True) -> bool:

    topic: str = main_dict[chat_id]['quizz']['topic']
    start_msg: types.Message = main_dict[chat_id]['quizz']['start_msg']
    wait_msg_text = f'Создаю для вас квизы на тему: <b>"{topic}"</b>' if is_first \
        else 'Сейчас подгружу ещё квизов, минуточку'

    try:
        await start_msg.edit_reply_markup(reply_markup=None)
    except:
        pass

    # Две попытки на успешный список вопросов для квизов
    if is_background:
        for _ in range(2):
            main_dict[chat_id]['wait'] = True
            is_successful_gpt = await asyncio.gather(asyncio.create_task(generate_q_list(chat_id, topic, 4)))
            if is_successful_gpt:
                break
            else:
                main_dict[chat_id]['wait'] = False
    else:
        for _ in range(2):
            main_dict[chat_id]['wait'] = True
            is_successful_gpt, _ = await asyncio.gather(asyncio.create_task(generate_q_list(chat_id, topic, 5)),
                                                        asyncio.create_task(wait_msg(start_msg, wait_msg_text)))
            if is_successful_gpt:
                break
            else:
                main_dict[chat_id]['wait'] = False

    if not is_successful_gpt:
        await start_msg.answer('Кажется проиозошла ошибка, давайте попоробуем ещё раз')
    else:
        save_quizzes_data_in_db(chat_id)
        return True


@router.message(States.wait_topic_for_quizzes)
async def first_quizzes(msg: types.Message, state: FSMContext):
    """Функция обрабатывает сообщение с темой для квизов от пользователя
    Сохраняем тему и вызываем создание пака квизов"""

    main_dict[msg.chat.id]['quizz']['id_quiz'] = db.insert_row(Tables.QUIZZES, (msg.text,))
    main_dict[msg.chat.id]['quizz']['topic'] = msg.text
    await state.set_state(States.solving_quiz)
    if await create_pack_quizzes(msg.chat.id,
                                 is_first=True,
                                 is_background=False):
        pprint(main_dict)
        start_msg: types.Message = main_dict[msg.chat.id]['quizz']['start_msg']
        await start_msg.edit_text('Всё готово! Можем начинать',
                                  reply_markup=create_kb({'next_quizz': 'Поехали!'}))
        await msg.delete()


@router.callback_query(Text(['next_quizz']))
async def next_quizz(cb: types.CallbackQuery, state: FSMContext):
    """Функция вызывает следующий квиз"""
    # check need update quizzes
    if main_dict[cb.from_user.id]["quizz"]['quizzes_to_go'] <= 0:
        await cb.message.edit_reply_markup(reply_markup=None)
        if main_dict[cb.from_user]['wait']:
            await cb.message.edit_text('Новые квизы уже подгружаются, минуточку)')
        if not await create_pack_quizzes(cb.from_user.id,
                                         is_first=False,
                                         is_background=False):
            await cb.message.edit_text('Произошла ошибка при создание новых вопросов. Попробуйте ещё раз',
                                       reply_markup=create_kb({'next_quizz': 'Попробывать ещё раз'}))

    text = update_current_quiz(cb.from_user.id, cb.message)
    try:
        msg = await cb.message.answer_poll(question='❔',
                                           options=main_dict[cb.from_user.id]['quizz']['current_quizz']['answer_choices'],
                                           type='quiz',
                                           protect_content=True,
                                           is_anonymous=False,
                                           correct_option_id=main_dict[cb.from_user.id]['quizz']['current_quizz']['correct_answer'],
                                           )
        main_dict[cb.from_user.id]['quizz']['current_quizz']['quiz_options_msg'] = msg
    except Exception as ex:
        print(ex)
        await next_quizz(cb, state)

    await cb.message.edit_text(text)
    if main_dict[cb.from_user.id]["quizz"]['quizzes_to_go'] < 5:
        if not main_dict[cb.from_user]['wait']:
            await create_pack_quizzes(msg.chat.id,
                                      is_first=False,
                                      is_background=True)


@router.poll_answer()
async def user_answer(ans: types.PollAnswer, state: FSMContext):
    """Функция обработаывает ответ пользователя, обновляет стату и меняет кнопки"""

    main_dict[ans.user.id]["quizz"]['quizzes_to_go'] -= 1
    main_dict[ans.user.id]['quizz']['counter_all_quiz'] += 1
    cur_quiz = main_dict[ans.user.id]['quizz']['current_quizz']

    poll_ans = ans.option_ids
    is_correct = False
    if poll_ans[0] == int(cur_quiz['correct_answer']):
        main_dict[ans.user.id]['quizz']['counter_right_answers'] += 1
        is_correct = True

    text = text_after_answer(ans.user.id, is_correct)
    msg: types.Message = cur_quiz['quiz_msg']
    await asyncio.sleep(1)
    await msg.edit_text(text,
                        reply_markup=create_kb({
                            'theory_question': 'Больше теории 📓',
                            'cancel_quiz': 'Завершить 🛑',
                            'next_quizz': 'Следующий ➡️'
                        }, long_f=False))
    quiz_options_msg: types.Message = cur_quiz.get('quiz_options_msg')
    await quiz_options_msg.delete()


@router.callback_query(Text(['cancel_quiz']))
async def cancel_quiz(cb: types.CallbackQuery, state: FSMContext):
    """Функция отменяет режима квиза"""
    await state.set_state(States.initial)
    await back_main_menu(cb, state, addit_text='Закончили решать квизы')
