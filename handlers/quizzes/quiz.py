import asyncio

from aiogram import Router, types
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext

from database.dbw import Tables, db
from keyboards.main_keyboards import create_kb
from menu.main_menu import back_main_menu
from menu.states import States
from redis_cash.redis_client import QuizRedis
from gpt.gpt_client import QuizGPT
from handlers.quizzes.assistant import QuizAssistant

router = Router()


@router.message(States.wait_topic_for_quizzes)
async def first_quizzes(msg: types.Message, state: FSMContext):
    data = QuizRedis(msg.chat.id)
    assistant = QuizAssistant(msg.chat.id)

    # данные
    quiz_id = db.insert_row(Tables.QUIZZES, (msg.text,))
    data.set_data(data.QUIZ_ID, quiz_id)
    data.set_data(data.QUIZ_TOPIC, msg.text)
    data.set_data(data.QUIZ_LEVEL, 4)
    main_msg: types.Message = data.get_message(data.MAIN_MSG)

    await state.set_state(States.solving_quiz)
    await msg.delete()

    # здесь нужно создать первый пакет квизов
    gpt = asyncio.create_task(QuizGPT(msg.chat.id).get_new_quizzes())
    wait = asyncio.create_task(assistant.wait_gpt_quiz())
    await asyncio.gather(gpt, wait)

    if True:
        await main_msg.edit_text('Все готово! Можем начинать',
                                 reply_markup=create_kb({'next_quizz': 'Поехали!'}))
        notif_msg = await main_msg.answer('Готово!')
        await notif_msg.delete()


@router.callback_query(Text(['next_quizz']))
async def next_quizz(cb: types.CallbackQuery):
    data = QuizRedis(cb.from_user.id)
    assistant = QuizAssistant(cb.from_user.id)
    quizzes_to_go = int(data.get_data(data.QUIZZES_TO_GO))

    # если доступные квизы кончились, то создаём новый пакет
    if quizzes_to_go <= 0:
        gpt = asyncio.create_task(QuizGPT(cb.from_user.id).get_new_quizzes())
        wait = asyncio.create_task(assistant.wait_gpt_quiz())
        if int(data.get_flag_gpt_process()):
            await asyncio.gather(wait)
        else:
            await asyncio.gather(gpt, wait)

    # Обновляем данные и получаем новый текст и аргументы для викторины
    new_text, poll_kwargs = QuizAssistant(cb.from_user.id).next_quiz()
    if new_text:
        # отправляем викторину
        if data.get_data(data.QUIZ_MSG):
            print('Прошлый квиз ещё не удалён!')
        try:
            quiz_msg = await cb.message.answer_poll(**poll_kwargs)
            data.set_message(data.QUIZ_MSG, quiz_msg)
        except Exception as ex:
            print(ex)
            await next_quizz(cb)
            return False


    # меняем текст главного сообщения
    await cb.message.edit_text(new_text)

    # если квиты заканчиваются, то делаем новые фоново
    if quizzes_to_go < 5:
        if not int(data.get_flag_gpt_process()):
            gpt = asyncio.create_task(QuizGPT(cb.from_user.id).get_new_quizzes())
            await asyncio.gather(gpt)


@router.poll_answer()
async def user_answer(ans: types.PollAnswer):
    data = QuizRedis(ans.user.id)
    poll_ans = ans.option_ids[0]

    new_text, keyboard = QuizAssistant(ans.user.id).process_answer_quiz(poll_ans)
    quiz_msg: types.Message = data.get_message(data.QUIZ_MSG)
    main_msg: types.Message = data.get_message(data.MAIN_MSG)


    await main_msg.edit_text(new_text,
                             reply_markup=keyboard)
    await quiz_msg.delete()
    data.remove_user_data(data.QUIZ_MSG)


@router.callback_query(Text(['cancel_quiz', 'cancel_gpt_process']))
async def cancel_quiz(cb: types.CallbackQuery, state: FSMContext):
    """Функция отменяет режима квиза"""
    data = QuizRedis(cb.from_user.id)
    data.set_flag_gpt_process(0)
    await state.set_state(States.initial)
    await back_main_menu(cb, state, addit_text='Закончили решать квизы')