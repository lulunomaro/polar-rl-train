"""New annotation/CAS only, with live ledger allowed to account through its owner."""
from stage_reviewed_fullstate_once import D,R,E,B,NEW,connect_both,cleanup,linux_json,save,put
from pathlib import Path
import json,time,traceback
def main():
 actual_path=sorted(R.glob('FULLSTATE_ACTUAL_[0-9]*.json'))[-1];actual=json.loads(actual_path.read_bytes())
 save('FULLSTATE_METADATA_SYNC_STARTED.json',dict(epoch=time.time(),actual_path=str(actual_path),annotation_only=True,no_canonical_write_or_GPU_action=True))
 n,w=connect_both()
 try:
  reports={'E1_CURB20_FULLSTATE_REVIEWED_CURRENT_ACTUAL.json':actual_path.read_bytes(),
   'E1_CURB20_FULLSTATE_REVIEWED_TARGET_CPU_VERIFIED.json':(R/'REVIEWED_TARGET_CPU_PASSED.json').read_bytes(),
   'E1_CURB20_FULLSTATE_REVIEWED_DISPATCH_ACTUAL_RECEIPT.json':(R/'REVIEWED_DISPATCH_ACTUAL_RECEIPT.json').read_bytes(),
   'E1_CURB20_FULLSTATE_PREDEPLOY_VALIDATOR_REVIEW.json':(R/'PREDEPLOY_VALIDATOR_SOURCE_REVIEW.json').read_bytes()}
  formal=sorted(R.glob('OWN_FORMAL_CPU_VERIFIED_[0-9]*.json'))
  if formal:reports['E1_CURB20_FULLSTATE_OWN_FORMAL_CPU_VERIFIED.json']=formal[-1].read_bytes()
  with n.open_sftp() as f:
   for name,raw in reports.items():put(f,E+'/reports/'+name,raw)
  result=linux_json(n,r'''from pathlib import Path
import json,time,os,hashlib
R=Path(CENTRAL)/'reports';B=Path(BUDGET);protected={name:(R/name).read_bytes() for name in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json')}
j=lambda p:json.loads(p.read_bytes());actual=j(R/'E1_CURB20_FULLSTATE_REVIEWED_CURRENT_ACTUAL.json');cpu=j(R/'E1_CURB20_FULLSTATE_REVIEWED_TARGET_CPU_VERIFIED.json')
assert cpu['passed'] and cpu['corrected_CURB_fullschema_CPU_fixture_passed'] and actual['root']==ROOT
state=actual['reports']['E1_STATE.json'];passed=actual['reports'].get('e1_CURB20_independent_observation_PASSED.json')
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();v=json.loads(before);revision=v['terrain_subexpert_revision004'];assert revision['approved'] and revision['active_next_expert']=='E1_CURB' and 'curb20_fullstate_reviewed_scope' not in revision
revision['curb20_fullstate_reviewed_scope']=dict(epoch=time.time(),root=ROOT,source_count=380,source_SHA='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e',current_actual=str(R/'E1_CURB20_FULLSTATE_REVIEWED_CURRENT_ACTUAL.json'),target_CPU=str(R/'E1_CURB20_FULLSTATE_REVIEWED_TARGET_CPU_VERIFIED.json'),actual_phase_at_sync=state['phase'],SDK_native_exact_reused=True,new_fullstate_PPO_preflight_complete='E1_COMPLETE_PPO_PREFLIGHT_PASSED.json' in actual['reports'],own_formal_complete=passed is not None,requires_complete133_behavior_review=True,no_more_PPO_automatic=True,new_budget_seconds=0,E0_Wave_protected=True,gate_untrained=True,old_native_scope_pending_snapshots_historical=True)
if passed:revision['curb20_fullstate_reviewed_scope']['own_formal_checkpoint']=passed['checkpoint']
assert p.read_bytes()==before;tmp=p.with_name(p.name+'.CURB380-'+str(time.time_ns()));tmp.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode());os.replace(tmp,p)
hp=R/'LATEST_HANDOFF.md';old=hp.read_bytes();marker='CURB380 independent fullstate scope actual:';assert marker.encode() not in old
msg='\n\n'+marker+' '+ROOT+'; phase '+state['phase']+'. Source364/3c97 complete129, old372/378 bytes retained, CPU original strict sourceidentity load then explicitnewassignment binding/privateRNG/schema checked. SDK/native/clock exactreuse, 128x2/20kx4 new fullstate preflight each once charged by ownparent, then bounded300s and own133 fourcase review. No E0/Wave overwrite or gate/RM002 qualification. Stdlib torch preimport rejection and predeployment validator review preserved. Alloldonce main/resume/native/SDK/budgettail excluded; actual source/PID/fullsave/PASSED/unique segment always priority.\n'
assert hp.read_bytes()==old;tmp=hp.with_name(hp.name+'.CURB380-'+str(time.time_ns()));tmp.write_bytes(old+msg.encode());os.replace(tmp,hp)
assert all((R/n).read_bytes()==b for n,b in protected.items());assert j(B)['authorized_training_seconds']==828000
print(json.dumps(dict(epoch=time.time(),new_fullstate_scope_metadata_synced=True,actual_phase_at_sync=state['phase'],master_approval_tracks_RM_bytes_preserved=True,no_canonical_write=True,normal_parent_accounting_may_change_dynamic_canonical_bytes=True)))
'''.replace('CENTRAL',repr(E)).replace('BUDGET',repr(B)).replace('ROOT',repr(NEW)))
  p=save('FULLSTATE_METADATA_SYNCED.json',result)
  with n.open_sftp() as f:put(f,E+'/reports/E1_CURB20_FULLSTATE_REVIEWED_METADATA_SYNCED.json',p.read_bytes())
  print(json.dumps(result))
 finally:cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('FULLSTATE_METADATA_SYNC_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_sync_replay_check_actual_CAS_first=True));raise
