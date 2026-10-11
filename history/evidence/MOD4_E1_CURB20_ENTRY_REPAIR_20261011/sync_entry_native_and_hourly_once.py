from repair_io import *
def main():
 save('ENTRY_NATIVE_HOURLY_SYNC_STARTED.json',dict(epoch=time.time(),annotations_only=True,no_PPO_or_budget_mutation=True))
 n,w=connect_both()
 try:
  names={'E1_CURB20_ENTRY_V2_COMPONENT_CPU_ACTUAL_REVIEW.json':R/'ENTRY_V2_COMPONENT_CPU_PASSED.json','E1_CURB20_ENTRY_V1_CPU_REJECTED.json':R/'ENTRY_COMPONENT_V1_CPU_REJECTED.json','E1_CURB20_ENTRY_NATIVE_DISPATCH_ACTUAL_RECEIPT.json':R/'ENTRY_NATIVE_DISPATCH_ACTUAL_RECEIPT.json','MOD4_HOURLY_MONITOR_ACTUAL_VERIFIED_20261011.json':R/'HOURLY_MONITOR_ACTUAL_VERIFIED.json','NEXT_E1_CURB20_ENTRY_FULLSTATE_AND_BOUNDED_RETRAIN_WORK_ORDER.md':R/'NEXT_CURB20_ENTRY_FULLSTATE_AND_BOUNDED_RETRAIN_WORK_ORDER.md'}
  actual=sorted(R.glob('ENTRY_NATIVE_ACTUAL_*.json'))[-1];names['E1_CURB20_ENTRY_NATIVE_CURRENT_ACTUAL.json']=actual
  with n.open_sftp() as f:
   prior=f.listdir(E+'/reports');assert not set(names)&set(prior)
   for name,p in names.items():put(f,E+'/reports/'+name,p.read_bytes())
  v=linux_json(n,r'''from pathlib import Path
import json,time,os,hashlib
R=Path(CENTRAL)/'reports';B=Path(BUDGET);b=B.read_bytes();l=json.loads(b);assert l['authorized_training_seconds']==1188000 and l['active_segment'] is None
protected={x:(R/x).read_bytes() for x in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json')}
j=lambda p:json.loads(p.read_bytes());m=j(R/'MOD4_HOURLY_MONITOR_ACTUAL_VERIFIED_20261011.json');assert m['status']=='ACTIVE' and m['rrule']=='FREQ=HOURLY;INTERVAL=1'
scope=dict(root=NEWROOT,source_count=398,reset_only_axis=True,new_command_geometry_reward_LR_DR_clock_changes=False,CPU_passed=True,native_dispatch_receipt=str(R/'E1_CURB20_ENTRY_NATIVE_DISPATCH_ACTUAL_RECEIPT.json'),actual_current=str(R/'E1_CURB20_ENTRY_NATIVE_CURRENT_ACTUAL.json'),fullstate_PPO_formal_pending=True,work_order=str(R/'NEXT_E1_CURB20_ENTRY_FULLSTATE_AND_BOUNDED_RETRAIN_WORK_ORDER.md'))
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';old=p.read_bytes();c=json.loads(old);rev=c['terrain_subexpert_revision004'];assert rev['approved'] and rev['active_next_expert']=='E1_CURB'
rev.update(curb20_entry_native_scope=scope,active_next_phase='CURB20_entry_new_SDK_native_contract',actual_monitor_receipt=str(R/'MOD4_HOURLY_MONITOR_ACTUAL_VERIFIED_20261011.json'))
assert p.read_bytes()==old;tmp=p.with_name(p.name+'.ENTRY-'+str(time.time_ns()));tmp.write_bytes(json.dumps(c,ensure_ascii=False,indent=2).encode());os.replace(tmp,p)
p=R/'LATEST_HANDOFF.md';old=p.read_bytes();note='\n\nCURB20 new deterministic reset-entry V2 CPU admitted; independent source398 SDK/native-only controller actually dispatched. Original v1 CPU footprint refusal retained. New fullstate/PPO/formal still pending. Human explicitly changes existing mod4-10 heartbeat to ACTIVE every1h; healthypending DONT_NOTIFY, noextra5minSSH task. New workorder and actual own stage receipts linked in current. Canonical1188000/7extensions unchanged; E0/SLOPE scopes frozen.\n';assert p.read_bytes()==old;tmp=p.with_name(p.name+'.ENTRY-'+str(time.time_ns()));tmp.write_bytes(old+note.encode());os.replace(tmp,p)
assert B.read_bytes()==b and all((R/x).read_bytes()==raw for x,raw in protected.items())
print(json.dumps(dict(epoch=time.time(),metadata_synced=True,scope=scope,canonical_SHA=hashlib.sha256(b).hexdigest(),protected_bytes_preserved=True,hourly_monitor_actual=True,no_PPO_budget_or_live_source_write=True)))
'''.replace('CENTRAL',repr(E)).replace('BUDGET',repr(B)).replace('NEWROOT',repr(NEW)))
  p=save('ENTRY_NATIVE_HOURLY_METADATA_SYNCED.json',v)
  with n.open_sftp() as f:put(f,E+'/reports/E1_CURB20_ENTRY_NATIVE_HOURLY_METADATA_SYNCED.json',p.read_bytes())
  print(json.dumps(dict(metadata_synced=True,native_scope_root=NEW,hourly=True)))
 finally:cleanup(n,w)
if __name__=='__main__':main()
