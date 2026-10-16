from pathlib import Path
import sys,os,json,time,getpass,traceback
D=Path(__file__).resolve().parent;R=D/'reports';sys.path.insert(0,str(D))
from deploy_V9_actual_CPU_status_fix_E2_E3_CURB_deferred_once import ROOTS,code,H,connect72,t,PY
from collect_first_two_native_and_E2_handoff_actual_readonly_once import READ
from collect_hourly2223_V7_actual_finals_cost_exit_resources_readonly_once import CANON
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 put('V9_FIRST_ACTUAL_STAGE_READER_STARTED.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_transport=True,readonly=True));pw=getpass.getpass('Host72 V9 own scope read only (hidden): ');c=None;v={}
 try:c=t.connect();v['curb']=code(c,t.PY,READ,ROOTS['curb'],'curb');v['canonical']=code(c,t.PY,CANON)
 finally:t.close(c);c=None
 try:
  c=connect72(pw);pw=None
  for key in ('e2','recovery'):v[key]=code(c,PY,READ,ROOTS[key],key)
 finally:
  pw=None
  if c:c.close()
 v['epoch']=time.time();put('V9_ACTUAL_E2_E3_STAGES_NATIVE_REUSE_CPU_STATUS_CURB_DEFERRED_READONLY.json',v)
 for key in ROOTS:
  fs=v[key]['files'];cur=next((x['value'] for x in fs if x['path'].endswith('/'+('OWNER_CURRENT.json' if key=='curb' else 'NODE_CURRENT.json'))),{});print(json.dumps(dict(key=key,epoch=v[key]['epoch'],current=cur,processes=v[key]['actual_own_processes'],errors=[x for x in fs if 'ORIGINAL_ERROR' in x['path']])),flush=True)
 print(json.dumps(dict(active=v['canonical']['active'],locks=v['canonical']['actual_two_fcntl'])),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put('V9_FIRST_ACTUAL_STAGE_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_runtime_mutation=True));raise
