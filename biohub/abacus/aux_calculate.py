import threading
from time import sleep


CALCULATE_QUEUE = []

THREAD_POOL = []

def calculate(id):
    # print(id, a, b)
    id = int(id)
    if id in CALCULATE_QUEUE:
        return
    else:
        CALCULATE_QUEUE.append(id)

def threads(id):
    id = int(id)
    from .models import Abacus

    abacus = Abacus.load(id)
    if abacus is None:
        return

    abacus.status = Abacus.PROCESSING
    sleep(10)
    abacus.status = Abacus.FINISHED

def manager():
    while True:
        sleep(1)
        if len(THREAD_POOL) < 5 and len(CALCULATE_QUEUE) > 0:
            id = CALCULATE_QUEUE.pop(0)
            print('id - > ', id, str(id))
            thread = threading.Thread(target=threads, args=(str(id), ))
            thread.setDaemon(True)
            thread.start()
            THREAD_POOL.append(thread)

        print('wathing...')

MAIN_THREAD = threading.Thread(target=manager)
MAIN_THREAD.setDaemon(True)

def start():
    MAIN_THREAD.start()
