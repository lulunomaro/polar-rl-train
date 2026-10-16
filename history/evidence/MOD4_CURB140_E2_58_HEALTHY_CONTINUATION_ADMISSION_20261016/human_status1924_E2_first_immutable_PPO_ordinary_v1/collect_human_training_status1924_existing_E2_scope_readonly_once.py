from pathlib import Path
import sys,os,json,time,getpass,traceback
D=Path(__file__).resolve().parent;R=D/'reports';sys.path.insert(0,str(D))
from collect_new_E2_closed75_native_CPU_and_first_model_finite_once import SOURCE,READ
from deploy_new_E2_closed75_same4_native_then_single_bounded_learning_once import S,T,PY,t,code,H,connect72
def put(name,value):
 with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
def main():
 put('HUMAN_TRAINING_STATUS1924_READONLY_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),one_connection_per_host_sequential=True,actual_alive_only_transport_owner=True,no_runtime_launch_signal_or_budget_write=True))
 pw=getpass.getpass('Host72 existing E2 status read only (hidden): ');c=None;v={}
 try:
  c=t.connect();v['source']=code(c,t.PY,SOURCE,S,timeout=60)
 finally:t.close(c);c=None
 try:
  c=connect72(pw);pw=None;target=code(c,PY,READ.replace("'own_restored0.pt'","'own_startup0.pt'"),T,'e2',timeout=90)
  sf=c.open_sftp();sf.get_channel().settimeout(90);folder=D/'actual_E2_human_status1924_models';local=[]
  try:
   for row in target['models']:
    if not row['role'].startswith('production/'):continue
    folder.mkdir(exist_ok=True);p=folder/row['role'].replace('/','_');tmp=p.with_suffix('.pt.partial');assert not p.exists() and not tmp.exists()
    sf.get(row['path'],str(tmp));assert tmp.stat().st_size==row['bytes'] and H(tmp)==row['SHA'];tmp.replace(p)
    local.append(dict(**row,local_path=str(p),twohost_bytes_SHA_exact=True))
  finally:sf.close()
  target['local_models']=local;v['target']=target
 finally:
  pw=None
  if c:c.close()
 v['epoch']=time.time();put('HUMAN_TRAINING_STATUS1924_EXISTING_E2_READONLY_COMPLETE_ACTUAL.json',v)
 current=next((r['value'] for r in v['source']['files'] if r['path'].endswith('/OWNER_CURRENT.json')),{});row=current.get('row') or {}
 print(json.dumps(dict(epoch=v['epoch'],current_phase=row.get('phase'),latest_save=row.get('latest_save'),source_owner=v['source']['actual_owner_processes'],target_processes=v['target']['actual_own_processes'],locks=v['source']['actual_original_two_fcntl'],models=local,owner_error=any(r['path'].endswith('OWNER_ORIGINAL_ERROR.json') for r in v['source']['files'])),ensure_ascii=False),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put('HUMAN_TRAINING_STATUS1924_READONLY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_runtime_retry_or_mutation=True));raise
