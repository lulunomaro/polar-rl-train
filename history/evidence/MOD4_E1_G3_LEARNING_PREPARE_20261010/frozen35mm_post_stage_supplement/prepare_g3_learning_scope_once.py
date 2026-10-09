"""Isolated35mm integration after complete126 data review; prior source330 bytes preserved."""
from pathlib import Path
import ast,hashlib,json,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';OLD=W/'MOD4_E1_G2_LEARNING_PREPARE_20261010';NEW=W/'MOD4_E1_G3_LEARNING_PREPARE_20261010';H=lambda b:hashlib.sha256(b).hexdigest()
OLDROOT='/home/egde/rl_candidates/MOD4_S3_E1_G2_MATCHED_CONTINUE_20261010';NEWROOT='/home/egde/rl_candidates/MOD4_S3_E1_G3_REVIEWED_20261010'
def save(n,v):
 p=R/n;assert not p.exists();p.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode())
def block(s,name,replacement):
 a=next(n for n in ast.parse(s).body if isinstance(n,ast.FunctionDef) and n.name==name);lines=s.splitlines(keepends=True);return ''.join(lines[:a.lineno-1])+replacement+'\n'+''.join(lines[a.end_lineno:])
def main():
 save('G3_LEARNING_PREPARE_STARTED.json',dict(epoch=time.time(),trial_id='E1-G3-35MM-LEARNING-PREPARE-07',no_GPU_or_budget_change=True))
 diagnosis=json.loads((R/'G3_126_PREFIX_DIAGNOSIS.json').read_bytes());assert diagnosis['old_ground_contact_and_data_contracts_passed'] and diagnosis['ordinary']==0 and not diagnosis['full_35mm_course_passed']
 assert not NEW.exists();NEW.mkdir();(NEW/'reports').mkdir();payload=NEW/'payload';code=payload/'isaac/mod4';code.mkdir(parents=True)
 for p in (D/'payload').iterdir():
  if p.name in ('g3_cad_profile.json','g3_cad_wave_geometry.py'):(code/p.name).write_bytes(p.read_bytes())
 for p in (OLD/'payload').rglob('*.py'):
  if p.name=='g2_cad_wave_geometry.py':continue
  name=p.name.replace('G2','G3').replace('g2','g3');rel=p.relative_to(OLD/'payload').with_name(name);s=p.read_text(encoding='utf8').replace('G2','G3').replace('g2','g3').replace('derived_20mm','derived_35mm').replace('derived20mm','derived35mm').replace('20mm','35mm')
  if p.name=='g2_terrain_checkpoint.py':
   s=s.replace('G3_height_peak_to_trough_m\']==.02','G3_height_peak_to_trough_m\']==.035').replace('G3_height_peak_to_trough_m=.02','G3_height_peak_to_trough_m=.035')
   s=s.replace('Explicit G0->G3','Explicit G2->G3').replace('G0->G3','G2->G3').replace('G0_to_G3','G2_to_G3')
   s=s.replace("  old.validate(state,env.num_envs)\n  assert os.environ", "  from g2_terrain_checkpoint import validate as validate_previous_G2\n  validate_previous_G2(state,env.num_envs)\n  assert os.environ")
   s=s.replace("assert state['profile']=='mod4_intro_gentle_v1'", "assert state['profile']=='mod4_G2_CAD_derived_20mm_v1'")
  elif p.name=='test_g2_state_cpu.py':s=s.replace("('G3_height_peak_to_trough_m',.01)","('G3_height_peak_to_trough_m',.02)")
  elif p.name=='supervise_e1_G2_reviewed_short_observation.py':
   s=s.replace("G0_to_G3_35mm","G2_to_G3_35mm").replace('/home/egde/rl_candidates/MOD4_S3_E1_G1_REPAIR_20261009',OLDROOT).replace('assert len(old)==321 and len(f)==329','assert len(old)==330 and len(f)==338')
   s=s.replace("names={'train_e1_g3_reviewed_resume_ppo.py'", "names={'train_e1_g2_reviewed_resume_ppo.py','train_e1_g2_fresh_preflight_ppo.py','train_e1_g3_reviewed_resume_ppo.py'")
   s=s.replace('reviewed32053','reviewed32058').replace('655a36b78926bc17d4230996fe152b62d0f997f3037105d5247582697440481f','42cdc9d24519778a9da3e35b05a3eb3bb5745760c26a5842c78fcde2bd39e53b')
   s=s.replace("        (validate if ck['E1_terrain_state']['profile']=='mod4_G3_CAD_derived_35mm_v1' else old_validate)(ck['E1_terrain_state'],count)","        from g2_terrain_checkpoint import validate as previous_G2_validate\n        validator=validate if ck['E1_terrain_state']['profile']=='mod4_G3_CAD_derived_35mm_v1' else (previous_G2_validate if ck['E1_terrain_state']['profile']=='mod4_G2_CAD_derived_20mm_v1' else old_validate)\n        validator(ck['E1_terrain_state'],count)")
   s=s.replace("'e1_G1_repair_observation_PASSED.json'","'e1_G2_matched_continuation_PASSED.json'").replace("'E1_G1_repair_saved_review_ready'","'E1_G2_matched_continuation_saved_review_ready'").replace('71687419','72519910')
   s=s.replace("['G3_height_peak_to_trough_m']==.02","['G3_height_peak_to_trough_m']==.035").replace("'123-e1-g3-observation'","'127-e1-g3-observation'")
   s=s.replace('# Actual122 same selected source full-wave scope is already complete; do not replay anchor.','# Actual126 complete35mm data/physical interface reviewed; partial42of54 routes retained, no graduation or replay.')
   s=s.replace("assert read(R/'SELECTED_E1_G3_SOURCE.json')['actual_behavior_review_complete']","assert read(R/'SELECTED_E1_G3_SOURCE.json')['actual_behavior_review_complete']\n    admission=read(R/'G3_FROZEN_SCOPE_ADMITTED.json');assert admission['old_ground_contact_and_data_contracts_passed'] and admission['ordinary']==0 and not admission['full_35mm_course_passed']")
   s=s.replace("terrain['E1_episode_incremented_once'] and not terrain['PhysX_exact_resume_claimed']", "terrain['E1_episode_incremented_once'] and not terrain['PhysX_exact_resume_claimed']\n        assert not terrain['terrain_state_restored_exact'] and terrain['explicit_G2_to_G3_geometry_transition'] and terrain['explicitly_new_E1_terrain']")
  ast.parse(s);out=payload/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(s.encode())
 files=[p for p in payload.rglob('*') if p.is_file()];assert len(files)==8
 for p in files:
  if p.suffix=='.py':ast.parse(p.read_text(encoding='utf8'))
 sel=json.loads((R/'REPAIRED_PREPARED.json').read_bytes())['selected_source'];selected=dict(epoch=time.time(),source=sel,actual_behavior_review_complete=True,no_unreviewed_latest_source=True,complete_old_skill_review_source=str(W/'MOD4_E1_G2_MATCHED_CONTINUE_20261010/reports/MATCHED_123_REVIEW.json'),actual_new35mm_scope=diagnosis,not_full35mm_graduation=True,no_permanent_anti_forgetting_proof=True)
 NR=NEW/'reports';(NR/'SELECTED_E1_G3_SOURCE.json').write_bytes(json.dumps(selected,indent=2).encode());(NR/'G3_FROZEN_SCOPE_ADMITTED.json').write_bytes(json.dumps(diagnosis,indent=2).encode())
 pkg=json.loads((R/'REPAIRED_PREPARED.json').read_bytes())['package'];ready=dict(epoch=time.time(),package=pkg,actual_new_scope_126_complete_reviewed=True,partial_route_coverage_retained=True,no_full35mm_pass=True,no_GPU_or_PPO_deployed=True,new_budget_seconds=0);(NR/'G3_BEHAVIOR_PACKAGE_BUILT.json').write_bytes(json.dumps(ready,indent=2).encode())
 # New stage script, originalstage once remains untouched.
 s=(OLD/'stage_g2_reviewed_once.py').read_text(encoding='utf8').replace('G2','G3').replace('g2','g3').replace('original321','original330').replace('len(f[\'sha256\'])==321','len(f[\'sha256\'])==330').replace('source329','source338').replace('source_count=329','source_count=338')
 s=s.replace('/home/egde/rl_candidates/MOD4_S3_E1_G1_REPAIR_20261009',OLDROOT).replace('/home/egde/rl_candidates/MOD4_S3_E1_G3_REVIEWED_20261010',NEWROOT).replace("'E1_G1_repair_saved_review_ready'","'E1_G2_matched_continuation_saved_review_ready'")
 s=s.replace("for name in ('SELECTED_E1_G3_SOURCE.json','E1_PLANNED_BEHAVIOR_PUBLISHED.json'):","for name in ('SELECTED_E1_G3_SOURCE.json','G3_FROZEN_SCOPE_ADMITTED.json','E1_PLANNED_BEHAVIOR_PUBLISHED.json'):")
 s=s.replace('new_G3_behavior_pending=False','new_G3_behavior_pending=False,full35mm_graduation_not_claimed=True')
 ast.parse(s);(NEW/'stage_g3_reviewed_once.py').write_bytes(s.encode())
 (NR/'PREPARED.json').write_bytes(json.dumps(dict(epoch=time.time(),trial_id='E1-G3-35MM-LEARNING-PREPARE-07',files={p.relative_to(payload).as_posix():dict(bytes=p.stat().st_size,sha256=H(p.read_bytes())) for p in files},original330_preserved=True,new_G3_file_count=8,expected_source_count=338,new_geometry_transition='G2_to_G3_35mm',first_observation_seconds=300,actual126_full_data_reviewed=True,partial_after_support17of27_forward25of27_reverse_preserved=True,all_oldclock_DR_scope_evidence_reused=True,noGPUorbudgetchange=True),indent=2).encode())
 print(json.dumps(dict(root=str(NEW),files=8,source338_expected=True,newgeometry_G2_to_G3=True,CPU_preparation_only=True)))
if __name__=='__main__':
 try:main()
 except Exception:save('G3_LEARNING_PREPARE_ERROR.json',dict(epoch=time.time(),trial_id='E1-G3-35MM-LEARNING-PREPARE-07',error=traceback.format_exc(),noGPUorbudgetchange=True));raise
