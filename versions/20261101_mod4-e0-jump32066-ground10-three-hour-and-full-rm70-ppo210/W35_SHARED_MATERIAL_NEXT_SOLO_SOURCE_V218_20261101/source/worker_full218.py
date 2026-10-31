"""Unexecuted next-window wrapper; delegates byte-identical frozen214 worker.

Original owner/node retain EX, GO, accounting, STOP_AFTER_SAVE and child wait.
"""
from pathlib import Path
import argparse
import json
import runpy
import sys
from contract218 import metadata, validate_job_before_delegate, h_bytes, WORKER214_SHA


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=('train',), required=True)
    parser.add_argument('--num-envs', type=int, required=True)
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    job = args.out.resolve().parent
    task, _, _ = metadata(job / 'TASK.json')
    go, _, _ = metadata(job / 'GO_PRODUCTION.json')
    assert args.num_envs == 20000 and args.out.resolve() == job / 'production'
    assert args.run_id == task['run_id'] == go['run_id'] and not args.out.exists()
    receipt = validate_job_before_delegate(job, go, task)
    assert h_bytes(Path(__file__).read_bytes()) == task['entrypoint_SHA']
    delegate = job / 'worker_full214.py'
    assert h_bytes(delegate.read_bytes()) == WORKER214_SHA
    with (job / 'PREDELEGATE218_METADATA_GATE_ACTUAL.json').open('x', encoding='utf8') as f:
        json.dump(receipt, f, indent=2)
    sys.argv[0] = str(delegate)
    runpy.run_path(str(delegate), run_name='__main__')


if __name__ == '__main__':
    main()
