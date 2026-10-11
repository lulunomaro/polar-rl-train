"""Close reviewed143 metadata and publish one new approved50mm frozen scope, never old training."""
from second_io import *
sys.path.insert(0,str(W/'MOD4_E1_SLOPE5_INDEPENDENT_PREPARE_20261011'))
from slope8_worker_actual import worker_actual
from curb_io import WIN
import re
def main():
 assert not (R/'WAVE50_FROZEN_PUBLISHED.json').exists()
 cpu=sorted(R.glob('SECOND_OWN_FORMAL_CPU_ACTUAL_[0-9]*.json'))[-1];review=sorted(R.glob('WAVE143_REVIEW_[0-9]*.json'))[-1];collection=sorted(R.glob('WAVE143_COLLECTED_[0-9]*.json'))[-1];selected=sorted(R.glob('WAVE143_SELECTED_SOURCE_REVIEW_[0-9]*.json'))[-1];trace=sorted(R.glob('SECOND_FULL_TRAINING_TRACE_ACTUAL_[0-9]*.json'))[-1];actual=sorted(R.glob('SECOND_ACTUAL_[0-9]*.json'))[-1]
 proof=json.loads(cpu.read_bytes());decision=json.loads((R/'WAVE143_COMPLETE_OBSERVED_SCOPE_DECISION.json').read_bytes());prepared=json.loads((R/'WAVE50_COMPONENT_FROZEN_PREPARED.json').read_bytes())
 assert proof['passed'] and proof['closeout_ready'] and decision['observed35mm_complete_ten_wave_scope_accepted_and_frozen']
 assert H(Path(prepared['package']['path']).read_bytes())==prepared['package']['sha256']
 uploads={'E1_WAVE35_SECOND_BOUNDED_OWN_FINAL_CPU_VERIFIED.json':cpu,'E1_WAVE35_SECOND_BOUNDED_FORMAL_FINAL_ACTUAL_REVIEW.json':review,'E1_WAVE35_SECOND_BOUNDED_FORMAL_FINAL_CURRENT_ACTUAL.json':actual,'E1_WAVE35_143_COMPLETE_ACTUAL_COLLECTION.json':collection,'E1_WAVE35_143_COMPLETE_ACTUAL_REVIEW.json':review,'E1_WAVE35_143_SELECTED129_MATCHED_REVIEW.json':selected,'E1_WAVE35_143_DIRECT142_MATCHED_REVIEW.json':R/'WAVE143_DIRECT142_MATCHED_FULL_REVIEW.json','E1_WAVE35_143_COMPLETE_OBSERVED_SCOPE_DECISION.json':R/'WAVE143_COMPLETE_OBSERVED_SCOPE_DECISION.json','E1_WAVE35_SECOND_COMPLETE_DYNAMIC_FAMILY_TRACE_REVIEW.json':trace,'E1_WAVE35_143_LEGACY_SPIN_RESET_READER_SCHEMA_REVIEW.json':R/'WAVE143_LEGACY_SPIN_RESET_READER_SCHEMA_REVIEW.json','E1_WAVE50_COMPONENT_FROZEN_PREPARED.json':R/'WAVE50_COMPONENT_FROZEN_PREPARED.json','E1_WAVE50_AUTHORED_JOIN_QUERY_CPU_REVIEW.json':R/'WAVE50_AUTHORED_JOIN_QUERY_CPU_REVIEW.json'}
 n,w=io.connect_both()
 try:
  with n.open_sftp() as f:
   for name,p in uploads.items():io.put(f,io.E+'/reports/'+name,p.read_bytes())
  authority=run(n,r'''from pathlib import Path
import json,time,os,hashlib,fcntl
E=Path(CENTRAL_TOKEN);R=E/'reports';D=Path(ROOT_TOKEN);B=Path(BUDGET_TOKEN);j=lambda p:json.loads(p.read_bytes())
v=j(R/'E1_WAVE35_SECOND_BOUNDED_OWN_FINAL_CPU_VERIFIED.json');dec=j(R/'E1_WAVE35_143_COMPLETE_OBSERVED_SCOPE_DECISION.json');assert v['passed'] and v['closeout_ready'] and dec['observed35mm_complete_ten_wave_scope_accepted_and_frozen']
st=j(D/'reports/E1_STATE.json');passed=j(D/'reports/e1_WAVE35_second_bounded_observation_PASSED.json');assert st['phase']=='E1_WAVE35_second_bounded_saved_review_ready' and st['child'] is None
assert passed['checkpoint']['sha256']==v['own_checkpoint']['sha256']==dec['own_checkpoint']['sha256'] and passed['source_count']==369 and not passed['discarded_preflight']
cp=Path(passed['checkpoint']['path']);assert cp.stat().st_size==17615538 and hashlib.sha256(cp.read_bytes()).hexdigest()==passed['checkpoint']['sha256']
budget=B.read_bytes();b=json.loads(budget);assert b['active_segment'] is None and b['authorized_training_seconds']==1188000 and len(b['budget_extensions'])==7
assert passed['unique_completed_segment']==[x for x in b['completed_segments'] if x['pid']==2932922] and len(passed['unique_completed_segment'])==1
locators=[st['owner'],j(D/'reports/E1_GUARDIAN_STARTED.json'),dict(pid=2932922,start_ticks=88740346)];rows=[]
for loc in locators:
 p=Path('/proc')/str(loc['pid']);a=None
 if p.exists():
  s=(p/'stat').read_text().split(') ',1)[1].split();a=dict(state=s[0],start_ticks=int(s[19]));assert a['state']=='Z' or a['start_ticks']!=loc['start_ticks']
 rows.append(dict(locator=loc,actual=a))
locks=[]
for p in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(str(p))
protected={name:(R/name).read_bytes() for name in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json')}
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();c=json.loads(before);rev=c['terrain_subexpert_revision004'];scope=rev['wave35_second_bounded_scope'];assert rev['approved'] and scope['root']==str(D)
scope.update(phase=st['phase'],formal_final_pending=False,full_candidate_behavior_pending=False,full_training_trace_pending=False,actual_own_checkpoint=dec['own_checkpoint'],actual_own_final_CPU_report=str(R/'E1_WAVE35_SECOND_BOUNDED_OWN_FINAL_CPU_VERIFIED.json'),complete143_collection=str(R/'E1_WAVE35_143_COMPLETE_ACTUAL_COLLECTION.json'),complete143_review=str(R/'E1_WAVE35_143_COMPLETE_ACTUAL_REVIEW.json'),complete143_decision=str(R/'E1_WAVE35_143_COMPLETE_OBSERVED_SCOPE_DECISION.json'),actual_forward=27,actual_reverse=27,observed35mm_scope_accepted_and_frozen=True,full_same_scope_repair_complete=True,no_automatic_third_block=True,own_diagnostic_spin_env8_failure_retained=True,actual_training_trace=str(R/'E1_WAVE35_SECOND_COMPLETE_DYNAMIC_FAMILY_TRACE_REVIEW.json'))
rev['active_next_expert']='E1_WAVE';rev['active_next_phase']='WAVE50_new_frozen_scope_CPU_verified_before_publication';assert 'wave50_frozen_next_scope' not in rev
rev['wave50_frozen_next_scope']=dict(source_own369_checkpoint_SHA=dec['own_checkpoint']['sha256'],CPU_component_prepared=True,physical_result_pending=True,frozen_job_not_published=True,learning_executor_not_deployed=True,geometry_peak_to_trough_m=.05,CPU_report=str(R/'E1_WAVE50_COMPONENT_FROZEN_PREPARED.json'),query_report=str(R/'E1_WAVE50_AUTHORED_JOIN_QUERY_CPU_REVIEW.json'),no_PPO_until_actual_need_and_new_scope_admission=True)
assert p.read_bytes()==before;tmp=p.with_name(p.name+'.COMPLETE143-'+str(time.time_ns()));tmp.write_text(json.dumps(c,ensure_ascii=False,indent=2));os.replace(tmp,p)
assert all((R/name).read_bytes()==raw for name,raw in protected.items()) and B.read_bytes()==budget
z=dict(epoch=time.time(),metadata_synced=True,actual_processes=rows,two_actual_OS_locks_free=locks,own_final=passed['checkpoint'],unique_completed_segment=passed['unique_completed_segment'],canonical_SHA=hashlib.sha256(budget).hexdigest(),remaining_seconds=b['authorized_training_seconds']-b['charged_training_seconds'],active_segment=None,source_count=369,master_approval_tracks_RM_bytes_exact=True,canonical_not_written_by_metadata=True)
p=R/'E1_WAVE35_143_COMPLETE_AND_WAVE50_CPU_METADATA_SYNCED.json';assert not p.exists();p.write_text(json.dumps(z,indent=2));print(json.dumps(z))
'''.replace('CENTRAL_TOKEN',repr(io.E)).replace('ROOT_TOKEN',repr(ROOT)).replace('BUDGET_TOKEN',repr(io.B)))
  save('COMPLETE143_AND_WAVE50_CPU_METADATA_SYNCED.json',authority)
  with n.open_sftp() as nf,w.open_sftp() as wf:
   wa=worker_actual(w,wf);assert wa['attention'] is None and not [p for p in wa['processes'] if 'frozen_history_' in p.get('CommandLine','')]
   listings=dict(queue=nf.listdir(io.E+'/eval_queue'),results=nf.listdir(io.E+'/eval_results'),jobs=wf.listdir(WIN+'/jobs'))
   numbers=[int(m.group(1)) for names in listings.values() for name in names if (m:=re.match(r'clk2500-closure-episode-d3-(\d+)-',name))]
   number=max([143]+numbers)+1;jid=f'clk2500-closure-episode-d3-{number}-e1-wave50-source369-actualray-approach040-fullroute-flat'
   assert all(not any(name.startswith(f'clk2500-closure-episode-d3-{number}-') for name in names) for names in listings.values())
   prior=json.loads(collection.read_bytes());job=copy_job=next(x['manifest'] for x in prior['cases'].values() if 'full_route_raw' in x['probe']);job=json.loads(json.dumps(job))
   cp=job['artifacts']['checkpoint'];raw=nf.open(cp['path']).read();assert len(raw)==cp['bytes']==17615538 and H(raw)==cp['sha256']==decision['own_checkpoint']['sha256']
   pkg=prepared['package'];remote=io.E+'/artifacts/'+Path(pkg['path']).name;assert Path(remote).name not in nf.listdir(io.E+'/artifacts')
   nf.put(pkg['path'],remote+'.partial');assert H(nf.open(remote+'.partial').read())==pkg['sha256'];nf.rename(remote+'.partial',remote)
   job.update(job_id=jid,published_epoch=time.time(),protocol=prepared['protocol'],role='Approved RM003 single35to50mm frozen scope from full143 accepted own369',actual_behavior_scope='Derived50mm peak-to-trough complete ten-wave2.406422727m / .4m approach / both-wheels200mm aftersupport /15s, frozen only; not actual RM70mm',source369_complete143_selected=True,source_saved_terraincommand_remains35mm=True,frozen_only_source_fullstate_not_restored=True,learning_executor_not_deployed=True,revision004_approval_SHA=H(nf.open(io.E+'/reports/MOE_TERRAIN_SUBEXPERT_REVISION_004_APPROVAL.json').read()))
   job['artifacts']['runtime']=dict(path=remote,bytes=pkg['bytes'],sha256=pkg['sha256']);budget=nf.open(io.B).read();assert H(budget)==authority['canonical_SHA']
   raw=json.dumps(job,indent=2).encode();path=io.E+'/eval_queue/'+jid+'.json'
   with nf.open(path+'.partial','wbx') as f:f.write(raw)
   assert nf.open(path+'.partial').read()==raw;nf.rename(path+'.partial',path);assert nf.open(path).read()==raw and nf.open(io.B).read()==budget
   receipt=dict(epoch=time.time(),trial_id='E1-WAVE50-FROZEN-NEW-SCOPE-PUBLISH',jobs=[job],number=number,package=pkg,actual_authority=authority,actual_worker=wa,actual_queue_result_job_number_unused=True,queue_manifest_bytes_exact=True,canonical_bytes_preserved=True,no_4090_launch_PPO_or_learning_executor=True,source35mm_saved_state_and_other_experts_unchanged=True,full_frozen_actual_review_pending=True,new_budget_seconds=0)
   p=save('WAVE50_FROZEN_PUBLISHED.json',receipt);io.put(nf,io.E+'/reports/E1_WAVE50_FROZEN_PUBLISHED.json',p.read_bytes())
  print(json.dumps(dict(published=True,job_id=jid,number=number,source_SHA=cp['sha256'],package_SHA=pkg['sha256'],no_PPO=True)))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('COMPLETE143_NEW50_SYNC_PUBLISH_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_blind_old_once_replay=True));raise
