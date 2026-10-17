"""One bounded source210 metadata-only disk usage measurement; no training mutation."""
from pathlib import Path
import sys,os,json,time,traceback
J=Path(__file__).resolve().parent
N=J.parent/'MOD4_TWO72_E2_E3_HEALTHY_SAVED_CONTINUATIONS_20261017'
sys.path.insert(0,str(N))
import deploy_two72_new_native_after_actual_final_then_original_CURB_handoff_once as a
R=J/'reports'
CODE=r'''
from pathlib import Path
import os,sys,time,json,re,subprocess,shutil
begin=time.time();D=Path('/mnt/mod4_linux_durable_20261013');H=Path('/home/egde/rl_candidates')
assert D.is_dir() and H.is_dir()
def owned(p):
 return p.name.startswith('MOD4_') or bool(re.fullmatch(r'(?:C275_1610v\d+|H125_1710n\d+|N72_1710v\d+|T3_1710v\d+(?:r72)?)',p.name))
roots=sorted([p for p in D.iterdir() if owned(p) and not p.is_symlink()]+[p for p in H.iterdir() if p.name.startswith('MOD4_') and not p.is_symlink()],key=str)
assert roots
prefix=['ionice','-c','3'] if shutil.which('ionice') else []
def run(extra):
 r=subprocess.run(prefix+['du','-x','-B1']+extra+['--']+[str(p) for p in roots],capture_output=True,text=True,timeout=120)
 entries=[]
 for line in r.stdout.splitlines():
  n,p=line.split('\t',1);entries.append(dict(path=p,bytes=int(n)))
 return dict(returncode=r.returncode,stderr=r.stderr,rows=entries)
allocated=run(['--max-depth=2']);logical=run(['--summarize','--apparent-size'])
rootset={str(p) for p in roots};rootrows=[r for r in allocated['rows'] if r['path'] in rootset]
logicalrows=logical['rows'];sums={}
for key,base in [('Windows_D_owned_MOD4',D),('Linux_home_rl_candidates_MOD4',H)]:
 sums[key]=dict(allocated_bytes=sum(r['bytes'] for r in rootrows if Path(r['path']).is_relative_to(base)),apparent_bytes=sum(r['bytes'] for r in logicalrows if Path(r['path']).is_relative_to(base)),root_count=sum(Path(r['path']).is_relative_to(base) for r in rootrows))
disks={str(p):dict(zip(('total','used','free'),shutil.disk_usage(p))) for p in (D,Path('/'),Path('/mnt/mod4_windows_readonly_20261013/system'))}
mounts=subprocess.run(['findmnt','-J','-o','SOURCE,TARGET,FSTYPE,OPTIONS','--target',str(D)],capture_output=True,text=True,timeout=10)
value=dict(epoch_begin=begin,epoch_end=time.time(),actual_host='10.24.4.210 original single RTX4090',read_only_metadata_no_weight_hash_no_GPU_or_ledger_or_mount_changes=True,scope='Owned top-level MOD4_* plus exact known C275/H125/N72/T3 run namespace roots on Windows D; original MOD4_* under /home/egde/rl_candidates. No symlink following or other users data scan.',not_system_or_shared_SDK_installation_size=True,root_inventory=[str(p) for p in roots],excluded_non_MOD4_D_top_level_count=sum(not owned(p) for p in D.iterdir()),allocated=allocated,apparent=logical,scope_sums=sums,total_owned_allocated_bytes=sum(v['allocated_bytes'] for v in sums.values()),total_owned_apparent_bytes=sum(v['apparent_bytes'] for v in sums.values()),filesystem_usage=disks,D_findmnt=mounts.stdout,D_findmnt_rc=mounts.returncode,measurement_complete=allocated['returncode']==0 and logical['returncode']==0,largest_owned_roots=sorted(rootrows,key=lambda r:r['bytes'],reverse=True)[:20],largest_depth2_paths=sorted([r for r in allocated['rows'] if r['path'] not in rootset],key=lambda r:r['bytes'],reverse=True)[:25],live_finite_outputs_may_change_after_measurement=True)
print(json.dumps(value))
'''
def put(name,value):
 with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
def main():
 put('SOURCE210_OWN_DISK_METADATA_FINITE_READER_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_transport=True,source_only_one_connection=True,max_remote_seconds=270,no_GPU_or_old_once_or_budget_action=True))
 c=None
 try:c=a.t.connect();v=a.code(c,a.t.PY,CODE,timeout=270)
 finally:a.t.close(c)
 put('SOURCE210_OWN_MOD4_TRAINING_DISK_USAGE_READONLY_ACTUAL.json',v)
 print(json.dumps({k:v[k] for k in ('epoch_begin','epoch_end','measurement_complete','scope_sums','total_owned_allocated_bytes','total_owned_apparent_bytes','filesystem_usage','largest_owned_roots','largest_depth2_paths')}),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  put('SOURCE210_DISK_METADATA_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_remote_runtime_or_file_mutation=True));raise
