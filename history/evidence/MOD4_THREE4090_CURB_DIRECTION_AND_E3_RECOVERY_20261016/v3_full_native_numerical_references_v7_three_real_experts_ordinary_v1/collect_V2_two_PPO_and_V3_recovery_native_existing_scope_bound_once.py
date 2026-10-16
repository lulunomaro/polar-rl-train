from pathlib import Path
import os,sys,json,time,getpass,traceback
D=Path(__file__).resolve().parent;R=D/'reports';sys.path.insert(0,str(D));from deploy_three_independent_V2_source_restore_then_new_axis_once import ROOTS,code,H,connect72,t,PY
from collect_first_two_native_and_E2_handoff_actual_readonly_once import READ
from collect_two_native_CPU_and_first_PPO_bound_same_connection_once import MODELS
T='/home/lc01/Zonglin Li/zonglin2/tasks/'+D.name+'/recovery_receipt_schema_v3'
def put(n,v,rolling=False):
 p=R/n
 if rolling:q=p.with_suffix('.json.partial');q.write_text(json.dumps(v,indent=2));q.replace(p)
 else:
  with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def models(c,py,root,key):
 v=code(c,py,MODELS,root,key);folder=D/'actual_V2_positive_and_V3_native_models'/key;folder.mkdir(parents=True);sf=c.open_sftp();sf.get_channel().settimeout(120);rows=[]
 try:
  for row in v['models']:
   p=folder/row['role'].replace('/','_');q=p.with_suffix('.pt.partial');assert not p.exists() and not q.exists();sf.get(row['path'],str(q));assert q.stat().st_size==row['bytes'] and H(q)==row['SHA'];q.replace(p);rows.append(dict(**row,local_path=str(p),twohost_complete_SHA_exact=True))
 finally:sf.close()
 return rows
def main():
 put('TWO_PPO_V3_NATIVE_COLLECTOR_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_transport=True,one_source_then_one_target_connection_bound900s=True,no_runtime_mutation=True));pw=getpass.getpass('Host72 actual PPO and new recovery native (hidden): ');c=None;v={}
 try:c=t.connect();v['curb']=code(c,t.PY,READ,ROOTS['curb'],'curb');v['curb']['local_models']=models(c,t.PY,ROOTS['curb'],'curb')
 finally:t.close(c);c=None
 try:
  c=connect72(pw);pw=None;v['e2']=code(c,PY,READ,ROOTS['e2'],'e2');v['e2']['local_models']=models(c,PY,ROOTS['e2'],'e2');begun=time.monotonic()
  while True:
   x=code(c,PY,READ,T,'recovery');put('RECOVERY_V3_EXISTING_NATIVE_CURRENT_FINITE_LOCAL_ACTUAL.json',x,True);terminal=any(r['path'].endswith('/PARENT_EXIT_ACTUAL.json') for r in x['files']);error=any('ORIGINAL_ERROR' in r['path'] for r in x['files'])
   if terminal or error or time.monotonic()-begun>=900:break
   time.sleep(20)
  v['recovery']=x;v['recovery']['local_models']=models(c,PY,T,'recovery')
 finally:
  pw=None
  if c:c.close()
 v['epoch']=time.time();put('V2_TWO_PPO_AND_V3_NATIVE_BOUND_COMPLETE_COLLECTION_ACTUAL.json',v);print(json.dumps(dict(epoch=v['epoch'],models={k:v[k]['local_models'] for k in ('curb','e2','recovery')},recovery_errors=[r for r in v['recovery']['files'] if 'ORIGINAL_ERROR' in r['path']])),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put('TWO_PPO_V3_COLLECTOR_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_replay=True));raise
