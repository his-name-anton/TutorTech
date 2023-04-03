import asyncio
import json
import os
import openai
from typing import List, Dict
from dotenv import load_dotenv, find_dotenv
from openai import OpenAIError
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

        :param user_id: Идентификатор пользователя.
        """
        self.user_id = user_id
        self.chat_gpt = openai.ChatCompletion.create
        self.model_gpt = DEFAULT_GPT_MODEL
        self.template_init_list = None
        self.data = QuizRedis(user_id)
        self.message = []

    openai.api_key = os.getenv('OPENAI_KEY')

    async def _create_request(self, message):
        """
        Асинхронная функция для создания запроса к GPT модели.

        :param message: Сообщение для отправки.
        :return: Ответ от модели в виде строки.
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

        :param verified: Словарь, структуру которого нужно проверить.
        :param template: Словарь-шаблон с требуемой структурой и типами данных ключей.
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

    def __create_system_mesage(self, prompt: str) -> Dict:
        return {'role': 'system', 'content': prompt}

    def __create_user_message(self, prompt: str, *args: str) -> Dict:
        content = prompt.format(*args)
        return {'role': 'user', 'content': content}

    def set_message(self, **kwargs) -> List[Dict]:
        system_prompt = kwargs.get('system_prompt')
        user_prompt = kwargs.get('user_prompt')
        user_settings = kwargs.get('user_settings')
        system_message: Dict[str: str] = self.__create_system_mesage(system_prompt)
        user_message: Dict[str: str] = self.__create_user_message(user_prompt, *user_settings)
        self.message = [system_message, user_message]

    async def asc_gpt(self, message, **kwargs) -> dict:
        """
        Асинхронная функция для выполнения запроса к модели GPT-3.

        :param message: Текстовое сообщение, для которого нужно получить ответ от модели.
        :param kwargs: Дополнительные параметры функции.
            Template - словарь-шаблон с требуемой структурой и типами данных ключей для получаемых данных.
        :return: Словарь с полученными данными, если структура и типы данных соответствуют шаблону, иначе - None.
        """
        text = await self._create_request(message)
        json_data = self._extract_json_from_text(text)
        if self._check_dict_structure(json_data, kwargs.get('template')):
            return json_data