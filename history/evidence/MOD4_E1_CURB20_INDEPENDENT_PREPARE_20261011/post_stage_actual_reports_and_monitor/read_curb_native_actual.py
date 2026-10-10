"""Read actual new CURB native parent, own children and receipts; no launch API."""
from curb_io import *
from stage_curb_native_contract_once import NEW

def main():
    n,w=connect_both()
    try:
        v=linux_json(n,r'''from pathlib import Path
import json,time,hashlib,fcntl
D=Path(NEW_ROOT);R=D/'reports';B=Path(BUDGET)
def proc(v):
 if not v:return None
 p=Path('/proc')/str(v['pid'])
 if not p.exists():return dict(locator=v,actual=None)
 s=(p/'stat').read_text().split(') ',1)[1].split()
 return dict(locator=v,actual=dict(pid=v['pid'],state=s[0],start_ticks=int(s[19]),cwd=str(p.resolve()) if s[0]=='Z' else str((p/'cwd').resolve()),argv=[x.decode() for x in (p/'cmdline').read_bytes().split(b'\0') if x]))
files={};receipts={}
for name in ('CURB_NATIVE_SCOPE_STARTED.json','CURB_NATIVE_SCOPE_STATE.json','CURB_SDK10_PID_RECEIPT.json','CURB_NATIVE20K_PID_RECEIPT.json','CURB_SDK10_PASSED.json','CURB_NATIVE20K_PASSED.json','CURB_NATIVE_SCOPE_PASSED.json','CURB_NATIVE_SCOPE_ATTENTION.json'):
 p=R/name
 if p.exists():
  b=p.read_bytes();receipts[name]=json.loads(b);files[str(p)]=dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
state=receipts.get('CURB_NATIVE_SCOPE_STATE.json',{})
started=receipts.get('CURB_NATIVE_SCOPE_STARTED.json',{})
logs={}
for name in ('curb_native_parent.log','CURB_SDK10.log','CURB_NATIVE20K.log'):
 p=D/name
 if p.exists():
  b=p.read_bytes();logs[name]=dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),last_lines='\n'.join(b.decode(errors='replace').splitlines()[-30:]))
outputs={}
for name in ('CURB_SDK10.json','CURB_NATIVE20K.json'):
 p=D/name
 if p.exists():
  b=p.read_bytes();outputs[name]=json.loads(b);files[str(p)]=dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
locks=[]
for p in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('r') as f:
  try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN);free=True
  except BlockingIOError:free=False
 locks.append(dict(path=str(p),OS_lock_free=free,file_exists=True))
ledger=json.loads(B.read_bytes())
print(json.dumps(dict(epoch=time.time(),root=str(D),receipts=receipts,files=files,outputs=outputs,logs=logs,actual_parent=proc(state.get('owner') or started.get('owner')),actual_child=proc(state.get('child')),two_actual_OS_locks=locks,canonical_SHA=hashlib.sha256(B.read_bytes()).hexdigest(),authorized_seconds=ledger['authorized_training_seconds'],remaining_seconds=ledger['authorized_training_seconds']-ledger['charged_training_seconds'],active_segment=ledger['active_segment'],read_only=True)))
'''.replace('NEW_ROOT',repr(NEW)).replace('BUDGET',repr(B)))
        p=save('CURB_NATIVE_ACTUAL_'+str(time.time_ns())+'.json',v)
        print(json.dumps(dict(report=str(p),phase=v['receipts'].get('CURB_NATIVE_SCOPE_STATE.json',{}).get('phase'),attention=v['receipts'].get('CURB_NATIVE_SCOPE_ATTENTION.json'),actual_parent=v['actual_parent'],actual_child=v['actual_child'],outputs=list(v['outputs']),no_PPO=True)))
    finally:cleanup(n,w)
if __name__=='__main__':main()
