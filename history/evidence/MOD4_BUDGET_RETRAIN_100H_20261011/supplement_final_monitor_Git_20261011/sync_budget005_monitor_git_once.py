"""Only sync new005 monitor/Git receipts; applied seventh extension is read-only."""
from prepare_authorization_and_dispatch_once import *
from slope_io import linux_json


def main():
 assert json.loads((R/'STAGE_GIT_RECORDED.json').read_bytes())['remote_main_tag_peeled_verified']
 names={'MOD4_BUDGET_RETRAIN_100H_005_STAGE_GIT_RECORDED.json':R/'STAGE_GIT_RECORDED.json',
  'MOD4_BUDGET_RETRAIN_100H_005_MONITOR_ACTUAL_VERIFIED.json':R/'MONITOR_ACTUAL_VERIFIED.json',
  'MOD4_MONITOR_CURRENT_BUDGET005_RETRAIN_PROMPT.md':D/'MONITOR_CURRENT_BUDGET005_RETRAIN_PROMPT.md'}
 save('FINAL_MONITOR_GIT_SYNC_STARTED.json',dict(epoch=time.time(),new_metadata_only=True,no_budget_write=True))
 n,w=connect_both()
 try:
  with n.open_sftp() as f:
   prior=f.listdir(E+'/reports');assert not any(name in prior for name in names)
   for name,path in names.items():put(f,CENTRAL+name,path.read_bytes())
  code=r'''from pathlib import Path
import json,time,hashlib,os
R=Path(__E__)/'reports';B=Path(__B__);budget=B.read_bytes();b=json.loads(budget)
assert b['authorized_training_seconds']==1188000 and len(b['budget_extensions'])==7 and b['active_segment'] is None
applied=json.loads((R/'USER_ADD100H_20261011_7TH_APPLIED.json').read_bytes());assert applied['after_sha256']==hashlib.sha256(budget).hexdigest()
protected={x:(R/x).read_bytes() for x in ('PLAN_APPROVAL.json','MOD4_MOE_EXECUTION_CONTRACT.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json')}
g=json.loads((R/'MOD4_BUDGET_RETRAIN_100H_005_STAGE_GIT_RECORDED.json').read_bytes());m=json.loads((R/'MOD4_BUDGET_RETRAIN_100H_005_MONITOR_ACTUAL_VERIFIED.json').read_bytes())
assert g['remote_main_tag_peeled_verified'] and not g['push_pending'] and m['prompt_exact'] and m['status']=='ACTIVE' and m['rrule']=='FREQ=HOURLY;INTERVAL=2'
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';old=p.read_bytes();v=json.loads(old);rev=v['terrain_subexpert_revision004']
assert v['budget_retrain_revision005']['authorized_training_seconds']==1188000 and rev['active_next_expert']=='E1_CURB'
v['budget_retrain_revision005'].update(stage_Git_receipt=str(R/'MOD4_BUDGET_RETRAIN_100H_005_STAGE_GIT_RECORDED.json'),monitor_receipt=str(R/'MOD4_BUDGET_RETRAIN_100H_005_MONITOR_ACTUAL_VERIFIED.json'))
rev.update(actual_monitor_receipt=str(R/'MOD4_BUDGET_RETRAIN_100H_005_MONITOR_ACTUAL_VERIFIED.json'),actual_monitor_prompt=str(R/'MOD4_MONITOR_CURRENT_BUDGET005_RETRAIN_PROMPT.md'))
assert p.read_bytes()==old;tmp=p.with_name(p.name+'.BUDGET005-'+str(time.time_ns()));tmp.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode());os.replace(tmp,p)
h=R/'LATEST_HANDOFF.md';hb=h.read_bytes();note='\n\n005 seventh100h/retraining stage Git remote main/tag/peeled verified '+g['commit']+'/'+g['tagobject']+'. Existing mod4-10 ACTIVE2h latest budget005/retraining prompt exact, same targetthread/noextra schedule. Applied canonical total1188000s/7extensions remains exact; no newlearning started. New monitor/Git receipts referenced; later saved report ordinarysupplement required.\n'
assert h.read_bytes()==hb;tmp=h.with_name(h.name+'.BUDGET005-'+str(time.time_ns()));tmp.write_bytes(hb+note.encode());os.replace(tmp,h)
assert B.read_bytes()==budget and all((R/x).read_bytes()==raw for x,raw in protected.items())
print(json.dumps(dict(epoch=time.time(),metadata_synced=True,new_monitor_Git_receipts_synced=True,canonical_and_post005_authorization_bytes_preserved=True,canonical_SHA=hashlib.sha256(budget).hexdigest(),active_next_expert='E1_CURB',learning_executor_started=False)))'''.replace('__E__',repr(E)).replace('__B__',repr(B))
  value=linux_json(n,code);p=save('FINAL_MONITOR_GIT_METADATA_SYNCED.json',value)
  with n.open_sftp() as f:put(f,CENTRAL+'MOD4_BUDGET_RETRAIN_100H_005_FINAL_MONITOR_GIT_METADATA_SYNCED.json',p.read_bytes())
  print(json.dumps(value))
 finally:cleanup(n,w)


if __name__=='__main__':
 try:main()
 except BaseException:
  save('FINAL_SYNC_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_old_sync_replay=True))
  raise
