import asyncio
from typing import List
from gpt.prompts import CreateQuizzesPrompts, VocabularyPrompts
from base.base_gpt import BaseGPT


class VocabularyGPT(BaseGPT):
    DEFAULT_EXAMPLE_DATA_TEMPLATE = {
        "language": "English",
        "example": "I had to hit the brakes suddenly to avoid hitting the car in front of me.",
        "translation": "Я должен был резко нажать на тормоза, чтобы избежать столкновения с автомобилем, ехавшим впереди меня.",
        "language_code": "ru"
    }

    def __init__(self, user_id):
        super().__init__(user_id)

    async def get_new_words(self):
        topic = None
        level = None
        user_prompt = f"topic = {topic} level = {level}"

        try:
            pass
        except:
            pass

        self.set_message(system_prompt=VocabularyPrompts.INIT_LIST_WORDS,
                         user_prompt=user_prompt,
                         user_settings=(topic, level))

        init_list = await self.asc_gpt(self.message,
                                       template=self.DEFAULT_EXAMPLE_DATA_TEMPLATE)


class QuizGPT(BaseGPT):
    """
    Класс QuizGPT предназначен для создания и сохранения списка вопросов для квиза, а также для получения данных по
    каждому вопросу, включая варианты ответов, правильный ответ, объяснение и пример.

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


    def _save_questions(self, json_data: dict) -> List:
        questions = json_data.get('quiz').get('questions')
        self.data.add_quiz_question(questions)
        return questions


    async def _create_question_data(self, q: str) -> None:
        topic = self.data.get_data(self.data.QUIZ_TOPIC)
        self.set_message(system_prompt=CreateQuizzesPrompts.Q_DATA,
                         user_prompt="topic = {} question = {}",
                         user_settings=(topic, q))
        q_json_data = await self.asc_gpt(self.message,
                                         template=self.DEFAULT_QUESTION_DATA_TEMPLATE)
        if q_json_data:
            q_json_data["question"] = q
            self.data.add_quiz_full_data(q_json_data)
            self.data.counter(self.data.QUIZZES_TO_GO, 1)


    async def get_new_quizzes(self) -> None:
        self.data.set_flag_gpt_process(1)

        topic = self.data.get_data(self.data.QUIZ_TOPIC)
        level = self.data.get_data(self.data.QUIZ_LEVEL)
        user_prompt = "тема = {}\nуровень сложности = {}"
        try:
            completed_quiz = ', '.join(self.data.get_quiz_questions(
                self.data.get_data(self.data.QUIZ_LIST)
            ))
            user_prompt += f'список пройденных квизов = {completed_quiz}'
        except:
            pass


        # Запрашиваем у GPT список вопросов
        self.set_message(system_prompt=CreateQuizzesPrompts.Q_LIST,
                         user_prompt=user_prompt,
                         user_settings=(topic, level))

        init_list = await self.asc_gpt(self.message,
                                       template=self.DEFAULT_LIST_JSON_TEMPLATE)


        # Сохраняем этот список
        if int(self.data.get_flag_gpt_process()):
            if not init_list:
                return False

            questions = self._save_questions(init_list)

            tasks = [self._create_question_data(q) for q in questions]
            await asyncio.gather(*tasks)

        self.data.set_flag_gpt_process(0)