import asyncio
import json
import os
from typing import List, Any

import openai
from dotenv import load_dotenv, find_dotenv
from openai import OpenAIError
from gpt.prompts import CreateQuizzesPrompts
from redis_cash.redis_client import QuizRedis

load_dotenv(find_dotenv())

DEFAULT_GPT_MODEL = "gpt-3.5-turbo"


class BaseGPT:
    """
    Базовый класс для работы с GPT моделью OpenAI
    """
    def __init__(self, user_id):
        """
        Конструктор класса.

        :param user_id: идентификатор пользователя.
        """
        self.user_id = user_id
        self.chat_gpt = openai.ChatCompletion.create
        self.model_gpt = DEFAULT_GPT_MODEL
        self.template_init_list = None
        self.data = QuizRedis(user_id)

    openai.api_key = os.getenv('OPENAI_KEY')

    async def _create_request(self, message):
        """
        Асинхронная функция для создания запроса к GPT модели.

        :param message: сообщение для отправки.
        :return: ответ от модели в виде строки.
        """
        try:
            response = await asyncio.to_thread(self.chat_gpt,
                                               model=self.model_gpt,
                                               messages=message)
        except OpenAIError as er:
            print(er)
            return False
        return response['choices'][0]['message']['content']

    def _extract_json_from_text(self, text):
        """
        Функция для извлечения JSON данных из текста.

        :param text: текст, содержащий JSON данные.
        :return: словарь с JSON данными.
        """
        try:
            return json.loads(text[text.index('<json>') + len('<json>'):text.index('</json>')])
        except Exception as ex:
            try:
                return json.loads(text)
            except Exception as ex:
                try:
                    start = text.find('{')
                    json_string = text[start: text.rfind('}') + 1]
                    return json.loads(json_string)
                except Exception as ex:
                    print(f"Ошибка при загрузке данных JSON для текста:\n{text}")

    def _check_dict_structure(self, verified: dict, template: dict = None) -> bool:
        """
        Функция для проверки структуры словаря и типов данных ключей.

        :param verified: словарь, структуру которого нужно проверить.
        :param template: словарь-шаблон с требуемой структурой и типами данных ключей.
        :return: True, если структура и типы данных совпадают, и False в противном случае.
        """

        # Если шаблона нет, то сразу возвращаем True
        if not template:
            return True

        # Проверяем, что тип аргументов является словарем
        if not isinstance(verified, dict):
            return False

        # Проверяем, что количество ключей совпадает
        if len(verified) != len(template):
            return False

        # Проверяем, что все ключи из шаблона присутствуют в словаре для проверки
        if not all(key in verified for key in template):
            return False

        # Проверяем, что все значения ключей имеют правильный тип данных
        for key, value in verified.items():
            # Если значение является словарем, рекурсивно проверяем его структуру
            if isinstance(value, dict):
                result = self._check_dict_structure(verified[key], template[key])
                if not result:
                    return False
            # Иначе проверяем, что значение ключа совпадает со значением из шаблона
            else:
                if not isinstance(value, type(template[key])):
                    return False

                # Проверка словаря на типи элементов
                if isinstance(value, list):
                    type_in_list = type(template[key][0])
                    for item in value:
                        if not isinstance(item, type_in_list):
                            return False
                        if isinstance(item, str):
                            if not len(value) > 0:
                                return False

                # проверка на длину строки
                if isinstance(value, str):
                    if not len(value) > 0:
                        return False

        return True

    async def asc_gpt(self, message, **kwargs) -> dict:
        """
        Асинхронная функция для выполнения запроса к модели GPT-3.

        :param message: текстовое сообщение, для которого нужно получить ответ от модели.
        :param kwargs: дополнительные параметры функции.
            template - словарь-шаблон с требуемой структурой и типами данных ключей для получаемых данных.
        :return: словарь с полученными данными, если структура и типы данных соответствуют шаблону, иначе - None.
        """
        text = await self._create_request(message)
        json_data = self._extract_json_from_text(text)
        if self._check_dict_structure(json_data, kwargs.get('template')):
            return json_data


class VocabularyGPT(BaseGPT):
    DEFAULT_EXAMPLE_DATA_TEMPLATE = {
      "language": "English",
      "example": "I had to hit the brakes suddenly to avoid hitting the car in front of me.",
      "translation": "Я должен был резко нажать на тормоза, чтобы избежать столкновения с автомобилем, ехавшим впереди меня.",
      "language_code": "ru"
    }

    def __init__(self, user_id):
        super().__init__(user_id)


    def _create_message_words_list(self):
        pass



