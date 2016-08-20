"""Generate directories for Python 401d4 class assignments."""


# BUGFIX:
# setting multiple "include" params does not work; only returns last item

# Todo
# proper argparse
# set the name of the grading branch to grading-student-name for clarification

# check if submission type is a .py or other type of file; download that
# may be able to use /tree/ or /blob/ as refspecs instead of master

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
DEFAULT_DIR_ORDER = 'as'
DIR_ORDERS = 'mas', 'as', 'sa', 'msa'

FILEXISTS_ERRNO = 17
FILEDOESNOTEXIST_ERRNO = 2


def api_request(url, **kwargs):
    """Return json information from specified API query."""
    params = DEFAULT_PARAMS.copy()
    params.update(kwargs)
    response = requests.get(url, params=params)
    result = response.json()
    # Currently assumes that result is a list of json objects.
    for item in result:
        yield item
    try:
        next_url = response.links['next']['url']
        for item in api_request(next_url, **kwargs):
            yield item
    except KeyError:
        pass


def joined_api_request(*args, **kwargs):
    """Return JSON from a sub-attribute of a given course."""
    url = '/'.join(args + ('', ))
    for item in api_request(url, **kwargs):
        yield item


def get_course_modules(course_id):
    """Return list of module dicts of the course specified by ID."""
    args = (API_ROOT, 'courses', course_id, 'modules')
    for module in joined_api_request(*args):
        yield module


def get_course_students(course_id):
    """Return list of student dicts of the course specified by ID."""
    args = (API_ROOT, 'courses', course_id, 'students')
    for student in joined_api_request(*args):
        yield student


def get_course_assignments(course_id):
    """Return list of assignment dicts of the course specified by ID."""
    args = (API_ROOT, 'courses', course_id, 'assignments')
    for assignment in joined_api_request(*args):
        yield assignment


def get_course_submissions(course_id):
    """Return list of submission dicts of the course specified by ID."""
    args = (API_ROOT, 'courses', course_id, 'students', 'submissions')
    kwargs = dict(student_ids='all', include='assignment')
    # include='user', # WON'T WORK to submit multiple includes!
    for submission in joined_api_request(*args, **kwargs):
        yield submission


def get_assignment_submissions(asgn):
    """Return list of submission dicts for the specified assignment."""
    url = asgn.get('url', asgn.get('submissions_download_url', '').split('?')[0])
    for submission in joined_api_request(url, 'submissions', include='user'):
        yield submission


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
    """Return boolean of whether the given submission is a git repository."""
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


def get_git_repo(submission, student, path):
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
    local_branchname = '-'.join(('grading', make_dirname(student['name'])))

    print('cloning from {}'.format(repo_url))
    call(['git', 'clone', repo_url, path], cwd=path)
    print('fetching from refspec: {}'.format(refspec))
    call(['git', 'fetch', 'origin', ':'.join((refspec, local_branchname))], cwd=path)
    call(['git', 'checkout', local_branchname], cwd=path)
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


def github_repo_submissions(course_id):
    """Generate only course combinations where submission is a github repo."""
    for asgn, stu, sub in all_course_combos(course_id):
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

    for asgn, stu, sub in github_repo_submissions(COURSE_ID):
        print("\n{}'s submission for {}: {}".format(
            stu['name'], asgn['name'], sub['url'])
        )
        # download .py or other files
        path = make_dir_path(root, asgn, stu, dir_order)
        make_directory(path)
        get_git_repo(sub, stu, path)
