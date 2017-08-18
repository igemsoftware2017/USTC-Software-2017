class TaskInterruption(Exception):
    pass


class TaskRegistered(Exception):

    def __init__(self, task_name):
        self.task_name = task_name

    def __str__(self):
        return "Task '%s' was registered." % self.task_name


class TaskInstanceNotExists(Exception):

    def __init__(self, task_id):
        self.task_id = task_id

    def __str__(self):
        return "Task instance with id '%s' doesn't exist." % self.task_id
