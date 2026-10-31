"""Worker binding for the separate normal-H1 PPO40050 branch; no authority IO."""
from pathlib import Path
import hashlib,json,os,time
KIND='MOD4_NORMAL_H1_PPO86B_400N50_NEW86_V1'
SOURCE_SHA='71db5543b14919eb11d2a8606f9ffe1acf0814260d7d89aa823565a49a7b21c4'
GPU='GPU-90a66ae2-f536-7033-79c0-487536ae36d3'
FIELDS=dict(kind=KIND,key='normal_h1_86',logical_slot='normal_h1_86',canonical_worker_key='h1',execution_backend='target86',GPU_UUID=GPU,source_SHA=SOURCE_SHA,source_Adamstep=832460,num_envs=20000,policy_hz=50,physics_dt_s=.0025,decimation=8,feedback_hz=100,public_phase_tick_hz=100,nominal_gas_N_each=400,nominal_gas_k_N_m=2000,original_H1_true270_reward_task=True,normal_PPO_not_native=True)
def validate_task_go(task,go,manifest_SHA):
 for k,v in FIELDS.items():assert task[k]==go[k]==v,k
 assert go['payload_manifest_SHA']==manifest_SHA and go['worker_SHA']==task['worker_SHA']
 assert go['source_CPU_SHA']==task['source_CPU_SHA'] and go['CPU_waited_proof_SHA']==task['CPU_waited_proof_SHA']
 for k in ('worker_SHA','source_CPU_SHA','CPU_waited_proof_SHA'):
  assert isinstance(task[k],str) and len(task[k])==64 and all(c in '0123456789abcdef' for c in task[k]),k
 assert go['run_id']==task['run_id'] and isinstance(go['run_id'],str) and go['run_id']
 assert go['max_parent_seconds']==3900 and go['exit_headroom_seconds']==300
 start=go['learning_started_epoch'];assert go['save_deadline']==start+3600 and go['nominal_end_epoch']==start+3900
 assert time.time()<go['save_deadline']
 assert os.environ['CUDA_VISIBLE_DEVICES']==GPU
 return True
def check_payload(root,task,go):
 root=Path(root).resolve();p=root/'NORMAL_H1_PPO40050_COMPLETE_INPUT_MANIFEST_V1.json';raw=p.read_bytes();m=json.loads(raw);manifest_SHA=hashlib.sha256(raw).hexdigest();validate_task_go(task,go,manifest_SHA)
 for r in m['files']:
  q=root/r['relative'];assert q.resolve().is_relative_to(root) and not q.is_symlink() and q.stat().st_size==r['bytes']
  # Binary producer verification is a real admission action, never a Git reread.
  with q.open('rb') as f:actual=hashlib.file_digest(f,'sha256').hexdigest()
  assert actual==r['SHA'],r['relative']
 assert task['source_filename']=='NORMAL_H1_86B138_N20K_PPO50_GAS400_NOT_GPU_ADMITTED.pt'
 return manifest_SHA
