import sqlite3


class Tables:
    TABLES = {
        'users': ['chat_id', 'first_name', 'last_name', 'user_name'],
        'courses': ['name'],
        'chapters': ['course_id', 'name', 'sequence_number'],
        'sub_chapters': ['chapter_id', 'name', 'sequence_number'],
        'lessons': ['sub_chapter_id', 'name', 'sequence_number'],
        'parts_lesson': ['lesson_id', 'text', 'sequence_number'],
    }
    USERS = 'users'
    COURSES = 'courses'


class DataBase:

    def __init__(self):
        self.conn = sqlite3.connect('/Users/antonlarin/PycharmProjects/TutorTech/database/DB')
        self.curs = self.conn.cursor()

    def insert_row(self, table: str, values: tuple) -> int:
        columns_list = Tables.TABLES.get(table)
        if columns_list:
            columns = ', '.join(columns_list)
        else:
            raise ValueError(f'Table {table} not find')
        sql = "INSERT INTO " + table + " (" + columns + ")" + " VALUES (" + ','.join(
            ['?' for _ in range(len(values))]) + ")"
        with self.conn:
            self.curs.execute(sql, values)
            return self.curs.lastrowid


db = DataBase()

print(db.insert_row(Tables.USERS, (1, 'asd', 'asd', None)))