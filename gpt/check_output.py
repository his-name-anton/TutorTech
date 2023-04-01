import re


def has_russian(text, minimum=1):
    pattern = re.compile("[а-яА-Я]+")
    matches = pattern.findall(text)
    return len(matches) >= minimum


def check_q_list(json_data):
    if "quiz" not in json_data:
        print(f"json don't have key 'quiz'")
        return False
    if "questions" not in json_data.get('quiz'):
        print(f"json don't have key 'questions'")
        return False
    if not isinstance(json_data.get('quiz').get("questions"), list):
        print(f"value in questions is not list")
        return False

    q_list = json_data.get('quiz').get('questions')
    checked_list = []
    for q in q_list:
        if q is dict:
            q_str = q.get('question')
            if not has_russian(q_str):
                print(f'{q} is not on russian')
                return False
            checked_list.append(q_str)
        else:
            if not has_russian(q):
                print(f'{q} is not on russian')
                return False
            checked_list.append(q)

    return checked_list


def check_q_data(json_data):
    if not isinstance(json_data.get('answer_choices'), list):
        print('answer_choices is not list')
        return False
    for item in json_data.get('answer_choices'):
        if not isinstance(item, str):
            print('answer is not str')
            return False
        if len(item) == 0:
            print('answer == 0')
            return False

    if not isinstance(json_data.get('correct_answer'), int):
        try:
            json_data['correct_answer'] = int(json_data['correct_answer'])
        except Exception as ex:
            print(f"can't change type {json_data['correct_answer']}")
            return False

    if not isinstance(json_data.get('explanation'), str):
        print('explanation is not str')
        return False

    if not isinstance(json_data.get('example'), str):
        print('example is not str')
        return False

    return True
