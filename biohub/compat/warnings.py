"""
This module is to better print out warning message. It:

 + Switches on warnings capture in logging system.
 + Monkey patches `warnings._formatwarnmsg_impl` to override default warning
   message format.
 + Sets up logging handler `py.warnings` to output warning messages.
"""

import warnings
import logging
import logging.config

logging.captureWarnings(True)

RESET_SEQ = "\033[0m"
RED_SEQ = "\033[;31m"
BOLD_SEQ = "\033[1m"


def _formatwarnmsg_impl(msg):

    return '%s%s%s: %s%s' % (
        RED_SEQ, BOLD_SEQ,
        msg.category.__name__, msg.message,
        RESET_SEQ)


warnings._formatwarnmsg_impl = _formatwarnmsg_impl

logging.config.dictConfig({
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler'
        }
    },
    'loggers': {
        'py.warnings': {
            'handlers': ['console'],
            'level': 'WARNING'
        }
    }
})
