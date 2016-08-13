"""Generate directories for Python 401d4 class assignments."""
from __future__ import unicode_literals
import os
import re
import requests
from string import punctuation

HERE = os.path.dirname(__file__)
ROOT = os.path.join(HERE, 'grading')

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
    return [student['name'] for student in get_course_students(course_id)
            if student['name'] is not 'Test Student']


def get_module_assignment_names(items_url):
    """Return json information on modules in course specified by course ID."""
    for item in get_canvas_json(items_url):
        if item['type'] == 'Assignment':
            yield item['title']


def make_dir_path(path, name):
    """Return new string with no punctuation and spaces replaced with '-'.."""
    name = re.sub(BAD_CHARS_PAT, '', name)
    name = re.sub('\s+', '-', name)
    return os.path.join(path, name)


def make_directory(path):
    """Create a new directory with the given dirname."""
    try:
        os.mkdir(path)
    except IOError:
        pass


def main(course_id):
    """Create local directory tree for grading assignments."""
    student_names = get_course_student_names(course_id)
    for module in get_course_modules(course_id):
        module_path = make_dir_path(ROOT, module['name'])
        print('Making module dir: {}'.format(module_path))
        make_directory(module_path)

        for asgn_name in get_module_assignment_names(module['items_url']):
            asgn_path = make_dir_path(module_path, asgn_name)
            print('\tMaking assignment dir: {}'.format(asgn_path))
            make_directory(asgn_path)

            for stu_name in student_names:
                stu_path = make_dir_path(asgn_path, stu_name)
                print('\t\tMaking student dir: {}'.format(stu_path))
                make_directory(stu_path)


if __name__ == '__main__':
    main(COURSE_ID)
