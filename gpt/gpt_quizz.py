import asyncio
import datetime
import json
from menu.other import main_dict
import openai
import os
from dotenv import find_dotenv, load_dotenv
from gpt.prompts import CreateQuizzesPrompts
from openai import OpenAIError
import concurrent.futures

load_dotenv(find_dotenv())
openai.api_key = os.getenv('OPENAI_KEY')


async def generate_q_list(chat_id: int, topic: str, level: int) -> bool:
    print(f'start generate_q_list at : {datetime.datetime.now().strftime("%H:%M:%S")}')

    quizzes_complete = ', '.join(main_dict[chat_id]['quizz']['q_list'])
    message = [{'role': 'system',
                'content': CreateQuizzesPrompts.Q_LIST},
               {'role': 'user',
                'content': f"""topic = {topic}
                            level of difficulty = {level}
                            list of quizzes completed = {quizzes_complete}"""}]

    try:
        response = await asyncio.to_thread(openai.ChatCompletion.create,
                                           model="gpt-3.5-turbo",
                                           messages=message)
    except OpenAIError as er:
        print(er)
        main_dict[chat_id]['wait'] = False
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

    q_list = json_data.get('quiz').get('questions')
    check_q_list = []
    for q in q_list:
        if q is dict:
            check_q_list.append(q.get('question'))
        else:
            check_q_list.append(q)

    main_dict[chat_id]['quizz']['q_list'].extend(check_q_list)
    run_get_q_data(chat_id)
    return True


def gpt_q_data(chat_id, q):
    print(f'get q data for q: {q}\nat: {datetime.datetime.now().strftime("%H:%M:%S")}')
    topic = main_dict[chat_id]['quizz']['topic']
    message = [{'role': 'system',
                'content': CreateQuizzesPrompts.Q_DATA},
               {'role': 'user',
                'content': f"""topic = {topic}
                            question = {q}"""}]

    try:
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=message)
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

    json_data['question'] = q
    main_dict[chat_id]['quizz']['quizzes_list'].append(json_data)
    main_dict[chat_id]["quizz"]['quizzes_to_go'] += 1
    print(f'Составлен квиз по вопросу: {q}')


def run_get_q_data(chat_id):
    print('run_get_q_data')
    q_list = main_dict[chat_id]['quizz']['q_list']
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(gpt_q_data, chat_id, q) for q in q_list]
        for future in concurrent.futures.as_completed(futures):
            future.result()

    main_dict[chat_id]['wait'] = False
