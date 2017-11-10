import signal
from channels import worker


def _safe_register(signum, handler):

    old_handler = signal.getsignal(signum)

    if callable(old_handler):

        def new_handler(*args, **kwargs):
            old_handler(*args, **kwargs)
            handler(*args, **kwargs)

        signal.signal(signum, new_handler)
    else:
        signal.signal(signum, handler)


def patched_install_signal_handler(self):
    _safe_register(signal.SIGTERM, self.sigterm_handler)
    _safe_register(signal.SIGINT, self.sigterm_handler)


worker.Worker.install_signal_handler = worker.WorkerGroup.install_signal_handler = patched_install_signal_handler
