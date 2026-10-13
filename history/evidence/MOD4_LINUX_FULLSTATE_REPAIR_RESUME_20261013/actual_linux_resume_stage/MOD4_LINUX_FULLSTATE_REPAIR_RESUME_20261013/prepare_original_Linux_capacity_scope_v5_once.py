"""Use unchanged original Linux PhysxCfg defaults, no Windows buffer scaling."""
from pathlib import Path
import json
from remote_session import execute
from prepare_u32_capacity_reviewed_scope_v4_once import NEW as OLD
D=Path(__file__).resolve().parent
NEW=OLD.replace('fullscale20k_u32_capacity_reviewed_v4','fullscale20k_original_Linux_capacity_v5')
def main():
    assert not (D/'reports/LINUX_ORIGINAL_CAPACITY_V5_DISPATCH_ACTUAL.json').exists()
    source=r'''
from pathlib import Path
import json,os,shutil,hashlib,fcntl,time,subprocess
P=Path;old=P(OLD);R=P(NEW);assert not R.exists()
err=json.loads((old/'attempts/native/output/ORIGINAL_ERROR.json').read_bytes());exit=json.loads((old/'attempts/native/EXIT_RECEIPT.json').read_bytes());assert err['prePPO'] and exit['no_PPO'] and exit['child_actually_absent'] and 'Failed to allocate' in err['error']
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
f=R/'payload_v2/temporary_worker.py';before=f.read_bytes();s=before.decode()
needle="    assert capacities == manifest['admitted_Windows20k_GPU_buffer_capacities'], 'reviewed Linux resource buffer identity'"
assert needle in s
s=s.replace(needle,"    assert not manifest['temporary_small_batch_capacities'] and manifest['reuse_original_Linux_PhysxCfg_defaults']\n    assert capacities == original_capacities, 'Original Linux default resource capacities unchanged'")
s=s.replace("actual_new_Windows20k_cfg=capacities", "actual_Linux20k_cfg=capacities, actual_original_Linux_defaults=original_capacities")
s=s.replace('capacity_overrides_applied=True','capacity_overrides_applied=False')
compile(s,str(f),'exec');f.write_text(s)
m=json.loads((old/'LINUX_SCOPE_MANIFEST.json').read_bytes());m['source']['path']=m['source']['path'].replace(OLD,NEW);m['target_CPU_receipt']['path']=m['target_CPU_receipt']['path'].replace(OLD,NEW)
m['temporary_small_batch_capacities']={};m['reuse_original_Linux_PhysxCfg_defaults']=True;m['resource_capacity_disclosure']=dict(original_Linux_cfg_unchanged=True,no_Windows_capacity_projection=True,all_actual_values_read_before_env_initialization=True,old_precontrol_OOM_preserved=True)
files=[]
for folder in (R/'runtime',R/'payload_v2'):
 for f in sorted(folder.rglob('*')):
  if f.is_file() and '__pycache__' not in str(f):files.append(dict(path=str(f),bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
m['sourcefreeze_files']=files;(R/'LINUX_SCOPE_MANIFEST.json').write_text(json.dumps(m,indent=2))
argv=['/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python','-u',str(R/'payload_v2/linux_resume_parent_guard005_reviewed.py')]
p=subprocess.Popen(argv,cwd=R,stdout=(R/'parent_stdout.log').open('xb'),stderr=subprocess.STDOUT,start_new_session=True)
tail=(P('/proc')/str(p.pid)/'stat').read_text().split(') ',1)[1].split();r=dict(epoch=time.time(),pid=p.pid,start_ticks=int(tail[19]),root=str(R),argv=argv,only_removed_Windows_buffer_overrides=True,worker_old_SHA=hashlib.sha256(before).hexdigest(),worker_new_SHA=hashlib.sha256((R/'payload_v2/temporary_worker.py').read_bytes()).hexdigest(),old_Linux_runtime_all_bytes_except_selected_hook_unchanged=True,old_original_Linux_parameters_unchanged=True,all_old_error_roots_preserved=True,new_native_fullrestore_PPO_pending=True,sourcefreeze=files)
(R/'DISPATCH_RECEIPT.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
'''
    r,p=execute('OLD='+repr(OLD)+'\nNEW='+repr(NEW)+'\n'+source,'LINUX_ORIGINAL_CAPACITY_V5_DISPATCH_ACTUAL',timeout=75)
    (D/'reports/LINUX_ORIGINAL_CAPACITY_V5_DISPATCH_ACTUAL.json').write_text(json.dumps(r,indent=2),encoding='utf8');print(json.dumps(dict(root=r['root'],pid=r['pid'],original_Linux_capacities=True)))
if __name__=='__main__':main()
