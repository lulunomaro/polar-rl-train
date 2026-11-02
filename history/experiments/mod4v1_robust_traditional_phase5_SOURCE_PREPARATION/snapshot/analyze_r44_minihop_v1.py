"""Causal diagnosis of fresh DR mini-hop recovery, not archive rehash or tuning on holdout."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parent;B=json.loads((R/'batches/r44_minihop_DR4/BATCH_RESULT.json').read_bytes());cases=[]
for b in B['rows']:
    name=b['case'];res=json.loads((R/'results'/name/'result.json').read_bytes())
    with(R/'results'/name/'trace.jsonl').open(encoding='utf-8')as f:rows=[json.loads(s)for s in f]
    events=[]
    for t in(1.5,1.64,1.95,1.99,2.05,2.15,2.3,2.5,3.,4.,6.):
        r=min(rows,key=lambda r:abs(r['command_time_s']-t))
        events.append(dict(command_time=r['command_time_s'],phase=r['phase'],estimated_pitch=r['estimated14'][2],true_pitch_before=r['grade_before']['pitch_true'],
             estimated_v=r['estimated14'][7],true_v_before=r['grade_before']['body_velocity'][0],wheel_rate_mean=r['wheel_rate_mean2'],
             requested_tau6=r['requested_tau6'],main_contact_mean=r['main_contact_mean_N2'],no_other_contact=r['no_other_contact_in_control']))
    landing=res['first_landing'];guide_first=None
    # Only the failure's private highrate stream is read for new causal identity/stage diagnosis.
    if not res['proposed_flat_clear80mm_recover2s_v2']:
        with(R/'results'/name/'physics.jsonl').open(encoding='utf-8')as f:
            for s in f:
                p=json.loads(s)
                if p['stage_time_s']>=1.5 and p['guide_normal_N']>1.:
                    guide_first=p;break
    cases.append(dict(case=name,complete=res['complete'],passed=res['proposed_flat_clear80mm_recover2s_v2'],actual_physics_steps=res['physics_steps'],
        first_air=res['first_all_world_air_s'],first_landing=landing,predicted_capture_s=1.99,first_guide_after_trigger=guide_first,
        max_air_mesh_clearance_m=res['maximum_main_mesh_clearance_during_full_air_m'],endstable_s=res['end_stable_s'],
        guide_ticks=res['after_trigger_guide_contact_physics_ticks'],hard_ticks=res['after_trigger_hard_contact_physics_ticks'],
        peak_mechanical_W=res['peak_positive_mechanical_power_W'],events=events,source_DR_feedback_delay_s=res['DR'].get('feedback_delay_s'),
        trace_ref=res['trace_artifact'],physics_ref=res['physical_artifact']))
report=dict(kind='R44_NEW_FULLDR_MINIHOP_OBSERVED_RECOVERY_FACTS',source_SHA=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),n=len(cases),
 complete=sum(c['complete']for c in cases),passed=sum(c['passed']for c in cases),physics_steps_already_executed=sum(c['actual_physics_steps']for c in cases),
 new_physics_steps_in_analysis=0,old_R39_not_regraded=True,raw_read_for_new_failure_diagnosis_only=True,cases=cases)
with(R/'reports/R44_MINIHOP_FACTS.json').open('x',encoding='utf-8')as f:json.dump(report,f,indent=2,allow_nan=False)
# Keep console bounded; full per-control observations persist in report.
print(json.dumps({k:v for k,v in report.items()if k!='cases'},indent=2))
for c in cases:print(json.dumps({k:v for k,v in c.items()if k not in('events','trace_ref','physics_ref')},indent=2))
