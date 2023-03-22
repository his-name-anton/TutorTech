import asyncio
import time
from pprint import pprint
from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from keyboards.main_keyboards import create_kb
from menu.main_menu import KbButtons
from menu.other import main_dict
from menu.states import States
from gen_course.detailed_table import create_detailed_table, create_topic_suggestion, create_sections
from database.dbw import db, Tables

router: Router = Router()


async def wait_msg(msg: types.Message, text: str):
    emj_list = ['🌕', '🌖', '🌗', '🌘', '🌑', '🌒', '🌓', '🌔']
    message = await msg.answer(f'{text}\n\nОжидайте пожалуйста, я очень стараюсь {emj_list[0]}')
    i = 1
    while main_dict[msg.chat.id]['wait']:
        await message.edit_text(
            f'{text}\n\nОжидайте пожалуйста, я очень стараюсь {emj_list[i % len(emj_list)]}')
        i += 1
        time.sleep(.5)
    await message.delete()


@router.message(States.wait_theme_from_user)
async def wait_suggestion_topic(msg: types.Message, state: FSMContext):
    main_dict[msg.chat.id]['wait'] = True
    pprint(main_dict)
    create_task = asyncio.create_task(create_topic_suggestion(msg.chat.id, msg.text))
    wait_task = asyncio.create_task(
        wait_msg(msg, f'Формирую курсы на тему <b>"{msg.text}"</b>, которые могут быть вам подойти'))

    res, _ = await asyncio.gather(create_task, wait_task)
    if not res:
        await msg.answer('Кажется проиозошла ошибка, давайте попоробуем ещё раз')
    else:
        await select_suggestion_topic(msg, state)


async def select_suggestion_topic(msg: types.Message, state: FSMContext):
    topic_suggestion = main_dict[msg.chat.id]["new_course"]['topic_suggestion']

    answer_str = ''
    data_for_kb = {}
    suggestion_data = {}
    for i, item in enumerate(topic_suggestion):
        answer_str += f"<b>{item.get('short_title')}</b>\n"
        answer_str += item.get('description') + '\n\n'
        data_for_kb[f'recent_course_{i}'] = item.get('short_title')
        suggestion_data[f'recent_course_{i}'] = item

    main_dict[msg.chat.id]["new_course"]['topic_suggestion'] = suggestion_data

    pprint(main_dict)
    await msg.answer(answer_str + 'Выберите какой курс будем изучать',
                     reply_markup=create_kb(data_for_kb))


@router.callback_query(lambda c: 'recent_course_' in c.data)
async def create_course_program(cb: types.CallbackQuery, state: FSMContext):
    await state.set_state(States.select_suggestion_topic)
    await cb.message.edit_reply_markup(reply_markup=None)

    main_dict[cb.from_user.id]['wait'] = True
    course_data: dict[str: str] = main_dict[cb.from_user.id]["new_course"]['topic_suggestion'].get(cb.data)
    short_title = course_data.get('short_title')
    description = course_data.get('description')

    create_task = asyncio.create_task(create_detailed_table(cb.from_user.id, [short_title, description]))
    wait_task = asyncio.create_task(wait_msg(cb.message, f'Отличный выбор 👍\nСейчас я создам для вас оглавление курса:\n<b>{short_title}</b>'))
    res, _ = await asyncio.gather(create_task, wait_task)

    pprint(main_dict)

    if not res:
        await cb.message.answer('Кажется проиозошла ошибка, давайте попоробуем ещё раз')
    else:
        detailed_table_str = ''
        for chapter in main_dict[cb.from_user.id]["new_course"]['course']['detailed_table']:
            detailed_table_str += f'<b>Глава {chapter["chapter_number"]}. {chapter["chapter_title"]}</b>\n'
            for sub_chapters in chapter["sub_chapters"]:
                detailed_table_str += f'{chapter["chapter_number"]}.{sub_chapters["sub_chapter_number"]} {sub_chapters["sub_chapter_title"]}\n'
                for lesson in sub_chapters['lessons']:
                    detailed_table_str += f'{chapter["chapter_number"]}.{sub_chapters["sub_chapter_number"]}.{lesson["lesson_number"]} {lesson["lesson_title"]}\n'

        main_dict[cb.from_user.id]['new_course']['detailed_table_str'] = detailed_table_str

        await cb.message.answer(f"Составил программу курса на тему:\n"
                                f"<b>{main_dict[cb.from_user.id]['new_course']['course']['course_title']}</b>\n"
                                f"Продолжительность курса (часы): {main_dict[cb.from_user.id]['new_course']['course']['course_duration']}\n\n"
                                f'{detailed_table_str}\n\n'
                                'Создаём курс?',
                                reply_markup=create_kb(KbButtons.CREATE_COURSE_PROGRAM),
                                parse_mode='html')


async def running_course(cb: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    main_dict[cb.from_user.id]['wait'] = True
    course_id = db.insert_row(Tables.COURSES,
                              (
                                  cb.from_user.id,
                                  main_dict[cb.from_user.id]["new_course"]['course']['course_title'],
                                  main_dict[cb.from_user.id]["new_course"]['course']['course_duration'],
                                  main_dict[cb.from_user.id]['new_course']['detailed_table_str'],
                              )
                              )

    db.pars_and_save_road_map(course_id,
                              main_dict[cb.from_user.id]["new_course"]['course']['detailed_table'])
    id_sub_chapter, sub_chapter = db.get_first_sub_chapter(course_id)

    await cb.message.edit_reply_markup(reply_markup=None)

    create_task = asyncio.create_task(create_sections(cb.from_user.id,
                                                      main_dict[cb.from_user.id]['new_course']['detailed_table_str'],
                                                      sub_chapter))
    wait_task = asyncio.create_task(
        wait_msg(cb.message, f'Создаю контекнт для первого урока!'))
    res, _ = await asyncio.gather(create_task, wait_task)


    if not res:
        await cb.message.answer('Кажется проиозошла ошибка, давайте попоробуем ещё раз')
    else:
        lesson_ids = []
        answer_str = ''
        for i, lesson in enumerate(main_dict[cb.from_user.id]['new_course']['first_lessons'].get('themes')):
            less_id = db.insert_row(Tables.LESSONS, (id_sub_chapter, lesson, i+1))
            lesson_ids.append(less_id)
            answer_str += f'{i+1}. {lesson}\n'


        db.insert_row(Tables.PROGRESS_TABLE, (cb.from_user.id,
                                              course_id,
                                              lesson_ids[0],
                                              'theory'))
        pprint(main_dict)

        await state.set_state(States.running_course)
        await cb.message.answer(answer_str,
                                reply_markup=create_kb({'start': 'Начать первый урок!'}))
        await cb.answer()
