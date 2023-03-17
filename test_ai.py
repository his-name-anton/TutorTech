from pprint import pprint

import openai
import json

# Set up OpenAI API credentials
openai.api_key = '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'

prompt_create_block_topic = (
        f"""I want you to act as a table of contents generator. I will give you a topic, and you will generate a 
        detailed table of contents for studying this topic. It is desirable to achieve triple nesting, for example 1. 
        Chapter 1 1.1. Sub-chapter 1 1.2 sub-chapter 2 1.1.1 Block 1 1.1.1 block2 and so on
        generate detailed table of contents for topic python OOP"""
)

prompt_create_lession_theary = """
I want you to generate theoretical material on a certain topic. I'll give you a general topic, chapter, sub-chapter, and lesson topic. You have to give me back the theoretical materials for the lesson.
topic = python OOP
chapter = Chapter 1: Introduction to Object-Oriented Programming in Python
sub-chapter = Basic Concepts 
lession = Objects
"""

prompt_create_exmple = """
I want you to act as an example generator. I will give you theoretical material, and you must return examples that best reflect the essence of the received theoretical text.

Theoretical Material (Objects): 
Objects are the basic building block of any object-oriented programming language. In Python, an object is an instance of the class and is used to store data and state. A class is a template or blue-print for creating objects. It is a collection of methods, variables and constants that are used to create individual objects.
An Object has attributes, which are variables associated with the object, as well as methods, which are functions that act upon the object. Objects in Python have a unique, immutable identity (‘identityhash’). This identity is used to determine if two instances of the same class are, in fact, the same object. If two objects have the same identity, then the two objects are considered to be equal. 
Objects also encapsulate information, meaning that the object’s data and state are separate from the outside world. This allows for data to be hidden within objects and makes coding much easier.
Objects are created from classes, and each object is an instance of a class. This is done by writing the keyword ‘class’ followed by a class name and parent classes, if needed. Whenever an object of a class is initiated, the object’s variables, as well as the methods within the class, are all inherited by the object. 
Objects are powerful tools that can be used to better organize code and make it easier to maintain. By using objects, developers can create abstractions that encapsulate the logic and data of the application, making it simpler and more maintainable. This is the essence of Object-Oriented Programming in Python.
"""

# Set up the OpenAI API parameters
model = "text-davinci-003"
temperature = 1
max_tokens = 2048
stop_sequence = "\n\n"

# Generate the training program using the OpenAI API
response = openai.Completion.create(
    engine=model,
    prompt=prompt_create_exmple,
    temperature=temperature,
    max_tokens=max_tokens,
    # stop=stop_sequence,
)
need_trans = response.choices[0].text
print(need_trans)
#
# response = openai.Completion.create(
#   model="text-davinci-003",
#   prompt="Translate this into Russian \n" + need_trans,
#   temperature=0.3,
#   max_tokens=2048,
#   top_p=1.0,
#   frequency_penalty=0.0,
#   presence_penalty=0.0
# )
#
# pprint(response)
#
# # Parse the JSON response and print the training program
# print(response.choices[0].text)
