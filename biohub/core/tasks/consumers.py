from biohub.core.tasks.broker import broker


def task_consumer(message):
    broker.run_task(message['task_id'])
