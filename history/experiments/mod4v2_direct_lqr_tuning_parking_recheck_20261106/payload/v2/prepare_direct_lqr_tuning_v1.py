"""Direct human-requested bounded LQR tuning, not another observer audit.
Three fixed settings: baseline, rate/velocity LQR, that LQR with softer/damped differential legs.
"""
from pathlib import Path
import json
R=Path(__file__).resolve().parent;S=R/'T01_NOMINAL_BAND_M0_V1';D=R/'DIRECT_LQR_TUNING_V1'
def main():
 if D.exists():raise RuntimeError('Direct tuning prefix exists')
 p=json.loads((S/'PROTOCOL.json').read_text(encoding='utf-8'));text=(S/'run_nominal_band_m0.py').read_text(encoding='utf-8')
 settings={'baseline':{},'lqr_damped':dict(pitchrate_weight=4.,velocity_weight=2.25),
  'lqr_compliant':dict(pitchrate_weight=4.,velocity_weight=2.25,leg_kp=90.,leg_kd=6.)}
 def one(a,b):
  nonlocal text
  if text.count(a)!=1:raise RuntimeError('Nonunique source anchor:'+a)
  text=text.replace(a,b,1)
 one("    dump(out/'config.json', cfg)","    cfg.update(tuning_name=spec['tuning_name'],tuning=spec['tuning'],human_direct_tuning=True)\n    dump(out/'config.json', cfg)")
 anchor='        original_build, original_dr, original_plant = runtime.terrain.build_model, runtime.bridge.FullDR, runtime.BufferedImuPlant'
 one(anchor,"""        original_controller=runtime.GroundController
        def tuned_controller(gain,config=None,**kw):
            c=dict(config or {});c.update(spec['tuning'])
            return original_controller(gain,c,**kw)
        runtime.GroundController=tuned_controller
"""+anchor)
 one("            timing['engine_setup_wall_s'] = time.perf_counter()-t","            runtime.GroundController=original_controller\n            timing['engine_setup_wall_s'] = time.perf_counter()-t")
 semantic="meta['original_default_M0_controller_unchanged']=True"
 matches=[line for line in text.splitlines()if line.strip()==semantic]
 if len(matches)!=1:raise RuntimeError('Semantic metadata line unavailable')
 line=matches[0];indent=line[:len(line)-len(line.lstrip())]
 one(line,indent+"meta['original_default_M0_controller_unchanged']=not bool(spec['tuning'])")
 one("        dump(out/'meta.json', meta)","        meta.update(actual_tuning=spec['tuning'],tuning_name=spec['tuning_name'],actual_leg_kp=engine.controller.leg_kp,actual_leg_kd=engine.controller.leg_kd)\n        dump(out/'meta.json', meta)")
 one("controller_changed=False,previous_three_mechanisms_frozen=True,", "controller_changed=bool(spec['tuning']),actual_tuning=spec['tuning'],tuning_name=spec['tuning_name'],previous_three_mechanisms_frozen=True,")
 # Preserve original strict checks; a separate engineering score is not a new pass definition.
 one('        assessed=all(value is not None for value in checks.values())',"""        tuning_score=(metrics['pitch_rms_rad']/.035+metrics['roll_rms_rad']/.035+metrics['slow_vx_rmse_m_s']/.1+metrics['final_stop_body_vx_rms_m_s']/.05+.5*metrics['slow_max_lateral_m']/.2)
        engineering_eligible=bool(engine.controls==n and checks['complete_finite_no_auto_reset'] and contact_metrics is not None and contact_metrics['guide_support_duty']==0 and contact_metrics['hard_contact_ticks']==0 and metrics['pitch_abs_peak_rad']<=.1 and metrics['roll_abs_peak_rad']<=.1 and min(contact_metrics['mainwheel_support_duty2'])>=.95)
        assessed=all(value is not None for value in checks.values())""")
 one('            case_screen_pass=all(checks.values()) if assessed else None,case_fully_assessed=assessed,','            case_screen_pass=all(checks.values()) if assessed else None,case_fully_assessed=assessed,tuning_score=tuning_score,engineering_eligible=engineering_eligible,score_not_formal_pass=True,')
 p.update(id='MOD4V2_HUMAN_DIRECT_LQR_TUNING_001',status='fixed_before_any_new_draw',
  scope='Human2026-11-06 requests actual LQR tuning after excessive audit loop. Old nominal FF3 failures retained;new bounded two feedback parameter alternatives,not grid/observer retuning.',
  settings=settings,formal_cases=[dict(id=k,seed=530300,nominal=False,profile='slow',tuning_name=k,tuning=v)for k,v in settings.items()],
  tuning_rationale=dict(lqr_damped='Qpitchrate x4 and Qvelocity x2.25 halve allowed rate error and reduce allowed velocity error by1.5;DARE is re-solved on actualv2 Ad/Bd,not postmultiplying oldK.',
   lqr_compliant='Same LQR plus differential Kp120->90 and Kd4->6 to reduce noise/bias stiffness and add damping;no new force FF or terrain oracle.'),
  execution_policy=dict(train_seed=530300,independent_validation_seed=530301,max_training_settings=3,max_parallel_workers=3,
   no_retry_seed_redraw_or_score_window_relax=True,observer_fixed_original=True,selection='Lowest fixed engineering score among eligible;candidate must beat baseline by5percent before one new independent paired validation.',
   original_strict_gates_retained=True,engineering_score_not_skill_pass=True,oldcases_not_replayed=True))
 p['notes']=[s for s in p['notes']if 'Four DR TRAIN'not in s]+['Actual new feedback tuning,not changing observer/gates/model or hiding oldFF failures.',
  'Engineering score fixed before runs: pitchRMS/.035+rollRMS/.035+vRMSE/.1+stopRMS/.05+.5*lateral/.2. Original whole0 and source scope remain separately visible.',
  'Any winner is a training recipe pending fresh independent validation;not T01/T36/95percent reliability.']
 compile(text,str(D/'run_tuning_case.py'),'exec');D.mkdir(exist_ok=False)
 (D/'run_tuning_case.py').write_text(text,encoding='utf-8');(D/'PROTOCOL.json').write_text(json.dumps(p,indent=2),encoding='utf-8')
 (D/'PREPARATION.json').write_text(json.dumps(dict(models=0,physics=0,old_raw=0,observer_changed=False,actual_LQR_DARE_config_changed=True,original_gates_changed=False,settings=settings),indent=2),encoding='utf-8')
 print('DIRECT_LQR_TUNING_READY 3 fixed settings,realDARE changes,no observer or gate changes')
if __name__=='__main__':main()
