"""Select a fully reviewed stable source for the existing CPU-only publisher.

This is an evidence admission, not a training restart or a GPU test.
"""
from pathlib import Path
import hashlib,json,sys,time

D=Path(__file__).resolve().parent;R=D/'reports';B=D.parent
read=lambda p:json.loads(p.read_text(encoding='utf8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (R/'D7_BLOCK1_D9_SOURCE_SELECTED.json').exists()
master=sha(B/'polar-rl-train/history/plans/MOD4_MOE_MASTER_PLAN.md')
assert master=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
a=read(B/'MOD4_D7_FULL_CONTRACT_20261009/reports/D7_CURRENT_ACTUAL.json')
v=read(B/'MOD4_D7_FULL_CONTRACT_20261009/reports/D7_ACTUAL_BASELINE_SCOPE_REVIEW.json')
assert a['attention'] is None and a['no_GPU_PPO_or_budget_write']
assert time.time()-a['epoch']<1800
row=a['completed']['d7_stable_block1_PASSED'];h=row['checkpoint']['sha256']
assert h=='b10958d2a8631b12c0f9502bf7fa9230d9a7a1ae9863443bb68388604bed61f8'
assert row['checkpoint']['finite_tensors']==94 and not row['discarded_preflight']
health=row['health'];pid=row['own_PID_bound_receipt']['pid']
assert pid==health['pid']==1516991
assert health['termination_reason_coverage_exact'] and not health['nonfinite_observed']
assert health['integrity_task_reset_events']==health['unknown_task_reset_events']==0 and health['stop_reason'] is None
assert health['actual_physics_callbacks']==health['expected_physics_callbacks']==health['control_steps']*4
assert row['actual_updates']*24==health['control_steps']
assert row['actual_environment_steps']==health['control_steps']*20000
seg=row['unique_completed_segment'];assert len(seg)==1 and seg[0]['pid']==pid
assert seg[0]['accounted_through_epoch']==seg[0]['ended_epoch']
duration=seg[0]['ended_epoch']-seg[0]['started_epoch']
cases=v['cases']['99-d7-com-pd-b1'];base=v['cases']['98-d7-com-pd-anchor']
assert set(cases)=={'flat','spin','world'} and len([x for x in v['pairs'] if x['label']=='99-d7-com-pd-b1'])==3
paired={}
for kind,c in cases.items():
 assert c['source_SHA']==h and c['identity']==base[kind]['identity']
 assert c['facts']['v4']['pass_'],c['facts']
 jid='clk2500-closure-episode-d3-99-d7-com-pd-b1-'+kind
 folder=B/'MOD4_D7_FULL_CONTRACT_20261009/reports/stage_scope'/jid
 paired[kind]=dict(job_id=jid,source_sha256=h,probe_sha256=sha(folder/'probe.json'),result_sha256=sha(folder/'result.json'),manifest_sha256=sha(folder/'manifest.json'),full_root_q_actual_parameters_recipes_assignments_exact=True,task_model_data_scope_accepted=True)
world=cases['world']['facts'];assert world['passed']==world['count']==64
assert all(x['passed']==x['count']==8 for x in cases['spin']['facts']['pure4pi'])
assert all(c['error']<=b['error'] for c,b in zip(cases['flat']['facts']['straight'],base['flat']['facts']['straight']))
assert world['max_abs_cross']<base['world']['facts']['max_abs_cross']
selected=dict(epoch=time.time(),behavior_review_complete=True,source_count=277,snapshot_count=44,finite_tensors=94,source=row['checkpoint'],own_PID_bound_receipt=row['own_PID_bound_receipt'],unique_completed_segment=seg,paired_cases=paired,scope=v['scope'],selection_basis='Actual complete paired first D7 stable block; both straight errors and whole-circle cross improved; world64/64 and pure left/right8/8; not directory-max/preflight/reward selection',firstseed_white3_only=True,development_not_heldout=True,no_active_training_source_switch=True)
sys.path.insert(0,str(B/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect();E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports';root='/home/egde/rl_candidates/MOD4_D9_COMBINATION_PREPARE_20261009/reports'
try:
 with c.open_sftp() as f:
  fetched={}
  for name in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOE_PLAN_EXECUTION_CURRENT.json','LATEST_HANDOFF.md','D6_FINAL_D7_BASELINE_D9_PREPARATION_REPORT.md','D6_FINAL_D7_BASELINE_D9_COMPACT.json','D6_FINAL_D7_BASELINE_D9_GIT_RECORDED.json','D9_PREPARATION_METADATA_SYNCED.json','D6_FINAL_MATCHED_SCOPE_REVIEW.json','D7_ACTUAL_BASELINE_SCOPE_REVIEW.json','D9_NOMINAL_ACTUAL_SDK_REVIEW.json','D9_PUBLICATION_CURRENT_ACTUAL.json','MOD4_RM_TERRAIN_SPIN_ENTRY_LIP_ANNOTATION.json','MOD4_RM_TERRAIN_SPIN_ENTRY_LIP_ANNOTATION.md'):
   raw=f.open(E+'/'+name).read();(R/('SELECTION_READ_'+name)).write_bytes(raw);fetched[name]=dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
  approval=read(R/'SELECTION_READ_PLAN_APPROVAL.json');assert approval['approved_plan_sha256']==master and 'S2' in approval['allowed_stages']
  native='/home/egde/rl_candidates/MOD4_D7_FULL_CONTRACT_20261009'
  m=json.loads(f.open(row['run']+'/run_manifest.json').read());freeze=json.loads(f.open(native+'/reports/SOURCE_FREEZE.json').read())
  rolling=json.loads(f.open(row['run']+'/rolling_source_freeze.json').read())
  assert m['source_map']==freeze['sha256']==rolling['sha256'] and len(m['source_map'])==277 and len(m['src_sha256'])==44
  nativepassed=json.loads(f.open(native+'/reports/d7_stable_block1_PASSED.json').read());assert nativepassed==row
  q=root+'/SELECTED_D7_BEHAVIOR_SOURCE.json'
  try:f.stat(q)
  except FileNotFoundError:pass
  else:raise RuntimeError('Selector already exists; do not overwrite or re-admit')
  raw=json.dumps(selected,indent=2).encode('utf8');tmp=q+'.selected_block1_partial'
  with f.open(tmp,'wb') as out:out.write(raw)
  f.posix_rename(tmp,q);assert f.open(q).read()==raw
  (R/'SELECTED_D7_BEHAVIOR_SOURCE.json').write_bytes(raw)
  compact=dict(epoch=time.time(),master_SHA_unchanged=master,source=selected,training_health=health,actual_updates=row['actual_updates'],actual_control_steps=health['control_steps'],actual_environment_steps=row['actual_environment_steps'],actual_callbacks=health['actual_physics_callbacks'],unique_elapsed_seconds=duration,ordinary_event_rate_per_million_environment_control_steps=1e6*health['ordinary_episode_reset_events']/row['actual_environment_steps'],baseline_summary=v['summary']['98-d7-com-pd-anchor'],candidate_summary=v['summary']['99-d7-com-pd-b1'],actual_main_owner=a['actual_owner'],actual_main_guardian=a['actual_guardian'],actual_main_child=a['actual_child'],main_source_preserved=a['state']['source'],budget_snapshot=a['budget'],tail_adjusted_remaining_seconds_snapshot=a['actual_tail_adjusted_remaining_seconds'],new_GPU_PPO_canonical_transactions=0,no_repeated_clock45min_or_PPO=True,read_before_selection=fetched,large_evidence_sha256=dict(own_actual=sha(B/'MOD4_D7_FULL_CONTRACT_20261009/reports/D7_CURRENT_ACTUAL.json'),matched_review=sha(B/'MOD4_D7_FULL_CONTRACT_20261009/reports/D7_ACTUAL_BASELINE_SCOPE_REVIEW.json')),all_original_flags_raw_and_legacy_single_peak_false_preserved=True)
  (R/'D7_BLOCK1_D9_SOURCE_SELECTED.json').write_text(json.dumps(compact,indent=2),encoding='utf8')
  print(json.dumps(dict(selected_actual_source=h,own_pid=pid,updates=row['actual_updates'],steps=row['actual_environment_steps'],callbacks=health['actual_physics_callbacks'],ordinary=health['ordinary_episode_reset_events'],closure_peak_mm=1000*health['max_closure_error_m'],unique_elapsed_seconds=duration,baseline=compact['baseline_summary'],candidate=compact['candidate_summary'],main_training_unchanged=True)))
finally:c.close()
