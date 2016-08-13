"""Generate directories for Python 401d4 class assignments."""
from __future__ import unicode_literals
import os
import requests

TOKEN = os.environ['API_TOKEN']
COURSE_ID = os.environ['COURSE_ID']
COURSES_ROOT = 'https://canvas.instructure.com/api/v1/courses/'
AUTH_PARAMS = {'access_token': TOKEN}


def get_canvas_json(path):
    """Return json information on course specified by course ID."""
    response = requests.get(path, params=AUTH_PARAMS)
    return response.json()


if __name__ == '__main__':
    json_data = get_canvas_json(COURSES_ROOT + COURSE_ID)
