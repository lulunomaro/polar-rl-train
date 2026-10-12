import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'MOD4_E1_WAVE50_DIRECTION_SECOND_BOUNDED_20261012'))
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'MOD4_E1_WAVE50_EPISODE_DIRECTION_PREPARE_20261012'))
"""Read-only own386 candidate audit; complete cases only, no evaluation replay."""
from wave_direction_io import *
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
ROOT='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ROUTE_FIXTURE_REVIEWED_20261012'
def save(name,value):
 p=R/name;assert not p.exists();p.write_bytes(json.dumps(value,ensure_ascii=False,indent=2).encode());return p

import ast,numpy as np
sys.path.insert(0,str(W/'MOD4_E1_G1_ACTUAL_REVIEW_20261010'))
import review_actual_schema_checked as common
from review_second_candidate_actual import final_sensor_receipt_pair
from review_second_candidate_reset_schema_actual import reset_audit
read=lambda p:json.loads(p.read_bytes())
prepared=read(previous.old.PRIOR/'reports/WAVE50_WORLDMESH_QUERY_PREPARED.json')
hashfile=lambda p:H(p.read_bytes())
from route443_feedback_reset_schema import recipe_manager
node=next(n for n in ast.parse(common.oldterrain.read_text(encoding='utf8')).body if isinstance(n,ast.FunctionDef) and n.name=='terrain')
class NewProtocolOnly(ast.NodeTransformer):
 def visit_Constant(self,n):
  if n.value=='approved_E1_gentle_route_behavior_v1':n.value=prepared['protocol']
  return n
exec(compile(ast.fix_missing_locations(ast.Module(body=[NewProtocolOnly().visit(node)],type_ignores=[])),str(common.oldterrain)+'#unchanged50protocol','exec'))
node=next(n for n in ast.parse((W/'MOD4_E1_G2_20MM_SCOPE_PREPARE_20261010/review20mm_allowlist_actual.py').read_text(encoding='utf8')).body if isinstance(n,ast.FunctionDef) and n.name=='audit')
exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),'original-full-wave-contact-route-audit#unchanged','exec'))
sys.path.insert(0,str(previous.old.PRIOR/'wave50_worldmesh_scope'))
from g4_worldmesh_query_contract import expected_ground
def latest(glob):return max(R.glob(glob),key=lambda p:int(p.stem.rsplit('_',1)[1]))
def initial_legacy_pair(p,b):
 keys=('reset_root_before_physics','reset_joint_pos_before_physics','sensor_recipe','feedback_delay_recipe','physical_action_delay_recipe','spring_pressure_recipe','gas_damping_recipe','chassis_PD_recipe','physical_action_initial_episode_assignments','spring_pressure_initial_episode_assignments','gas_damping_initial_episode_assignments','chassis_PD_initial_episode_assignments')
 for k in keys:assert p[k]==b[k],k
 params=lambda x:x.get('initial_parameter_audit') or x.get('mild_initial_parameters')
 assert params(p)==params(b)
