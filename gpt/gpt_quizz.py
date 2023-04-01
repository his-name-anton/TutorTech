import asyncio
import datetime
import json
from menu.other import main_dict
import openai
import os
from dotenv import find_dotenv, load_dotenv
from gpt.prompts import CreateQuizzesPrompts
from openai import OpenAIError
from gpt.check_output import check_q_data, check_q_list

load_dotenv(find_dotenv())
openai.api_key = os.getenv('OPENAI_KEY')


async def generate_q_list(chat_id: int, topic: str, level: int) -> bool:
    print(f'start generate_q_list at : {datetime.datetime.now().strftime("%H:%M:%S")}')

    quizzes_complete = ', '.join(main_dict[chat_id]['quizz']['q_list'])
    message = [{'role': 'system',
                'content': CreateQuizzesPrompts.Q_LIST},
               {'role': 'user',
                'content': f"""тема = {topic}
                            уровень сложности = {level}
                            список пройденных квизов = {quizzes_complete}"""}]

    try:
        response = await asyncio.to_thread(openai.ChatCompletion.create,
                                           model="gpt-3.5-turbo",
                                           messages=message)
    except OpenAIError as er:
        print(er)
        return False

    text = response['choices'][0]['message']['content']
    print(text)
    try:
        json_data: list = json.loads(text[text.index('<json>') + len('<json>'):text.index('</json>')])
    except Exception as ex:
        try:
            json_data: list = json.loads(text)
        except Exception as ex:
            print(f"Ошибка при загрузке данных JSON для текста:\n{text}")

            return False


    checked_list = check_q_list(json_data)
    if not checked_list:
        return False

    main_dict[chat_id]['quizz']['q_list'].extend(checked_list)

    await run_get_q_data(chat_id)
    return True


async def gpt_q_data(chat_id, q):
    print(f'Делаю квиз на вопрос: {q}')
    topic = main_dict[chat_id]['quizz']['topic']
    message = [{'role': 'system',
                'content': CreateQuizzesPrompts.Q_DATA},
               {'role': 'user',
                'content': f"""topic = {topic}
                            question = {q}"""}]

    try:
        response = await asyncio.to_thread(openai.ChatCompletion.create,
                                           model="gpt-3.5-turbo",
                                           messages=message)
    except OpenAIError as er:
        print(er)
        return False

    text = response['choices'][0]['message']['content']
    try:
        json_data: list = json.loads(text[text.index('<json>') + len('<json>'):text.index('</json>')])
    except Exception as ex:
        try:
            json_data: list = json.loads(text)
        except Exception as ex:
            print(f"Ошибка при загрузке данных JSON для текста:\n{text}")
            return False

    if not check_q_data(json_data):
        return False

    json_data['question'] = q
    main_dict[chat_id]['quizz']['quizzes_list'].append(json_data)
    main_dict[chat_id]["quizz"]['quizzes_to_go'] += 1

    print(f'Составлен квиз по вопросу: {q}')



async def run_get_q_data(chat_id):
    q_list = main_dict[chat_id]['quizz']['q_list']
    tasks = [gpt_q_data(chat_id, q) for q in q_list]
    await asyncio.gather(*tasks)
    main_dict[chat_id]['wait'] = False