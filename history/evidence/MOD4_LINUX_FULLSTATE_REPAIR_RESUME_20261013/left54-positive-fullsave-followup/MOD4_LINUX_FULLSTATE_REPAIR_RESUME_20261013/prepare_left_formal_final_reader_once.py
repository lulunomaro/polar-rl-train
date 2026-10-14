"""Prepare an independent final-only fulltrace reader, never execute it early."""
from pathlib import Path
import json,time,hashlib
D=Path(__file__).resolve().parent
s=(D/'review_original_linux20k_final_complete_trace_CPU_actual.py').read_text()
s=s.replace('from deploy_original_linux20k_formal_once import S as BASE,PY,D',"D=Path(__file__).resolve().parent\nPY='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'")
s=s.replace("S=BASE.replace('_v1','_runtime_assets_complete_v3')","S='/mnt/mod4_linux_durable_20261013/MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013/left_exploration20k_first_formal_v1'")
old="R=Path(S);close=json.loads((R/'INDEPENDENT_POSTEXIT_TYPED_SCHEMA_ACTUAL.json').read_bytes());assert close['independent_postexit_pass']\np=Path(close['ownfullsave']['path']);ck=torch.load(p,map_location='cpu',weights_only=False);run=p.parent"
new="""R=Path(S);actual=json.loads((R/'LEFT_FORMAL_SAVED_REVIEW_READY.json').read_bytes());assert actual['actual_first_formal_window'] and actual['actor9_changed']
ex=json.loads((R/'left_formal3600_v1/EXIT_RECEIPT.json').read_bytes());assert ex['returncode']==0 and ex['child_actually_absent'] and ex['canonical_cost_charged_once'] and not ex['physics_capacity_error']
import fcntl,psutil
who=ex['child'];assert not psutil.pid_exists(who['pid']) or psutil.Process(who['pid']).create_time()!=who['created']
B=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');assert json.loads(B.read_bytes())['active_segment'] is None
for lock in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with lock.open('r+b') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
close=dict(ownfullsave=dict(path=actual['own_checkpoint'],sha256=actual['checkpoint_sha256']),actual_saved_updates=actual['actual_saved_updates'])
p=Path(close['ownfullsave']['path']);ck=torch.load(p,map_location='cpu',weights_only=False);run=p.parent"""
assert old in s;s=s.replace(old,new)
s=s.replace('FINAL_FULL_TRAINING_TRACE_CPU_ACTUAL.json','LEFT_FORMAL_FINAL_FULLTRACE_CPU_ACTUAL.json').replace('ORIGINAL_LINUX20K_FINAL_FULLTRACE_CPU_ACTUAL_','LEFT_FORMAL_FINAL_FULLTRACE_CPU_ACTUAL_')
q=D/'review_left_formal_final_complete_trace_CPU_actual.py';assert not q.exists();compile(s,str(q),'exec');q.write_text(s,encoding='utf8')
(D/'reports/LEFT_FORMAL_FUTURE_FULLTRACE_READER_PREPARED.json').write_text(json.dumps(dict(epoch=time.time(),prepared_path=str(q),sha256=hashlib.sha256(q.read_bytes()).hexdigest(),no_GPU_CPU_review_executed_yet=True,requires_actual_own_final_parent_unique_closed_and_two_locks_free=True,no_import_once=True),indent=2),encoding='utf8');print(str(q))
