"""Generate directories for Python 401d4 class assignments."""
from __future__ import unicode_literals
import os
import re
import requests
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
    return [student['name'] for student in get_course_students(course_id)]


def get_module_assignment_names(items_url):
    """Return json information on modules in course specified by course ID."""
    for item in get_canvas_json(items_url):
        if item['type'] == 'Assignment':
            yield item['title']


def convert_to_dirname(name):
    """Return new string with no punctuation and spaces replaced with '-'.."""
    name = re.sub(BAD_CHARS_PAT, '', name)
    return re.sub('\s+', '-', name)


def main(course_id):
    """Create local directory tree for grading assignments."""
    student_names = get_course_student_names(course_id)
    for module in get_course_modules(course_id):
        module_name = convert_to_dirname(module['name'])
        print('Making module dir named {}'.format(module_name))

        for asgn_name in get_module_assignment_names(module['items_url']):
            asgn_name = convert_to_dirname(asgn_name)
            print('\tMaking assignment dir named {}'.format(asgn_name))

            for stu_name in student_names:
                stu_name = convert_to_dirname(stu_name)
                print('\t\tMaking student dir named {}'.format(stu_name))


if __name__ == '__main__':
    module_data = main(COURSE_ID)
