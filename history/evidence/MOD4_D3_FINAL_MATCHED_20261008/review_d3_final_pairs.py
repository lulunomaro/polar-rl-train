"""Reuse the original independent facts reader on existing final D3 cases."""
from pathlib import Path
import ast,json,time,hashlib,sys,math,statistics
D=Path(__file__).resolve().parent;R=D/'reports';P=D.parent/'MOD4_D4_ACTION_QUEUE_COMPONENT_PREPARE_20261008'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
sys.path.insert(0,str(D.parent/'MOD4_S1A_MATCHED_EVALUATION_20261007/review_contracts'))
from scut_curriculum_gate_v4 import evidence
from world_progress_contract import target
source=D.parent/'MOD4_CLOSURE_EPISODE_CONTINUATION_20261008/review_block1_matched_scope.py'
tree=ast.parse(source.read_text(encoding='utf8'));facts_tree=ast.Module(body=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='facts'],type_ignores=[])
exec(compile(facts_tree,str(source),'exec'))
actual=read(P/'reports/ACTUAL_D3_BLOCKS_AND_D4_SOURCE.json');block=actual['blocks']['3'];row=block['receipt']
assert read(R/'D3_BLOCK3_FULL_CPU.json')['sha256']==row['checkpoint']['sha256']
ev=read(P/'reports/D3_EXISTING_ASYNC_CASES.json');jobs={j['id']:j for j in ev['jobs']}
assert not actual['attention'] and not ev['attention']
h=row['health'];assert h['version']==3 and h['integrity_task_reset_events']==h['unknown_task_reset_events']==0 and not h['nonfinite_observed'] and h['stop_reason'] is None
assert h['termination_reason_coverage_exact'] and h['actual_physics_callbacks']==h['expected_physics_callbacks']
report=dict(epoch=time.time(),scope='Same3060/2.5ms32-4/firstseed20261002/white_v3/noise-bias/0-10msfeedback/1500control15s; not all DR or seeds',block3=row,charged_once_seconds=block['charged_once_seconds'],CPU84_source234_19snapshot_verified=True,block2={},block3_candidate={},pairs=[],large_returned_files=[],new_GPU_PPO_or_budget_operation=0,original_reader_SHA256=hashlib.sha256(source.read_bytes()).hexdigest())
for kind in ('flat','spin','world'):
 pair={}
 for role,prefix,sha in [('block2','20-b2-','ded074be755d5320a4050f69753163800a409d6eaf077fb3b990b686d9547a61'),('block3_candidate','20-b3-',row['checkpoint']['sha256'])]:
  job='clk2500-closure-episode-d3-'+prefix+kind;j=jobs.get(job)
  if not j or not j['complete']:raise SystemExit('Existing final D3 '+kind+' pending; no new probe')
  folder=P/'reports/windows'/job;p=read(folder/'probe.json');m=read(folder/'manifest.json');res=read(folder/'result.json')
  assert res['exit_code']==0 and not res['errors'] and not res['error_files']
  assert p==j['probe'] and m==j['manifest'] and res==j['result']
  assert res['checkpoint']['sha256']==m['artifacts']['checkpoint']['sha256']==sha and res['checkpoint']['finite_tensors']==84
  assert m['steps']==p['steps']==res['steps']==1500 and p['seed']==m['seed']==res['seed']==20261002 and m['profile']==res['profile']=='white_v3'
  assert m['physics_dt_s']==res['physics_dt_s']==.0025 and m['control_dt_s']==.01 and m['solver_position']==32 and m['solver_velocity']==4
  assert m['artifacts']['runtime']['sha256']==res['runtime_archive_sha256']=='56f6ac8fe847b27e4a59e679b6dba99912652efe6b077d255f85754963fd359d'
  assert m['no_learning'] and not m['canonical_write_authority']
  for n in ('probe.json','result.json'):
   raw=(folder/n).read_bytes();assert hashlib.sha256(raw).hexdigest()==j['sha256'][n];report['large_returned_files'].append(dict(job=job,name=n,sha256=j['sha256'][n],bytes=len(raw)))
  report[role][kind]=facts(p,kind);pair[role]=(p,m,res)
 b,bm,_=pair['block2'];n,nm,_=pair['block3_candidate'];params=lambda p:p.get('initial_parameter_audit') or p.get('mild_initial_parameters')
 check=dict(kind=kind,initial_root_exact=b['reset_root_before_physics']==n['reset_root_before_physics'],initial_q_exact=b['reset_joint_pos_before_physics']==n['reset_joint_pos_before_physics'],parameters_exact=params(b)==params(n),probe_exact=b.get('probe_sha256')==n.get('probe_sha256'),runtime_exact=bm['artifacts']['runtime']==nm['artifacts']['runtime'],sensor_recipe_exact=b['sensor_recipe']==n['sensor_recipe'],feedback_delay_recipe_exact=b['feedback_delay_recipe']==n['feedback_delay_recipe'],actual_feedback_age_assignments_exact=b['sensor_actual_manager_audit']['actual_feedback_sample_apply']==n['sensor_actual_manager_audit']['actual_feedback_sample_apply'])
 assert all(v for k,v in check.items() if k!='kind');report['pairs'].append(check)
def summary(role):
 a=report[role];return dict(world={k:v for k,v in a['world'].items() if k in ('passed','count','max_abs_cross','along_range','directions')},straight=a['flat']['straight'],pure4pi=[{k:v for k,v in x.items() if k!='values'} for x in a['spin']['pure4pi']],closure_mm={k:a[k]['closure_mm'] for k in ('flat','spin','world')})
report['summary']={role:summary(role) for role in ('block2','block3_candidate')}
report['cost']=dict(candidate_process_wall_seconds=sum(jobs['clk2500-closure-episode-d3-20-b3-'+k]['result']['physics_process_wall_seconds'] for k in ('flat','spin','world')),candidate_transfer_seconds=sum(jobs['clk2500-closure-episode-d3-20-b3-'+k]['result']['transfer_seconds'] for k in ('flat','spin','world')))
report['decision']=dict(original6h_window_complete=True,block3_complete_learning_source_valid=True,D4_preflight_uses_already_reviewed27575_without_waiting=True,strict_world_facts_retained=True,no_graduation_percentage_threshold_created=True,not_dualseed_allprofile_D3_graduation=True,no_clock45min_repeat=True)
(R/'D3_MODEL28648_FINAL_MATCHED_REVIEW.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(dict(summary=report['summary'],cost=report['cost'],decision=report['decision'])))
