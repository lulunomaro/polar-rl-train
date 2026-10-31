"""Original node CLI -> metadata guard -> complete same-profile full PPO."""
from pathlib import Path
import argparse
import json
import runpy
from contract227 import validate_job


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--mode', choices=('train',), required=True)
    p.add_argument('--num-envs', type=int, required=True)
    p.add_argument('--run-id', required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    job = a.out.resolve().parent
    task = json.loads((job/'TASK.json').read_bytes())
    go = json.loads((job/'GO_PRODUCTION.json').read_bytes())
    validate_job(job, task, go)
    # The underlying full worker verifies its own SHA with this separate field.
    assert task['worker_SHA'] == task['full_worker227_SHA']
    runpy.run_path(str(job/'worker_full227.py'), run_name='__main__')


if __name__ == '__main__':
    main()
