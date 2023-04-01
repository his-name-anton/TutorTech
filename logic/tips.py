import re


def _has_russian(text, minimum=1) -> bool:
    pattern = re.compile("[а-яА-Я]+")
    matches = pattern.findall(text)
    return len(matches) >= minimum


def _good_len_str(string) -> bool:
    return True if len(string) > 0 else False


class Tips:
    DICT_TEMPlATE = {
        "tips_pack_title": 'title',
        "tips_themes": [
            "theme 1",  "theme 2",  "theme 3",  "theme 4",
            "theme 5", "theme 6",  "theme 7",  "theme 8",
            "theme 9", "theme 10",
        ]
    }

    def __init__(self):
        pass

    def _check_dict_structure(self, dict_to_check: dict, dict_template: dict = None) -> bool:
        """
        Функция для проверки структуры словаря и типов данных ключей.

        :param dict_to_check: словарь, структуру которого нужно проверить.
        :param dict_template: словарь-шаблон с требуемой структурой и типами данных ключей.
        :return: True, если структура и типы данных совпадают, и False в противном случае.
        """

        dict_template = self.DICT_TEMPlATE if dict_template is None else dict_template

        # Проверяем, что тип аргументов является словарем
        if not isinstance(dict_to_check, dict):
            return False

        # Проверяем, что количество ключей совпадает
        if len(dict_to_check) != len(dict_template):
            return False

        # Проверяем, что все ключи из шаблона присутствуют в словаре для проверки
        if not all(key in dict_to_check for key in dict_template):
            return False

        # Проверяем, что все значения ключей имеют правильный тип данных
        for key, value in dict_to_check.items():
            # Если значение является словарем, рекурсивно проверяем его структуру
            if isinstance(value, dict):
                result = self.check_dict_structure(dict_to_check[key], dict_template[key])
                if not result:
                    return False
            # Иначе проверяем, что значение ключа совпадает со значением из шаблона
            else:
                if not isinstance(value, type(dict_template[key])):
                    return False

                # Проверка словаря на типи элементов
                if isinstance(value, list):
                    type_in_list = type(dict_template[key][0])
                    for item in value:
                        if not isinstance(item, type_in_list):
                            return False
                        if isinstance(item, str):
                            if not _good_len_str(value):
                                return False

                # проверка на длину строки
                if isinstance(value, str):
                    if not _good_len_str(value):
                        return False

                # проверка на русский язык
                if key == 'tips_themes':
                    if not any(_has_russian(item) for item in value):
                        print('Нет вопросов на русском')
                        return False

        # Если все проверки прошли успешно, возвращаем True
        return True




check_dict = {
        "tips_pack_title": 'asd',
        "tips_themes": [
            "asd",  "asd",  "qwe",  "qwe",
        ]
    }

t = Tips()

print(t.check_dict_structure(check_dict))