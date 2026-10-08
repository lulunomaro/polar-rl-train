"""Collect completed frozen jobs and verify the existing bridge return bytes.

Read only: never enqueues work or launches physics/training.
"""
from pathlib import Path
import json, sys, time, hashlib

D = Path(__file__).resolve().parent
R = D / 'reports'
sys.path.insert(0, str(D.parent / 'MOD4_AUTONOMY_SLEEP_20261003'))
sys.path.insert(0, str(D.parent / 'MOD4_MOE_PLAN_EXECUTION_20261007'))
from remote_io import connect
from eval_remote_io import connect_eval

prefix = 'clk2500-closure-episode-d3-'
labels = [f'40-d4-anchor-{k}' for k in ('flat', 'spin', 'world')]
labels += [f'50-d4-b1-{k}' for k in ('flat', 'spin', 'world')]
labels += ['45-d4world-anchor-world', '55-d4world-b1-world']
native_root = '/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/eval_results'
eval_root = 'D:/MOD4_async_eval/closure_episode_clock2500_v15/jobs'
native = connect()
evaluator = connect_eval()
try:
    rows = []
    pending = []
    with native.open_sftp() as n, evaluator.open_sftp() as w:
        for label in labels:
            job = prefix + label
            try:
                w.stat(eval_root + '/' + job + '/complete.json')
                n.stat(native_root + '/' + job + '/result.json')
                n.stat(native_root + '/' + job + '/probe.json')
            except FileNotFoundError:
                pending.append(job)
                continue
            folder = R / 'windows' / job
            folder.mkdir(parents=True, exist_ok=True)
            hashes = {}
            for name in ('manifest.json', 'complete.json', 'result.json', 'probe.json'):
                raw = w.open(eval_root + '/' + job + '/' + name).read()
                (folder / name).write_bytes(raw)
                bridge_exact = None
                if name in ('result.json', 'probe.json'):
                    returned = n.open(native_root + '/' + job + '/' + name).read()
                    assert returned == raw, (job, name, 'bridge differs')
                    bridge_exact = True
                hashes[name] = dict(sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw),
                                    automatic_bridge_return_bytes_exact=bridge_exact)
            result = json.loads((folder / 'result.json').read_text(encoding='utf8'))
            assert result['exit_code'] == 0 and not result['errors'] and not result['error_files']
            rows.append(dict(id=job, files=hashes, result=result))
    value = dict(epoch=time.time(), jobs=rows, pending=pending,
                 no_GPU_PPO_publication_or_budget_write=True)
    (R / 'COMPLETED_D4_SCOPE_FILES.json').write_text(json.dumps(value, indent=2), encoding='utf8')
    print(json.dumps(dict(complete=[r['id'] for r in rows], pending=pending,
                         bridge_returned_JSON_files_exact=2*len(rows))))
finally:
    evaluator.close()
    native.close()
