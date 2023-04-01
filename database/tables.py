import sqlite3

conn = sqlite3.connect("DB.db")

conn.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    chat_id INTEGER NOT NULL UNIQUE,
    phone INTEGER,
    first_name TEXT,
    last_name TEXT,
    user_name TEXT,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')


# COURSE STRUCTURE
conn.execute('''CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY,
    chat_id INTEGER,
    name VARCHAR(250),
    duration VARCHAR(250),
    detailed_table_text TEXT,
    description TEXT,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')

conn.execute('''CREATE TABLE IF NOT EXISTS chapters (
    id INTEGER PRIMARY KEY,
    course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,
    name VARCHAR(250),
    sequence_number INTEGER,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')

conn.execute('''CREATE TABLE IF NOT EXISTS sub_chapters (
    id INTEGER PRIMARY KEY,
    chapter_id INTEGER REFERENCES chapters(id) ON DELETE CASCADE,
    name VARCHAR(250),
    sequence_number INTEGER,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')

conn.execute('''CREATE TABLE IF NOT EXISTS lessons (
    id INTEGER PRIMARY KEY,
    sub_chapter_id INTEGER REFERENCES sub_chapters(id) ON DELETE CASCADE,
    name VARCHAR(250),
    sequence_number INTEGER,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')

conn.execute('''CREATE TABLE IF NOT EXISTS progress_table (
    id INTEGER PRIMARY KEY,
    chat_id INTEGER, 
    course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,
    lesson_id INTEGER REFERENCES lessons(id) ON DELETE CASCADE,
    status VARCHAR(50),
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')

# quizzes
conn.execute('''CREATE TABLE IF NOT EXISTS quizzes (
    id INTEGER PRIMARY KEY,
    topic VARCHAR(100),
    title VARCHAR(100),
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')

conn.execute('''CREATE TABLE IF NOT EXISTS quizzes_questions (
    id INTEGER PRIMARY KEY,
    quiz_id INTEGER REFERENCES quizzes(id) ON DELETE CASCADE,
    question TEXT,
    explanation TEXT,
    example TEXT,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')

conn.execute('''CREATE TABLE IF NOT EXISTS question_options (
    id INTEGER PRIMARY KEY,
    question_id INTEGER REFERENCES quizzes_questions(id) ON DELETE CASCADE,
    option TEXT,
    is_correct INTEGER,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')




conn.commit()
conn.close()