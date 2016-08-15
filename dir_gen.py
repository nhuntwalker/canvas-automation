"""Generate directories for Python 401d4 class assignments."""


# Some Assignments not showing up!!
# e.g. Mailroom Madness, Tom Swift

# git fetch is not updating an open pull request when it is updated
# need to git pull from that branch as well?

# Todo
# get the list of submissions for that assignment
# also check if submission type is a .py file; download that


from __future__ import unicode_literals
import os
import re
import git
import requests
from subprocess import call, CalledProcessError
from string import punctuation

HERE = os.path.abspath(os.path.dirname(__file__))
ROOT_NAME = 'grading'

TOKEN = os.environ['API_TOKEN']
COURSE_ID = os.environ['COURSE_ID']
COURSES_ROOT = 'https://canvas.instructure.com/api/v1/courses'
AUTH_PARAMS = {'access_token': TOKEN}
BAD_CHARS_PAT = re.compile(r'[' + re.escape(punctuation) + r']+')
GITHUB_REPO_PAT = re.compile(r'https://github.com/.+/.+')


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
    repo_url = sub['url']
    try:
        repo_url, pull_num = repo_url.split('/pull/')
        try:
            pull_num, _ = pull_num.split('/commits/')
        except ValueError:
            pass
        refspec = '/'.join(('pull', pull_num, 'head'))
    except ValueError:
        for pathspec in ('/tree/', '/blob/'):
            try:
                repo_url, _ = repo_url.split(pathspec)
            except ValueError:
                pass
            finally:
                refspec = 'master'

    repo_url = repo_url + '.git' * (not repo_url.endswith('.git'))
    print('cloning from {}'.format(repo_url))
    print('fetching from refspec {}'.format(refspec))

    call(['git', 'clone', repo_url, path], cwd=path)
    call(['git', 'fetch', 'origin', refspec + ':grading'], cwd=path)
    call(['git', 'checkout', 'grading'], cwd=path)


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

        # Refactor this block into a function
        names = (module['name'], asgn.get('title', ''), stu.get('name', ''))
        dirnames = (make_dirname(name) for name in names)
        path = os.path.join(root, *dirnames)
        make_directory(path)

        if not all((module, asgn, stu)):
            continue

        # possible to get all submissions for assignment + student names? faster?
        sub = get_assignment_student_submission(asgn, stu)

        print('{} - {} - {}'.format(*names))

        if sub['submission_type'] == 'online_url' and GITHUB_REPO_PAT.match(sub['url']):
            print("\n{}'s submission: {}".format(stu['name'], sub['url']))
            git_grading_branch(sub, path)
