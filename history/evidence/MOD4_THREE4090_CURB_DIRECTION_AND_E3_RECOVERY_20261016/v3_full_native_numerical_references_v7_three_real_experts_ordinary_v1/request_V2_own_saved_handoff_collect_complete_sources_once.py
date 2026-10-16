from pathlib import Path
import os,sys,time,json,getpass,traceback
D=Path(__file__).resolve().parent;R=D/'reports';sys.path.insert(0,str(D));from deploy_three_independent_V2_source_restore_then_new_axis_once import ROOTS,code,H,connect72,t,PY
from collect_first_two_native_and_E2_handoff_actual_readonly_once import READ
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
STOP=r'''
from pathlib import Path
import sys,json,time,hashlib,psutil
B=Path(sys.argv[1]);key=sys.argv[2];out=B/'job0'/('production_only' if key=='curb' else 'production');v=json.loads((out/'latest_complete.json').read_bytes());assert v['updates']>=1 and Path(v['path']).stat().st_size==v['bytes'] and hashlib.sha256(Path(v['path']).read_bytes()).hexdigest()==v['SHA'];procs=[]
for p in psutil.process_iter(['pid','create_time','cmdline']):
 try:
  if str(B/'production_worker.py') in (p.info['cmdline'] or []):procs.append(p.info)
 except psutil.Error:pass
p=out/'STOP_AFTER_SAVE.json';created=False
if procs and not p.exists():
 with p.open('x') as f:json.dump(dict(epoch=time.time(),reason='Human requested maximum three4090 utilization: cooperative complete-update/save handoff to unified three-expert dispatch. Retain progress and actual original costs.',no_POSIX_signal_or_force_kill=True),f,indent=2)
 created=True
print(json.dumps(dict(epoch=time.time(),root=str(B),latest_complete_before_handoff=v,actual_workers=procs,own_cooperative_save_flag_created=created,prior_flag=json.loads(p.read_bytes()) if p.exists() else None,no_other_scope_or_SDK_changed=True)))
'''
FINALS=r'''
from pathlib import Path
import sys,json,time,hashlib
B=Path(sys.argv[1]);out=B/'job0'/('production_only' if sys.argv[2]=='curb' else 'production');v=json.loads((out/'FINAL.json').read_bytes());assert v['passed'];row=v['final'];p=Path(row['path']);assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA'];print(json.dumps(row))
'''
def download(c,row,key):
 folder=D/'actual_V2_safe_handoff_final_models';folder.mkdir(exist_ok=True);p=folder/(key+'_final.pt');q=p.with_suffix('.pt.partial');assert not p.exists() and not q.exists();sf=c.open_sftp();sf.get_channel().settimeout(120)
 try:sf.get(row['path'],str(q));assert q.stat().st_size==row['bytes'] and H(q)==row['SHA'];q.replace(p)
 finally:sf.close()
 return dict(**row,local_path=str(p),twohost_bytes_SHA_exact=True)
def main():
 put('SAFE_COMPLETE_UPDATE_HANDOFF_TRANSPORT_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_transport=True,human_three_card_use_safe_saved_handoff=True,local_readonly_collector_keyboard_interrupt_retained_not_remote_signal=True));pw=getpass.getpass('Host72 own complete-update saved handoff (hidden): ');c=None;v={}
 try:c=t.connect();v['curb_flag']=code(c,t.PY,STOP,ROOTS['curb'],'curb');put('V2_CURB_OWN_COOPERATIVE_SAVED_HANDOFF_REQUEST_ACTUAL.json',v['curb_flag'])
 finally:t.close(c);c=None
 try:c=connect72(pw);v['e2_flag']=code(c,PY,STOP,ROOTS['e2'],'e2');put('V2_E2_OWN_COOPERATIVE_SAVED_HANDOFF_REQUEST_ACTUAL.json',v['e2_flag'])
 finally:
  if c:c.close();c=None
 try:
  c=t.connect();begun=time.monotonic()
  while True:
   x=code(c,t.PY,READ,ROOTS['curb'],'curb')
   if any(r['path'].endswith('/OWNER_EXIT_ACTUAL.json') for r in x['files']):break
   assert time.monotonic()-begun<240,'Own complete save/exit not yet observed; no force action';time.sleep(10)
  assert not x['actual_own_processes'];v['curb']=x;v['curb_model']=download(c,code(c,t.PY,FINALS,ROOTS['curb'],'curb'),'curb');v['canonical']=code(c,t.PY,"from pathlib import Path;import time,json,fcntl;C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');v=json.loads(C.read_bytes());assert v['active_segment'] is None;locks=[]\nfor p in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):\n with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN);locks.append(str(p))\nprint(json.dumps(dict(epoch=time.time(),active=None,remaining=v['remaining_training_seconds'],charged=v['charged_training_seconds'],last_completed=v['completed_segments'][-1],actual_two_fcntl_free=locks)))")
 finally:t.close(c);c=None
 try:
  c=connect72(pw);pw=None;v['e2']=code(c,PY,READ,ROOTS['e2'],'e2');assert not v['e2']['actual_own_processes'];v['e2_model']=download(c,code(c,PY,FINALS,ROOTS['e2'],'e2'),'e2')
 finally:
  pw=None
  if c:c.close()
 v['epoch']=time.time();put('V2_TWO_REAL_PPO_COMPLETE_SAFE_HANDOFF_MODELS_AND_CANONICAL_ACTUAL.json',v);print(json.dumps(dict(epoch=v['epoch'],curb_model=v['curb_model'],e2_model=v['e2_model'],actual_original_cost=v['canonical']['last_completed']['experts'],old_canonical_active=None,no_progress_discarded_or_refund=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put('SAFE_HANDOFF_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_force_retry_or_GPU_replay=True));raise
