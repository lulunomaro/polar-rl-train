from pathlib import Path
import json
from remote_session import execute
from prepare_PhysicsCfg_API_reviewed_scope_v3_once import NEW as OLD
D=Path(__file__).resolve().parent
NEW=OLD.replace('fullscale20k_PhysicsCfg_API_reviewed_v3','fullscale20k_u32_capacity_reviewed_v4')
def main():
    assert not (D/'reports/LINUX_U32_CAPACITY_V4_DISPATCH_ACTUAL.json').exists()
    source=r'''
from pathlib import Path
import json,os,shutil,hashlib,fcntl,time,subprocess
P=Path;old=P(OLD);R=P(NEW);assert not R.exists()
err=json.loads((old/'attempts/native/output/ORIGINAL_ERROR.json').read_bytes());assert err['prePPO'] and 'gpuCollisionStackSize' in err['error'] and 'unsigned int' in err['error']
assert not (old/'attempts/native/output/PROBE_PROGRESS.json').exists()
for p in P('/proc').iterdir():
 if p.name.isdigit():
  try:assert OLD.encode() not in (p/'cmdline').read_bytes()
  except OSError:pass
for p in ('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/native_floor_supervisor.lock','/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock'):
 with open(p,'r+b') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
B=P('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');assert json.loads(B.read_bytes())['active_segment'] is None
R.mkdir()
for name in ('runtime','source','payload_v2'):shutil.copytree(old/name,R/name,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
for name in ('TARGET_FULLSTATE_CPU_PASSED.json','LOCAL_PARENT_SOURCE_AND_EXPANSION_CPU_PROOF.json'):shutil.copyfile(old/name,R/name)
m=json.loads((old/'LINUX_SCOPE_MANIFEST.json').read_bytes());m['source']['path']=m['source']['path'].replace(OLD,NEW);m['target_CPU_receipt']['path']=m['target_CPU_receipt']['path'].replace(OLD,NEW)
capacity=4026531840;assert 0<capacity<2**32 and capacity/20000>162398352/1024
for key in ('temporary_small_batch_capacities','admitted_Windows20k_GPU_buffer_capacities'):m[key]['gpu_collision_stack_size']=capacity
m['resource_capacity_disclosure']['collision_stack_bytes']=capacity;m['uint32_schema_limit_explicit_CPU_checked']=True
files=[]
for folder in (R/'runtime',R/'payload_v2'):
 for f in sorted(folder.rglob('*')):
  if f.is_file() and '__pycache__' not in str(f):files.append(dict(path=str(f),bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
m['sourcefreeze_files']=files;(R/'LINUX_SCOPE_MANIFEST.json').write_text(json.dumps(m,indent=2))
argv=['/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python','-u',str(R/'payload_v2/linux_resume_parent_guard005_reviewed.py')]
p=subprocess.Popen(argv,cwd=R,stdout=(R/'parent_stdout.log').open('xb'),stderr=subprocess.STDOUT,start_new_session=True)
tail=(P('/proc')/str(p.pid)/'stat').read_text().split(') ',1)[1].split();r=dict(epoch=time.time(),pid=p.pid,start_ticks=int(tail[19]),root=str(R),argv=argv,capacity_old_bytes=4294967296,capacity_new_bytes=capacity,allocation_fits_native_USD_uint32=True,no_physics_solver_reward_DR_or_tolerance_change=True,all_other_source_bytes_exact=True,old_parent_child_exit_locksfree_noactive=True,old_precontrol_error_root_preserved=True,new_native_fullrestore_PPO_pending=True,sourcefreeze=files)
(R/'DISPATCH_RECEIPT.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
'''
    r,p=execute('OLD='+repr(OLD)+'\nNEW='+repr(NEW)+'\n'+source,'LINUX_U32_CAPACITY_V4_DISPATCH_ACTUAL',timeout=75)
    (D/'reports/LINUX_U32_CAPACITY_V4_DISPATCH_ACTUAL.json').write_text(json.dumps(r,indent=2),encoding='utf8');print(json.dumps(dict(root=r['root'],pid=r['pid'],collision_stack_bytes=r['capacity_new_bytes'])))
if __name__=='__main__':main()
