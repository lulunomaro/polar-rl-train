"""Original SSH transport; local collectors do not serialize separate GPUs.

Human 2026-11-05: 不用等控制器释放，账本共用，直接开训别浪费时间.
Actual server canonical admission and private GPU leases remain authoritative.
"""
from contextlib import contextmanager
from pathlib import Path
import importlib.util
import json
import os
import sys
import time

N = Path(__file__).resolve().parent
OLD = N.parent / 'mod4v1_scut_step270_2h_20261103'
PRIOR = N.parent / 'h1_target_limit_cont_20261103/run.py'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@contextmanager
def connection(reports, label):
    reports = Path(reports)
    inventory = load('v2_shared_local_inventory', OLD / 'run.py')
    original = load('v2_original_shared_transport', PRIOR)

    def put(name, value, root=None):
        with (reports / name).open('x', encoding='utf8') as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)

    def gate(current_label):
        rows = inventory.local_rows()
        own = [row for row in rows if row['ProcessId'] == os.getpid()]
        put(current_label + '_LOCAL_CIM.json', dict(
            epoch=time.time(), rows=rows,
            local_controller_inventory_informational=True,
            global_local_serial_wait_removed=True,
            human_authorization='不用等控制器释放，账本共用，直接开训别浪费时间',
            server_canonical_and_actual_GPU_leases_authoritative=True))
        assert len(own) == 1 and own[0]['CreationDate']
        assert own[0]['ExecutablePath'].replace('\\', '/').lower() == sys.executable.replace('\\', '/').lower()

    original.R = reports
    original.put = put
    original.gate = gate
    with original.connection(label) as pair:
        yield pair
