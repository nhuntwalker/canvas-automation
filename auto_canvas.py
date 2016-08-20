"""Generate directories for Python 401d4 class assignments."""


# Todo
# set the name of the grading branch to grading-student-name for clarification

# check if submission type is a .py or other type of file; download that
# Change to dir structure: student/assignment
# make dir structure an command line option, along with course ID, token, etc
# may be able to use /tree/ or /blob/ as refspecs instead of master

# API request: return a generator of items across multiple pages to save memory

from __future__ import unicode_literals
import os
import re
import sys
import argparse
import requests
from subprocess import call
from string import punctuation

HERE = os.path.abspath(os.path.dirname(__file__))
DEFAULT_ROOT_NAME = 'grading'

TOKEN = os.environ['API_TOKEN']
COURSE_ID = os.environ['COURSE_ID']
API_ROOT = 'https://canvas.instructure.com/api/v1/'
DEFAULT_PARAMS = {'access_token': TOKEN, 'per_page': 999999}
BAD_CHARS_PAT = re.compile(r'[' + re.escape(punctuation) + r']+')
GITHUB_REPO_PAT = re.compile(r'https://github.com/.+/.+')
DEFAULT_DIR_ORDER = 'mas'
DIR_ORDERS = 'mas', 'as', 'sa', 'msa'

FILEXISTS_ERRNO = 17
FILEDOESNOTEXIST_ERRNO = 2


def api_request(url, **kwargs):
    """Return json information from specified API query."""
    params = DEFAULT_PARAMS.copy()
    params.update(kwargs)
    response = requests.get(url, params=params)
    result = response.json()
    method = getattr(result, 'update', getattr(result, 'extend'))
    try:
        next_url = response.links['next']['url']
        method(api_request(next_url, **kwargs))
    except KeyError:
        pass
    # import pdb;pdb.set_trace()
    return result


def joined_api_request(*args, **kwargs):
    """Return JSON from a sub-attribute of a given course."""
    url = '/'.join(args + ('', ))
    return api_request(url, **kwargs)


def get_course_modules(course_id):
    """Return list of module dicts of the course specified by ID."""
    return joined_api_request(API_ROOT, 'courses', course_id, 'modules')


def get_course_students(course_id):
    """Return list of student dicts of the course specified by ID."""
    return joined_api_request(API_ROOT, 'courses', course_id, 'students')


def get_course_assignments(course_id):
    """Return list of assignment dicts of the course specified by ID."""
    return joined_api_request(API_ROOT, 'courses', course_id, 'assignments')


def get_course_submissions(course_id):
    """Return list of submission dicts of the course specified by ID."""
    return joined_api_request(
        API_ROOT,
        'courses',
        course_id,
        'students',
        'submissions',
        student_ids='all',
        include='assignment',
        # include='user', # WON'T WORK to submit multiple includes!
    )


# # possible to re-write without extra loop?
# def get_module_assignments(module):
#     """Return list of assignment dicts of the specified module."""
#     return [item for item in api_request(module['items_url'])
#             if item['type'] == 'Assignment']


def get_assignment_submissions(asgn):
    """Return list of submission dicts for the specified assignment."""
    try:
        return joined_api_request(asgn['url'], 'submissions', include='user')
    except KeyError:
        try:
            url = asgn['submissions_download_url'].split('?')[0]
            return api_request(url, include='user')
        except KeyError:
            return []


# def get_assignment_student_submission(asgn, student):
#     """Return single submission dict specified by assignment and student."""
#     try:
#         return joined_api_request(asgn['url'], 'submissions', str(student['id']))
#     except KeyError:
#         try:
#             url = asgn['submissions_download_url'].split('?')[0]
#             return joined_api_request(url, str(student['id']))
#         except KeyError:
#             return {}


def make_dirname(name):
    """Return new string with no punctuation and spaces replaced with '-'."""
    name = re.sub(BAD_CHARS_PAT, '', name)
    name = re.sub('\s+', '-', name)
    return name.lower()


def make_dir_path(root, assignment, student, dir_order):
    """Create a directory path from the given components."""
    charmap = {
        'a': assignment,
        's': student,
    }
    items = map(lambda char: charmap[char], dir_order)
    names = map(lambda item: item.get('name', item.get('title', '')), items)
    dirnames = map(make_dirname, names)
    return os.path.join(root, *dirnames)


def make_directory(path):
    """Create a new directory with the given path."""
    try:
        os.mkdir(path)
    except OSError as e:
        # Path already exists; ignore.
        if e.errno == FILEXISTS_ERRNO:
            pass
        elif e.errno == FILEDOESNOTEXIST_ERRNO:
            # Parent path does not exist; try to make it.
            parent, child = os.path.split(path)
            make_directory(parent)
            make_directory(path)


def is_git_repo(submission):
    """Determine if the given submission is a git repository."""
    try:
        sub_type = submission['submission_type'] or ''
        url = submission['url'] or ''
    except KeyError:
        return False
    return all((
        sub_type == 'online_url',
        re.match(GITHUB_REPO_PAT, url),
        'profile' not in url,
    ))


def get_git_repo(submission, path):
    """Clone student repo, fetch submitted pull request into grading branch."""
    repo_url = submission['url']
    try:
        repo_url, pull_info = repo_url.split('/pull/')
        pull_num = pull_info.split('/')[0]
        refspec = '/'.join(('pull', pull_num, 'head'))
    except ValueError:
        # may be able to use /tree/ or /blob/ as refspecs instead of master
        for pathspec in ('/tree/', '/blob/'):
            repo_url = repo_url.split(pathspec)[0]
        refspec = 'master'

    repo_url = repo_url + '.git' * (not repo_url.endswith('.git'))
    print('cloning from {}'.format(repo_url))
    call(['git', 'clone', repo_url, path], cwd=path)
    print('fetching from refspec: {}'.format(refspec))
    call(['git', 'fetch', 'origin', refspec + ':grading'], cwd=path)
    call(['git', 'checkout', 'grading'], cwd=path)
    print('pulling from refspec: {}'.format(refspec))
    call(['git', 'pull', 'origin', refspec], cwd=path)


def all_course_combos(course_id):
    """Generate all combinations of assignment, student and submission."""
    students_by_id = {stu['id']: stu for stu in get_course_students(course_id)}
    for submission in get_course_submissions(course_id):
        assignment = submission['assignment']
        try:
            student = students_by_id[submission['user_id']]
            yield assignment, student, submission
        except KeyError:
            # Student is no longer enrolled in the class.
            pass


def get_github_repo_submissions(course_id):
    """Generate only course combinations where submission is a github repo."""
    for asgn, stu, sub in all_course_combos(course_id):
        # download .py or other files
        if is_git_repo(sub):
            yield asgn, stu, sub


if __name__ == '__main__':

    try:
        dir_order = sys.argv[1]
    except IndexError:
        dir_order = DEFAULT_DIR_ORDER

    if dir_order not in DIR_ORDERS:
        print('Invalid directory order acronym.')
        sys.exit()

    root = os.path.join(HERE, DEFAULT_ROOT_NAME)

    for asgn, stu, sub in get_github_repo_submissions(COURSE_ID):
        # download .py or other files
        print("\n{}'s submission for {}: {}".format(
            stu['name'], asgn['name'], sub['url'])
        )
        path = make_dir_path(root, asgn, stu, dir_order)
        make_directory(path)
        # get_git_repo(sub, path)
