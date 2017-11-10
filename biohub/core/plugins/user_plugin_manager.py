import os
import enum
import subprocess
import os.path as path

from biohub.accounts.models import User
from biohub.utils.redis import Storage
from biohub.core.conf import settings as biohub_settings
from django.utils.functional import cached_property
from rest_framework.exceptions import APIException

from .registry import manager as plugin_manager
from .ipc_slave import bridge


class UserPluginStatus(enum.Enum):

    RUNNING = 'RUNNING'
    REJECTED = 'REJECTED'
    PENDING = 'PENDING'


class UserPluginRequestStatus(enum.Enum):

    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'
    PENDING = 'PENDING'
    NONE = 'NONE'


class UserPluginInfo:

    def __init__(self, username, repo, commit='', status=UserPluginStatus.PENDING, message='', request_status=UserPluginRequestStatus.PENDING):
        self.__load(username, repo, commit, status, message, request_status)

    def __load(self, username, repo, commit, status, message, request_status):

        self.username = username
        self.repo = repo
        self.commit = commit
        self.status = UserPluginStatus(status)
        self.message = message
        self.request_status = UserPluginRequestStatus(request_status)

    @property
    def tuple(self):
        return (self.username, self.repo, self.commit, self.status.value, self.message, self.request_status.value)

    @classmethod
    def from_tuple(cls, tuple):
        return cls(*tuple)


class RepositoryException(APIException):

    status_code = 400

    def __init__(self, user, message):
        self.user = user
        self.message = message

    @property
    def detail(self):
        return self.message


redis_storage = Storage('_user_plugin_')


class RepositoryRequest:

    def __init__(self, user, username, repo, commit):

        if not hasattr(user, 'id') and not hasattr(user, 'pk'):
            user = User(pk=user)

        self.user = user
        self.commit = commit
        self.username = username
        self.repo = repo

    def delete(self):
        self.remove()

    @classmethod
    def from_string(cls, string):
        return cls(*string.split('##'))

    @cached_property
    def repository_instance(self):
        return Repository(self.user)

    @property
    def value(self):
        return '{}##{}##{}##{}'.format(self.user.id, self.username, self.repo, self.commit)

    def remove(self):
        redis_storage.lrem('requests', 1, self.value)

    def send(self):
        self.remove()
        redis_storage.lpush('requests', self.value)

    def approve(self, message):
        self.remove()
        self.repository_instance.approve(self, message)

    def reject(self, message):
        self.remove()
        self.repository_instance.reject(self, message)


