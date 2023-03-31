import asyncio
from pprint import pprint
from aiogram import types, Router
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from keyboards.main_keyboards import create_kb
from menu.other import main_dict
from menu.states import States
from gpt.gpt_quizz import generate_q_list
from menu.new_course import wait_msg
from menu.main_menu import back_main_menu

router: Router = Router()


async def create_pack_quizzes(chat_id: int, is_first: bool = True, is_background=True) -> bool:
    main_dict[chat_id]['wait'] = True
    topic: str = main_dict[chat_id]['quizz']['topic']
    start_msg: types.Message = main_dict[chat_id]['quizz']['start_msg']
    wait_msg_text = f'Создаю для вас квизы на тему: <b>"{topic}"</b>' if is_first \
        else 'Сейчас подгружу ещё квизов, минуточку'

    pprint(main_dict)

    if is_background:
        is_successful_gpt = await asyncio.gather(asyncio.create_task(generate_q_list(chat_id, topic, 4)))
    else:
        is_successful_gpt, _ = await asyncio.gather(asyncio.create_task(generate_q_list(chat_id, topic, 5)),
                                                    asyncio.create_task(wait_msg(start_msg, wait_msg_text)))

    if not is_successful_gpt:
        await start_msg.answer('Кажется проиозошла ошибка, давайте попоробуем ещё раз')
    else:
        return True


@router.message(States.wait_topic_for_quizzes)
async def first_quizzes(msg: types.Message, state: FSMContext):
    """Функция обрабатывает сообщение с темой для квизов от пользователя
    Сохраняем тему и вызываем создание пака квизов"""

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
        if not await create_pack_quizzes(cb.from_user.id,
                                         is_first=False,
                                         is_background=False):
            return False

    # get data
    main_dict[cb.from_user.id]['quizz']['iter'] += 1
    quizzes_list: dict = main_dict[cb.from_user.id]['quizz']['quizzes_list']
    iter: int = main_dict[cb.from_user.id]['quizz']['iter']
    quizz: dict = quizzes_list[iter]
    question: str = quizz.get('question')
    answer_choices: list = quizz.get('answer_choices')
    correct_answer: int = quizz.get('correct_answer')
    explanation: str = quizz.get('explanation')
    example: str = quizz.get('example')

    # set data
    main_dict[cb.from_user.id]['quizz']['current_quizz'] = {"question": question,
                                                            "answer_choices": answer_choices,
                                                            "correct_answer": correct_answer,
                                                            "explanation": explanation,
                                                            "example": example,
                                                            "quiz_msg": cb.message}

    short_top_list = ['A', 'B', 'C', 'D']
    if any(len(item) >= 100 for item in answer_choices):
        question += '\n\nВарианты ответа:\n'
        for index, item in enumerate(answer_choices):
            question += f'({short_top_list[index]}) {item}\n'
        answer_choices = short_top_list

    try:
        msg = await cb.message.answer_poll(question='❔',
                                           options=answer_choices,
                                           type='quiz',
                                           protect_content=True,
                                           is_anonymous=False,
                                           correct_option_id=correct_answer,
                                           )
        main_dict[cb.from_user.id]['quizz']['current_quizz']['quiz_options_msg'] = msg
    except Exception as ex:
        print(ex)
        await next_quizz(cb, state)

    await cb.message.edit_text(f'Вопрос:\n{question}')
    if main_dict[cb.from_user.id]["quizz"]['quizzes_to_go'] < 5:
        await create_pack_quizzes(msg.chat.id,
                                  is_first=False,
                                  is_background=True)


@router.poll_answer()
async def user_answer(ans: types.PollAnswer, state: FSMContext):
    """Функция обработаывает ответ пользователя, обновляет стату и меняет кнопки"""

    cur_quiz = main_dict[ans.user.id]['quizz']['current_quizz']
    poll_ans = ans.option_ids
    main_dict[ans.user.id]["quizz"]['quizzes_to_go'] -= 1

    correct_answer = cur_quiz.get('answer_choices')[int(cur_quiz.get('correct_answer'))].replace('<br>', '').replace('<br/>', '')
    explanation = cur_quiz.get("explanation").replace('<br>', '').replace('<br/>', '')
    example = cur_quiz.get("example").replace('<br>', '').replace('<br/>', '')

    main_dict[ans.user.id]['quizz']['counter_all_quiz'] += 1
    if poll_ans[0] == int(cur_quiz['correct_answer']):
        main_dict[ans.user.id]['quizz']['counter_right_answers'] += 1
        result_text = 'Верно! 😎\n' \
                      f'И всё же немного теории: <i>{explanation}</i>\n\nПример: {example}'
    else:
        result_text = 'Неверно 🥲\n' + \
                      f"Правильный ответ: <b>{correct_answer}</b>\n" + \
                      f'Пояснение: <i>{explanation}</i>\n\n' \
                      f'Пример: {example}'

    statistic_text = f"Пройдено квизов: {main_dict[ans.user.id]['quizz']['counter_all_quiz']}\n" \
                     f"Верных ответов: {main_dict[ans.user.id]['quizz']['counter_right_answers']}"

    msg: types.Message = cur_quiz['quiz_msg']

    await asyncio.sleep(1)
    await msg.edit_text(f"Вопрос: {cur_quiz.get('question')}\n\n{result_text}\n\n{statistic_text}",
                        reply_markup=create_kb({
                            'like_quiz': 'Лайк 👍',
                            'dislike_quiz': 'Дизлайк 👎',
                            'cancel_quiz': 'Завершить 🛑',
                            'next_quizz': 'Следующий ➡️'
                        }, long_f=False))
    pprint(main_dict)
    quiz_options_msg: types.Message = cur_quiz.get('quiz_options_msg')
    await quiz_options_msg.delete()


@router.callback_query(Text(['cancel_quiz']))
async def cancel_quiz(cb: types.CallbackQuery, state: FSMContext):
    """Функция отменяет режима квиза"""
    await state.set_state(States.initial)
    await back_main_menu(cb, state, addit_text='Закончили решать квизы')