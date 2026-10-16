from pathlib import Path
import os,sys,time,json,getpass,traceback
D=Path(__file__).resolve().parent;R=D/'reports';sys.path.insert(0,str(D));from deploy_V7_three_experts_corrected_E3_admission_finite_once import ROOTS,code,H,connect72,t,PY
from collect_first_two_native_and_E2_handoff_actual_readonly_once import READ
from collect_two_native_CPU_and_first_PPO_bound_same_connection_once import MODELS
def put(n,v,rolling=False):
 p=R/n
 if rolling:q=p.with_suffix('.json.partial');q.write_text(json.dumps(v,indent=2),encoding='utf8');q.replace(p)
 else:
  with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def models(c,py,key,prior):
 folder=D/'actual_V7_three_expert_native_first_models'/key;folder.mkdir(parents=True,exist_ok=True);skip=[p.name for p in folder.glob('*.pt')];script=MODELS.replace("if p.is_file():rows.append", "if p.is_file() and (phase+'/'+name).replace('/','_') not in json.loads(sys.argv[3]):rows.append");v=code(c,py,script,ROOTS[key],key,json.dumps(skip));out=list(prior);sf=c.open_sftp();sf.get_channel().settimeout(120)
 try:
  for row in v['models']:
   p=folder/row['role'].replace('/','_');q=p.with_suffix('.pt.partial');assert not p.exists() and not q.exists();sf.get(row['path'],str(q));assert q.stat().st_size==row['bytes'] and H(q)==row['SHA'];q.replace(p);out.append(dict(**row,local_path=str(p),twohost_bytes_SHA_exact=True))
 finally:sf.close()
 return out
def main():
 prior=json.loads((R/'THREE_V7_ALL_NATIVE_CPU_AND_AVAILABLE_FIRST_MODELS_BOUND_COLLECTION_ACTUAL.json').read_bytes());put('V7_MISSING_FIRST_MODELS_FINITE_COLLECTOR_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_transport_owner=True,max_one_source_connection900seconds=True,no_runtime_mutation=True,only_new_model_artifacts_not_old_complete_downloads=True));pw=getpass.getpass('Host72 only new immutable first saves (hidden): ');c=None;v={}
 try:
  c=t.connect();begun=time.monotonic()
  while True:
   x=code(c,t.PY,READ,ROOTS['curb'],'curb');put('V7_REMAINING_FIRST_SOURCE_CURRENT_FINITE_LOCAL_ACTUAL.json',x,True);current=next((r['value'] for r in x['files'] if r['path'].endswith('/OWNER_CURRENT.json')),{});rows=current.get('rows') or {};positive=all((rows.get(k,{}).get('latest_save') or {}).get('updates',0)>=1 and rows.get(k,{}).get('phase')=='production' for k in ROOTS);error=any(r.get('original_error') for r in rows.values())
   if positive or error or any(r['path'].endswith('/OWNER_EXIT_ACTUAL.json') for r in x['files']) or time.monotonic()-begun>=900:break
   time.sleep(20)
  v['curb']=x;v['curb']['local_models']=models(c,t.PY,'curb',prior['curb']['local_models'])
 finally:t.close(c);c=None
 try:
  c=connect72(pw);pw=None
  for key in ('e2','recovery'):v[key]=code(c,PY,READ,ROOTS[key],key);v[key]['local_models']=models(c,PY,key,prior[key]['local_models'])
 finally:
  pw=None
  if c:c.close()
 v['epoch']=time.time();put('V7_COMPLETED_IMMUTABLE_FIRST_MODELS_BOUND_COLLECTION_ACTUAL.json',v);print(json.dumps(dict(epoch=v['epoch'],models={k:v[k]['local_models'] for k in ROOTS},errors={k:[r for r in v[k]['files'] if 'ORIGINAL_ERROR' in r['path']] for k in ROOTS})),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put('V7_MISSING_FIRST_FINITE_COLLECT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_replay=True));raise
