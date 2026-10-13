from pathlib import Path
import json
from remote_session import execute
from prepare_original_Linux_capacity_scope_v5_once import NEW as OLD
D=Path(__file__).resolve().parent
NEW=OLD.replace('fullscale20k_original_Linux_capacity_v5','fullscale20k_pureCPU_import_reviewed_v6')
def main():
    assert not (D/'reports/LINUX_EXPORT_INTERFACE_V6_DISPATCH_ACTUAL.json').exists()
    source=r'''
from pathlib import Path
import json,os,shutil,hashlib,fcntl,time,subprocess
P=Path;old=P(OLD);R=P(NEW);assert not R.exists()
err=json.loads((old/'attempts/native/output/ORIGINAL_ERROR.json').read_bytes());exit=json.loads((old/'attempts/native/EXIT_RECEIPT.json').read_bytes());assert err['prePPO'] and exit['no_PPO'] and exit['child_actually_absent'] and "cannot import name 'GEOMETRY_SHA'" in err['error']
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
f=R/'payload_v2/temporary_probe_contract_base.py';before=f.read_bytes();s=before.decode();needle='from temporary_state_binding import H, same, DONOR_SHA, GEOMETRY_SHA, PARTITION_SHA, ASSIGNMENT_SHA';assert needle in s;s=s.replace(needle,'from temporary_state_binding import H, same, DONOR_SHA\nfrom expanded_source_projection import GEOMETRY_SHA, PARTITION_SHA, ASSIGNMENT_SHA');compile(s,str(f),'exec');f.write_text(s)
python='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python';check="import sys,torch,json;sys.path.insert(0,"+repr(str(R/'payload_v2'))+");import temporary_state_binding,temporary_probe_contract_base,temporary_probe_contract,temporary_training_runtime;assert not torch.cuda.is_initialized();print(json.dumps({'pure_CPU_imports_passed':True,'GPU_not_initialized':True}))"
cp=subprocess.run([python,'-c',check],capture_output=True,text=True,timeout=45);(R/'PURE_CPU_IMPORT_ACTUAL.json').write_text(json.dumps(dict(code=cp.returncode,stdout=cp.stdout,stderr=cp.stderr),indent=2));assert cp.returncode==0,cp.stderr
m=json.loads((old/'LINUX_SCOPE_MANIFEST.json').read_bytes());m['source']['path']=m['source']['path'].replace(OLD,NEW);m['target_CPU_receipt']['path']=m['target_CPU_receipt']['path'].replace(OLD,NEW);m['pure_CPU_consumer_imports_actually_passed']=True
files=[]
for folder in (R/'runtime',R/'payload_v2'):
 for f in sorted(folder.rglob('*')):
  if f.is_file() and '__pycache__' not in str(f):files.append(dict(path=str(f),bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
m['sourcefreeze_files']=files;(R/'LINUX_SCOPE_MANIFEST.json').write_text(json.dumps(m,indent=2))
argv=[python,'-u',str(R/'payload_v2/linux_resume_parent_guard005_reviewed.py')];p=subprocess.Popen(argv,cwd=R,stdout=(R/'parent_stdout.log').open('xb'),stderr=subprocess.STDOUT,start_new_session=True)
tail=(P('/proc')/str(p.pid)/'stat').read_text().split(') ',1)[1].split();r=dict(epoch=time.time(),pid=p.pid,start_ticks=int(tail[19]),root=str(R),argv=argv,only_pure_CPU_constant_export_dependency_changed=True,old_SHA=hashlib.sha256(before).hexdigest(),new_SHA=hashlib.sha256((R/'payload_v2/temporary_probe_contract_base.py').read_bytes()).hexdigest(),actual_CPU_imports=json.loads(cp.stdout),all_original_Linux_parameters_and_defaults_unchanged=True,all_old_error_roots_preserved=True,new_native_fullrestore_PPO_pending=True,sourcefreeze=files)
(R/'DISPATCH_RECEIPT.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
'''
    r,p=execute('OLD='+repr(OLD)+'\nNEW='+repr(NEW)+'\n'+source,'LINUX_EXPORT_INTERFACE_V6_DISPATCH_ACTUAL',timeout=80)
    (D/'reports/LINUX_EXPORT_INTERFACE_V6_DISPATCH_ACTUAL.json').write_text(json.dumps(r,indent=2),encoding='utf8');print(json.dumps(dict(root=r['root'],pid=r['pid'],CPU_imports=r['actual_CPU_imports'])))
if __name__=='__main__':main()
