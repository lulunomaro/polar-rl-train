"""CPU source guard, sourcefreeze and real resource guard for one isolated repairaxis."""
from pathlib import Path
import hashlib,json,os,subprocess,shutil,psutil
D=Path(__file__).resolve().parent
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
INITIAL_SHA='91d428f02d27cdc6c876e30f355e1dcab6c7398042c2f240a1f177e5b3a898f4'
PROFILE='left_crank_effective_exploration_recenter_v1'

def source_guard(source_proof,checkpoint,repair_mode):
 proof_path=Path(source_proof).resolve();assert proof_path.is_relative_to((D/'reports').resolve())
 proof=json.loads(proof_path.read_bytes());assert proof['passed'] is True and proof['finite_floating_tensors']==107 and proof['num_envs']==128
 path=Path(checkpoint).resolve();assert path==Path(proof['checkpoint']['path']).resolve() and H(path)==proof['checkpoint']['sha256']
 if repair_mode=='initial':assert H(path)==INITIAL_SHA
 else:assert repair_mode=='sameidentity' and proof['same_repair_identity'] is True and proof['repair_profile']==PROFILE
 operator=D/'immutable_repair_operator/left_head_exploration_migration_cpu_v1.py'
 cp=json.loads((D/'immutable_repair_operator/LEFT_HEAD_EFFECTIVE_EXPLORATION_CPU_ACTUAL_PROOF.json').read_bytes())
 assert cp['passed'] is True and cp['CPU_only_no_GPU_or_PPO'] is True and cp['prepared_floating_schema_exact107'] is True
 inputs=cp['inputs'];values=inputs.values() if isinstance(inputs,dict) else inputs
 assert any(isinstance(r,dict) and (r.get('sha256') or r.get('sha'))==H(operator) for r in values),'CPU operator sourceSHA not bound'
 return proof

def resources(target_seconds):
 assert target_seconds in (0,3600),'Only current prepared3600 learning window; no automatic extra duration'
 first=D.parent/'MOD4_LOCAL_WAVE50_TEMP_TRAIN_20261013/attempts/temporary_train128_v10_sameidentity_saved_source/output'
 whole=sum(p.stat().st_size for p in first.rglob('*') if p.is_file())
 scale=2 if target_seconds else 1
 # Exact previous local guard margins, plus independent action-request/guarded-targettrace reservation.
 action_trace_reserve=2*max(target_seconds,120)*128*20*4
 required=2*scale*whole+2*1024**3+action_trace_reserve
 available=shutil.disk_usage(D).free;ram=psutil.virtual_memory().available
 gpu=subprocess.run(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],check=True,capture_output=True,text=True)
 free=int(gpu.stdout.strip().splitlines()[0])
 passed=available>=required and ram>=8*1024**3 and free>=8500
 return dict(passed=passed,durable_free_bytes=available,required_durable_bytes=required,actual_completed1800_whole_output_bytes=whole,
  target_seconds=target_seconds,rule='2xscaledactualcompleted1800whole+2GiB+actiontrace reserve',RAM_available_bytes=ram,minimum_RAM_bytes=8*1024**3,
  GPU_free_MiB=free,minimum_GPU_free_MiB=8500,no_threshold_reduction_or_deletion=True)
