import requests
import os
from biohub.abacus import util
from biohub.abacus.models import Abacus


POST_URL = 'http://localhost:8989/api/abacus-server/post/'
CALLBACK_URL = 'http://localhost:8988/api/abacus/callback/?id='

def post_task(task, filepath):
    if not os.path.exists(filepath):
        task.status = 'ERROR'
        return
    f = open(filepath, 'wb')
    data = {'callback' : CALLBACK_URL + str(task.abacus.id)}
    response = requests.post(POST_URL, files = f, data=data)

    jsn = response.json()
    task.task_id = int(jsn['task_id'])
    task.task_url = jsn('status')
    task.task_status = 'PENDING'

def get_task_status(task):
    response = requests.get(POST_URL + task.task_url)
    jsn = response.json()
    status = jsn['status']
    if 'SUCCESS' == status:
        result = jsn['result']
        try:
            download(result, util.generate_download_path(task.abacus.id))
            task.abacus.status = Abacus.FINISHED
            task.delete()
        except Exception as e:
            task.abacus.status = Abacus.ERROR
            task.delete()
            raise e
    elif 'PENDING' == status:
        task.abacus.status = Abacus.QUEUING
        task.task_status = status
    elif 'ERROR' == status:
        task.abacus.status = Abacus.ERROR
        task.delete()

    return result

def download(url, dest):
    r = requests.get(url, stream=True)
    print(r.status_code)
    if r.status_code == requests.codes.ok:
        util.copy_file(r.raw, dest)
    else:
        raise Exception('Url cannot found!' + str(r.status_code))
