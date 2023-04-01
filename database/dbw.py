import sqlite3


class Tables:
    TABLES = {
        'users': ['chat_id', 'first_name', 'last_name', 'user_name'],
        'courses': ['chat_id', 'name', 'duration', 'detailed_table_text'],
        'chapters': ['course_id', 'name', 'sequence_number'],
        'sub_chapters': ['chapter_id', 'name', 'sequence_number'],
        'lessons': ['sub_chapter_id', 'name', 'sequence_number'],
        'progress_table': ['chat_id', 'course_id', 'lesson_id', 'status'],
        'quizzes': ['topic'],
        'quizzes_questions': ['quiz_id', 'question', 'explanation', 'example'],
        'question_options': ['question_id', 'option', 'is_correct']
    }
    USERS = 'users'
    COURSES = 'courses'
    CHAPTERS = 'chapters'
    SUB_CHAPTERS = 'sub_chapters'
    LESSONS = 'lessons'
    PARTS_LESSON = 'parts_lesson'
    PROGRESS_TABLE = 'progress_table'
    QUIZZES = "quizzes"
    QUIZZES_QUESTIONS = "quizzes_questions"
    QUIZZES_OPTIONS = "question_options"


class DataBase:

    def __init__(self):
        self.conn = sqlite3.connect('/Users/antonlarin/PycharmProjects/TutorTech/database/DB.db')
        self.curs = self.conn.cursor()

    def insert_row(self, table: str, values: tuple) -> int:
        """
        Inserts a row of data into the specified table in the SQLite database.

        Args:
        table (str): The name of the table to insert the data into.
        values (tuple): A tuple containing the values to insert into the table. The order of values must match the order of columns in the table.

        Returns:
        int: The ID of the last row inserted.

        Raises:
        ValueError: If the specified table is not found in the database.

        Notes:
        - This function assumes that the database connection has already been established.
        - The function first checks if the specified table exists in the database, and raises a ValueError if it does not.
        - The function constructs the SQL query dynamically, based on the number of columns in the table and the number of values to insert.
        - The function uses a parameterized query to prevent SQL injection attacks.
        - The function returns the ID of the last row inserted, which can be useful for tracking newly inserted records.

        Example usage:
        conn = sqlite3.connect('my_database.db')
        my_table = 'users'
        my_values = ('John', 'Doe', 'johndoe@example.com')
        row_id = insert_row(conn, my_table, my_values)
        """

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

    def pars_and_save_road_map(self, course_id: int, json_data: dict):
        for chapter in json_data:
            chapter_number = chapter.get('chapter_number')
            title = chapter.get('title')
            sections = chapter.get('sub_chapters')
            chapter_id = self.insert_row(Tables.CHAPTERS, (course_id, title, chapter_number))
            for sub_chapters in sections:
                chapter_number = sub_chapters.get('chapter_number')
                chapter_title = sub_chapters.get('chapter_title')
                sub_chapter_id = self.insert_row(Tables.SUB_CHAPTERS, (chapter_id, chapter_title, chapter_number))
                for lesson in sub_chapters['lessons']:
                    lesson_title = lesson["lesson_title"]
                    lesson_number = lesson["lesson_number"]
                    self.insert_row(Tables.LESSONS, (sub_chapter_id, lesson_title, lesson_number))


    def get_detailed_table(self, course_id) -> str:
        with self.conn:
            self.curs.execute(f"SELECT detailed_table_text FROM courses WHERE id = {course_id} limit 1")
            res = self.curs.fetchall()
            return res[0][0]


    def get_first_sub_chapter(self, course_id) -> list:
        with self.conn:
            self.curs.execute(f"""
                select sc.id, sc.name
                from courses c
                join chapters c2 on c.id = c2.course_id
                join sub_chapters sc on c2.id = sc.chapter_id
                where c.id = {course_id}
                and c2.sequence_number = 1
                and sc.sequence_number = 1
                limit 1
            """)
            res = self.curs.fetchall()
            return res[0]



db = DataBase()
