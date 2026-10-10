"""Verify actual app prompt and append only new134/Git evidence metadata."""
from review133_io import *
import os,tomllib,traceback

def main():
 p=Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))/'automations/mod4-10/automation.toml';v=tomllib.loads(p.read_text(encoding='utf8'))
 expected=(D/'MONITOR_CURRENT_ACTUAL_PROMPT.md').read_text(encoding='utf8').strip()
 assert v['prompt'].strip()==expected and v['status']=='ACTIVE' and v['rrule']=='FREQ=HOURLY;INTERVAL=2' and v['target_thread_id']=='01a07a2d-9036-7531-a012-692df9f56353'
 monitor=dict(epoch=time.time(),automation_id='mod4-10',actual_status=v['status'],actual_rrule=v['rrule'],prompt_bytes=len(v['prompt'].encode()),prompt_sha256=H(v['prompt'].encode()),actual_app_prompt_exact=True,no_new_periodic_or_GPU_actions=True)
 save('MONITOR_CURRENT_ACTUAL_VERIFIED.json',monitor)
 save('READONLY_WINDOWS_GLOB_LOCATOR_ERROR_RETAINED.json',dict(epoch=time.time(),trial_id='CURB133-READONLY-WINDOWS-GLOB-02',operation='rg path ending literal wildcard/*.py',actual_error='Windows IO error123 invalid filename/directory syntax',resolved_by='Read exact known source file review_completed_block2_reset_diagnostic.py',read_only_no_GPU_PPO_mutation=True))
 collection=sorted(R.glob('SLOPE134_COLLECTED_[0-9]*.json'))[-1];git=json.loads((R/'STAGE_GIT_RECORDED.json').read_bytes());assert git['remote_main_tag_peeled_verified'] and not git['push_pending']
 save('POSTSTAGE134_GIT_METADATA_SYNC_STARTED.json',dict(epoch=time.time(),only_metadata_new_snapshot_refs=True))
 n,w=connect_both()
 try:
  reports={'E1_SLOPE5_134_CURRENT_ACTUAL_COLLECTION.json':collection.read_bytes(),'E1_CURB133_SLOPE134_STAGE_GIT_RECORDED.json':(R/'STAGE_GIT_RECORDED.json').read_bytes(),'E1_CURB133_SLOPE134_MONITOR_CURRENT_ACTUAL_VERIFIED.json':(R/'MONITOR_CURRENT_ACTUAL_VERIFIED.json').read_bytes()}
  with n.open_sftp() as f:
   names=f.listdir(E+'/reports');assert all(x not in names for x in reports)
   for name,raw in reports.items():put(f,E+'/reports/'+name,raw)
  receipt=linux_json(n,r'''from pathlib import Path
import json,time,os,hashlib
R=Path(CENTRAL)/'reports';B=Path(BUDGET);budget=B.read_bytes();protected={n:(R/n).read_bytes() for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json')}
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();v=json.loads(before);rev=v['terrain_subexpert_revision004'];assert rev['active_next_expert']=='E1_SLOPE'
s=rev['slope5_134_frozen_scope'];assert not s['learning_executor_deployed'] and len(s['jobs'])==1
g=json.loads((R/'E1_CURB133_SLOPE134_STAGE_GIT_RECORDED.json').read_bytes());assert g['remote_main_tag_peeled_verified'] and not g['push_pending']
s.update(actual_collection=str(R/'E1_SLOPE5_134_CURRENT_ACTUAL_COLLECTION.json'),actual_collector='collect_slope134_actual.py',actual_reviewer='review_slope134_actual.py')
rev.update(complete133_slope134_git_receipt=str(R/'E1_CURB133_SLOPE134_STAGE_GIT_RECORDED.json'),complete133_slope134_monitor_receipt=str(R/'E1_CURB133_SLOPE134_MONITOR_CURRENT_ACTUAL_VERIFIED.json'))
assert p.read_bytes()==before;tmp=p.with_name(p.name+'.134POST-'+str(time.time_ns()));tmp.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode());os.replace(tmp,p)
assert B.read_bytes()==budget and all((R/n).read_bytes()==raw for n,raw in protected.items())
print(json.dumps(dict(epoch=time.time(),metadata_synced=True,current134_collection_and_Git_monitor_refs_synced=True,master_approval_tracks_RM_canonical_bytes_preserved=True,canonical_SHA=hashlib.sha256(budget).hexdigest(),no_GPU_PPO_or_budget_actions=True)))
'''.replace('CENTRAL',repr(E)).replace('BUDGET',repr(B)))
  p=save('POSTSTAGE134_GIT_MONITOR_METADATA_SYNCED.json',receipt)
  with n.open_sftp() as f:put(f,E+'/reports/E1_CURB133_SLOPE134_POSTSTAGE_GIT_MONITOR_METADATA_SYNCED.json',p.read_bytes())
  print(json.dumps(dict(monitor=monitor,metadata=receipt)))
 finally:cleanup(n,w)

if __name__=='__main__':
 try:main()
 except BaseException:save('POSTSTAGE134_GIT_MONITOR_SYNC_ERROR.json',dict(error=traceback.format_exc(),no_blind_replay=True));raise
