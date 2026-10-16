"""Only if the first finite collection expires before E3's immutable first save."""
from pathlib import Path
import os,sys,time,json,getpass,traceback,subprocess
U=Path(__file__).resolve().parent;R=U/'reports'
import collect_new_three_slot_actual_native_and_first_models_finite_once as c
CHECK=r'''
from pathlib import Path
import sys,json,time
B=Path(sys.argv[1]);p=B/'job0/production/model_update1.pt'
print(json.dumps(dict(epoch=time.time(),first_exists=p.is_file(),node_terminal=(B/'NODE_TERMINAL_ACTUAL.json').is_file(),node_error=(B/'NODE_ORIGINAL_ERROR.json').is_file())))
'''
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def get_only_missing(conn,rows):
 folder=U/'actual_three_slot_first_models/recovery';folder.mkdir(parents=True,exist_ok=True);sf=conn.open_sftp();sf.get_channel().settimeout(120);out=[]
 try:
  for row in rows:
   p=folder/Path(row['path']).name;tmp=p.with_suffix('.pt.partial');assert not p.exists() and not tmp.exists();sf.get(row['path'],str(tmp));assert tmp.stat().st_size==row['bytes'] and c.a.H(tmp)==row['SHA'];tmp.replace(p);out.append(dict(row,local_path=str(p),twohost_complete_SHA=True))
 finally:sf.close()
 return out
def main():
 old=json.loads((R/'THREE_SLOT_ACTUAL_NATIVE_FIRST_IMMUTABLE_MODELS_COMPLETE_BOUND_COLLECTION.json').read_bytes());assert not any(x['kind']=='immutable_first' for x in old['downloaded_models']['recovery'])
 # No parallel host access with the original finite collector. CIM includes creation time.
 q=subprocess.run(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object {$_.Name -like 'python*' -and $_.CommandLine -like '*collect_new_three_slot_actual_native_and_first_models_finite_once.py*'} | Select-Object ProcessId,CreationDate | ConvertTo-Json -Compress"],text=True,capture_output=True,check=True);assert not q.stdout.strip(),q.stdout
 put('E3_MISSING_FIRST_ONLY_FINITE_COLLECTOR_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),prior_collector_actual_CIM_absent=True,only_missing_first_read_no_runtime_mutation=True,one_target72_connection_max600seconds=True))
 pw=getpass.getpass('Host72 missing immutable E3 first only (hidden): ');conn=None
 try:
  conn=c.a.connect72(pw);pw=None;begin=time.time();root=c.ROOTS['recovery'];checks=[]
  while True:
   v=c.a.code(conn,c.a.PY,CHECK,root);checks.append(v)
   if v['first_exists'] or v['node_terminal'] or v['node_error'] or time.time()-begin>=600:break
   time.sleep(15)
  latest=c.a.code(conn,c.a.PY,c.READ,root,'recovery');have={x['kind']:x for x in old['downloaded_models']['recovery']};missing=[x for x in latest['models'] if x['kind'] not in have];downloads=get_only_missing(conn,missing);merged=dict(old);merged['recovery']=latest;merged['downloaded_models']={**old['downloaded_models'],'recovery':list(have.values())+downloads};merged['epoch']=time.time();merged['existing_h1_e2_and_E3_completed_zero_native_not_redownloaded']=True;merged['original_collection_path']=str(R/'THREE_SLOT_ACTUAL_NATIVE_FIRST_IMMUTABLE_MODELS_COMPLETE_BOUND_COLLECTION.json');merged['missing_E3_first_only_bounded_checks']=checks;put('THREE_SLOT_EXISTING_COMPLETE_MODELS_PLUS_MISSING_E3_FIRST_ONLY_BOUND_COLLECTION_V2.json',merged);print(json.dumps(dict(new_downloads=downloads,first_seen=v['first_exists'],only_missing_first_collected=True)),flush=True)
 finally:
  pw=None
  if conn:conn.close()
if __name__=='__main__':
 try:main()
 except BaseException:
  put('E3_MISSING_FIRST_ONLY_COLLECTION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_native_or_once_replay=True));raise
