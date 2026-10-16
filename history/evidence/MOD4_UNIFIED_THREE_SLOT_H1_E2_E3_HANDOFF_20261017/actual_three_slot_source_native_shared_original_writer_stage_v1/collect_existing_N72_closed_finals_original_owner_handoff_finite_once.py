"""One finite same-connection collection of current owned finals, never a GPU replay."""
from pathlib import Path
import os,sys,time,json,getpass,traceback
U=Path(__file__).resolve().parent;R=U/'reports';P=U.parent/'MOD4_E1_CURB275_BRIDGE_FROM_CURB35_40_20261016';sys.path.insert(0,str(P))
from collect_hourly0044_existing_V9_FINAL_and_CURB275_production_readonly_once import SNAP,CANON,code,H,t,connect72,PY
ROOTS={k:'/home/lc01/Zonglin Li/zonglin2/tasks/N72_1710v2/'+k for k in ('e2','recovery')};S='/mnt/mod4_linux_durable_20261013/N72_1710v2';READ=SNAP.replace("'NODE_IDENTITY.json',","'NODE_TERMINAL_ACTUAL.json','NODE_IDENTITY.json',")
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 put('EXISTING_N72_FINAL_FINITE_COLLECTOR_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_transport=True,max_same_target_connection1800_seconds=True,no_GPU_runtime_or_budget_mutation=True));pw=getpass.getpass('Host72 existing two expert final artifacts only (hidden): ');c=None;v={};done={};begin=time.time()
 try:
  c=connect72(pw);pw=None;sf=c.open_sftp();sf.get_channel().settimeout(120)
  try:
   while True:
    for key,root in ROOTS.items():
     row=code(c,PY,READ,root,key);v[key]=row
     if key not in done and not row['actual_own_processes'] and any(x['path'].endswith('/NODE_EXIT_ACTUAL.json') for x in row['files']):
      model=next((m for m in row['models'] if m['kind']=='actual_final'),None)
      if model:
       folder=U/'actual_previous_N72_finals'/key;folder.mkdir(parents=True);p=folder/Path(model['path']).name;tmp=p.with_suffix('.pt.partial');assert not p.exists() and not tmp.exists();sf.get(model['path'],str(tmp));assert tmp.stat().st_size==model['bytes'] and H(tmp)==model['SHA'];tmp.replace(p);done[key]=dict(model,local_path=str(p),twohost_complete_SHA=True);put('EXISTING_'+key.upper()+'_ACTUAL_CLOSED_FULL_FINAL_COLLECTED.json',dict(epoch=time.time(),state=row,model=done[key]))
    if len(done)==2 or time.time()-begin>=1800:break
    put_current=dict(epoch=time.time(),observed_closed=list(done),source_keys={k:next((x['value'] for x in v[k]['files'] if x['path'].endswith('/NODE_CURRENT.json')),{}).get('row',{}).get('phase') for k in ROOTS});p=R/'EXISTING_N72_FINAL_FINITE_COLLECTION_CURRENT.json';tmp=p.with_suffix('.json.partial');tmp.write_text(json.dumps(put_current,indent=2));tmp.replace(p);time.sleep(15)
  finally:sf.close()
 finally:
  pw=None
  if c:c.close();c=None
 try:
  c=t.connect();started=time.time()
  while True:
   v['previous_owner']=code(c,t.PY,READ,S,'coordinator');v['canonical']=code(c,t.PY,CANON.replace('(576492,581261)','(576492,581261,594718)'))
   if not v['previous_owner']['actual_own_processes'] and v['canonical']['active'] is None and not any(x['actual_held'] for x in v['canonical']['actual_two_fcntl']):break
   if len(done)!=2 or time.time()-started>90:break
   time.sleep(5)
 finally:t.close(c)
 v['epoch']=time.time();v['downloaded_final_models']=done;v['both_current_N72_scopes_actual_closed_and_source_handoff']=len(done)==2 and not v['previous_owner']['actual_own_processes'] and v['canonical']['active'] is None and not any(x['actual_held'] for x in v['canonical']['actual_two_fcntl']);put('EXISTING_N72_TWO_FINALS_ORIGINAL_CANONICAL_ACTUAL_HANDOFF_COLLECTION.json',v);print(json.dumps(dict(epoch=v['epoch'],both_closed_actual_original_handoff=v['both_current_N72_scopes_actual_closed_and_source_handoff'],models=done)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put('EXISTING_N72_FINAL_COLLECTION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_runtime_or_once_replay=True));raise
