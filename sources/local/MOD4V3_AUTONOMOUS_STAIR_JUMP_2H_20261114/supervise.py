"""Evaluate complete checkpoints on free GPU1 without changing the training window."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import time

GPU1 = 'GPU-c27eecbd-6838-7290-1cd2-37e34522213d'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', required=True)
    parser.add_argument('--train-job', required=True)
    args = parser.parse_args()
    plan = json.loads(Path(args.plan).read_bytes())
    root, train = Path(plan['task_root']), Path(args.train_job)
    active = None
    history = root / ('SUPERVISION_' + train.name + '.jsonl')

    def record(value):
        with history.open('a', encoding='utf8') as stream:
            stream.write(json.dumps(dict(epoch=time.time(), **value)) + '\n')

    record(dict(event='started', automatic_training_extension=False, training_pid_owned=False))
    while True:
        if active is not None:
            proc, name = active
            if proc.poll() is None:
                time.sleep(10.)
                continue
            record(dict(event='evaluation_closed', name=name, returncode=proc.returncode))
            active = None
        if (train / 'ERROR.json').exists() or ((train / 'SAFE_CLOSED.json').exists() and not (train / 'FINAL.json').exists()):
            record(dict(event='training_failed', training_restarted=False))
            return
        candidates = sorted(path for path in train.glob('model_*.pt') if path.name != 'model_first_complete.pt')
        pending = [path for path in candidates if not (root / ('LAUNCH_eval_' + train.name + '_' + path.stem + '.json')).exists()]
        if pending:
            owners = subprocess.run(['nvidia-smi', '--query-compute-apps=gpu_uuid,pid', '--format=csv,noheader'],
                                    capture_output=True, text=True, check=True).stdout
            if GPU1 not in owners:
                checkpoint = pending[0]
                name = 'eval_' + train.name + '_' + checkpoint.stem
                job = root / name
                env = dict(os.environ, CUDA_VISIBLE_DEVICES=GPU1)
                cmd = [plan['python'], '-u', str(Path(plan['root']) / 'autonomous_stair/run.py'),
                       '--plan', args.plan, '--job', str(job), '--mode', 'evaluate',
                       '--num-envs', '256', '--checkpoint', str(checkpoint)]
                # Module execution preserves the versioned package's relative imports.
                cmd[2:3] = ['-c', 'import sys;sys.path.insert(0,' + repr(plan['root']) + ');from autonomous_stair.run import main;main()']
                with (root / (name + '.log')).open('xb', buffering=0) as stream:
                    proc = subprocess.Popen(cmd, cwd=root, env=env, stdin=subprocess.DEVNULL,
                                            stdout=stream, stderr=stream, start_new_session=True)
                receipt = dict(epoch=time.time(), pid=proc.pid, physical_gpu=1, checkpoint=str(checkpoint),
                               job=str(job), optimizer_updates=0, cmd=cmd)
                (root / ('LAUNCH_' + name + '.json')).write_text(json.dumps(receipt, indent=2) + '\n')
                record(dict(event='evaluation_started', name=name, pid=proc.pid))
                active = proc, name
        elif (train / 'FINAL.json').exists() and (train / 'SAFE_CLOSED.json').exists():
            final_eval = root / ('eval_' + train.name + '_model_final')
            record(dict(event='complete', training_restarted=False,
                        final_checkpoint_evaluated=(final_eval / 'RESULT.json').exists(),
                        final_evaluation_failed=(final_eval / 'ERROR.json').exists()))
            return
        time.sleep(10.)


if __name__ == '__main__':
    main()
