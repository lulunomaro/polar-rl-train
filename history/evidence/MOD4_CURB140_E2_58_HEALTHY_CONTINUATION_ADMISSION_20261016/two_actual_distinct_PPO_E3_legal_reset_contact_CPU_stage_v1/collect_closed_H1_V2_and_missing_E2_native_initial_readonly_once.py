"""Complete old H1 handoff while new CURB/E2 continue; no GPU or budget writes."""
from pathlib import Path
import sys,json,time,getpass,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';N=W/'MOD4_H1_GROUNDED_PRELAUNCH_PROGRESS_V2_20261016';sys.path.insert(0,str(N));from collect_V2_actual_native_CPU_and_first_immutable_production_finite_once import SOURCE,TARGET,code,H,t,S,T,PY,connect72
def main():
 p=R/'OLD_H1_V2_FINAL_AND_E2_MISSING_NATIVE0_READONLY_ACTUAL.json';assert not p.exists();pw=getpass.getpass('Host72 closed H1 and missing native0 read-only password (hidden): ');v={};c=sf=None
 try:c=t.connect();v['H1_source']=code(c,t.PY,SOURCE,S)
 finally:t.close(c);c=None
 try:
  c=connect72(pw);pw=None;v['H1_target']=code(c,PY,TARGET,T);final=next((x['value'] for x in v['H1_target']['files'] if x['path'].endswith('/production/FINAL.json')),None);sources=[]
  if final:
   row=final['final'];sources.append(dict(**row,local_name='H1_V2_final_model.pt'))
  e2root='/home/lc01/Zonglin Li/zonglin2/tasks/'+D.name+'/e2';missing=code(c,PY,"from pathlib import Path;import json,sys,hashlib;B=Path(sys.argv[1]);v=json.loads((B/'job0/native/STARTUP_SOURCE_ACTUAL.json').read_bytes())['zero'];p=Path(v['path']);assert p.stat().st_size==v['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==v['SHA'];print(json.dumps(v))",e2root);sources.append(dict(**missing,local_name='E2_native_own_startup0.pt'));folder=D/'actual_closed_H1_and_missing_native0';folder.mkdir();sf=c.open_sftp();sf.get_channel().settimeout(120);local=[]
  for row in sources:
   out=folder/row['local_name'];tmp=out.with_suffix('.pt.partial');assert not out.exists() and not tmp.exists();sf.get(row['path'],str(tmp));assert tmp.stat().st_size==row['bytes'] and H(tmp)==row['SHA'];tmp.replace(out);local.append(dict(path=str(out),remote=row['path'],bytes=row['bytes'],SHA=row['SHA'],role=row['local_name'],twohost_bytes_SHA_exact=True))
  sf.close();sf=None;v['local_models']=local;v['GPU_snapshot']=code(c,PY,"import subprocess,json,time;print(json.dumps(dict(epoch=time.time(),gpus=subprocess.check_output(['nvidia-smi','--query-gpu=index,uuid,memory.used,memory.free','--format=csv,noheader,nounits']).decode(),compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode())))");v.update(epoch=time.time(),old_H1_not_restarted_or_budget_changed=True);p.write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(dict(H1_actual_final=final,H1_target_actual_processes=v['H1_target']['actual_own_processes'],H1_source_matching_segments=v['H1_source']['own_matching_completed_segments'],GPU=v['GPU_snapshot'],local_models=local)),flush=True)
 finally:
  pw=None
  if sf:sf.close()
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:(R/('H1_CLOSED_RECEIPT_OR_MISSING_NATIVE0_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_replay_or_budget_write=True),indent=2),encoding='utf8');raise