class Repository:

    def __init__(self, user):
        self.__user = user
        self.__redis = redis_storage
        self.__info = None
        self.__load()

    @property
    def info(self):
        assert self.initialized
        return self.__info

    def __load(self):
        value = self.__redis.get(self.redis_key)

        if value is None:
            self.__info = None
        else:
            self.__info = UserPluginInfo.from_tuple(value)

        if self.__info and not path.isdir(self.repository_directory):
            self.delete_redis()
            self.__info = None

    def broadcast(self, data):
        from biohub.core.websocket.tool import broadcast_user

        broadcast_user('user-plugin', self.__user, data)

    def delete_redis(self):
        self.__redis.delete(self.redis_key)
        self.broadcast(None)

    def __dump(self):
        self.__redis.set(self.redis_key, self.__info and self.__info.tuple)
        self.__redis.persist(self.redis_key)
        self.broadcast(self.serialize())

    def __read_head_commit(self):
        if not self.initialized:
            return None

        output, _ = subprocess.Popen(
            [
                'git',
                'log',
                '-1',
                'origin/HEAD'
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            cwd=self.repository_directory
        ).communicate()

        return output.decode().partition('\n')[0][7:]

    def __clone(self):

        if path.isdir(self.repository_directory):
            return

        p = subprocess.Popen(
            [
                'git',
                'clone',
                self.repository_url,
                self.repository_directory
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            env=dict(GIT_TERMINAL_PROMPT='0')
        )
        _, error = p.communicate()

        if p.returncode != 0:
            self.__drop_repository
            self.__raise(error)

    def __drop_repository(self):

        try:
            import shutil
            shutil.rmtree(self.repository_directory)
        except OSError:
            pass

    def __raise(self, message):
        raise RepositoryException(self.__user, str(message))

    def __send_request(self, commit=None):
        r = RepositoryRequest(self.__user, self.__info.username, self.__info.repo, commit or self.__info.commit)
        r.send()

        return r

    @property
    def repository_url(self):
        return 'https://github.com/{}/{}'.format(self.__info.username, self.__info.repo)

    @property
    def repository_directory(self):
        assert self.__info is not None
        return path.join(biohub_settings.PLUGINS_DIR, self.__info.repo)

    @property
    def initialized(self):
        return self.__info is not None and self.__info.status != UserPluginStatus.REJECTED

    def serialize(self):

        if self.__info is None:
            return 0

        return dict(
            username=self.__info.username,
            repo=self.__info.repo,
            status=self.__info.status.value,
            request_status=self.__info.request_status.value,
            message=self.__info.message,
            commit=self.__info.commit
        )

    def init(self, username, repo):

        if self.initialized:
            self.__raise('Repository has been initialized.')

        if not (repo and all(s.isidentifier() for s in repo.split('.'))):
            self.__raise('Invalid repo name.')

        try:
            import importlib
            importlib.import_module(repo)
        except ModuleNotFoundError:
            pass
        else:
            self.__raise('Repo name conflicts with an existing module.')

        self.__info = UserPluginInfo(
            username=username,
            repo=repo
        )

        self.__clone()

        self.__info.commit = self.__read_head_commit()
        request = self.__send_request(self.__info.commit)
        self.__info.message = 'Requesting to install plugin at commit {}...'.format(self.__info.commit)
        self.__dump()

        return request

    def approve(self, request, message):
        p = subprocess.Popen(
            ['git', 'checkout', '-qf', request.commit],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            cwd=self.repository_directory
        )

        _, error = p.communicate()

        if p.returncode != 0:
            self.__raise(error)

        if self.__info.repo in plugin_manager.plugin_infos:
            plugin_manager.refresh_plugins([self.__info.repo])
            bridge.send(('refresh', [self.__info.repo]))
        else:
            plugin_manager.install([self.__info.repo], update_config=True)
            bridge.send(('install', [self.__info.repo]))

        self.__info.status = UserPluginStatus.RUNNING
        self.__info.request_status = UserPluginRequestStatus.APPROVED
        self.__info.message = 'Your request has been approved. {}'.format(message)
        self.__dump()

    def reject(self, request, message):

        if self.__info.status != UserPluginStatus.RUNNING:
            self.__info.status = UserPluginStatus.REJECTED

        self.__info.request_status = UserPluginRequestStatus.REJECTED
        self.__info.message = 'Your request has been rejected. {}'.format(message)
        self.__dump()

    def request_upgrade(self):

        if self.__info.status == UserPluginStatus.PENDING:
            self.__raise('The plugin is still pending.')

        p = subprocess.Popen(
            [
                'git', 'fetch', 'origin', 'master'
            ],
            cwd=self.repository_directory,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE
        )

        _, error = p.communicate()

        if p.returncode != 0:
            self.__raise(error)

        new_commit = self.__read_head_commit()
        if new_commit == self.__info.commit and 'ERROR_IF_NO_NEW' in os.environ:
            self.__raise('No new commit on master branch.')

        request = self.__send_request(new_commit)
        self.__info.message = 'Requesting to upgrade to commit {}...'.format(new_commit)
        self.__info.request_status = UserPluginRequestStatus.PENDING
        self.__dump()

        return request

    def remove(self):
        if not self.__info:
            return

        self.delete_redis()

        plugin_manager.remove([self.__info.repo], update_config=True)
        self.__drop_repository()

    @cached_property
    def redis_key(self):
        return 'user-plugin-{}'.format(self.__user.id)


def get_requests():
    return list(redis_storage.lrange('requests', 0, -1))