def terrain_case(p,row,jid):
 assert row['raw_SHA_exact'] and row['query_two_host_byteSHA_exact']
 g=p['geometry_recipe']['G4_geometry_change'];assert g['peak_to_trough_m']==.05 and g['other_four_families_unchanged'] and g['proportions_unchanged'] and g['not_RM70mm']
 s=p['route_scope'];orig=np.asarray(s['actual_world_ray_origins']);assert orig.shape==(80,35,3) and np.array_equal(orig,orig.astype(np.float32).astype(np.float64))
 x=orig[:,:,0]-np.asarray(s['tile_centers'])[:,None,0];assert np.array_equal(x,np.asarray(s['actual_canonical_ray_x']))
 qp=Path(row['query_evidence_local']);qi=s['query_worldmesh_evidence'];assert H(qp.read_bytes())==qi['sha256'] and qp.stat().st_size==qi['bytes']
 with np.load(qp,allow_pickle=False) as q:
  assert np.array_equal(q['actual_world_ray_origins'],orig) and np.array_equal(q['actual_canonical_ray_x'],x) and np.array_equal(q['actual_sampled_ground'],np.asarray(s['actual_sampled_ground']))
  tri=q['world_triangles'];assert tri.ndim==4 and tri.shape[0]==80 and tri.shape[2:]==(3,3)
  vertices=tri.reshape(-1,3);faces=np.arange(len(vertices)).reshape(-1,3);expected,receipts,_=expected_ground(vertices,faces,np.asarray(s['tile_centers']),orig)
  assert np.array_equal(expected,q['expected_actual_ground']) and np.array_equal(expected,np.asarray(s['expected_actual_sampled_ground'])) and receipts==s['world_mesh_receipts']
  error=float(np.max(abs(expected-q['actual_sampled_ground'])));assert error<=1e-6 and s['actual_query_ground_tolerance_m']==1e-6 and error==s['actual_query_height_error_m']
  ideal_diff=float(np.max(abs(q['actual_sampled_ground']-q['ideal_profile_ground'])));assert ideal_diff==s['ideal_profile_difference_m']
 a=audit(p,R/'cases'/jid);assert s['flat_support_margin_m']==.4 and p['geometry']['all_faces_and_winding_retained']
 c=read(max((previous.old.PRIOR/'reports').glob('WAVE50_WORLDMESH_ACTUAL_COLLECTED_[0-9]*.json'),key=lambda p:int(p.stem.rsplit('_',1)[1])))
 source=next(x['probe'] for x in c['cases'].values() if 'full_route_raw' in x['probe'])
 for k in ('initial','geometry','geometry_recipe','feedback_recipe','action_recipe','spring_recipe','gas_recipe','chassis_PD_recipe','body_names'):assert p[k]==source[k],('same50_source145',k)
 a['sensor_final_receipt_source145']=final_sensor_receipt_pair(p,source)
 a.update(actual_world_float32_query_identity_exact=True,all_actual_world_triangles_procedural_byteexact=True,query_NPZ_two_host_byteSHA_exact=True,independent_CPU_ground_error_m=error,ideal_profile_difference_m=ideal_diff,original_ground1e6_tolerance_passed=True,same50_source145_initial_root30q_parameters_recipes_assignments_exact=True)
 return a
