from biohub.utils import redis


storage = redis.Storage('__biohub_tasks__')


def clear_keys():
    storage.delete_pattern('*')
