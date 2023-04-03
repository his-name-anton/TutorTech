import datetime
import json
import pickle
from pprint import pprint
from typing import Any, List
import redis
from aiogram import types
from aiogram.types import Message, Chat, User, InlineKeyboardMarkup, InlineKeyboardButton


def decode_utf8(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if isinstance(result, bytes):
            try:
                return result.decode('utf-8')
            except:
                return None
        elif isinstance(result, list):
            return [r.decode('utf-8') if isinstance(r, bytes) else r for r in result]
        elif isinstance(result, dict):
            return {k.decode('utf-8'): v.decode('utf-8') if isinstance(v, bytes) else v for k, v in result.items()}
        else:
            return result

    return wrapper


class BaseRedis:
    """
    Класс, предоставляющий базовую реализацию доступа к Redis-хранилищу.
    """

    USER = "user"

    def __init__(self, user_id, name=None):
        """
        Инициализирует объект BaseRedis.

        :param user_id: идентификатор пользователя.
        """
        self.user_id = user_id
        self.cash: redis.Redis = redis.Redis(host='localhost', port=6379, db=0)
        self.name = "pass" if not name else name
        self.base_path = f'user:{self.user_id}:{self.name}:'

    def set_data(self, path, value):
        """
        Устанавливает значение данных по заданному пути.

        :param path: путь к данным.
        :param value: значение для установки.
        """
        full_path = self.base_path + path
        self.cash.set(full_path, value)

    @decode_utf8
    def get_data(self, path=None):
        """
        Получает данные по заданному пути.

        :param path: путь к данным.
        :return: значение данных.
        """
        if not path:
            full_path = self.base_path[:-1]
        else:
            full_path = self.base_path + path

        if self.cash.type(full_path).decode('utf-8') == 'list':
            return self.cash.lrange(full_path, 0, -1)

        value = self.cash.get(full_path)
        try:
            value = int(value)
        except:
            pass
        return value

    @decode_utf8
    def get_keys(self) -> list:
        """
        Получает список ключей данных, находящихся по текущему пути.

        :return: список ключей.
        """
        return self.cash.keys(self.base_path + '*')

    def remove_user_data(self, keys: str | bool | list = None):
        """
        Удаляет данные пользователя.

        :param keys: список ключей, данные которых нужно удалить.
        """
        if keys:
            if keys is str:
                self.cash.delete(self.base_path + keys)
            if keys is list:
                self.cash.delete(self.base_path + ' '.join(keys))
        else:
            keys_to_delete = self.cash.keys(self.base_path + '*')

            if keys_to_delete:
                self.cash.delete(*keys_to_delete)



class QuizRedis(BaseRedis):
    """
    Класс для работы с квизом в Redis.
    Наследует класс BaseRedis.

    Атрибуты:
    ---------
    QUIZ_BASE_DATA : str
        Ключ для хранения базовых данных квиза в Redis.
    QUIZ_TOPIC : str
        Ключ для хранения темы квиза в Redis.
    QUIZ_LEVEL : str
        Ключ для хранения уровня квиза в Redis.
    CURRENT_QUIZ : str
        Ключ для хранения текущего вопроса квиза в Redis.
    CUR_Q : str
        Ключ для хранения номера текущего вопроса квиза в Redis.
    CUR_OPT : str
        Ключ для хранения списка вариантов ответов текущего вопроса квиза в Redis.
    CUR_CORRECT : str
        Ключ для хранения правильного ответа на текущий вопрос квиза в Redis.
    CUR_EXPLANATION : str
        Ключ для хранения пояснения к текущему вопросу квиза в Redis.
    CUR_EXAMPLE : str
        Ключ для хранения примера к текущему вопросу квиза в Redis.
    COUNTER : str
        Ключ для хранения счетчика ответов в Redis.
    RIGHT_ANSWERS : str
        Ключ для хранения количества правильных ответов в Redis.
    COUNT_ANSWERS : str
        Ключ для хранения общего количества ответов в Redis.
    INDEX_QUIZ : str
        Ключ для хранения индекса текущего вопроса в Redis.
    QUIZZES_TO_GO : str
        Ключ для хранения количества оставшихся вопросов квиза в Redis.
    MESSAGE : str
        Ключ для хранения сообщения в Redis.
    QUIZ_MSG : str
        Ключ для хранения сообщения с вопросом в Redis.
    MAIN_MSG : str
        Ключ для хранения основного сообщения в Redis.
    QUIZ_LIST : str
        Ключ для хранения списка вопросов квиза в Redis.
    QUIZZES_DATA : str
        Ключ для хранения списка всех данных квизов в Redis.
    PROCESS : str
        Ключ для хранения состояния процесса в Redis.
    GPT_PROCESS : str
        Ключ для хранения состояния процесса генерации ответа GPT в Redis.
    """

    # quiz base data
    QUIZ_BASE_DATA = 'quiz_base_data'
    QUIZ_TOPIC = 'quiz_topic'
    QUIZ_LEVEL = 'quiz_level'
    QUIZ_ID = 'id_quiz'

    # current quiz path
    CURRENT_QUIZ = "current_quiz"
    CUR_Q = "cur_q"
    CUR_OPT = "cur_opt"
    CUR_CORRECT = "cur_correct"
    CUR_EXPLANATION = 'cur_explanation'
    CUR_EXAMPLE = 'cur_example'

    # counter path
    COUNTER = "counter"
    RIGHT_ANSWERS = "right_answers"
    COUNT_ANSWERS = "count_answers"
    INDEX_QUIZ = "index_quiz"
    QUIZZES_TO_GO = "quizzes_to_go"

    # message path
    MESSAGE = "message"
    QUIZ_MSG = "quiz_msg"
    MAIN_MSG = "main_msg"

    # quiz json list path
    QUIZ_LIST = "quiz_list"
    QUIZZES_DATA = 'quizzes_data'

    # process path
    PROCESS = "process"
    GPT_PROCESS = "gpt_process"

    def __init__(self, user_id, name):
        """
        Конструктор класса QuizRedis.

        Параметры:
        ---------
        user_id : str
            Идентификатор пользователя.
        """
        super().__init__(user_id)
        self.name = 'quiz'
        self.base_path = f'user:{self.user_id}:{name}:'

    def set_current_quiz(self, **kwargs: Any):
        """
        Метод для сохранения текущего вопроса теста.

        :param kwargs: словарь с ключами CUR_Q, CUR_OPT, CUR_CORRECT, CUR_EXPLANATION, CUR_EXAMPLE
        :return: None
        """
        pipeline = self.cash.pipeline()

        pipeline.set(self.base_path + self.CUR_Q, kwargs.get(self.CUR_Q))
        pipeline.set(self.base_path + self.CUR_OPT, json.dumps(kwargs.get(self.CUR_OPT)))
        pipeline.set(self.base_path + self.CUR_CORRECT, kwargs.get(self.CUR_CORRECT))
        pipeline.set(self.base_path + self.CUR_EXPLANATION, kwargs.get(self.CUR_EXPLANATION))
        pipeline.set(self.base_path + self.CUR_EXAMPLE, kwargs.get(self.CUR_EXAMPLE))

        pipeline.execute()

    @decode_utf8
    def get_current_quiz(self, key_list: list = None) -> List:
        """
        Метод для получения сохраненного текущего вопроса теста.

        :param key_list: список ключей, которые нужно получить из сохраненных данных текущего вопроса теста
        :return: список значений сохраненных данных текущего вопроса теста
        """
        key_list = [
            self.CUR_Q,
            self.CUR_OPT,
            self.CUR_CORRECT,
            self.CUR_EXPLANATION,
            self.CUR_EXAMPLE,
        ] if key_list is None else key_list

        pipeline = self.cash.pipeline()

        for key in key_list:
            pipeline.get(self.base_path + key)

        return pipeline.execute()

    def update_counter_after_answer(self, is_correct: bool) -> None:
        """
        Метод для обновления счетчика правильных ответов и общего числа ответов на текущий вопрос теста.

        :param is_correct: флаг, указывающий, был ли дан правильный ответ на текущий вопрос теста
        :return: None
        """
        pipeline = self.cash.pipeline()

        pipeline.set(self.base_path + self.COUNT_ANSWERS, self.cash.get(self.base_path + self.COUNT_ANSWERS) + 1)
        pipeline.set(self.base_path + self.INDEX_QUIZ, self.cash.get(self.base_path + self.INDEX_QUIZ) + 1)
        if is_correct:
            pipeline.set(self.base_path + self.RIGHT_ANSWERS, self.cash.get(self.base_path + self.RIGHT_ANSWERS) + 1)

        pipeline.execute()

    def init_counter(self) -> None:
        """
        Метод для инициализации счетчика правильных ответов и общего числа ответов на текущий вопрос теста.

        :return: None
        """
        pipeline = self.cash.pipeline()

        pipeline.set(self.base_path + self.COUNT_ANSWERS, 0)
        pipeline.set(self.base_path + self.INDEX_QUIZ, -1)
        pipeline.set(self.base_path + self.RIGHT_ANSWERS, 0)

        pipeline.execute()

    def add_quiz_question(self, *args):
        """
        Метод для добавления новых вопросов в список вопросов теста.

        :param args: новые вопросы теста
        :return: None
        """
        pipeline = self.cash.pipeline()

        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            for item in args[0]:
                pipeline.rpush(self.base_path + self.QUIZ_LIST, item)
        else:
            for item in args:
                pipeline.rpush(self.base_path + self.QUIZ_LIST, item)
        pipeline.execute()

    def add_quiz_full_data(self, value: dict) -> None:
        """
        Метод для добавления полной информации нового кивза

        :param value: Данные о новом квизе
        :return: None
        """
        self.cash.lpush(self.base_path + self.QUIZZES_DATA, json.dumps(value))

    def get_quiz_full_data(self) -> List[dict]:
        """
        Метод для получения списка полной информации всех добавленных квизов

        :return: List[dict]
        """
        quiz_list = self.cash.lrange(self.base_path + self.QUIZZES_DATA, 0, -1)
        transformed_quiz_list = [json.loads(item) for item in quiz_list]
        return transformed_quiz_list

    @decode_utf8
    def get_quiz_questions(self):
        """
        Получить список вопросов из базы вопросов.

        :return: список вопросов
        """
        return self.cash.lrange(self.base_path + self.QUIZ_LIST, 0, -1)

    def set_flag_gpt_process(self, flag: int = 1) -> None:
        """
        Установить флаг процесса GPT.

        :param flag: устанавливаемый флаг
        """
        self.cash.set(self.base_path + self.GPT_PROCESS, flag)

    @decode_utf8
    def get_flag_gpt_process(self) -> int:
        """
        Получить значение флага процесса GPT.

        :return: значение флага процесса GPT
        """
        return self.cash.get(self.base_path + self.GPT_PROCESS)

    @decode_utf8
    def counter(self, path: str, value: int) -> int:
        """
        Увеличить или уменьшить счетчик на заданное значение.

        :param path: путь к счетчику
        :param value: значение, на которое нужно увеличить или уменьшить счетчик
        :return: новое значение
        """
        if value > 0:
            return self.cash.incr(self.base_path + path)
        else:
            return self.cash.decr(self.base_path + path)

    def set_message(self, path, message: types.Message) -> None:
        """
        Метод сериализует объект aiogram Message и сохраняет его в redis

        :param path: путь куда сохранить сериализованный объект
        :param message: объект Message, который нужно сериализовать и сохранить
        :return: None
        """
        message_bytes = pickle.dumps(message)
        self.cash.set(self.base_path + path, message_bytes)


    def get_message(self, path) -> types.Message:
        """
        Метод достаёт байтовую строку, которая содержит объект Message aiogram из переданного пути.
        Десериализуют его и вовзращает

        :param path: путь к сообщению, которые нужно доставть
        :return: объект Message aiogram
        """
        message_bytes_from_redis = self.cash.get(self.base_path + path)
        message = pickle.loads(message_bytes_from_redis)
        return message