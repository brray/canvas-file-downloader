import requests
import os
from pathlib import Path
import re
import urllib
from tqdm.contrib.concurrent import process_map

queue = []

class File:
    def __init__(self, id, display_name, filename, url, course):
        self.id = id
        self.display_name = display_name
        self.filename = filename
        self.url = url
        self.course = course

class Course:
    def __init__(self, id, name):
        self.id = id
        self.name = re.sub('[\W]', '_', name)
        self.files = []
        self.get_files()
        try:
            os.mkdir(os.path.join(Path.home(), 'canvas_documents', self.name))
        except FileExistsError:
            pass

    def get_files(self):

        r = canvas.get(api_url + '/courses/' + str(self.id) + '/files?per_page=3000', headers=headers)
        for file in r.json():
            try:
                self.files.append(File(file['id'], file['display_name'], file['filename'], file['url'], self.name))
            except:
                pass

    def queue_files(self):
        global queue
        for file in self.files:
            queue.append(file)

def download_file(file):
    os.chdir(os.path.join(Path.home(), 'canvas_documents', file.course))
    urllib.request.urlretrieve(file.url, filename=file.filename)
    return file.filename

if __name__ == '__main__':
    canvas = requests.Session()

    api_url = 'https://mst.instructure.com/api/v1'

    api_key = os.environ['canvas_api_key']

    headers = {'Authorization' : 'Bearer {}'.format(api_key)}

    courses = []
    try:
        os.mkdir(os.path.join(Path.home(), 'canvas_documents'))
    except FileExistsError:
        pass

    r = canvas.get(api_url + '/courses?per_page=1000', headers=headers)

    for course in r.json():
        try:
            courses.append(Course(course['id'], course['course_code']))
        except KeyError:
            pass

    for course in courses:
        course.queue_files()

list_len = len(queue)

r = process_map(download_file, queue, max_workers=5)
