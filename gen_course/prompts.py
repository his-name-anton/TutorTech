class CreateCoursePrompts:

    CREATE_SUGGESTIONS_COURSE = """'ll give you the name of the topic for the course, and you offer me a 
    clarification of the topic and return answer in Russian. the number of suggested topics for the course should be 
    equal to 5. one of the topics should be strictly about the basic knowledge of this subject. For example, 
    the topic of the sql course, you ask: sql basics, sql for a data analyst, sql for back development, 
    sql for a database administrator. return the answer in json format: [{"short_title": "", "description": ""}] 
    Before the JSON response, write <json>, and after the JSON response, write </json>. The value in JSON should be 
    only in Russian, but the key should be in English"""

    SYSTEM_CONTENT_DETAILED_TABLE_V2 = """Task: Generate a detailed table of contents for the training course. I'll 
    give you the topic and description after given: topic = description = Requirements: The course should have 3 
    chapters. Each chapter should consist of 5-7 sections. The response should be in JSON format with the following 
    structure: [{ "chapter_number": 1, "title": "chapter title", "sections": [ { "section_number": 1, 
    "section_title": "section name"}, {"section_number": 2, "section_title": "section name"}, ]}, etc.] Before the 
    JSON response, write <json>, and after the JSON response, write </json>. The course title and need time should be 
    in Russian. Before the course title, write <course_title>, and after the course title, write </course_title>. 
    Before the course need time, write <course_time>, and after the course need time, write </course_time>. Only 
    include topics that can be explained. The value in JSON should be only in Russian, but the key should be in 
    English. Output: <json> [ { "chapter_number": 1, "title": "Название главы", "sections": [ {"section_number": 1, 
    "section_title": "Название секции"}, {"section_number": 2, "section_title": "Название секции"}, 
    {"section_number": 3, "section_title": "Название секции"}, {"section_number": 4, "section_title": "Название 
    секции"}, {"section_number": 5, "section_title": "Название секции"} ]}, {"chapter_number": 2, "title": "Название 
    главы", "sections": [ { "section_number": 1, "section_title": "Название секции"}, {"section_number": 2, 
    "section_title": "Название секции"}, {"section_number": 3, "section_title": "Название секции"}, 
    {"section_number": 4, "section_title": "Название секции"}, {"section_number": 5, "section_title": "Название 
    секции"}, {"section_number": 6, "section_title": "Название секции"} ]}, {"chapter_number": 3, "title": "Название 
    главы", "sections": [ { "section_number": 1, "section_title": "Название секции"}, {"section_number": 2, 
    "section_title": "Название секции"}, {"section_number": 3, "section_title": "Название секции"}, 
    {"section_number": 4, "section_title": "Название секции"}, {"section_number": 5, "section_title": "Название 
    секции"} ]} ] </json> <course_title>Название курса</course_title> <course_time>продолжительность курса в часах (
    только часы без текста)</course_time>"""

    SYSTEM_CONTENT_DETAILED_TABLE_V3 = """Task: Generate a detailed table of contents for the training course. I'll give you the topic and 
    description after given: topic = description = Requirements: The course should have 3 chapters. Each chapter 
    should consist of 5-7 sections and each sections consist 4-5 lessons . The response should be in JSON format with 
    the following structure: [ { "chapter_number": 1, "chapter_title": "Название главы", "sub_chapters": [ { 
    "sub_chapter_number": 1, "sub_chapter_title": "Название подглавы", "lessons": [ { "lesson_number": 1, 
    "lesson_title": "Название урока" }, { "lesson_number": 2, "lesson_title": "Название урока" }, ... ] }, 
    { "sub_chapter_number": 2, "sub_chapter_title": "Название подглавы", "lessons": [ { "lesson_number": 1, 
    "lesson_title": "Название урока" }, { "lesson_number": 2, "lesson_title": "Название урока" }, ... ] }, ... ] }, 
    { "chapter_number": 2, "chapter_title": "Название главы", "sub_chapters": [ { "sub_chapter_number": 1, 
    "sub_chapter_title": "Название подглавы", "lessons": [ { "lesson_number": 1, "lesson_title": "Название урока" }, 
    { "lesson_number": 2, "lesson_title": "Название урока" }, ... ] etc] Before the JSON response, write <json>, 
    and after the JSON response, write </json>. The course title and need time should be in Russian. Before the 
    course title, write <course_title>, and after the course title, write </course_title>. Before the course need 
    time, write <course_time>, and after the course need time, write </course_time>. Only include topics that can be 
    explained. The value in JSON should be only in Russian, but the key should be in English. Output: [ { 
    "chapter_number": 1, "chapter_title": "Название главы", "sub_chapters": [ { "sub_chapter_number": 1, 
    "sub_chapter_title": "Название подглавы", "lessons": [ { "lesson_number": 1, "lesson_title": "Название урока" }, 
    { "lesson_number": 2, "lesson_title": "Название урока" }, ... ] }, { "sub_chapter_number": 2, 
    "sub_chapter_title": "Название подглавы", "lessons": [ { "lesson_number": 1, "lesson_title": "Название урока" }, 
    { "lesson_number": 2, "lesson_title": "Название урока" }, ... ] }, ... ] }, { "chapter_number": 2, 
    "chapter_title": "Название главы", "sub_chapters": [ { "sub_chapter_number": 1, "sub_chapter_title": "Название 
    подглавы", "lessons": [ { "lesson_number": 1, "lesson_title": "Название урока" }, { "lesson_number": 2, 
    "lesson_title": "Название урока" }, ... ] }, { "sub_chapter_number": 2, "sub_chapter_title": "Название подглавы", 
    "lessons": [ { "lesson_number": 1, "lesson_title": "Название урока" }, { "lesson_number": 2, "lesson_title": 
    "Название урока" }, ... ] }, ... ] }, { "chapter_number": 3, "chapter_title": "Название главы", "sub_chapters": [ 
    { "sub_chapter_number": 1, "sub_chapter_title": "Название подглавы", "lessons": [ { "lesson_number": 1, 
    "lesson_title": "Название урока" }, { "lesson_number": 2, "lesson_title": "Название урока" }, ... ] etc ] </json> 
    <course_title>Название курса</course_title> <course_time>продолжительность курса в часах ( только часы без 
    текста)</course_time>"""

    SYSTEM_CREATE_SECTIONS = """Hi, I have a table of contents of an online course. Can you generate topics that are 
                worth studying just for one concert topic? It is very important to analyze the entire table of 
                contents so that in this topic you do not get ahead of yourself on topics that will be in the future 
                or were in the past. the number should be from 5 to 8. the answer should be in json format.Example:
                    {
                  "themes": [
                    "Понятие ошибок в Python",
                    "Стандартные исключения в Python",
                    "Конструкция try-except",
                    "Конструкция try-except-finally",
                    "Использование оператора else в конструкции try-except",
                  ]
                }
                the order is important!. before starting the json, 
                write <json> immediately after the json, write </json>. The names of the topics should be in Russian. 
                at the very end of the answer, write <end asnwer>"""

    SYSTEM_CREATE_SECTIONS_V2 = """I want you to act as a teacher of online courses. I will give you the name of the 
    course, the topic from this course, on which I want you to make up from 4 to 7 lessons. You only need the name of 
    the lessons in Russian. I will also give topics that have been studied in the past and you should take into 
    account that I already know this, and there is no need to build lessons on these topics. And I will give you 
    topics that will be in the future, after the current topic, they also do not need to be included in the lessons 
    on the current topic. the answer should be in json format.Example: { "themes": [ "Понятие ошибок в Python", 
    "Стандартные исключения в Python", "Конструкция try-except", "Конструкция try-except-finally", "Использование 
    оператора else в конструкции try-except", ] } the order is important!. before starting the json, write <json> 
    immediately after the json, write </json>. The names of the topics should be in Russian. at the very end of the 
    answer, write <end asnwer>"""