def main():
 cp=latest('ROUTE443_CANDIDATE_COLLECTED_[0-9]*.json');v=read(cp);b=v['own']
 if b is None:print(json.dumps(dict(pending=True,own_final_absent=True)));return
 cpu=read(latest('ROUTE443_OWN_FORMAL_CPU_ACTUAL_[0-9]*.json'));assert cpu['passed'] and cpu['closeout_ready'] and cpu['actual_source_count']==443 and cpu['own_checkpoint']['sha256']==b['checkpoint']['sha256']
 assert not b['discarded_preflight'] and len(b['unique_completed_segment'])==1
 h=b['health'];assert h['control_steps']==b['actual_updates']*24 and h['actual_physics_callbacks']==h['expected_physics_callbacks']==h['control_steps']*4 and h['termination_reason_coverage_exact'] and h['truncation_reason_coverage_exact'] and not h['nonfinite_observed'] and h['stop_reason'] is None
 retention={};terr=None;matched={}
 for jid,row in v['cases'].items():
  p,m,r=row['probe'],row['manifest'],row['result'];assert r['phase']=='complete' and not r['exit_code'] and not r['errors'] and not r['error_files'] and not r['new_learning']
  assert r['checkpoint']['sha256']==m['artifacts']['checkpoint']['sha256']==b['checkpoint']['sha256'] and r['checkpoint']['finite_tensors']==b['checkpoint']['finite_tensors']==cpu['actual_finite_tensor_count']
  assert r['runtime_archive_sha256']==m['artifacts']['runtime']['sha256'] and r['steps']==m['steps']==p['steps']==1500 and m['no_learning'] and not m['canonical_write_authority']
  assert m['physics_dt_s']==.0025 and m['control_dt_s']==.01 and m['solver_position']==32 and m['solver_velocity']==4
  if 'full_route_raw' in p:
   assert p['checkpoint_sha256']==b['checkpoint']['sha256'] and r['runtime_archive_sha256']==prepared['package']['sha256'];terr=terrain_case(p,row,jid)
  else:
   assert p['checkpoint'].replace('\\','/').lower()==('D:/MOD4_async_eval/closure_episode_clock2500_v15/jobs/'+jid+'/checkpoint.bin').lower()
   kind=m['kind'];assert p['seed']==m['seed']==20261002 and m['profile']=='white_v3' and r['runtime_archive_sha256']=='8a964c1d0cfa291ea8faf72d978464daa8b2a8e90834554c435d528ffb222871'
   baseline=read(common.BASE/('clk2500-closure-episode-d3-115-e1-retention32053-'+kind)/'probe.json');initial_legacy_pair(p,baseline)
   f=W/'MOD4_E1_G3_COMMAND_RETENTION_PREPARE_20261010/reports/cases'/('clk2500-closure-episode-d3-129-e1-g3-command-retention-retention-'+kind)
   source,sm,sr=[read(f/n) for n in ('probe.json','manifest.json','result.json')]
   assert sr['phase']=='complete' and not sr['exit_code'] and not sr['errors'] and not sr['error_files'] and sr['checkpoint']['sha256']==sm['artifacts']['checkpoint']['sha256']=='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e'
   initial_legacy_pair(p,source)
   a=p['physical_action_delay_audit'];assert a['callback_counts']==dict(legs=6000,wheels=6000) and a['application_formula_max_error']==0
   assert p['spring_pressure_audit']['actual_PhysX_buffer_implicit_model_exact'] and p['gas_damping_audit']['actual_PhysX_buffer_implicit_model_exact'] and p['chassis_PD_audit']['parameter_auditor']['actual_parameters_pass']
   resets=reset_audit(p);age=p['sensor_actual_manager_audit']['actual_feedback_sample_apply']==baseline['sensor_actual_manager_audit']['actual_feedback_sample_apply']
   if not age:assert resets['episode_increment_sum']>0
   retention[kind]=dict(candidate=common.facts(p,kind),source129=common.facts(source,kind),baseline115=common.facts(baseline,kind),initial30q_parameters_recipes_assignments_exact=True,reset_audit=resets,feedback_age_pair_exact=age)
  matched[jid]=dict(result_SHA_manifest_SHA_own_formal_SHA_exact=True,own_finite_tensor_schema_exact=True,two_host_probe_result_byteSHA_exact=True)
 compact=lambda x:{k:x[k] for k in ('straight','pure4pi','passed','count','max_abs_cross','along_range','closure_mm','original_flags') if k in x}
 out=dict(epoch=time.time(),collection=str(cp),own=b,terrain=terr,retention=retention,matched_cases=matched,summary=dict(terrain=terr['groups'] if terr else None,retention={k:{role:compact(x[role]) for role in ('source129','candidate')} for k,x in retention.items()}),pending=v['pending'],review_complete=terr is not None and set(retention)=={'flat','spin','world'} and not v['pending'],original_flags_failed_valid_prefixes_and_strictfalse_preserved=True,no_scope_graduation_from_partial_or_PPO_fullsave=True,no_permanent_antiforgetting_RM70mm_MoE_claim=True,no_GPU_PPO_queue_budget_write=True)
 p=save('ROUTE443_CANDIDATE_ACTUAL_REVIEW_'+str(time.time_ns())+'.json',out);print(json.dumps(dict(report=str(p),summary=out['summary'],review_complete=out['review_complete'],pending=out['pending'])))
if __name__=='__main__':
 try:main()
 except BaseException:save('CANDIDATE_RESET_SCHEMA_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),read_only=True,original_sources_and_results_preserved=True,no_GPU_or_budget_replay=True));raise
