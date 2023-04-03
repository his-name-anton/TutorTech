import math
import re
from pprint import pprint

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bs4 import BeautifulSoup

from redis_cash.redis_client import QuizRedis


# 1. Должен сделать счётчик
# 2. Должен отдавать итоговой текст для сообщения
# 3. Должен отдавать клавиатуру
# 4. логировать данные


class BaseAssistant:
    def __init__(self, user_id):
        self.user_id = user_id
        self.data = QuizRedis(user_id)

    def _create_kb(self, items: dict[str: str], long_f: object = True) -> InlineKeyboardBuilder:
        if long_f:
            board = InlineKeyboardBuilder()
            for key, value in items.items():
                board.row(InlineKeyboardButton(
                    text=value,
                    callback_data=key
                ))
        else:
            buttons = []
            row = []
            for key, value in items.items():
                row.append(InlineKeyboardButton(
                    text=value,
                    callback_data=key
                ))
                if len(row) == 2:
                    buttons.append(row)
                    row = []
            if len(row) == 1:
                buttons.append(row)
            board = InlineKeyboardBuilder(buttons)
        return board.as_markup()

    def _generate_text(self, *args) -> str:
        for item in args:
            if not isinstance(item, str):
                raise ValueError('Тип аргументов должен быть строкой')
        return ''.join(args)

    def change_data_redis(self):
        pass

    def change_data_db(self):
        pass


class QuizAssistant(BaseAssistant):

    def __init__(self, user_id):
        super().__init__(user_id)

    def next_quiz(self) -> tuple[str, dict]:
        quiz_index = self.data.counter(self.data.INDEX_QUIZ, 1)
        quizzes_list: list = self.data.get_quiz_full_data()
        try:
            quizz: dict = quizzes_list[quiz_index]
        except IndexError:
            return False, False

        pprint(quizz)

        question: str = quizz.get('question')
        answer_choices: list = quizz.get('answer_choices')
        correct_answer: int = quizz.get('correct_answer')
        explanation: str = quizz.get('explanation')
        example: str = quizz.get('example')

        self.data.set_current_quiz(cur_q=question,
                                   cur_opt=answer_choices,
                                   cur_correct=correct_answer,
                                   cur_explanation=explanation,
                                   cur_example=example)

        short_top_list = ['A', 'B', 'C', 'D']
        if any(len(item) >= 100 for item in answer_choices):
            question += '\n\n<b>Варианты ответа</b>:\n'
            for index, item in enumerate(answer_choices):
                question += f'({short_top_list[index]}) {item}\n'
            answer_choices = short_top_list

        text = f'<b>Вопрос</b>: {question}'
        formatted_text = str(BeautifulSoup(text, "html.parser"))

        poll_kwargs = {'question': '❔',
                       'options': answer_choices,
                       'type': 'quiz',
                       'protect_content': True,
                       'is_anonymous': False,
                       'correct_option_id': correct_answer}

        return formatted_text, poll_kwargs

    def _process_tags(self, s):
        s = re.sub(r'<code>', r'<code>\n', s)
        s = re.sub(r'</code>', r'</code>\n', s)
        s = re.sub(f'<br>', '', s)
        s = re.sub(f'</br>', '', s)
        return s

    def process_answer_quiz(self, answer_index):
        q, opt, correct, explanation, example = self.data.get_current_quiz()

        # Обновляй счётчики
        self.data.counter(self.data.QUIZZES_TO_GO, -1)
        self.data.counter(self.data.COUNT_ANSWERS, 1)

        is_correct = False
        if int(answer_index) == int(correct):
            is_correct = True
            self.data.counter(self.data.RIGHT_ANSWERS, 1)

        correct_answer = self._process_tags(eval(opt)[int(correct)])
        explanation = self._process_tags(explanation)
        example = self._process_tags(example)

        count_answers = self.data.get_data(self.data.COUNT_ANSWERS)
        right_answers = self.data.get_data(self.data.RIGHT_ANSWERS)

        if is_correct:
            result_text = 'Верно! 😎\n' \
                          f'И всё же немного теории: <i>{explanation}</i>\n\nПример: {example}'
        else:
            result_text = 'Неверно 🥲\n' + \
                          f"<b>Правильный ответ</b>\n{correct_answer}\n\n" + \
                          f'<b>Пояснение</b>\n<i>{explanation}</i>\n\n' \
                          f'<b>Пример</b>\n{example}'

        statistic_text = f"Пройдено квизов: {count_answers}\n" \
                         f"Верных ответов: {right_answers}\n" \
                         f"% Верныйх ответов: {round((right_answers / count_answers) * 100)}%"

        text = f"<b>Вопрос</b>: {q}\n\n{result_text}\n\n{statistic_text}"
        formatted_text = str(BeautifulSoup(text, "html.parser"))
        keyboard = self._create_kb({'theory_question': 'Больше теории 📓',
                                    'cancel_quiz': 'Завершить 🛑',
                                    'next_quizz': 'Следующий ➡️'},
                                   long_f=False)
        return formatted_text, keyboard

    # def save_quizzes_data_in_db(chat_id):
    #     # LOGIN IN DB
    #     start_index = main_dict[chat_id]['quizz']['counter_all_quiz']
    #     quizzes_list = main_dict[chat_id]['quizz']['quizzes_list']
    #     id_quiz = main_dict[chat_id]['quizz']['id_quiz']
    #
    #     for index in range(start_index, len(quizzes_list)):
    #         question_json = quizzes_list[index]
    #         # log question
    #         q_id = db.insert_row(Tables.QUIZZES_QUESTIONS,
    #                              (id_quiz,
    #                               question_json['question'],
    #                               question_json['explanation'],
    #                               question_json['example']))
    #         print(f'iter: {index} сохранил вопрос: {question_json["question"]}')
    #         answer_choices = question_json['answer_choices']
    #         correct_answer = int(question_json['correct_answer'])
    #
    #         # log options
    #         for i, answer in enumerate(answer_choices):
    #             is_correct = 1 if i == correct_answer else 0
    #             db.insert_row(Tables.QUIZZES_OPTIONS,
    #                           (q_id,
    #                            answer,
    #                            is_correct))
    #             print(f'Сохранил ответы {answer}')
    #
    #         print('\n\n')

