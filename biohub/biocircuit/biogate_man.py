__author__ = 'E-Neo <e-neo@qq.com>'

import json
import os
import logging
import filelock
import tempfile

from django.utils.functional import SimpleLazyObject


logger = logging.getLogger(__name__)

dirname = os.path.dirname(os.path.abspath(__file__))
GatesJsonFile = os.path.join(dirname, 'gates_lizhi.json')
GatesPyFile = os.path.join(dirname, 'biogate.py')

gates_updating_lock = filelock.FileLock(
    os.path.join(tempfile.gettempdir(), 'biohub.biocircuit.gates.updating.lock')
)


def get_d_gate(lizhi):
    """Get d_gate from gates_lizhi.json.

    Parameters
    ----------
    lizhi : dict
        A string parsed from lizhi.json

    Returns
    -------
    d_gate_d : dict
        Record the 4 parameters.
    """
    g_and = {}
    g_not = {}
    g_or = {}
    for i in lizhi:
        logging.debug('map:')
        for j in i['map']:
            logging.debug(j)
        for j in i:
            if j != 'map':
                logging.debug('%s: %s' % (j, i[j]))
        para = [0, 0, 0, 0]
        for j in i['map']:
            if j['type'] == 'inh':
                para[0] += 1
            elif j['type'] == 'act':
                para[1] += 1
            elif j['type'] == 'lock':
                para[2] += 1
            elif j['type'] == 'key':
                para[3] += 1
        para = tuple(para)
        if i['id'][0] == 'A':
            g_and[i['id']] = para
        elif i['id'][0] == 'N':
            g_not[i['id']] = para
        elif i['id'][0] == 'O':
            g_or[i['id']] = para
    d_gate_d = {'not': g_not, 'and': g_and, 'or': g_or}
    return d_gate_d


def update_d_gate():
    locked = gates_updating_lock.is_locked

    with gates_updating_lock:
        if locked:
            return

        logging.info('Updating the gates from %s.' % GatesJsonFile)

        d_gate = get_d_gate(load_gates_json())

        with open(GatesPyFile, 'w') as fp:
            fp.write('d_gate = {}'.format(d_gate))


def load_gates_json():
    with open(GatesJsonFile, 'r') as fp:
        result = json.load(fp)
    return result


def _fetch_biogate():
    try:
        from . import biogate
    except ImportError:
        update_d_gate()
        from . import biogate

    return biogate


biogate = SimpleLazyObject(_fetch_biogate)
