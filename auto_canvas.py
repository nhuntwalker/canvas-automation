"""Generate directories for Ungraded Canvas Course Submissions."""

from __future__ import unicode_literals
import os
import re
import sys
import requests
from subprocess import call
from string import punctuation

# strings of student id's or blank for all
MY_STUDENT_IDS = []

HERE = os.path.abspath(os.path.dirname(__file__))
DEFAULT_ROOT_NAME = 'grading'

try:
    TOKEN = os.environ['API_TOKEN']
    COURSE_ID = os.environ['COURSE_ID']
except KeyError:
    raise KeyError('Please activate your secret file containing tokens.')

API_ROOT = 'https://canvas.instructure.com/api/v1'
DEFAULT_PARAMS = {'access_token': TOKEN, 'per_page': 999999}
BAD_CHARS_PAT = re.compile(r'[' + re.escape(punctuation) + r']+')
GITHUB_REPO_PAT = re.compile(r'https://github.com/.+/.+')
DEFAULT_DIR_ORDER = 'as'
DIR_ORDERS = 'mas', 'as', 'sa', 'msa'

FILEXISTS_ERR_NUM = 17
FILEDOESNOTEXIST_ERR_NUM = 2


def students_request_string(students=MY_STUDENT_IDS):
    """Return list of strings for request of student id's."""
    if not students:
        return ['all']
    return students


def api_request(url, **kwargs):
    """Return json information from specified API query."""
    params = DEFAULT_PARAMS.copy()
    params.update(kwargs)
    response = requests.get(url, params=params)
    print('url:', response.url)

    try:
        # Currently assumes that result is a list of json objects.
        result = response.json()
    except:
        # slightly hacky, but will fix later
        print('\n', '!! server error, resetting parameters!')
        curr_page = re.search('&page=(\d+)', url).group(1)
        students = '&student_ids[]='.join(students_request_string())
        url = API_ROOT + '/courses/' + COURSE_ID + \
            '/students/submissions?include%5B%5D=assignment&include%5B%5D=user&'\
            + students + '&page=' + curr_page + '&per_page=100'
        response = requests.get(url, params=params)
        print('request:', response.url, '\n')
        result = response.json()

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
    kwargs = {
        'student_ids[]': students_request_string(),
        'include[]': ['assignment', 'user']
    }

    for submission in joined_api_request(*args, **kwargs):
        yield submission


def get_assignment_submissions(asgn):
    """Return list of submission dicts for the specified assignment."""
    url = asgn.get(
        'url',
        asgn.get('submissions_download_url', '').split('?')[0])
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
        if e.errno == FILEXISTS_ERR_NUM:
            pass
        elif e.errno == FILEDOESNOTEXIST_ERR_NUM:
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


def needs_grading(submission):
    """Return boolean of whether the given submission needs to be graded."""
    return any((
        submission['grade_matches_current_submission'] is False,
        submission['grade'] is None,
        submission['score'] is None,
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
    call(
        ['git', 'fetch', 'origin', ':'.join((refspec, local_branchname))],
        cwd=path
    )
    call(['git', 'checkout', local_branchname], cwd=path)
    print('pulling from refspec: {}'.format(refspec))
    call(['git', 'pull', '--no-edit', 'origin', refspec], cwd=path)


def print_failures(fail_list):
    """Print failuers from main script.

    This appears to happen when someone does not submit a valid PR.
    """
    print('----------' * 5)
    print('FAILURES:')
    for fail in fail_list:
        print(re.split(DEFAULT_ROOT_NAME, fail)[1])


if __name__ == '__main__':

    fail_list = []
    try:
        dir_order = sys.argv[1]
    except IndexError:
        dir_order = DEFAULT_DIR_ORDER

    if dir_order not in DIR_ORDERS:
        print('Invalid directory order acronym.')
        sys.exit()

    root = os.path.join(HERE, DEFAULT_ROOT_NAME)
    submissions = get_course_submissions(COURSE_ID)
    submissions_to_grade = filter(needs_grading, submissions)
    github_submissions = filter(is_git_repo, submissions_to_grade)

    for sub in github_submissions:
        asgn = sub['assignment']
        stu = sub['user']
        print("\n{}'s submission for {}: {}".format(
            stu['name'], asgn['name'], sub['url'])
        )

        path = make_dir_path(root, asgn, stu, dir_order)
        make_directory(path)
        try:
            get_git_repo(sub, stu, path)
        except OSError:
            fail_list.append(path)

    if len(fail_list):
        print_failures(fail_list)
