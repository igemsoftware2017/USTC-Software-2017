from biohub.core.tasks import AsyncResult, TaskStatus

from biohub.abacus import remote, consts, conf

remote_status_mapping = dict(
    PENDING=TaskStatus.PENDING,
    RECEIVED=TaskStatus.PENDING,
    STARTED=TaskStatus.RUNNING,
    SUCCESS=TaskStatus.SUCCESS,
    FAILURE=TaskStatus.ERROR,
    REVOKED=TaskStatus.ERROR,
)


class AbacusAsyncResult(AsyncResult):

    properties = ['ident', 'user', 'signature']

    def _after_ready(self, status, result):
        """
        Broadcasts a message when ready.
        """
        from biohub.core.websocket.tool import broadcast_user

        broadcast_user('abacus', self.user, self.response(status, result))

    def _set_ident(self, value):
        if self._get_field('ident') is not None:
            raise AttributeError('ident can only be set once.')

        self._set_field('ident', value)

    def _get_ident(self):
        if hasattr(self, '_ident'):
            return self._ident

        value = self._get_field('ident')
        if value is None:
            value = conf.settings.ident
        else:
            self._ident = value

        return value

    def resolve_remote_response(self, response):

        status = remote_status_mapping[response['status']]
        result = response.get('output', None)

        if status == TaskStatus.SUCCESS:
            self.resolve(result)
        elif status == TaskStatus.ERROR:
            self.error(result)
        elif status == TaskStatus.RUNNING:
            self.run()
        elif status == TaskStatus.PENDING:
            self.pend()

        return status

    def _get_status(self):

        if self.ident == consts.REMOTE and not self.exists():
            return TaskStatus.GONE

        super_get = super(AbacusAsyncResult, self)._get_status

        if self.ident == consts.LOCAL or hasattr(self, '_status'):
            return super_get()

        status = super_get()

        if status.is_ready:
            self._status = status
            return status

        return self.resolve_remote_response(remote.query(self.task_id))

    def response(self, status=None, result=None):
        """
        Returns a unified status response.
        """
        if status is None:
            status = self.status

        ret = dict(status=status.value)
        if status == TaskStatus.SUCCESS:
            ret['output'] = result if result is not None else self.result

        return ret
