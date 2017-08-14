from .models import Abacus
from .task import task


def calculate(id):
    abacus = Abacus.load(id)
    if abacus is not None:
        task.create_task(id)
    return