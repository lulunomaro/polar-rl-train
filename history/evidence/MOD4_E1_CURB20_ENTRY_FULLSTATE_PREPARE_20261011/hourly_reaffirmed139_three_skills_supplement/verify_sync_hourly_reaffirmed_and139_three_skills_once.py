"""Verify the same heartbeat hourly; append three-skill actual facts without replay."""
from pathlib import Path
import sys,json,time,tomllib,hashlib,traceback
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent
sys.path.insert(0,str(D));from stage_dispatch_seed_reviewed_once import NEW,save
sys.path.insert(0,str(W/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011'));import repair_io as io
def main():
 t=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'));req=json.loads((R/'MOD4_HOURLY_REAFFIRMED_MONITOR_REQUEST.json').read_bytes())
 assert all(t[k]==req[k] for k in ('id','kind','name','status','rrule','target_thread_id'))
 p=(D/'MONITOR_CURRENT_HOURLY_REAFFIRMED_PROMPT.md').read_text(encoding='utf8');assert t['prompt'].replace('\r\n','\n')==p
 verified=save('MOD4_HOURLY_REAFFIRMED_MONITOR_ACTUAL_VERIFIED.json',dict(epoch=time.time(),id=t['id'],kind=t['kind'],name=t['name'],status=t['status'],rrule=t['rrule'],target_thread_id=t['target_thread_id'],same_existing_heartbeat=True,actual_interval_minutes=60,actual_prompt_raw_string_SHA=io.H(t['prompt'].encode()),normalized_prompt_SHA=io.H(p.encode()),human_request=req['human_request'],old_30min_snapshot_retained=True,healthy_pending_silent=True,new_automation_created=False,no_training_physical_or_budget_action=True))
 names={'MOD4_HOURLY_REAFFIRMED_MONITOR_REQUEST.json':R/'MOD4_HOURLY_REAFFIRMED_MONITOR_REQUEST.json','MOD4_HOURLY_REAFFIRMED_MONITOR_ACTUAL_VERIFIED.json':verified,'E1_CURB20_ENTRY139_THREE_SKILL_ACTUAL_COLLECTION.json':R/'CURB139_COLLECTED_1791706365827053100.json','E1_CURB20_ENTRY139_THREE_SKILL_ACTUAL_REVIEW.json':R/'CURB139_SCHEMA_REVIEW_1791706413790143300.json'}
 n,w=io.connect_both()
 try:
  with n.open_sftp() as f:
   assert not set(names)&set(f.listdir(io.E+'/reports'))
   for name,p in names.items():io.put(f,io.E+'/reports/'+name,p.read_bytes())
  v=io.linux_json(n,r'''from pathlib import Path
import json,time,hashlib,os
R=Path(CENTRAL)/'reports';B=Path(BUDGET);j=lambda p:json.loads(p.read_bytes());verified=j(R/'MOD4_HOURLY_REAFFIRMED_MONITOR_ACTUAL_VERIFIED.json');collection=j(R/'E1_CURB20_ENTRY139_THREE_SKILL_ACTUAL_COLLECTION.json');review=j(R/'E1_CURB20_ENTRY139_THREE_SKILL_ACTUAL_REVIEW.json')
assert verified['actual_interval_minutes']==60 and verified['status']=='ACTIVE' and verified['same_existing_heartbeat']
assert not review['review_complete'] and set(review['retention'])=={'flat','spin','world'} and review['terrain'] is None and len(collection['pending'])==1
assert collection['passed']['checkpoint']['sha256']=='2fe67400d4119b94dbf33d7770b7fec44a9c73c568256e8161c3d8298ad73a04'
protected={x:(R/x).read_bytes() for x in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json')};budget_before=B.read_bytes();p=R/'MOE_PLAN_EXECUTION_CURRENT.json';old=p.read_bytes();c=json.loads(old);rev=c['terrain_subexpert_revision004'];scope=rev['curb20_entry_seed_reviewed_scope'];assert scope['root']==ROOT and scope['source_count']==410
scope.update(actual_139_collection=str(R/'E1_CURB20_ENTRY139_THREE_SKILL_ACTUAL_COLLECTION.json'),actual_139_partial_review=str(R/'E1_CURB20_ENTRY139_THREE_SKILL_ACTUAL_REVIEW.json'),actual_139_complete_cases=list(collection['cases']),actual_139_pending=collection['pending'],actual_139_review_complete=False)
rev.update(monitor_cadence_minutes=60,monitor_latest_human_request='监守调成一小时一次吧',monitor_actual_verified=str(R/'MOD4_HOURLY_REAFFIRMED_MONITOR_ACTUAL_VERIFIED.json'))
assert p.read_bytes()==old;tmp=p.with_name(p.name+'.HOURLYREAF-'+str(time.time_ns()));tmp.write_bytes(json.dumps(c,ensure_ascii=False,indent=2).encode());os.replace(tmp,p)
p=R/'LATEST_HANDOFF.md';old=p.read_bytes();note='\n\nLatest direct human instruction: keep the same mod4-10 heartbeat ACTIVE every1hour; old30min/2hour cadence is historical. Native app setting and same target actual verified, quiet healthy/pending retained, no additional monitor/5minSSH/ping/Rich/budget. Three139 skills now actual complete/errorfree, twohost JSONbyteSHAexact and strict115/129 initialization/parameter/recipe/assignment pair review completed; terrain still actualpending and fullreviewfalse. Source364 to own410 negative4pi7/8 to5/8, positive8/8, world63/64 with maxcross.050733746, originalfalse retained; ownCURB passage decision still required beforemorePPO orhigher geometry. All saved currentreports/cadence/sync receipts requireordinary Git supplement, no oldonce/GPU/record/tag/budget replay and no WASD action.\n';assert p.read_bytes()==old;tmp=p.with_name(p.name+'.HOURLYREAF-'+str(time.time_ns()));tmp.write_bytes(old+note.encode());os.replace(tmp,p)
assert all((R/x).read_bytes()==b for x,b in protected.items()) and B.read_bytes()==budget_before
print(json.dumps(dict(epoch=time.time(),metadata_synced=True,actual_interval_minutes=60,same_existing_heartbeat=True,actual_139_complete_cases=list(collection['cases']),actual_139_pending=collection['pending'],protected_master_approval_tracks_RM_exact=True,canonical_bytes_preserved=True,canonical_writer_actions=0,no_GPU_queue_or_training_action=True)))
'''.replace('CENTRAL',repr(io.E)).replace('BUDGET',repr(io.B)).replace('ROOT',repr(NEW)))
  receipt=save('MOD4_HOURLY_REAFFIRMED_AND139_THREE_SKILL_METADATA_SYNCED.json',v)
  with n.open_sftp() as f:io.put(f,io.E+'/reports/MOD4_HOURLY_REAFFIRMED_AND139_THREE_SKILL_METADATA_SYNCED.json',receipt.read_bytes())
  print(json.dumps(dict(actual_hourly=True,metadata_synced=True,complete_skills=len(v['actual_139_complete_cases']),terrain_pending=True)))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('MOD4_HOURLY_REAFFIRMED_SYNC_REJECTED.json',dict(epoch=time.time(),error=traceback.format_exc(),no_old_sync_replay=True));raise
