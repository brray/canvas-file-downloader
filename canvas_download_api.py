import requests
import os
from pathlib import Path
import re
from tqdm import tqdm
import urllib

class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)

class Course:
    def __init__(self, id, name):
        self.id = id
        self.name = re.sub('[\W]', '_', name)
        self.files = []
        self.get_files()
        os.mkdir(os.path.join(Path.home(), 'canvas_documents', self.name))

    def get_files(self):

        r = canvas.get(api_url + '/courses/' + str(self.id) + '/files?per_page=3000', headers=headers)

        for file in r.json():
            try:
                self.files.append(File(file['id'], file['display_name'], file['filename'], file['url']))
            except:
                pass

    def download_files(self):
        for file in self.files:
            file.download_file(self.name)

class File:
    def __init__(self, id, display_name, filename, url):
        self.id = id
        self.display_name = display_name
        self.filename = filename
        self.url = url

    def download_file(self, folder):
        os.chdir(os.path.join(Path.home(), 'canvas_documents', folder))
        
        with DownloadProgressBar(unit='B', unit_scale=True,
                             miniters=1, desc=self.filename) as t:
            urllib.request.urlretrieve(self.url, filename=self.filename, reporthook=t.update_to)
        return self.url

if __name__ == '__main__':
    canvas = requests.Session()

    api_url = 'https://mst.instructure.com/api/v1'

    api_key = os.environ['canvas_api_key']

    headers = {'Authorization' : 'Bearer {}'.format(api_key)}

    courses = []

    os.mkdir(os.path.join(Path.home(), 'canvas_documents'))

    r = canvas.get(api_url + '/courses?per_page=1000', headers=headers)

    for course in r.json():
        try:
            courses.append(Course(course['id'], course['course_code']))
        except KeyError:
            pass

    for course in courses:
        course.download_files()