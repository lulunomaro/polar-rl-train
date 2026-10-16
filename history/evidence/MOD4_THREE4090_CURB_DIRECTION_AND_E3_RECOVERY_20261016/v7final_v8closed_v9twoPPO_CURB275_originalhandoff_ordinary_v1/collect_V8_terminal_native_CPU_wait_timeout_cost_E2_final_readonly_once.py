from pathlib import Path
import sys,os,json,time,getpass,traceback
D=Path(__file__).resolve().parent;R=D/'reports';sys.path.insert(0,str(D));from deploy_V8_actual_V7_closed_three_source_healthy_blocks_once import ROOTS,code,H,connect72,t,PY
from collect_first_two_native_and_E2_handoff_actual_readonly_once import READ
from collect_hourly2223_V7_actual_finals_cost_exit_resources_readonly_once import CANON,FINALS
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 put('V8_TERMINAL_READER_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_transport=True,readonly_no_GPU_replay_or_budget_change=True));pw=getpass.getpass('Host72 original native CPU admission and terminal source (hidden): ');c=None;v={}
 try:c=t.connect();v['curb']=code(c,t.PY,READ,ROOTS['curb'],'curb');v['canonical']=code(c,t.PY,CANON);assert v['canonical']['active'] is None and v['canonical']['last_completed']['owner_parent_pid']==570954 and all(not q['actual_held'] for q in v['canonical']['actual_two_fcntl']) and not v['curb']['actual_own_processes']
 finally:t.close(c);c=None
 try:
  c=connect72(pw);pw=None
  for key in ('e2','recovery'):v[key]=code(c,PY,READ,ROOTS[key],key);assert not v[key]['actual_own_processes']
  row=code(c,PY,FINALS,ROOTS['e2'],'e2')['complete_model'];assert row;folder=D/'actual_V8_terminal_models';folder.mkdir();p=folder/'e2_final.pt';q=p.with_suffix('.pt.partial');sf=c.open_sftp()
  try:sf.get(row['path'],str(q));assert q.stat().st_size==row['bytes'] and H(q)==row['SHA'];q.replace(p)
  finally:sf.close()
  v['e2_model']=dict(**row,local_path=str(p),twohost_complete_SHA=True)
 finally:
  pw=None
  if c:c.close()
 v['epoch']=time.time();put('V8_TERMINAL_CPU_WAIT_TIMEOUT_E3_ADMITTED_NO_PPO_EXACT_COST_READONLY_ACTUAL.json',v);print(json.dumps(dict(epoch=v['epoch'],e2_model=v['e2_model'],last_cost={k:x for k,x in v['canonical']['last_completed'].items() if k not in ('actual_terminal_rows',)},all_own_processes_out=True,original_two_fcntl_free=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put('V8_TERMINAL_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_blind_retry=True));raise
