from second_io import *
def main():
 actualpath=sorted(R.glob('SECOND_ACTUAL_[0-9]*.json'))[-1];actual=json.loads(actualpath.read_bytes());assert actual['actual_parent'] and actual['actual_child'] and not actual['attention']
 uploads={'E1_WAVE35_SECOND_BOUNDED_TARGET_CPU_VERIFIED.json':R/'SECOND_TARGET_CPU_PASSED.json','E1_WAVE35_SECOND_BOUNDED_DISPATCH_ACTUAL_RECEIPT.json':R/'SECOND_DISPATCH_ACTUAL_RECEIPT.json','E1_WAVE35_SECOND_BOUNDED_DISPATCH_CURRENT_ACTUAL.json':actualpath,'E1_WAVE35_SECOND_BOUNDED_ACTUAL_SOURCE_REUSE.json':R/'SECOND_OLD_ACTUAL_BOUNDARY_AND_REUSE.json','E1_WAVE35_SECOND_BOUNDED_SOURCE_FREEZE.json':R/'SECOND_SOURCE_FREEZE.json'}
 n,w=io.connect_both()
 try:
  with n.open_sftp() as f:
   for name,p in uploads.items():io.put(f,io.E+'/reports/'+name,p.read_bytes())
  v=run(n,r'''from pathlib import Path
import json,time,os,sys
R=Path(CENTRAL_TOKEN)/'reports';D=Path(ROOT_TOKEN);B=Path(BUDGET_TOKEN);j=lambda p:json.loads(p.read_bytes())
sys.path[:0]=[str(D),str(D/'isaac/mod4')];import supervise_wave35_second_bounded_once as own
cpu=j(R/'E1_WAVE35_SECOND_BOUNDED_TARGET_CPU_VERIFIED.json');receipt=j(R/'E1_WAVE35_SECOND_BOUNDED_DISPATCH_ACTUAL_RECEIPT.json');st=j(D/'reports/E1_STATE.json')
assert cpu['passed'] and cpu['source_count']==369 and cpu['source']['sha256']==own.SOURCE_SHA
parent=own.identity(st['owner']['pid']);child=own.identity(st['child']['pid']);assert parent and child and parent['start_ticks']==receipt['controller']['start_ticks'] and child['start_ticks']==st['child']['start_ticks']
b=j(B);assert b['active_segment']['pid']==child['pid'] and b['authorized_training_seconds']==1188000 and len(b['budget_extensions'])==7
protected={name:(R/name).read_bytes() for name in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json')}
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();c=json.loads(before);rev=c['terrain_subexpert_revision004'];assert rev['approved'] and rev['active_next_expert']=='E1_WAVE'
assert j(R/'E1_WAVE35_142_COMPLETE_SCOPE_DECISION.json')['allow_one_additional_bounded_same_scope_block_under005']
rev['wave35_exposure_repair_next_scope']['next_same_scope_continuation_not_yet_deployed']=False
assert 'wave35_second_bounded_scope' not in rev
rev['wave35_second_bounded_scope']=dict(root=str(D),source_count=369,phase=st['phase'],source_selected_SHA=own.SOURCE_SHA,ancestral129_source_SHA='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e',seconds=1800,candidate_number=cpu['candidate_number'],target_CPU_passed=True,formal_dispatched=True,formal_final_pending=True,full_candidate_behavior_pending=True,full_training_trace_pending=True,same_G3_samecommand=True,no_new_geometry_reset_reward_LR_DR=True,no_automatic_third_block_or_50mm=True,target_CPU_report=str(R/'E1_WAVE35_SECOND_BOUNDED_TARGET_CPU_VERIFIED.json'),dispatch_receipt=str(R/'E1_WAVE35_SECOND_BOUNDED_DISPATCH_ACTUAL_RECEIPT.json'),actual_current=str(R/'E1_WAVE35_SECOND_BOUNDED_DISPATCH_CURRENT_ACTUAL.json'),actual_state=st,own_CUDA_startup_actual_pending=True)
rev['active_next_phase']=st['phase'];assert p.read_bytes()==before;tmp=p.with_name(p.name+'.SECOND-'+str(time.time_ns()));tmp.write_text(json.dumps(c,ensure_ascii=False,indent=2));os.replace(tmp,p)
p=R/'LATEST_HANDOFF.md';before=p.read_bytes();message='\n\nActual reviewed second Wave35 block dispatched under004005: isolatedsource369 root '+str(D)+', source own3687f1032ad CPU102 / complete142 forward25 reverse27of27; parent '+str(parent['pid'])+' child '+str(child['pid'])+'. SameG3samecommand/DR/reward/reset,1800s including loadlearnsaveexit, original15s guardian and unique canonical charge; no SDK/native/small/big/fresh/clock replay. OwnCUDA startup/PPO snapshot still actual pending at this dispatch receipt, not final or qualification. After own fullsave/PASSED/unique exit boundary, parent publishes actual unused candidate '+str(cpu['candidate_number'])+' four cases; complete raw/trace/142and129 pairing before next decision; no automaticthird/50mm. Old142/old366 failures and E0/CURB/SLOPE/player untouched. Hourly same heartbeat and Git actualstage/supplements required.\n'
assert p.read_bytes()==before;tmp=p.with_name(p.name+'.SECOND-'+str(time.time_ns()));tmp.write_bytes(before+message.encode());os.replace(tmp,p)
assert all((R/name).read_bytes()==raw for name,raw in protected.items())
v=dict(epoch=time.time(),metadata_synced=True,root=str(D),source_count=369,actual_parent=parent,actual_child=child,candidate_number=cpu['candidate_number'],master_approval_tracks_RM_bytes_exact=True,canonical_not_written_by_metadata=True,original_parent_only_accounting=True,own_future_startup_final_behavior_not_assumed=True)
p=R/'E1_WAVE35_SECOND_BOUNDED_DISPATCH_METADATA_SYNCED.json';assert not p.exists();p.write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('CENTRAL_TOKEN',repr(io.E)).replace('ROOT_TOKEN',repr(ROOT)).replace('BUDGET_TOKEN',repr(io.B)))
  save('SECOND_DISPATCH_METADATA_SYNCED.json',v);print(json.dumps(dict(metadata_synced=True,root=ROOT,child=v['actual_child']['pid'])))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('SECOND_DISPATCH_METADATA_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_budget_write=True));raise
