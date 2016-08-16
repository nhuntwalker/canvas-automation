"""Generate directories for Python 401d4 class assignments."""

# Change to dir structure: student/assignment

# Todo
# also check if submission type is a .py file; download that


from __future__ import unicode_literals
import os
import re
import requests
from subprocess import call
from string import punctuation

HERE = os.path.abspath(os.path.dirname(__file__))
ROOT_NAME = 'grading'

TOKEN = os.environ['API_TOKEN']
COURSE_ID = os.environ['COURSE_ID']
COURSES_ROOT = 'https://canvas.instructure.com/api/v1/courses'
DEFAULT_PARAMS = {'access_token': TOKEN, 'per_page': 999999}
BAD_CHARS_PAT = re.compile(r'[' + re.escape(punctuation) + r']+')
GITHUB_REPO_PAT = re.compile(r'https://github.com/.+/.+')


def api_request(url, **kwargs):
    """Return json information from specified API query."""
    params = DEFAULT_PARAMS.copy()
    params.update(kwargs)
    response = requests.get(url, params=params)
    return response.json()


def joined_api_request(*args, **kwargs):
    """Return JSON from a sub-attribute of a given course."""
    url = '/'.join(args + ('', ))
    return api_request(url, **kwargs)


def get_course_modules(course_id):
    """Return list of modules of the course specified by ID."""
    return joined_api_request(COURSES_ROOT, course_id, 'modules')


def get_course_students(course_id):
    """Return list of student dicts of the course specified by ID."""
    return joined_api_request(COURSES_ROOT, course_id, 'students')


def get_module_assignments(module):
    """Return list of assignment dicts of the specified module."""
    return [item for item in api_request(module['items_url'])
            if item['type'] == 'Assignment']


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


def get_assignment_student_submission(asgn, student):
    """Return single submission dict specified by assignment and student."""
    try:
        return joined_api_request(asgn['url'], 'submissions', str(student['id']))
    except KeyError:
        try:
            url = asgn['submissions_download_url'].split('?')[0]
            return joined_api_request(url, str(student['id']))
        except KeyError:
            return {}


def make_dirname(name):
    """Return new string with no punctuation and spaces replaced with '-'."""
    name = re.sub(BAD_CHARS_PAT, '', name)
    name = re.sub('\s+', '-', name)
    return name.lower()


def make_path(root, module, assignment, student):
    """Create a path from the given components."""
    names = (
        module.get('name', ''),
        assignment.get('title', ''),
        student.get('name', '')
    )
    dirnames = map(make_dirname, names)
    return os.path.join(root, *dirnames)


def make_directory(path):
    """Create a new directory with the given path."""
    try:
        os.mkdir(path)
    except (IOError, OSError):
        pass


def is_git_repo(submission):
    """Determine if the given submission is a git repository."""
    return (
        submission['submission_type'] == 'online_url' and
        re.match(GITHUB_REPO_PAT, submission['url']) and
        'profile' not in submission['url']
    )


def git_grading_branch(submission, path):
    """Clone student repo, fetch submitted pull request into grading branch."""
    repo_url = sub['url']
    try:
        repo_url, pull_num = repo_url.split('/pull/')
        pull_num = pull_num.split('/')[0]
        refspec = '/'.join(('pull', pull_num, 'head'))
    except ValueError:
        for pathspec in ('/tree/', '/blob/'):
            repo_url = repo_url.split(pathspec)[0]
        refspec = 'master'

    repo_url = repo_url + '.git' * (not repo_url.endswith('.git'))
    print('cloning from {}'.format(repo_url))
    call(['git', 'clone', repo_url, path], cwd=path)
    print('fetching from refspec: {}'.format(refspec))
    call(['git', 'fetch', 'origin', refspec + ':grading'], cwd=path)
    call(['git', 'checkout', 'grading'], cwd=path)
    call(['git', 'pull', 'origin', refspec], cwd=path)


def all_course_combos(course_id):
    """Generate all combinations of module, assignment, student names."""
    for module in get_course_modules(course_id):
        yield module, {}, {}, {}

        for asgn in get_module_assignments(module):
            yield module, asgn, {}, {}

            for sub in get_assignment_submissions(asgn):
                student = sub['user']
                yield module, asgn, student, sub


if __name__ == '__main__':
    modules = get_course_modules(COURSE_ID)

    root = os.path.join(HERE, ROOT_NAME)
    make_directory(root)

    for module, asgn, stu, sub in all_course_combos(COURSE_ID):
        path = make_path(root, module, asgn, stu)
        make_directory(path)

        if not all((module, asgn, stu, sub)):
            continue

        print("\n{}'s submission for {}: {}".format(
            stu['name'], asgn['title'], sub['url'])
        )
        if is_git_repo(sub):
            git_grading_branch(sub, path)
