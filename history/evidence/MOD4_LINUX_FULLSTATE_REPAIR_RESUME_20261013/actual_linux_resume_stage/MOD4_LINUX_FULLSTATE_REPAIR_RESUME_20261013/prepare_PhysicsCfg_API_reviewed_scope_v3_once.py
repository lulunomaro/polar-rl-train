"""New scope after own pre-control native6 config API refusal; no old replay."""
from pathlib import Path
import sys,os,json,time,hashlib
from remote_session import execute
from read_linux_resume_boundary_actual import connect_linux_only
from deploy_linux_runtime_cpu_once import S as OLD
D=Path(__file__).resolve().parent
NEW=OLD.replace('fullscale20k_latest512_state_v1','fullscale20k_PhysicsCfg_API_reviewed_v3')
def main():
    assert not (D/'reports/LINUX_PHYSICSCFG_V3_DISPATCH_ACTUAL.json').exists()
    text=r'''
from pathlib import Path
import json,os,shutil,hashlib,fcntl,time,subprocess
P=Path;old=P(OLD);R=P(NEW)
assert not R.exists()
err=json.loads((old/'attempts/native/output/ORIGINAL_ERROR.json').read_bytes());assert err['prePPO'] and "has no attribute 'physx'" in err['error']
assert not (old/'attempts/native/output/PROBE_PROGRESS.json').exists()
for p in P('/proc').iterdir():
 if p.name.isdigit():
  try:assert OLD.encode() not in (p/'cmdline').read_bytes()
  except OSError:pass
for p in ('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/native_floor_supervisor.lock','/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock'):
 with open(p,'r+b') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
B=P('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');assert json.loads(B.read_bytes())['active_segment'] is None
R.mkdir();shutil.copytree(old/'runtime',R/'runtime',ignore=shutil.ignore_patterns('__pycache__','*.pyc'));shutil.copytree(old/'source',R/'source');shutil.copytree(old/'payload_v2',R/'payload_v2',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
changed=[]
for name in ('temporary_worker.py','temporary_probe_contract_base.py'):
 f=R/'payload_v2'/name;before=f.read_bytes();s=before.decode();assert 'cfg.sim.physx' in s
 s=s.replace('cfg.sim.physx','cfg.sim.physics');compile(s,str(f),'exec');f.write_text(s)
 changed.append(dict(file=name,old_SHA=hashlib.sha256(before).hexdigest(),new_SHA=hashlib.sha256(f.read_bytes()).hexdigest(),only_PhysxCfg_member_API_name_changed=True))
plan=R/'payload_v2/LINUX_CODE_BINDING_PLAN.json';j=json.loads(plan.read_bytes());j['timeout_source_CPU_equivalence']['path']=j['timeout_source_CPU_equivalence']['path'];plan.write_text(json.dumps(j,indent=2))
shutil.copyfile(old/'TARGET_FULLSTATE_CPU_PASSED.json',R/'TARGET_FULLSTATE_CPU_PASSED.json');shutil.copyfile(old/'LOCAL_PARENT_SOURCE_AND_EXPANSION_CPU_PROOF.json',R/'LOCAL_PARENT_SOURCE_AND_EXPANSION_CPU_PROOF.json')
m=json.loads((old/'LINUX_SCOPE_MANIFEST.json').read_bytes());m['source']['path']=m['source']['path'].replace(OLD,NEW);m['target_CPU_receipt']['path']=m['target_CPU_receipt']['path'].replace(OLD,NEW);m['only_new_native6_PhysicsCfg_API_fix_after_precontrol_failure']=True
files=[]
for folder in (R/'runtime',R/'payload_v2'):
 for f in sorted(folder.rglob('*')):
  if f.is_file() and '__pycache__' not in str(f):files.append(dict(path=str(f),bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
m['sourcefreeze_files']=files;(R/'LINUX_SCOPE_MANIFEST.json').write_text(json.dumps(m,indent=2))
argv=['/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python','-u',str(R/'payload_v2/linux_resume_parent_guard005_reviewed.py')]
p=subprocess.Popen(argv,cwd=R,stdout=(R/'parent_stdout.log').open('xb'),stderr=subprocess.STDOUT,start_new_session=True)
tail=(P('/proc')/str(p.pid)/'stat').read_text().split(') ',1)[1].split();receipt=dict(epoch=time.time(),pid=p.pid,start_ticks=int(tail[19]),root=str(R),argv=argv,changes=changed,all_other_runtime_source_bytes_retained=True,old_precontrol_error_root_preserved=True,old_parent_child_gone_locksfree_budgetunchanged_verified=True,no_old_main_once_resume_replayed=True,new_GPU_result_and_PPO_pending=True,sourcefreeze=files)
(R/'DISPATCH_RECEIPT.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt))
'''
    r,p=execute('OLD='+repr(OLD)+'\nNEW='+repr(NEW)+'\n'+text,'LINUX_PHYSICSCFG_V3_DISPATCH_ACTUAL',timeout=75)
    (D/'reports/LINUX_PHYSICSCFG_V3_DISPATCH_ACTUAL.json').write_text(json.dumps(r,indent=2),encoding='utf8')
    print(json.dumps(dict(root=r['root'],pid=r['pid'],changes=r['changes'],report=str(p))))
if __name__=='__main__':main()
