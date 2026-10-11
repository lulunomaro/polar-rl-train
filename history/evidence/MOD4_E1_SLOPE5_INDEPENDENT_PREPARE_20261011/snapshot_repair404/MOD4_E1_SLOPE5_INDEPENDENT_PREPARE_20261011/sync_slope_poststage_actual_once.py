from slope_io import *
import os,tomllib,traceback
def main():
 app=Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))/'automations/mod4-10/automation.toml';v=tomllib.loads(app.read_text(encoding='utf8'));expected=(D/'MONITOR_CURRENT_SCOPE_PREFLIGHT_PROMPT.md').read_text(encoding='utf8').strip()
 assert v['prompt'].strip()==expected and v['status']=='ACTIVE' and v['rrule']=='FREQ=HOURLY;INTERVAL=2'
 mon=dict(epoch=time.time(),automation_id='mod4-10',actual_status=v['status'],actual_rrule=v['rrule'],prompt_bytes=len(v['prompt'].encode()),prompt_sha256=H(v['prompt'].encode()),app_prompt_exact=True,no_added_periodic_actions=True)
 mp=save('MONITOR_PREFLIGHT_ACTUAL_VERIFIED.json',mon)
 ap=sorted(R.glob('SLOPE_ACTUAL_[0-9]*.json'))[-1];actual=json.loads(ap.read_bytes());r=actual['own_reports'];git=json.loads((R/'STAGE_GIT_RECORDED.json').read_bytes())
 assert git['remote_main_tag_peeled_verified'] and not git['push_pending']
 save('POSTSTAGE_SYNC_STARTED.json',dict(epoch=time.time(),metadata_only_refs=True,no_controller_or_budget_action=True))
 n,w=connect_both()
 try:
  reports={'E1_SLOPE5_INDEPENDENT_CURRENT_ACTUAL.json':ap.read_bytes(),'E1_SLOPE5_INDEPENDENT_DISPATCH_ACTUAL_RECEIPT.json':(R/'DISPATCH_ACTUAL_RECEIPT.json').read_bytes(),'E1_SLOPE5_INDEPENDENT_NATIVE_ACTUAL_VERIFIED.json':json.dumps(r['SLOPE_NATIVE_SCOPE_PASSED.json'],indent=2).encode(),'E1_SLOPE5_INDEPENDENT_SMALL128_ACTUAL_VERIFIED.json':json.dumps(r['slope_discard128_PASSED.json'],indent=2).encode(),'E1_SLOPE5_INDEPENDENT_STAGE_GIT_RECORDED.json':(R/'STAGE_GIT_RECORDED.json').read_bytes(),'E1_SLOPE5_INDEPENDENT_MONITOR_ACTUAL_VERIFIED.json':mp.read_bytes()}
  with n.open_sftp() as f:
   names=f.listdir(E+'/reports');assert all(name not in names for name in reports)
   for name,raw in reports.items():put(f,E+'/reports/'+name,raw)
  receipt=linux_json(n,r'''from pathlib import Path
import json,hashlib,time,os
R=Path(CENTRAL)/'reports';B=Path(BUDGET);before_budget=B.read_bytes();protected={n:(R/n).read_bytes() for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json')}
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();v=json.loads(before);rev=v['terrain_subexpert_revision004'];assert rev['approved'] and rev['active_next_expert']=='E1_SLOPE';scope=rev['slope5_independent_scope'];assert scope['root']==ROOT
scope.update(learning_controller_staged_not_started=False,learning_controller_dispatched=True,actual_current=str(R/'E1_SLOPE5_INDEPENDENT_CURRENT_ACTUAL.json'),actual_dispatch=str(R/'E1_SLOPE5_INDEPENDENT_DISPATCH_ACTUAL_RECEIPT.json'),actual_new_SDK_native_PPO_pending=True,actual_native_PASSED=str(R/'E1_SLOPE5_INDEPENDENT_NATIVE_ACTUAL_VERIFIED.json'),actual_small128_PASSED=str(R/'E1_SLOPE5_INDEPENDENT_SMALL128_ACTUAL_VERIFIED.json'),new_native_and_small_complete=True,big_freshresume_and_formal_pending_at_snapshot=True,actual_collector='collect_slope135_actual.py',actual_reviewer='review_slope135_actual.py',ownformal_and135_review_required=True)
rev.update(slope5_stage_git_receipt=str(R/'E1_SLOPE5_INDEPENDENT_STAGE_GIT_RECORDED.json'),slope5_monitor_receipt=str(R/'E1_SLOPE5_INDEPENDENT_MONITOR_ACTUAL_VERIFIED.json'))
assert p.read_bytes()==before;tmp=p.with_name(p.name+'.SLOPE402ACTUAL-'+str(time.time_ns()));tmp.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode());os.replace(tmp,p)
after_budget=B.read_bytes();a=json.loads(before_budget);b=json.loads(after_budget);assert a['authorized_training_seconds']==b['authorized_training_seconds']==828000 and b['charged_training_seconds']>=a['charged_training_seconds']
assert all((R/n).read_bytes()==raw for n,raw in protected.items())
print(json.dumps(dict(epoch=time.time(),metadata_synced=True,actual_native_small_and_scope_Git_monitor_refs_synced=True,master_approval_tracks_RM_bytes_preserved=True,no_budget_write_by_metadata_reader=True,canonical_before_SHA=hashlib.sha256(before_budget).hexdigest(),canonical_after_SHA=hashlib.sha256(after_budget).hexdigest(),normal_parent_accounting_allowed=True,no_GPU_or_training_dispatch_by_sync=True)))
'''.replace('CENTRAL',repr(E)).replace('BUDGET',repr(B)).replace('ROOT',repr(NEW)))
  rp=save('POSTSTAGE_METADATA_SYNCED.json',receipt)
  with n.open_sftp() as f:put(f,E+'/reports/E1_SLOPE5_INDEPENDENT_POSTSTAGE_METADATA_SYNCED.json',rp.read_bytes())
  print(json.dumps(dict(monitor=mon,metadata=receipt)))
 finally:cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('POSTSTAGE_SYNC_ERROR.json',dict(error=traceback.format_exc(),no_blind_sync_replay=True));raise
