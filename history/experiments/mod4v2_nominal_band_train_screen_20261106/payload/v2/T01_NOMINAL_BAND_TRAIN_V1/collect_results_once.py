"""Read only this frozen screen's small result/ERROR JSONs; no raw, SDK or replay."""
from pathlib import Path
import json
D=Path(__file__).resolve().parent
NAMES={520181:'v2_t01_band_stand_nominal_520181_001',520182:'v2_t01_band_stand_dr_520182_001',
 520183:'v2_t01_band_slow_dr_520183_001',520184:'v2_t01_band_stand_dr_520184_001',520185:'v2_t01_band_slow_dr_520185_001'}
def main():
 out=D/'COLLECTION001'
 if out.exists():raise RuntimeError('Small-result collection already consumed')
 proto=json.loads((D/'PROTOCOL.json').read_text(encoding='utf-8'));records=[];results={}
 for spec in proto['formal_cases']:
  path=D/'runs'/NAMES[spec['seed']];rpath=path/'result.json';err=path/'ERROR.json'
  if rpath.exists():
   r=json.loads(rpath.read_text(encoding='utf-8'));c=r['config']
   if c['seed']!=spec['seed']or c['formal_id']!=spec['id']or c['nominal']!=spec['nominal']or c['protocol_id']!=proto['id']:raise RuntimeError('Case identity mismatch')
   results[spec['seed']]=r;dr=r['dr_meta'];motor=r['private_motor_observation']['sections']['all']
   records.append(dict(spec=spec,case=NAMES[spec['seed']],status='ASSESSED',result_path=str(rpath),
    complete=r['complete'],controls=r['controls'],physics_steps=r['physics_steps'],counts=r['counts'],wall_s=r['total_case_wall_s'],
    case_screen_pass=r['case_screen_pass'],observed_scope_pass=r['new_scenario_scope_valid'],
    false_checks=[k for k,v in r['checks'].items()if v is False],unknown_checks=[k for k,v in r['checks'].items()if v is None],
    metrics=r['metrics'],contact_metrics=r['contact_metrics'],source_plan_private_scope=r['source_plan_private_scope'],
    DR=dict(full_nominal=dr['nominal'],D0_only_nominal_branch=dr['D0']['D0_only_nominal_episode'],
     mass_inertia_factor=dr['D0']['all_moving_bodies_shared_mass_inertia_factor'],motor_gain6=dr['D0']['motor_gain6'],mu=dr['D0']['wheel_sliding_mu'],
     feedback_delay_us=dr['D3']['requested_delay_us'],action_delay_us6=dr['D4']['action_delay_us6'],D1_enabled=dr['D1']['enabled'],
     bias4_rad=dr['D2']['episode_leg_bias4_rad'],D5=dr['D5'],D6=dr['D6'],D7=dr['D7']),
    all_DC_changed_ticks=motor['any_dc_changed_ticks'],public_signal_observation=r['public_signal_observation'],
    producer_raw_receipts=r['producer_raw_receipts'],robust_corridor_certified=r['robust_corridor_certified']))
  elif err.exists():
   e=json.loads(err.read_text(encoding='utf-8'));records.append(dict(spec=spec,case=NAMES[spec['seed']],status='SOFTWARE_ERROR_PREFIX_RETAINED',error_path=str(err),
    controls=e.get('controls'),physics_steps=e.get('physics_steps'),counts=e.get('counts'),traceback=e.get('traceback')))
  else:records.append(dict(spec=spec,case=NAMES[spec['seed']],status='NOT_EXECUTED',controls=0,physics_steps=0,not_an_independent_failed_sample=True))
 def ok(seed):
  r=results.get(seed);return bool(r and r['complete']and r['case_screen_pass']is True and r['new_scenario_scope_valid']is True)
 first=ok(520181);w1=all(ok(x)for x in(520182,520183));w2=all(ok(x)for x in(520184,520185))
 if first and w1 and any(x not in results for x in(520184,520185)):raise RuntimeError('Screen still unfinished: permitted wave2 absent')
 if not first and any(x in results for x in(520182,520183,520184,520185)):raise RuntimeError('DR violated nominal-first stop policy')
 if not w1 and any(x in results for x in(520184,520185)):raise RuntimeError('Wave2 violated frozen failure stop policy')
 summary=dict(protocol_id=proto['id'],status='BOUNDED_SCREEN_COMPLETE_OR_PAUSED_ON_FROZEN_FAILURE',
  nominal_stand_pass=first,wave1_pass=w1,wave2_pass=w2,
  wave2_status='ASSESSED'if any(x in results for x in(520184,520185))else'PAUSED_BY_PREDECLARED_FAILURE_RULE',
  executed_case_count=len(results),executed_screen_passes=sum(r['case_screen_pass']is True for r in results.values()),
  physics_steps_total=sum((r.get('physics_steps')or 0)for r in records),controls_total=sum((r.get('controls')or 0)for r in records),
  fresh_model_builds_total=sum((r.get('counts')or{}).get('model_builds',0)for r in records),
  FullDR_constructors_total=sum((r.get('counts')or{}).get('FullDR_constructors',0)for r in records),
  records=records,controller_changed=False,original_gates_unchanged=True,M1_M2_M3_still_frozen=True,
  small_result_reads=len(results),old_case_reads=0,raw_payload_reads=0,models=0,forward=0,physics=0,
  no_independent_reliability_or_T36_claim=True,robust_corridor_certified=False)
 out.mkdir(exist_ok=False);(out/'RESULT.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
