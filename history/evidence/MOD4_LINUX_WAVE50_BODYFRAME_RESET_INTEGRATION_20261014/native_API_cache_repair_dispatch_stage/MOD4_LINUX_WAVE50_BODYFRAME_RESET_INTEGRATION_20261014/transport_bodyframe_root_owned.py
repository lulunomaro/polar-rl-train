"""Sequential root-owned Linux transport; import has no network side effects."""
from pathlib import Path
import hashlib
import json
import os
import sys
import time
import traceback

B = Path(__file__).resolve().parent; W = B.parent; REPORTS = B / 'reports'
PY = '/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
BASE = '/mnt/mod4_linux_durable_20261013/MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013'
ROOT = BASE + '/bodyframe20k_repair_pipeline_v1_20261014'
OLD = BASE + '/left_exploration20k_second_formal_sameidentity_v1'
SOURCE = 'e3e825b1e24f11885f2f9d5b196d85cbce4a46363cd09b440e7efa2b846fd47c'


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def connect():
    sys.path.insert(0, str(W / 'MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013'))
    from read_linux_resume_boundary_actual import connect_linux_only
    return connect_linux_only()
def close(c):
    if c: c.close()
    os.environ.pop('RM_SSH_PASSWORD', None)
def save(name, value):
    p = REPORTS / (name + '_' + str(time.time_ns()) + '.json')
    with p.open('x', encoding='utf8') as out: json.dump(value, out, ensure_ascii=False, indent=2)
    return p
def run(c, code, context, label, timeout=180):
    si, so, se = c.exec_command('CUDA_VISIBLE_DEVICES= ' + PY + ' -', timeout=timeout)
    si.write('CONTEXT=' + repr(context) + '\n' + code); si.flush(); si.channel.shutdown_write()
    out = so.read(); err = se.read(); rc = so.channel.recv_exit_status()
    receipt = save(label, dict(epoch=time.time(), code=rc, stdout=out.decode('utf8', errors='replace'),
        stderr=err.decode('utf8', errors='replace'), no_automatic_retry=True))
    assert rc == 0, str(receipt)
    return json.loads(out), receipt


INSPECT = r'''
from pathlib import Path
import os,json,hashlib,time,subprocess,fcntl,shutil,psutil
base=Path(CONTEXT['base']);old=Path(CONTEXT['old']);r=Path(CONTEXT['root'])
B=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
locks=[]
for p in [B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')]:
 f=p.open('r+b')
 try:
  try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:locks.append(dict(path=str(p),held=True))
  else:fcntl.flock(f,fcntl.LOCK_UN);locks.append(dict(path=str(p),held=False))
 finally:f.close()
d=json.loads(B.read_bytes());ready=json.loads((old/'LEFT_SECOND_FORMAL_SAVED_REVIEW_READY.json').read_bytes())
source=Path(ready['own_checkpoint'])
gpu=subprocess.check_output(['nvidia-smi','--query-gpu=name,memory.free','--format=csv,noheader,nounits'],text=True).strip()
apps=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],text=True).strip()
print(json.dumps(dict(epoch=time.time(),hostname=os.uname().nodename,available_RAM=psutil.virtual_memory().available,durable_free=shutil.disk_usage(base).free,GPU=gpu,GPU_apps=apps,locks=locks,canonical_active=d['active_segment'],canonical_remaining=d['remaining_training_seconds'],canonical_SHA=hashlib.sha256(B.read_bytes()).hexdigest(),source_path=str(source),source_SHA=hashlib.sha256(source.read_bytes()).hexdigest(),source_bytes=source.stat().st_size,newroot_exists=r.exists(),newroot_files=[x.name for x in r.iterdir()] if r.exists() else [],read_only=True)))
'''


if __name__ == '__main__':
    c = None
    try:
        c = connect(); result, p = run(c, INSPECT, dict(base=BASE, old=OLD, root=ROOT), 'BODYFRAME_LINUX_ACTUAL_BOUNDARY')
        print(json.dumps(dict(report=str(p), actual=result)))
    except BaseException:
        print(save('BODYFRAME_TRANSPORT_ORIGINAL_ERROR', dict(epoch=time.time(), error=traceback.format_exc(), no_retry=True)))
        raise
    finally: close(c)
