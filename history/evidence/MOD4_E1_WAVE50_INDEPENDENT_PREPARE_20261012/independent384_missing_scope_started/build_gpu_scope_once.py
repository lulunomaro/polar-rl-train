"""Build only the new missing50mm admission scope; no old executable replay."""
from wave50_io import *
import ast
P=D/'payload'
S=W/'MOD4_E1_SLOPE5_INDEPENDENT_PREPARE_20261011'

def replace_function(text,name,new):
 node=next(x for x in ast.parse(text).body if isinstance(x,ast.FunctionDef) and x.name==name)
 lines=text.splitlines(keepends=True);return ''.join(lines[:node.lineno-1])+new.rstrip()+'\n'+''.join(lines[node.end_lineno:])

def main():
 assert not P.exists();P.mkdir();C=P/'isaac/mod4';C.mkdir(parents=True)
 for q in (PRIOR/'wave50_learning_CPU_payload').iterdir():
  if q.is_file():(C/q.name).write_bytes(q.read_bytes())
 mapping={'slope5_geometry':'g4_cad_wave_geometry','slope5_profile.json':'g4_cad_profile.json','slope5_current_state':'g4_current_state','slope5_retention_runtime':'g4_retention_runtime','slope5_command_migration':'g4_command_migration','slope5_full_checkpoint':'g4_full_checkpoint','slope5_fullsave_cpu':'g4_fullsave_cpu','SLOPE5':'WAVE50','SLOPE':'WAVE50','slope5':'wave50','slope':'wave50'}
 def convert(t):
  for a,b in mapping.items():t=t.replace(a,b)
  return t
 workers=[(S/'snapshot_reviewed_payload/isaac/mod4/train_slope5_snapshot_reviewed_resume_ppo.py','train_wave50_full_resume_ppo.py'),(S/'payload/isaac/mod4/train_slope5_fresh_preflight_ppo.py','train_wave50_fresh_preflight_ppo.py'),(S/'payload/isaac/mod4/probe_slope5_fresh_process_full_resume.py','probe_wave50_fresh_process_full_resume.py')]
 for ref,name in workers:
  t=convert(ref.read_text()).replace("'g4_cad_wave_geometry.py','g4_cad_profile.json'","'g4_cad_wave_geometry.py','g4_cad_profile.json'")
  if name!='probe_wave50_fresh_process_full_resume.py':
   anchor="    manifest['actual_retained_command_scope']=env.command_manager.get_term('twist').audit_retention()"
   assert t.count(anchor)==1
   t=t.replace(anchor,"    env.command_manager.get_term('twist')._write_dynamic(torch.arange(env.num_envs,device=env.device))\n"+anchor)
   t=t.replace("for name in ('g4_command_migration.py','g4_full_checkpoint.py'):","for name in ('g4_command_migration.py','g4_full_checkpoint.py','g4_fullsave_cpu.py','g4_sdk_placement.py','wave50_fullscope_source_guard.py'):")
  if name=='train_wave50_full_resume_ppo.py':
   # The corrected404 file name is the executing new worker, never a copied old entry.
   t=t.replace('train_wave50_snapshot_reviewed_resume_ppo.py',name)
  (C/name).write_text(t,encoding='utf8')
 placement='''"""Diagnostic SDK placement only; original production reset/math untouched."""
import json,numpy as np,torch
from pathlib import Path
def prepare(env):
 rows=env.scene.terrain.retention_assignment;chosen=[]
 for i,row in enumerate(range(15,25)):
  candidates=sorted([x for x in rows if x['row']==row and x['family']=='random_uniform_for_rm' and not x['actual_mesh_flat']],key=lambda x:x['column'])
  assert len(candidates)==6;chosen.append(candidates[i%2])
 centers=np.array([[(x['bounds'][0][k]+x['bounds'][1][k])*.5 for k in (0,1)] for x in chosen])
 from g4_cad_wave_geometry import profile
 half=profile()['span_m']*.5;side=np.where(np.arange(10)%2==0,-1.,1.);xy=centers.copy();xy[:,0]+=side*(half+.8)
 points=env._rough_probe_bank['points'].cpu().numpy();extent=np.max(abs(points[:,:2]),axis=0)
 for i,x in enumerate(chosen):
  lo=np.array(x['bounds'][0][:2]);hi=np.array(x['bounds'][1][:2]);assert np.all(xy[i]-extent>lo) and np.all(xy[i]+extent<hi)
 assert .8-extent[0]>=.4 and np.unique(xy,axis=0).shape[0]==10
 actual=torch.as_tensor(xy,device=env.device,dtype=torch.float32)
 env.scene.env_origins[:,:2]=actual;env.scene.terrain.env_origins[:,:2]=actual
 return dict(chosen_actual_assignments=chosen,centers=centers.tolist(),actual_requested_starts=actual.cpu().tolist(),side=side.tolist(),full_bank_extent_xy=extent.tolist(),front_flat_clearance_m=float(.8-extent[0]),actual10G4_cells=True,two_front_support_sides=True,assignment_sha256=env.scene.terrain.retention_assignment_sha)
def verify(env,placement):
 root=env.scene['robot'].data.root_pos_w[:,:2];expected=torch.tensor(placement['actual_requested_starts'],device=env.device,dtype=root.dtype)
 assert torch.equal(root,expected) and torch.equal(env._rough_spawn_xy,expected)
 from e1_full_pose_reset import query
 ray=query(env);p=env._rough_probe_bank['points'];starts=p[None,:,:].repeat(10,1,1);starts[:,:,:2]+=root[:,None,:];starts[:,:,2]=float(ray.geometry.vertices[:,2].max())+2.
 out=ray.cast(starts.contiguous(),10.);assert out['hit'].all() and (out['normal'][...,2]>.99).all()
 spread=(out['height'].amax(1)-out['height'].amin(1));assert float(spread.max())<=1e-6
 for i,x in enumerate(placement['chosen_actual_assignments']):
  lo=torch.tensor(x['bounds'][0][:2],device=env.device);hi=torch.tensor(x['bounds'][1][:2],device=env.device)
  assert ((starts[i,:,:2]>lo)&(starts[i,:,:2]<hi)).all()
 return dict(placement,reset_root_before_physics_exact=True,complete_footprint_all_flat_hits=True,actual_G4_cell_count=10,actual_footprint_max_height_range_m=float(spread.max()),original_full_reset_receipt=env._rough_probe_reset_receipt)
'''
 (C/'g4_sdk_placement.py').write_text(placement,encoding='utf8')
 native=convert((S/'payload/native_e1_slopescope_probe.py').read_text())
 first=native.index(' sdk_wave50_placement=None');last=native.index(' env.reset();obs=',first)
 native=native[:first]+" sdk_wave50_placement=None\n if args.num_envs==10:\n  from g4_sdk_placement import prepare\n  sdk_wave50_placement=prepare(env)\n"+native[last:]
 anchor=" ground_error=0.;height_error=0."
 native=native.replace(anchor," if args.num_envs==10:\n  from g4_sdk_placement import verify\n  sdk_wave50_placement=verify(env,sdk_wave50_placement)\n  Path(args.output+'.assignment.json').write_text(json.dumps(sdk_wave50_placement,indent=2))\n"+anchor)
 native=native.replace('assert ground_error<1e-5 and height_error<1e-6','assert ground_error<=1e-6 and height_error<=1e-6')
 (P/'native_e1_wave50_scope_probe.py').write_text(native,encoding='utf8')
 guard='''"""005 authorization and exact own35mm/ancestry binding for new50mm scope."""
from pathlib import Path
from wave_budget005_source_guard import verify_original_records as original
SOURCE_SHA=SHA_TOKEN
ANCESTOR_SHA='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e'
def verify_original_records(q,D):
 original(q,D)
 row=q.w.read(D/'reports/SOURCE_SELECTED.json');assert row['sha256']==SOURCE_SHA and q.base.sha(Path(row['path']))==SOURCE_SHA
 old=q.w.read(D/'reports/OWN369_ACTUAL_SOURCE_BOUNDARY.json');assert old['complete129_ancestor_SHA']==ANCESTOR_SHA and old['own_source_SHA']==SOURCE_SHA and old['actual_old_fullsave_PASSED_and_unique_closed']
 b=q.base.budget_state();assert b['authorized_training_seconds']==1188000 and len(b['budget_extensions'])==7
 assert b['remaining_training_seconds']>120
'''.replace('SHA_TOKEN',repr(SOURCE_SHA))
 (P/'wave50_fullscope_source_guard.py').write_text(guard,encoding='utf8')
 controller=convert((S/'payload/supervise_slope5_independent_scope_once.py').read_text())
 controller=controller.replace("Path('/home/egde/rl_candidates/MOD4_S3_E1_CURB20_FORMAL_DISPATCH_REVIEWED_20261011')",'Path('+repr(OLD)+')').replace('3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e',SOURCE_SHA)
 controller=controller.replace('native_e1_wave50scope_probe.py','native_e1_wave50_scope_probe.py')
 controller=controller.replace('verified_G3_to_independent_WAVE505','verified_G3_to_independent_WAVE50')
 controller=controller.replace('inherited.verify_original_records(s.q,D)','verify_original_records(s.q,D)')
 controller=controller.replace('from clock_training_health import learning_health_pass','from clock_training_health import learning_health_pass\nfrom wave50_fullscope_source_guard import verify_original_records')
 controller=replace_function(controller,'verify','''def verify():
 verify_original_records(s.q,D)
 a=read(s.q.ER/'PLAN_APPROVAL.json');assert a['approved'] and 'S3' in a['allowed_stages']
 rev=read(s.q.ER/'MOE_PLAN_EXECUTION_CURRENT.json')['terrain_subexpert_revision004'];assert rev['approved'] and rev['active_next_expert']=='E1_WAVE'
 f=read(R/'SOURCE_FREEZE.json')['sha256'];old=read(OLD/'reports/SOURCE_FREEZE.json')['sha256'];assert len(old)==369 and all(f[n]==h for n,h in old.items())
 for n,h in f.items():assert s.q.base.sha(D/n)==h,n
 cpu=read(R/'WAVE50_TARGET_CPU_PASSED.json');assert cpu['passed'] and cpu['source_count']==len(f)
 decision=read(R/'FROZEN145_COMPLETE_SCOPE_DECISION.json');assert decision['actual_need_for_new_isolated50mm_learning'] and decision['checkpoint']['sha256']==SOURCE_SHA
 for row in read(R/'REUSED_ACTUAL_CONTRACTS.json')['actual_original_file_indices']:assert s.q.base.sha(Path(row['path']))==row['sha256']
 jobs=read(R/'WAVE50_FOUR_CASE_TEMPLATES.json')['jobs'];assert len(jobs)==4
 for t in jobs:assert s.q.base.sha(Path(t['artifacts']['runtime']['path']))==t['artifacts']['runtime']['sha256']
''')
 controller=replace_function(controller,'wait_existing','''def wait_existing():
 st=read(OLD/'reports/E1_STATE.json');assert st['phase']=='E1_WAVE35_second_bounded_saved_review_ready' and st['child'] is None
 p=read(OLD/'reports/e1_WAVE35_second_bounded_observation_PASSED.json');assert len(p['unique_completed_segment'])==1 and p['checkpoint']['sha256']==SOURCE_SHA
 for loc in (st['owner'],read(OLD/'reports/E1_GUARDIAN_STARTED.json'),dict(pid=p['own_PID_bound_receipt']['pid'],start_ticks=88740346)):
  a=identity(loc['pid']);assert not a or a['state']=='Z' or a['start_ticks']!=loc['start_ticks']
 assert not trainers() and s.q.base.budget_state()['active_segment'] is None and not read(s.q.ctl.STATE_PATH).get('active_training')
''')
 controller=controller.replace("t['profile']=='mod4_WAVE50_derived5deg_2m_mirrored_v1' and t['WAVE50_angle_deg']==5. and t['WAVE50_length_m']==2.","t['profile']=='mod4_G4_CAD_derived_50mm_v1' and t['G4_height_peak_to_trough_m']==.05")
 controller=controller.replace("v['SDK_WAVE50_actual_assignment_placement']['lower_upper_front_support_both_mirrors']","v['SDK_WAVE50_actual_assignment_placement']['reset_root_before_physics_exact'] and v['SDK_WAVE50_actual_assignment_placement']['actual_G4_cell_count']==10 and v['SDK_WAVE50_actual_assignment_placement']['complete_footprint_all_flat_hits']")
 controller=replace_function(controller,'publish','''def publish(init):
 sha=s.q.base.sha(init);dest=s.q.ER.parent/'artifacts'/('e1-wave50-own-'+sha+'.pt');assert not dest.exists();shutil.copy2(init,dest);assert s.q.base.sha(dest)==sha
 checkpoint=dict(path=str(dest),bytes=dest.stat().st_size,sha256=sha);templates=read(R/'WAVE50_FOUR_CASE_TEMPLATES.json')['jobs'];number=read(R/'CANDIDATE_JOB_UNUSED_ACTUAL.json')['number']
 for folder in ('eval_queue','eval_results'):
  assert not any('episode-d3-'+str(number)+'-' in p.name for p in (s.q.ER.parent/folder).iterdir())
 rows=[]
 for i,t in enumerate(templates):
  row=json.loads(json.dumps(t));kind=row['kind'];job='clk2500-closure-episode-d3-'+str(number)+'-e1-wave50-independent'+('-terrain' if i==0 else '-retention')+'-'+kind
  p=s.q.ER.parent/'eval_queue'/(job+'.json');assert not p.exists()
  row.update(job_id=job,published_epoch=time.time(),role='Own independent50mm fullsaved candidate; terrain acceptance and inherited diagnostic, no learned gate',scope_pending_actual_review=True,learning_executor_not_deployed=False,source_saved_terraincommand_remains35mm=False)
  row['artifacts']['checkpoint']=checkpoint;s.q.base.atomic_json(p,row);rows.append(row)
 write('E1_WAVE50_ASYNC_PUBLISHED.json',dict(epoch=time.time(),source=checkpoint,jobs=rows,no_GPU_or_canonical_write=True))
''')
 controller=controller.replace("read(R/'WAVE50_TARGET_FULLSTATE_CPU_PASSED.json')","read(R/'WAVE50_TARGET_CPU_PASSED.json')")
 controller=controller.replace("read(R/'WAVE50134_COMPLETE_ACTUAL_REVIEW.json')","read(R/'FROZEN145_COMPLETE_SCOPE_DECISION.json')")
 controller=controller.replace('old389_own_PASSED_actual_exits_two_OS_locks_held_active_empty','old369_own_PASSED_actual_exits_two_OS_locks_held_active_empty')
 controller=controller.replace('E0_Wave_CURB_not_optimizer_or_save_targets','E0_CURB_SLOPE_frozen_WAVE35_not_optimizer_or_save_targets')
 controller=controller.replace('requires_actual135_fourcase_review=True',"requires_actual_fourcase_review=True,candidate_number=read(R/'CANDIDATE_JOB_UNUSED_ACTUAL.json')['number']")
 (P/'supervise_wave50_independent_scope_once.py').write_text(controller,encoding='utf8')
 for q in P.rglob('*.py'):ast.parse(q.read_text())
 files={q.relative_to(P).as_posix():dict(bytes=q.stat().st_size,sha256=H(q.read_bytes())) for q in P.rglob('*') if q.is_file()}
 assert len(files)==15
 save('WAVE50_GPU_SCOPE_LOCAL_PREPARED.json',dict(epoch=time.time(),files=files,old377_components_preserved_exact=True,new_missing_GPU_scopes_only=True,first_formal_seconds=300,source_SHA=SOURCE_SHA,target=ROOT,not_target_CPU_or_GPU_admission=True))
 print(json.dumps(dict(local_new_files=len(files),GPU_not_launched=True)))
if __name__=='__main__':
 try:main()
 except BaseException:save('BUILD_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),before_GPU_or_old_once_replay=True));raise
