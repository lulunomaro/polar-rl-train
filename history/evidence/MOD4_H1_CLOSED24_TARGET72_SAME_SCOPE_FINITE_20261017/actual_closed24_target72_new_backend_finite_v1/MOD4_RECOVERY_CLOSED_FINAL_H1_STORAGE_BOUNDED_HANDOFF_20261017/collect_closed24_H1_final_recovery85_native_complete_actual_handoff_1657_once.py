"""One sequential metadata read and only two missing complete PTs; no launch or replay."""
from pathlib import Path
import sys,os,json,time,getpass,traceback,importlib.util
B=Path(__file__).resolve().parent;R=B/'reports';sys.path.insert(0,str(B))
from collect_new_H1_bounded_native_first_and_recovery85_native_only_finite_once import a,SOURCE,ROOTS,SNAP
G=B.parent/'MOD4_TWO72_CLOSED_SOURCES_HEALTHY_NEXT_BLOCK_20261017';sys.path.insert(0,str(G))
sp=importlib.util.spec_from_file_location('read_original_account_only_1657',G/'collect_existing_v5_actual_terminal_original_handoff_bounded_missing_final_only_once.py');f=importlib.util.module_from_spec(sp);sp.loader.exec_module(f)
def save(n,v):
 with (R/n).open('x',encoding='utf8') as h:json.dump(v,h,indent=2)
HASH=r'''
from pathlib import Path
import sys,os,json,hashlib
p=Path(sys.argv[1]);h=hashlib.sha256()
with p.open('rb') as f:
 s=os.fstat(f.fileno())
 for b in iter(lambda:f.read(4194304),b''):h.update(b)
 e=os.fstat(f.fileno());assert (s.st_ino,s.st_size,s.st_mtime_ns)==(e.st_ino,e.st_size,e.st_mtime_ns)
print(json.dumps(dict(path=str(p),bytes=s.st_size,SHA=h.hexdigest())))
'''
GPU=r'''
import json,subprocess,time,shutil
print(json.dumps(dict(epoch=time.time(),gpu=subprocess.check_output(['nvidia-smi','--query-gpu=index,uuid,utilization.gpu,memory.used,memory.total','--format=csv,noheader,nounits']).decode(),compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,process_name,used_gpu_memory','--format=csv,noheader,nounits']).decode(),durable_free=shutil.disk_usage('/mnt/mod4_linux_durable_20261013' if __import__('pathlib').Path('/mnt/mod4_linux_durable_20261013').is_dir() else '/home/lc01/Zonglin Li/zonglin2').free)))
'''
def model(c,py,path,key):
 row=a.code(c,py,HASH,path,timeout=90);p=B/'actual_closed24_and_native_models'/key/Path(path).name;p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists();part=p.with_suffix('.pt.partial');assert not part.exists()
 sf=c.open_sftp();sf.get_channel().settimeout(120)
 try:sf.get(path,str(part))
 finally:sf.close()
 assert part.stat().st_size==row['bytes'] and a.H(part)==row['SHA'];part.replace(p);return dict(row,local_path=str(p),twohost_complete_SHA=True)
def main():
 save('M_CLOSED24_NATIVE_COMPLETE_1657_READER_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_all_transport=True,one_source_then_one72_bounded_read_no_poll=True,no_launch_GPU_task_native_or_account_mutation=True))
 pw=getpass.getpass('Host72 missing native complete and own final handoff (hidden): ');c=None;v={};models={}
 try:
  c=a.t.connect();v['owner']=a.code(c,a.t.PY,SNAP,SOURCE,'metadata',timeout=90);v['h1']=a.code(c,a.t.PY,SNAP,ROOTS['h1'],'metadata',timeout=90);v['account']=a.code(c,a.t.PY,f.ACCOUNT,timeout=90);v['source_resources']=a.code(c,a.t.PY,GPU,timeout=40)
  final=next(x['value'] for x in v['h1']['files'] if x['path'].endswith('/job0/production/FINAL.json'));assert final['passed'];models['h1_final']=model(c,a.t.PY,final['final']['path'],'h1')
 finally:a.t.close(c);c=None
 try:
  c=a.connect72(pw);pw=None;v['recovery']=a.code(c,a.PY,SNAP,ROOTS['recovery'],'metadata',timeout=90);v['target_resources']=a.code(c,a.PY,GPU,timeout=40)
  final=next(x['value'] for x in v['recovery']['files'] if x['path'].endswith('/NATIVE_ONLY_FINAL_ACTUAL.json'));assert final['passed_native_GPU_and_full_CPU'];models['recovery_native']=model(c,a.PY,ROOTS['recovery']+'/job0/native/own_native336.pt','recovery')
 finally:
  pw=None
  if c:c.close()
 v.update(epoch=time.time(),downloaded_models=models,only_missing_final_and_native_complete_no_old_PT_or_raw_hash=True,actual_return_hands_all_transport_back=True)
 save('M_CLOSED24_H1_FINAL_RECOVERY85_NATIVE_COMPLETE_ORIGINAL_HANDOFF_1657_BOUND_ACTUAL.json',v)
 print(json.dumps(dict(epoch=v['epoch'],models=models,D_free=v['source_resources']['durable_free'],source_compute=v['source_resources']['compute'],target_compute=v['target_resources']['compute'],original_active=v['account']['original_canonical']['active_segment'],locks=v['account']['actual_locks'],own_processes={k:v[k]['actual_own_processes'] for k in ('owner','h1','recovery')})),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:save('M_CLOSED24_NATIVE_1657_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),unknown_outcome_no_blind_relaunch=True));raise
