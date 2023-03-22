import asyncio
import json
import re
from json import JSONDecodeError
from pprint import pprint
from menu.other import main_dict

import openai
import os
from dotenv import find_dotenv, load_dotenv

from database.dbw import Tables, db
from gen_course.prompts import CreateCoursePrompts

load_dotenv(find_dotenv())

openai.api_key = os.getenv('OPENAI_KEY')


async def create_topic_suggestion(chat_id: int, topic: str) -> dict:
    message = [{'role': 'system',
                'content': CreateCoursePrompts.CREATE_SUGGESTIONS_COURSE},
               {'role': 'user',
                'content': f"""I need get clarify for topick: {topic}"""}]
    response = await asyncio.to_thread(openai.ChatCompletion.create,
                                       model="gpt-3.5-turbo",
                                       messages=message)
    main_dict[chat_id]['wait'] = False
    text = response['choices'][0]['message']['content']
    try:
        json_data: list = json.loads(text[text.index('<json>') + len('<json>'):text.index('</json>')])
    except Exception:
        return False

    main_dict[chat_id]["new_course"]['topic_suggestion'] = json_data
    return True


async def create_detailed_table(chat_id: int, data: list[str, str]) -> dict:
    message = [{'role': 'system',
                'content': CreateCoursePrompts.SYSTEM_CONTENT_DETAILED_TABLE_V3},
               {'role': 'user', 'content': f"""\ngiven:\ntopic = {data[0]} description = {data[1]}"""}]

    response = await asyncio.to_thread(openai.ChatCompletion.create,
                                       model="gpt-3.5-turbo",
                                       messages=message)
    text = response['choices'][0]['message']['content']
    try:
        json_data = json.loads(text[text.find('<json>') + len('<json>'): text.find('</json>')])
    except Exception:
        return False

    course_title = text[text.find('<course_title>') + len('<course_title>'):text.find('</course_title>')]
    course_duration = text[text.find('<course_time>') + len('<course_time>'):text.find('</course_time>')]

    main_dict[chat_id]['wait'] = False
    main_dict[chat_id]["new_course"]['course'] = {'user_request': data,
                                                  'course_title': course_title,
                                                  'course_duration': course_duration,
                                                  'detailed_table': json_data}
    pprint(json_data)
    return True


async def create_sections(chat_id: int,
                          detailed_table_text: int,
                          sub_chapter: str) -> dict:


    user_content = """course name = {}
                    the current topic on which I need lessons = {}
                    previous topics covered  = {}
                    topics that will be in the future = {}"""

    message = [{'role': 'system',
                'content': CreateCoursePrompts.SYSTEM_CREATE_SECTIONS_V2},
               {'role': 'user',
                'content': f"""course structure:\n
                            {detailed_table_text}\n
                            Create themes for the topic: {sub_chapter}"""}]
    response = await asyncio.to_thread(openai.ChatCompletion.create,
                                       model="gpt-3.5-turbo",
                                       messages=message)
    text = response['choices'][0]['message']['content']
    try:
        json_data = json.loads(text[text.find('<json>') + len('<json>'): text.find('</json>')])
    except Exception:
        return False
    main_dict[chat_id]['wait'] = False
    main_dict[chat_id]["new_course"]['first_lessons'] = json_data
    return True
