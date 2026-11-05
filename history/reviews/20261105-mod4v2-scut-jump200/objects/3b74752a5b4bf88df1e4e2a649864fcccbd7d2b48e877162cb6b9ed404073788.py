"""Finite read of the original runtime and canonical, through the existing local gate."""
from pathlib import Path
import hashlib, importlib.util, json, time

HERE = Path(__file__).resolve().parent
REPORTS = HERE / 'reports'
REPORTS.mkdir(exist_ok=True)
OLD = HERE.parent / 'mod4v1_scut_step270_2h_20261103'
spec = importlib.util.spec_from_file_location('mod4v2_existing_transport', OLD / 'run.py')
local = importlib.util.module_from_spec(spec)
spec.loader.exec_module(local)
local.R = REPORTS

CODE = r'''
from pathlib import Path
import json,time,psutil,fcntl,subprocess,shutil
base=Path('/home/lc01/Zonglin Li/zonglin2')
root=base/'tasks/MOD4_STANDING200_RLBPTT_V6_1793639156617427400'
C=base/'state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json'
c=json.loads(C.read_bytes())
locks={}
for p in [C.parent/'native_floor_supervisor.lock',C.parent/'autonomy_controller.lock',C.parent.parent/'finite_environment_validation.lock']:
 try:
  with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
  locks[str(p)]=True
 except BlockingIOError:locks[str(p)]=False
files={}
for rel in ['runtime/isaac/mod4/train_mod4v1_e0.py','runtime/isaac/mod4/launcher_mod4v1_e0.py','runtime/isaac/mod4/mod4v1_e0_asset_compat.py','runtime/isaac/mod4/reset_bank.json','runtime/isaac/mod4/mod4_task.py','runtime/isaac/mod4/mod4v1_fresh_dr_guard.py','original_run_manifest.json']:
 p=root/rel;raw=p.read_bytes();import hashlib
 files[rel]=dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),text=raw.decode('utf8'))
old=base/'tasks/MOD4V1_SCUT_STEP270_2H_1793711274668684600/env20000_jump200_tuck_retraction_1h_20261105'
closed={name:json.loads((old/name).read_bytes()) for name in ['OWNER_EXIT.json','TRAIN_CLOSED.json']}
oldidentity=json.loads((old/'OWNER_STARTED.json').read_bytes())['identity']
alive=False
try:
 p=psutil.Process(oldidentity['pid']);alive=p.create_time()==oldidentity['creation'] and p.status()!=psutil.STATUS_ZOMBIE
except psutil.Error:pass
print(json.dumps(dict(epoch=time.time(),canonical=dict(path=str(C),active=c['active_segment'],remaining=c['remaining_training_seconds'],generation=c['authority_generation']),locks=locks,old_exit=closed,old_exact_alive=alive,files=files)))
'''

if __name__ == '__main__':
    assert not (REPORTS / 'DISCOVERY_ACTUAL.json').exists()
    with local.connection('MOD4V2_STOP_AND_RUNTIME_READ') as (client, transport):
        value = transport.code(client, transport.PY72, CODE, {}, timeout=60)
        (REPORTS / 'DISCOVERY_ACTUAL.json').write_text(json.dumps(value, indent=2), encoding='utf8')
        snapshot = HERE / 'runtime_refs'
        snapshot.mkdir()
        for rel, row in value['files'].items():
            target = snapshot / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(row['text'].encode('utf8'))
            assert hashlib.sha256(target.read_bytes()).hexdigest() == row['SHA']
    print(json.dumps({key: val for key, val in value.items() if key != 'files'}))
