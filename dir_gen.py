"""Generate directories for Python 401d4 class assignments."""

# Todo
# for each assignment, check if it requires a url.
# get the list of submissions for that assignment
# if the url is a github pull request, use pythongit API to discern clone path
# clone it or pull it to update if necessary

from __future__ import unicode_literals
import os
import re
import git
import requests
from subprocess import check_output, CalledProcessError
from string import punctuation

HERE = os.path.abspath(os.path.dirname(__file__))
ROOT_NAME = 'grading'

TOKEN = os.environ['API_TOKEN']
COURSE_ID = os.environ['COURSE_ID']
COURSES_ROOT = 'https://canvas.instructure.com/api/v1/courses'
AUTH_PARAMS = {'access_token': TOKEN}
BAD_CHARS_PAT = re.compile(r'[' + re.escape(punctuation) + r']+')


def api_request(url):
    """Return json information from specified API query."""
    response = requests.get(url, params=AUTH_PARAMS)
    return response.json()


# def get_course_attr(course_id, attr):
#     """Return JSON from a sub-attribute of a given course."""
#     path = '/'.join((COURSES_ROOT, course_id, attr, ''))
#     return api_request(path)


def joined_api_request(*args):
    """Return JSON from a sub-attribute of a given course."""
    url = '/'.join(args + ('', ))
    return api_request(url)


def get_course_modules(course_id):
    """Return modules of a given course."""
    return joined_api_request(COURSES_ROOT, course_id, 'modules')


def get_course_students(course_id):
    """."""
    return joined_api_request(COURSES_ROOT, course_id, 'students')


def get_module_assignments(module):
    """."""
    return [item for item in api_request(module['items_url'])
            if item['type'] == 'Assignment']


# def get_assignment_submissions(asgn):
#     """."""
#     try:
#         return joined_api_request(asgn['url'], 'submissions')
#     except KeyError:
#         try:
#             url = asgn['submissions_download_url'].split('?')[0]
#             return api_request(url)
#         except KeyError:
#             return []


def get_assignment_student_submission(asgn, student):
    """."""
    try:
        return joined_api_request(asgn['url'], 'submissions', str(student['id']))
    except KeyError:
        try:
            url = asgn['submissions_download_url'].split('?')[0]
            return joined_api_request(url, str(student['id']))
        except KeyError:
            return {}


def make_dirname(name):
    """Return new string with no punctuation and spaces replaced with '-'.."""
    name = re.sub(BAD_CHARS_PAT, '', name)
    name = re.sub('\s+', '-', name)
    return name.lower()


def make_directory(path):
    """Create a new directory with the given path."""
    try:
        os.mkdir(path)
    except IOError:
        pass


def git_grading_branch(submission, path):
    """Clone student repo, fetch submitted pull request into grading branch."""
    repo_url, pull_num = sub['url'].split('/pull/')
    refspec = '/'.join(('pull', pull_num, 'head')) + ':grading'
    check_output(['cd', path])
    try:
        check_output(['git', 'rev-parse'])
    except CalledProcessError:
        check_output(['git', 'clone', repo_url + '.git', path])
    check_output(['git', 'fetch', 'origin', refspec])
    check_output(['git', 'checkout', 'grading'])


def all_course_combos(course_id):
    """Generate all combinations of module, assignment, student names."""
    students = get_course_students(course_id)
    for module in get_course_modules(course_id):
        yield module, {}, {}

        for asgn in get_module_assignments(module):
            yield module, asgn, {}

            for student in students:
                if student['name'] == 'Test Student':
                    continue
                yield module, asgn, student


if __name__ == '__main__':
    modules = get_course_modules(COURSE_ID)

    root = os.path.join(HERE, ROOT_NAME)
    make_directory(root)

    for module, asgn, stu in all_course_combos(COURSE_ID):

        names = (module['name'], asgn.get('title', ''), stu.get('name', ''))
        names = (make_dirname(name) for name in names)
        path = os.path.join(root, *names)
        make_directory(path)
        # import pdb;pdb.set_trace()

        # Debugging
        if asgn.get('title') == 'Mathematical Series':
            sub = get_assignment_student_submission(asgn, stu)
            if sub.get('submission_type') == 'online_url' and 'github' in sub['url']:
                print("{}'s submission: {}".format(stu['name'], sub['url']))
                print('path: {}'.format(path))
                git_grading_branch(sub, path)
