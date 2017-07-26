import threading
from time import sleep


CALCULATE_QUEUE = []

THREAD_POOL = []

def calculate(id):
    # print(id, a, b)
    id = int(id)
    print("calculating -> ", id)
    pass

def manager():
    while True:
        sleep(1)
        if len(THREAD_POOL) < 15 and len(CALCULATE_QUEUE) > 0:
            id = CALCULATE_QUEUE.pop(0)
            print('id - > ', id, str(id))
            thread = threading.Thread(target=calculate, args=(str(id), ))
            thread.setDaemon(True)
            thread.start()
            THREAD_POOL.append(thread)

        print('wathing...')

MAIN_THREAD = threading.Thread(target=manager)
MAIN_THREAD.setDaemon(True)

def start():
    MAIN_THREAD.start()

# # MAIN_THREAD.start()
#
# if __name__ == "__main__":
#     CALCULATE_QUEUE.append(1)
#     CALCULATE_QUEUE.append(2)
#     CALCULATE_QUEUE.append(3)
#     CALCULATE_QUEUE.append(4)
#     CALCULATE_QUEUE.append(5)
#
#     sleep(10000)