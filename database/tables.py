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
    name VARCHAR(250),
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

conn.execute('''CREATE TABLE IF NOT EXISTS parts_lesson (
    id INTEGER PRIMARY KEY,
    lesson_id INTEGER REFERENCES lessons(id) ON DELETE CASCADE,
    text TEXT,
    sequence_number INTEGER,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')



conn.commit()
conn.close()