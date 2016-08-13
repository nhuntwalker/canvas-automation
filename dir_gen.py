"""Generate directories for Python 401d4 class assignments."""
from __future__ import unicode_literals
import os
import re
import requests
from itertools import product
from string import punctuation

TOKEN = os.environ['API_TOKEN']
COURSE_ID = os.environ['COURSE_ID']
COURSES_ROOT = 'https://canvas.instructure.com/api/v1/courses'
AUTH_PARAMS = {'access_token': TOKEN}
BAD_CHARS_PAT = re.compile(r'[' + re.escape(punctuation) + r']+')


def get_canvas_json(path):
    """Return json information from specified API query."""
    response = requests.get(path, params=AUTH_PARAMS)
    return response.json()


def get_course_attr(course_id, attr):
    """Return JSON from a sub-attribute of a given course."""
    path = '/'.join((COURSES_ROOT, course_id, attr, ''))
    return get_canvas_json(path)


def get_course_modules(course_id):
    """Return json information on modules in course specified by course ID."""
    return get_course_attr(course_id, 'modules')


def get_course_students(course_id):
    """Return json information on students in course specified by course ID."""
    return get_course_attr(course_id, 'students')


def get_course_student_names(course_id):
    """Return json information on students in course specified by course ID."""
    for student in get_course_students(course_id):
        yield student['name']


def get_course_module_names(course_id):
    """Return json information on modules in course specified by course ID."""
    for module in get_course_modules(course_id):
        yield module['name']


def convert_to_dirname(name):
    """Return new string with no punctuation and spaces replaced with '-'.."""
    name = re.sub(BAD_CHARS_PAT, '', name)
    return re.sub('\s+', '-', name)



if __name__ == '__main__':
    s_names = get_course_student_names(COURSE_ID)
    m_names = get_course_module_names(COURSE_ID)
    for student, module in product(s_names, m_names):
        student = convert_to_dirname(student)
        module = convert_to_dirname(module)
        print(' '.join((student, module)))
