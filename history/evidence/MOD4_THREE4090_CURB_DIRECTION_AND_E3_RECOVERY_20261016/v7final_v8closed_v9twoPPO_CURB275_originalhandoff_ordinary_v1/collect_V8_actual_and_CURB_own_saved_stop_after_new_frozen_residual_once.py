from pathlib import Path
import os,sys,json,time,getpass,traceback
D=Path(__file__).resolve().parent;R=D/'reports';sys.path.insert(0,str(D));from deploy_V8_actual_V7_closed_three_source_healthy_blocks_once import ROOTS,code,H,connect72,t,PY
from collect_first_two_native_and_E2_handoff_actual_readonly_once import READ
from collect_two_native_CPU_and_first_PPO_bound_same_connection_once import MODELS
from request_V2_own_saved_handoff_collect_complete_sources_once import STOP,FINALS
def put(n,v,rolling=False):
 p=R/n
 if rolling:q=p.with_suffix('.json.partial');q.write_text(json.dumps(v,indent=2),encoding='utf8');q.replace(p)
 else:
  with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def models(c,py,key):
 v=code(c,py,MODELS,ROOTS[key],key);folder=D/'actual_V8_native_first_models'/key;folder.mkdir(parents=True);sf=c.open_sftp();sf.get_channel().settimeout(120);rows=[]
 try:
  for row in v['models']:
   p=folder/row['role'].replace('/','_');q=p.with_suffix('.pt.partial');assert not p.exists() and not q.exists();sf.get(row['path'],str(q));assert q.stat().st_size==row['bytes'] and H(q)==row['SHA'];q.replace(p);rows.append(dict(**row,local_path=str(p),twohost_complete_SHA=True))
 finally:sf.close()
 return rows
def main():
 frozen=json.loads((D/'curb_v7final147_frozen35_3060_v1/reports/CURB35_V7FINAL147_FULL1500_ORIGINAL_ROUTE_ALL_PREFIX_CPU_ACTUAL.json').read_bytes());assert frozen['passed'] and frozen['counts']['ascending']['complete']==6 and frozen['counts']['descending']['complete']==27;put('V8_RESIDUAL_SAVED_STOP_FINITE_TRANSPORT_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_210_72_249_transport_owner=True,only_own_CURB_complete_update_save_stop_other_experts_unchanged=True));pw=getpass.getpass('Host72 independent continuing expert actual saves (hidden): ');c=None;v={}
 try:
  c=t.connect();begun=time.monotonic()
  while True:
   x=code(c,t.PY,READ,ROOTS['curb'],'curb');put('V8_SOURCE_CURRENT_RESIDUAL_REVIEW_FINITE_LOCAL_ACTUAL.json',x,True);current=next(r['value'] for r in x['files'] if r['path'].endswith('/OWNER_CURRENT.json'));curb=current['rows']['curb'];ready=curb.get('phase')=='production' and (curb.get('latest_save') or {}).get('updates',0)>=1
   if ready or curb.get('original_error') or time.monotonic()-begun>=300:break
   time.sleep(20)
  if ready:
   stop=STOP.replace('Human requested maximum three4090 utilization: cooperative complete-update/save handoff to unified three-expert dispatch. Retain progress and actual original costs.','New actual frozen CURB35 source06314 full1500 up6of27/down27of27/ordinary0: preserve complete update/model, stop more unchanged-axis exposure for independent residual diagnosis; other independent E2/E3 continue. No policy-failure or global skill claim.');v['curb_stop']=code(c,t.PY,stop,ROOTS['curb'],'curb');put('V8_CURB_OWN_COMPLETE_UPDATE_STOP_AFTER_NEW_FROZEN_UP6_ACTUAL.json',v['curb_stop']);begun=time.monotonic()
   while True:
    x=code(c,t.PY,READ,ROOTS['curb'],'curb');put('V8_SOURCE_CURRENT_RESIDUAL_REVIEW_FINITE_LOCAL_ACTUAL.json',x,True);current=next(r['value'] for r in x['files'] if r['path'].endswith('/OWNER_CURRENT.json'));curb=current['rows']['curb']
    if curb.get('terminal_all_own_children_waited') or time.monotonic()-begun>=180:break
    time.sleep(10)
  v['curb']=x;v['curb']['local_models']=models(c,t.PY,'curb');v['curb_final']=code(c,t.PY,FINALS,ROOTS['curb'],'curb') if curb.get('terminal_all_own_children_waited') and (curb.get('final') or {}).get('passed') else None
  if v['curb_final']:
   row=v['curb_final'];p=D/'actual_V8_native_first_models/curb/own_saved_review_final.pt';sf=c.open_sftp()
   try:sf.get(row['path'],str(p));assert p.stat().st_size==row['bytes'] and H(p)==row['SHA'];v['curb_final']=dict(**row,local_path=str(p),twohost_complete_SHA=True)
   finally:sf.close()
  v['canonical']=code(c,t.PY,"from pathlib import Path;import json,time;C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');v=json.loads(C.read_bytes());print(json.dumps(dict(epoch=time.time(),active=v['active_segment'],charged=v['charged_training_seconds'],remaining=v['remaining_training_seconds'],authorized=v['authorized_training_seconds'],extensions=len(v['budget_extensions']))))")
 finally:t.close(c);c=None
 try:
  c=connect72(pw);pw=None
  for key in ('e2','recovery'):v[key]=code(c,PY,READ,ROOTS[key],key);v[key]['local_models']=models(c,PY,key)
 finally:
  pw=None
  if c:c.close()
 v['epoch']=time.time();put('V8_CURB_SAVED_REVIEW_STOP_E2_E3_CONTINUING_ACTUAL_COLLECTION.json',v);print(json.dumps(dict(epoch=v['epoch'],curb_final=v['curb_final'],models={k:[r['role'] for r in v[k]['local_models']] for k in ROOTS},other_expert_errors={k:[r['path'] for r in v[k]['files'] if '/NODE_ORIGINAL_ERROR.json' in r['path']] for k in ('e2','recovery')})),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put('V8_RESIDUAL_STOP_COLLECTOR_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),unknown_actual_no_signal_or_replay=True));raise