class QuizGPT(BaseGPT):
    """
    Класс QuizGPT предназначен для создания и сохранения списка вопросов для квиза, а также для получения данных по каждому вопросу, включая варианты ответов, правильный ответ, объяснение и пример.

    Атрибуты:
    DEFAULT_LIST_JSON_TEMPLATE: шаблон для создания JSON-структуры списка вопросов.
    DEFAULT_QUESTION_DATA_TEMPLATE: шаблон для создания JSON-структуры данных по каждому вопросу.
    user_id: идентификатор пользователя.

    Методы:
    init(self, user_id): инициализирует объект класса QuizGPT.
    _create_message_init_list(self): создает сообщение для запроса списка вопросов.
    _create_message_get_questions_data(self, q): создает сообщение для запроса данных по конкретному вопросу.
    _check_json_structure(self): проверяет структуру JSON-данных.
    _save_questions(self, json_data): сохраняет список вопросов.
    async _create_question_data(self, q): создает данные по конкретному вопросу.
    async get_new_quizzes(self): получает новый список вопросов и сохраняет их данные.

    Пример использования:
    quiz_gpt = QuizGPT(user_id=123)
    await quiz_gpt.get_new_quizzes()
    """
    DEFAULT_LIST_JSON_TEMPLATE = {
        "quiz": {
            "questions": [
                "string",
                "string",
                "string",
            ]
        }
    }

    DEFAULT_QUESTION_DATA_TEMPLATE = {
        "answer_choices": [
            "string",
            "string",
            "string",
            "string"
        ],
        "correct_answer": 0,
        "explanation": "string",
        "example": "string"
    }

    def __init__(self, user_id):
        super().__init__(user_id)
        self.template_init_list = self.DEFAULT_LIST_JSON_TEMPLATE
        self.template_question_data = self.DEFAULT_QUESTION_DATA_TEMPLATE

    def _create_message_init_list(self) -> list[dict[str, str | Any] | dict[str, str]]:
        topic = self.data.get_data(self.data.QUIZ_TOPIC)
        level = self.data.get_data(self.data.QUIZ_LEVEL)

        user_content = f"""тема = {topic}
                                    уровень сложности = {level}"""
        try:
            completed_quiz = ', '.join(self.data.get_quiz_questions(
                self.data.get_data(self.data.QUIZ_LIST)
            ))
            user_content += f'список пройденных квизов = {completed_quiz}'
        except:
            pass


        message = [{'role': 'system',
                    'content': CreateQuizzesPrompts.Q_LIST},
                   {'role': 'user',
                    'content': user_content}]
        return message

    def _create_message_get_questions_data(self, q) -> list[dict[str, str | Any] | dict[str, str]]:
        topic = self.data.get_data(self.data.QUIZ_TOPIC)

        message = [{'role': 'system',
                    'content': CreateQuizzesPrompts.Q_DATA},
                   {'role': 'user',
                    'content': f"""topic = {topic}
                                    question = {q}"""}]
        return message


    def _save_questions(self, json_data: dict) -> List:
        questions = json_data.get('quiz').get('questions')
        self.data.add_quiz_question(questions)
        return questions


    async def _create_question_data(self, q: str) -> None:
        q_json_data = await self.asc_gpt(self._create_message_get_questions_data(q),
                                         template=self.DEFAULT_QUESTION_DATA_TEMPLATE)
        if q_json_data:
            q_json_data["question"] = q
            self.data.add_quiz_full_data(q_json_data)
            self.data.counter(self.data.QUIZZES_TO_GO, 1)


    async def get_new_quizzes(self) -> None:
        self.data.set_flag_gpt_process(1)
        print('start get_new_quizzes')

        # Запрашиваем у GPT список вопросов
        init_list = await self.asc_gpt(
            self._create_message_init_list(),
            template=self.DEFAULT_LIST_JSON_TEMPLATE
        )

        if int(self.data.get_flag_gpt_process()):
            # Сохраняем этот список
            if not init_list:
                return False

            questions = self._save_questions(init_list)

            tasks = [self._create_question_data(q) for q in questions]
            await asyncio.gather(*tasks)

        print('end get_new_quizzes')
        self.data.set_flag_gpt_process(0)


