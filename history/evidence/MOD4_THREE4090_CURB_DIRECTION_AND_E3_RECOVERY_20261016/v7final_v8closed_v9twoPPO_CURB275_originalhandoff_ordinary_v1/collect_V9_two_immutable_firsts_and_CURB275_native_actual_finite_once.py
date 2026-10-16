from pathlib import Path
import sys,os,json,time,getpass,traceback
D=Path(__file__).resolve().parent;R=D/'reports';sys.path.insert(0,str(D))
from deploy_V9_actual_CPU_status_fix_E2_E3_CURB_deferred_once import ROOTS,code,H,connect72,t,PY
from collect_first_two_native_and_E2_handoff_actual_readonly_once import READ
from collect_hourly2223_V7_actual_finals_cost_exit_resources_readonly_once import CANON
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
FILES=r'''
from pathlib import Path
import sys,json,time,hashlib
B=Path(sys.argv[1]);key=sys.argv[2];names=['job0/production/model_update1.pt','job0/production/own_startup0.pt'] if key!='curb' else [];rows=[]
for rel in names:
 p=B/rel
 if p.is_file():rows.append(dict(relative=rel,path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest()))
print(json.dumps(dict(epoch=time.time(),files=rows,first_and_source0_complete=len(rows)==len(names))))
'''
def main():
 put('V9_TWO_IMMUTABLE_FIRSTS_FINITE_READER_STARTED.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_transport=True,max_same_target_connection_wait_seconds=240,readonly=True));pw=getpass.getpass('Host72 actual immutable first saved models (hidden): ');c=None;v={}
 try:
  c=t.connect();v['curb_owner']=code(c,t.PY,READ,ROOTS['curb'],'curb');v['curb275_case']=code(c,t.PY,READ,ROOTS['curb']+'/curb275_bridge_case_v1','curb');v['canonical']=code(c,t.PY,CANON)
 finally:t.close(c);c=None
 try:
  c=connect72(pw);pw=None;begin=time.time()
  while True:
   found={k:code(c,PY,FILES,ROOTS[k],k) for k in ('e2','recovery')}
   if all(row['first_and_source0_complete'] for row in found.values()) or time.time()-begin>=240:break
   time.sleep(15)
  for key in ('e2','recovery'):
   v[key]=code(c,PY,READ,ROOTS[key],key);v[key]['immutable_models']=[];folder=D/'actual_V9_first_models'/key;folder.mkdir(parents=True);sf=c.open_sftp();sf.get_channel().settimeout(120)
   try:
    for row in found[key]['files']:
     p=folder/Path(row['relative']).name;q=p.with_suffix('.pt.partial');assert not p.exists() and not q.exists();sf.get(row['path'],str(q));assert q.stat().st_size==row['bytes'] and H(q)==row['SHA'];q.replace(p);v[key]['immutable_models'].append(dict(**row,local_path=str(p),twohost_complete_SHA=True))
   finally:sf.close()
 finally:
  pw=None
  if c:c.close()
 v['epoch']=time.time();put('V9_TWO_AVAILABLE_IMMUTABLE_FIRST_MODELS_CURB275_NATIVE_BOUND_COLLECTION_ACTUAL.json',v)
 for k in ('e2','recovery'):
  fs=v[k]['files'];cur=next((r['value'] for r in fs if r['path'].endswith('/NODE_CURRENT.json')),{});row=cur.get('row',{});print(json.dumps(dict(key=k,epoch=v[k]['epoch'],phase=row.get('phase'),latest_save=row.get('latest_save'),models=v[k]['immutable_models'],original_errors=[r['path'] for r in fs if 'ORIGINAL_ERROR' in r['path']],actual_processes=v[k]['actual_own_processes'])),flush=True)
 print(json.dumps(dict(curb275_actual_processes=v['curb275_case']['actual_own_processes'],curb275_actual_files=[r['path'] for r in v['curb275_case']['files'] if 'COMPLETE' in r['path'] or 'ERROR' in r['path'] or 'STARTUP' in r['path'] or 'latest' in r['path']])),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put('V9_TWO_FIRST_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_runtime_mutation=True));raise
