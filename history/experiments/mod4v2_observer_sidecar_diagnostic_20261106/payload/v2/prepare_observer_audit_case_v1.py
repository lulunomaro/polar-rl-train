"""ONE new observation-only DR episode; unchanged M0 actor, no paused-screen continuation."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parent;SRC=R/'T01_NOMINAL_BAND_TRAIN_V1';D=R/'T01_OBSERVER_AUDIT_V1'
def main():
 if D.exists():raise RuntimeError('Observation case prefix already prepared')
 test=json.loads((R/'OBSERVER_AUDIT_V1/check001/RESULT.json').read_text(encoding='utf-8'))
 if not test['passed']or test['summary']['maximum_estimate_output_difference']!=0.:raise RuntimeError('Sidecar transport not verified')
 protocol=json.loads((SRC/'PROTOCOL.json').read_text(encoding='utf-8'))
 old_gates=protocol['gates'].copy();old_windows=protocol['windows'].copy()
 protocol.update(id='MOD4V2_HW300N60_T01_OBSERVER_ONLY_DR_DIAGNOSTIC_001',
  status='frozen_before_one_new_diagnostic_episode_no_actor_change',
  scope='Observe original estimator fusion locals + noncontrolling witness on a fresh fixed DR draw;not a seed-redraw passing attempt or wave2 continuation.',
  formal_cases=[dict(id='observer_only_dr',seed=520190,nominal=False,profile='slow')],
  execution_policy=dict(single_new_case_only=True,max_parallel_physics_workers=1,threads_per_worker=1,no_retry_or_parameter_change=True,
   old_paused_seeds_stay_paused=[520184,520185,520112,520113,520114,520115],
   no_actor_output_or_score_change=True,no_4th_control_mechanism=True,not_matched_to_old_DR_failure=True),
  training_only=False,diagnostic_only=True,control_sidecar_connections=0)
 original_core=R.parent/'mod4v1_lqr_mpc_robust_20261102/sensor_core_jump_v1.py'
 for path in(R/'observer_audit_v1.py',original_core):
  protocol['frozen_small_sources'].append(dict(path=str(path),bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
 protocol['notes']+=['Source estimator runs unchanged and its exact original Estimate object is always returned to controller.',
  'Independent audit subclass has identical original update AST except diagnostic assignments;output differences recorded,not used to correct actor.',
  'True pose/velocity only grade residuals in runner,never sidecar/estimator/controller inputs. No extra model/forward/physics.',
  'Do not search seeds to obtain D3=10ms;report whatever the single fixed520190 episode draws.']
 text=(SRC/'run_band_train_case.py').read_text(encoding='utf-8')
 def one(a,b):
  nonlocal text
  if text.count(a)!=1:raise RuntimeError('Unstable source anchor: '+a)
  text=text.replace(a,b,1)
 one('        p = engine.plant; dt = float(p.dt)',
  '        from observer_audit_v1 import ObserverSidecar\n        sidecar=ObserverSidecar(engine.estimator);sidecar.attach(engine.estimator)\n        p = engine.plant; dt = float(p.dt)')
 one("        initial = p.grade_current(); origin = np.asarray(initial['xyz'][:2])",'''        initial = p.grade_current(); origin = np.asarray(initial['xyz'][:2])
        audit_truth_history={round(float(p.d.time)*1e6):initial}
        audit_regions={key:dict(calls=0,new_fusion=0,weight=[],gravity_innovation=[],vx_error=[],pitch_error=[],held_roll_sensor_error=[],roll_epoch_gap=[])for key in('initial','drive','brake','final')}
        def audit_stat(a):return dict(n=len(a),mean=None if not a else float(np.mean(a)),rms=None if not a else float(np.sqrt(np.mean(np.square(a)))),minimum=None if not a else min(a),maximum=None if not a else max(a))
        def private_estimate_audit(now,g):
            key='initial'if now<2. else'drive'if now<8. else'brake'if now<9. else'final'
            region=audit_regions[key];region['calls']+=1
            diag=sidecar.last or {};pre=diag.get('pre_fusion')
            if pre is not None:
                region['new_fusion']+=1;region['weight'].append(pre['gravity_correction_weight']);region['gravity_innovation'].append(pre['gravity_innovation_m_s2'])
            gap=diag.get('held_roll_to_first_order_arrival_gap_rad')
            if gap is not None:region['roll_epoch_gap'].append(gap)
            truth=audit_truth_history.get(round(now*1e6));sensor_truth=None if engine.packet is None else audit_truth_history.get(round(engine.packet.time_s*1e6))
            errors={}
            if truth is not None and engine.estimate is not None:
                errors['vx_error_at_command_m_s']=float(engine.estimate.state14[7]-truth['body_velocity'][0])
                errors['pitch_error_at_command_rad']=float(engine.estimate.state14[2]-truth['pitch_true'])
                region['vx_error'].append(errors['vx_error_at_command_m_s']);region['pitch_error'].append(errors['pitch_error_at_command_rad'])
            if sensor_truth is not None and engine.estimate is not None:
                errors['held_roll_error_at_sensor_rad']=float(engine.estimate.roll-sensor_truth['roll_true'])
                region['held_roll_sensor_error'].append(errors['held_roll_error_at_sensor_rad'])
            audit_truth_history[round(float(p.d.time)*1e6)]=g
            for stamp in sorted(audit_truth_history)[:-4]:del audit_truth_history[stamp]
            return dict(public_sidecar=diag,private_truth_comparison=errors,truth_never_passed_to_sidecar_or_actor=True)''')
 one("            g['finite'] = bool(g['finite'] and np.isfinite(p.d.ctrl).all())",
  "            g['finite'] = bool(g['finite'] and np.isfinite(p.d.ctrl).all())\n            observer_audit_row=private_estimate_audit(now,g)")
 one('source_time_metadata=metadata,source_plan_private_scope=private_scope_row,',
  'source_time_metadata=metadata,source_plan_private_scope=private_scope_row,observer_audit=observer_audit_row,')
 one("status='FROZEN_NOMINAL_BAND_M0_TRAIN_SCREEN_NOT_T36_OR_ROBUST_CORRIDOR_CERTIFICATE'",
  "status='ONE_NEW_OBSERVER_ONLY_DR_DIAGNOSTIC_UNCHANGED_M0_NOT_WAVE2_OR_T36'")
 one('controller_changed=False,previous_three_mechanisms_frozen=True,robust_corridor_certified=False,',
  "controller_changed=False,previous_three_mechanisms_frozen=True,robust_corridor_certified=False,\n            observer_sidecar_summary=sidecar.summary(),observer_regions={key:{field:audit_stat(value)if isinstance(value,list)else value for field,value in region.items()}for key,region in audit_regions.items()},\n            observer_diagnostic_valid=bool(not sidecar.failures and sidecar.calls==engine.controls and sidecar.max_difference==0.),")
 assert protocol['gates']==old_gates and protocol['windows']==old_windows
 compile(text,str(D/'run_observer_audit_case.py'),'exec')
 D.mkdir(exist_ok=False);(D/'run_observer_audit_case.py').write_text(text,encoding='utf-8')
 (D/'PROTOCOL.json').write_text(json.dumps(protocol,indent=2),encoding='utf-8')
 (D/'PREPARATION.json').write_text(json.dumps(dict(model=0,forward=0,physics=0,old_raw_or_QA=0,
  new_case='v2_t01_observer_only_dr_520190_001',actor_source_unchanged=True,old_gates_unchanged=True,
  only_new_physics_if_parent_runs=True,sidecar_output_connections=0),indent=2),encoding='utf-8')
 print('OBSERVER_DIAGNOSTIC_PREPARED onefresh520190; original actor/outputs/gates unchanged;no model/physics')
if __name__=='__main__':main()
