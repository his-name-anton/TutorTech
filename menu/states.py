from aiogram.fsm.state import State, StatesGroup


class States(StatesGroup):
    initial = State()
    wait_theme_from_user = State()
    select_suggestion_topic = State()
    running_course = State()

    wait_topic_for_quizzes = State()
    solving_quiz = State()

    wait_topic_for_words = State()