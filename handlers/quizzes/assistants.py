from aiogram import types
from bs4 import BeautifulSoup

from database.dbw import Tables, db
from menu.other import main_dict


def save_quizzes_data_in_db(chat_id):
    # LOGIN IN DB
    start_index = main_dict[chat_id]['quizz']['counter_all_quiz']
    quizzes_list = main_dict[chat_id]['quizz']['quizzes_list']
    id_quiz = main_dict[chat_id]['quizz']['id_quiz']

    for index in range(start_index, len(quizzes_list)):
        question_json = quizzes_list[index]
        # log question
        q_id = db.insert_row(Tables.QUIZZES_QUESTIONS,
                             (id_quiz,
                              question_json['question'],
                              question_json['explanation'],
                              question_json['example']))
        print(f'iter: {index} сохранил вопрос: {question_json["question"]}')
        answer_choices = question_json['answer_choices']
        correct_answer = int(question_json['correct_answer'])

        # log options
        for i, answer in enumerate(answer_choices):
            is_correct = 1 if i == correct_answer else 0
            db.insert_row(Tables.QUIZZES_OPTIONS,
                          (q_id,
                           answer,
                           is_correct))
            print(f'Сохранил ответы {answer}')

        print('\n\n')


def text_after_answer(chat_id: int, is_correct: bool) -> str:
    cur_quiz = main_dict[chat_id]['quizz']['current_quizz']
    correct_answer = cur_quiz.get('answer_choices')[int(cur_quiz.get('correct_answer'))].replace('<br>', '').replace(
        '<br/>', '')
    explanation = cur_quiz.get("explanation").replace('<br>', '').replace('<br/>', '')
    example = cur_quiz.get("example").replace('<br>', '').replace('<br/>', '')

    if is_correct:
        result_text = 'Верно! 😎\n' \
                      f'И всё же немного теории: <i>{explanation}</i>\n\nПример: {example}'
    else:
        result_text = 'Неверно 🥲\n' + \
                      f"<b>Правильный ответ</b>: <b>{correct_answer}</b>\n\n" + \
                      f'<b>Пояснение</b>: <i>{explanation}</i>\n\n' \
                      f'<b>Пример</b>: {example}'

    statistic_text = f"Пройдено квизов: {main_dict[chat_id]['quizz']['counter_all_quiz']}\n" \
                     f"Верных ответов: {main_dict[chat_id]['quizz']['counter_right_answers']}"

    text = f"<b>Вопрос</b>: {cur_quiz.get('question')}\n\n{result_text}\n\n{statistic_text}"
    formatted_text = str(BeautifulSoup(text, "html.parser"))
    return formatted_text


def update_current_quiz(chat_id: int, message: types.Message) -> str:

    main_dict[chat_id]['quizz']['iter'] += 1
    quizzes_list: dict = main_dict[chat_id]['quizz']['quizzes_list']
    iter: int = main_dict[chat_id]['quizz']['iter']
    quizz: dict = quizzes_list[iter]
    question: str = quizz.get('question')
    answer_choices: list = quizz.get('answer_choices')
    correct_answer: int = quizz.get('correct_answer')
    explanation: str = quizz.get('explanation')
    example: str = quizz.get('example')

    # set data
    main_dict[chat_id]['quizz']['current_quizz'] = {"question": question,
                                                    "answer_choices": answer_choices,
                                                    "correct_answer": correct_answer,
                                                    "explanation": explanation,
                                                    "example": example,
                                                    "quiz_msg": message}

    short_top_list = ['A', 'B', 'C', 'D']
    if any(len(item) >= 100 for item in answer_choices):
        question += '\n\n<b>Варианты ответа</b>:\n'
        for index, item in enumerate(answer_choices):
            question += f'({short_top_list[index]}) {item}\n'
        answer_choices = short_top_list

    text = f'<b>Вопрос</b>: {question}'
    formatted_text = str(BeautifulSoup(text, "html.parser"))

    return formatted_text
