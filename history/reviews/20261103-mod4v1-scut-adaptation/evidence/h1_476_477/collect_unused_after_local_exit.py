"""Recover only unused normal/CPU/eval after the original local controller exited.

Never replay POSTROUND_ONCE/launch/FIRST/bind. Each original stage retains its
own exclusive once. The unchanged original runner supplies all SSH/gates.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time

N = Path(__file__).resolve().parent
R = N/'reports'
spec = importlib.util.spec_from_file_location('run476_existing', N/'run.py')
run = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run)
if __name__ == '__main__':
    for name in ('NORMAL_ONCE.json', 'EVAL_ONCE.json', 'CPU476_NEW_FINAL_CONSUMED.json'):
        assert not (R/name).exists(), 'Stage already consumed: '+name
    rows = run.local_rows()
    assert not [x for x in rows if x['ProcessId'] != os.getpid()]
    run.put('LOCAL_POSTROUND_EXIT_UNUSED_RECOVERY.json', dict(
        epoch=time.time(), original_postround_PID=22620,
        original_postround_creation='2026-11-03T15:15:52.149930+08:00',
        original_local_process_absent=True, original_stderr_bytes=0,
        cause='Unknown local exit; no remote restart or original once replay',
        new_PID=os.getpid(), original_runner_SHA=hashlib.sha256((N/'run.py').read_bytes()).hexdigest(),
        stages='Only original unused normal/fullsave-transfer/CPU/eval/render',
        fresh_local_rows=rows))
    try:
        run.close_original()
        final = run.cpu_final()
        assert final['passed']
        run.wait_local()
        result = run.evaluate(final)
        render = subprocess.run([run.CONTROL, '-B', '-X', 'utf8', str(N/'render_saved_evaluation.py')],
                                cwd=N, capture_output=True, text=True, encoding='utf8')
        run.put('RENDER_PROCESS.json', dict(returncode=render.returncode, stdout=render.stdout, stderr=render.stderr))
        assert render.returncode == 0
        run.put('POSTROUND_RL_DECISION.json', dict(epoch=time.time(),
            status='EVALUATED_PENDING_NATIVE_REVIEW', final=final,
            strict=result['strict_successes'], terminations=result['terminations'],
            evalroot=str(run.V), next='Current model native image and all80 manifold review'))
    except BaseException:
        import traceback
        run.put('RECOVERY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json', dict(
            epoch=time.time(), error=traceback.format_exc(), no_automatic_replay=True))
        raise
