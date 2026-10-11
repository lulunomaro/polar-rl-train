"""CAS new Wave scope metadata only; never write the training ledger or other weights."""
from wave_io import *
def main():
 actualpath=sorted(R.glob('WAVE_EXPOSURE_ACTUAL_[0-9]*.json'))[-1];actual=json.loads(actualpath.read_bytes())
 assert actual['actual_parent'] and not actual['attention'] and actual['actual_state'] and actual['actual_state'].get('child')
 files={'E1_WAVE35_EXPOSURE_TARGET_CPU_VERIFIED.json':R/'WAVE_TARGET_CPU_PASSED.json',
  'E1_WAVE35_EXPOSURE_REUSED_ACTUAL_CONTRACTS.json':R/'WAVE_ACTUAL_SCOPE_REUSE_VERIFIED.json',
  'E1_WAVE35_EXPOSURE_DISPATCH_ACTUAL_RECEIPT.json':R/'WAVE_DISPATCH_ACTUAL_RECEIPT.json',
  'E1_WAVE35_EXPOSURE_DISPATCH_CURRENT_ACTUAL.json':actualpath,
  'E1_WAVE35_EXPOSURE_DURATION_DECISION.json':R/'WAVE_EXPOSURE_DURATION_DECISION_AFTER_CACHE.json',
  'E1_WAVE35_PIP_HTTP_CACHE_RECLAIM_ACTUAL.json':R/'WAVE_CACHE_RECLAIM_ACTUAL.json'}
 n,w=io.connect_both()
 try:
  with n.open_sftp() as f:
   for name,p in files.items():
    target=io.E+'/reports/'+name;raw=p.read_bytes()
    try:existing=f.open(target,'rb').read()
    except FileNotFoundError:io.put(f,target,raw)
    else:assert existing==raw
  v=run(n,r'''from pathlib import Path
import json,time,os,sys,hashlib
E=Path(CENTRAL_TOKEN);R=E/'reports';D=Path(ROOT_TOKEN);B=Path(BUDGET_TOKEN);j=lambda p:json.loads(p.read_bytes());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));import supervise_wave35_exposure_005_once as own
cpu=j(R/'E1_WAVE35_EXPOSURE_TARGET_CPU_VERIFIED.json');receipt=j(R/'E1_WAVE35_EXPOSURE_DISPATCH_ACTUAL_RECEIPT.json');st=j(D/'reports/E1_STATE.json')
assert cpu['passed'] and cpu['source_count']==368 and cpu['source']['sha256']==own.SOURCE_SHA
assert st['expert']=='E1_WAVE' and st['owner']['pid']==receipt['controller']['pid']
parent=own.identity(st['owner']['pid']);child=own.identity(st['child']['pid']);assert parent and child and parent['start_ticks']==st['owner']['start_ticks'] and child['start_ticks']==st['child']['start_ticks']
b=j(B);assert b['active_segment']['pid']==child['pid'] and b['authorized_training_seconds']==1188000 and len(b['budget_extensions'])==7
protected={name:(R/name).read_bytes() for name in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json')}
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();c=json.loads(before);rev=c['terrain_subexpert_revision004'];assert rev['approved'] and rev['active_next_expert']=='E1_WAVE'
rev['wave35_exposure_repair_next_scope'].update(root=str(D),source_count=368,phase=st['phase'],actual_state=st,
 new_implementation_targetCPU_CUDA_PPO_not_yet_deployed=False,target_CPU_passed=True,formal_dispatched=True,formal_final_pending=True,
 source_selected_SHA=own.SOURCE_SHA,target_seconds=1800,duration_only_axis=True,candidate_number=142,
 target_CPU_report=str(R/'E1_WAVE35_EXPOSURE_TARGET_CPU_VERIFIED.json'),dispatch_receipt=str(R/'E1_WAVE35_EXPOSURE_DISPATCH_ACTUAL_RECEIPT.json'),
 actual_current=str(R/'E1_WAVE35_EXPOSURE_DISPATCH_CURRENT_ACTUAL.json'),new_own_CUDA_startup_health_and_complete_behavior_required=True,
 no_automatic_more_PPO_or_50mm=True)
rev['active_next_phase']=st['phase'];assert p.read_bytes()==before;tmp=p.with_name(p.name+'.WAVE35-'+str(time.time_ns()));tmp.write_text(json.dumps(c,ensure_ascii=False,indent=2));os.replace(tmp,p)
p=R/'LATEST_HANDOFF.md';before=p.read_bytes();message='\n\nActual newWave35 source368 isolatedroot '+str(D)+' CPU102 warmstart reviewed1293c97, old366 complete startup/SDK/native/small/big/sourcefreeze exact reused; durationonly1800s bounded004005 block dispatched actualparent '+str(parent['pid'])+' child '+str(child['pid'])+'. Allgeometry/reset/commands12to16s/episode20s/rewardLRDRclockhardware unchanged. OwnsameG3samecommand CPUCUDA startup/health/fullsave/PID/unique segment and newunused142 completefourcase required, no automaticmorePPO/50mm/globalgraduation. Old131 unqualified22/25of27 and old2b4 frozen evidence retained; E0/CURB20 accepted7b/SLOPE24b/player untouched, gateuntrained. NewpreGPU resource guard rejected before rootcreation due2.5GB systemdisk; oldreproducible7day pipHTTPdownloads12.428GB reclaimed withactualpath-size-SHA, no trial/weight/installedenv/canonical touched,14.924GB afterward. Originalrejection/duplicateimmutablelocaldecision error/source preserved. No SDK/native/PPOpreflight/clock/oldonce or budget extension replay; parent alone canonicalloadlearnsaveexit. HourlyACTIVE monitor and allsavedreports/errors/sync/Gitreceipts supplementrequired.\n'
assert p.read_bytes()==before;tmp=p.with_name(p.name+'.WAVE35-'+str(time.time_ns()));tmp.write_bytes(before+message.encode());os.replace(tmp,p)
assert all((R/name).read_bytes()==raw for name,raw in protected.items())
v=dict(epoch=time.time(),metadata_synced=True,root=str(D),source_count=368,actual_parent=parent,actual_child=child,actual_state=st,
 master_approval_tracks_RM_bytes_exact=True,canonical_not_written_by_metadata=True,original_parent_only_accounting=True,own_future_startup_final_behavior_not_assumed=True)
out=R/'E1_WAVE35_EXPOSURE_DISPATCH_METADATA_SYNCED.json';assert not out.exists();out.write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('CENTRAL_TOKEN',repr(io.E)).replace('ROOT_TOKEN',repr(ROOT)).replace('BUDGET_TOKEN',repr(io.B)))
  save('WAVE_DISPATCH_METADATA_SYNCED.json',v);print(json.dumps(dict(metadata_synced=True,root=ROOT,actual_child=v['actual_child']['pid'])))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('WAVE_DISPATCH_METADATA_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_training_or_budget_mutation=True));raise
