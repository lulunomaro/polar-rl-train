"""Predeclared 1 nominal + 2 matched TRAIN cases, no H2 holdout selection.
Nominal admission is numerical/physical completion, NOT composite-skill pass.
All three profiles and source hashes freeze before any physics; no retuning.
"""
from pathlib import Path
import hashlib,json
from fresh_train_batch_v1 import launch,dump
R=Path(__file__).resolve().parent;D=R/'SPIN_CENTER_DECEL_GATE_V1';P=D/'preflight002'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    unit=json.loads((P/'RESULT.json').read_bytes());assert unit['status']=='PASS_ZERO_STEP_R61_SPIN_GATE'and unit['failures']==0
    review=json.loads((P/'PRE_EXEC_REVIEW.json').read_bytes());assert review['ready_for_physics']is True
    for item in review['checked_sources']:assert sha(item['path'])==item['SHA'],item['path']
    sources=json.loads((P/'SOURCE_PREEXEC.json').read_bytes())['sources']
    for item in sources:assert sha(item['path'])==item['SHA'],item['path']
    configs=[];templates=[]
    for seed in(0,201,202):
        path=R/'batches/r26_transitions26'/('r26_spin_cycle_'+str(seed)+'.json');cfg=json.loads(path.read_bytes())
        assert cfg['profile']=='spin'and cfg['feedback']=='sensors'and cfg['duration_s']==26. and cfg['accel_correction']==0.
        old=json.loads(json.dumps(cfg));name='r61_decelgate_spin_'+('nominal'if seed==0 else 'DR_'+str(seed))
        cfg['case_id']=name;cfg['controller']['center_through_yaw_decel']=True
        check=json.loads(json.dumps(cfg));check['case_id']=old['case_id'];del check['controller']['center_through_yaw_decel'];assert check==old
        assert not(R/'results'/name).exists();configs.append((name,cfg));templates.append(dict(path=str(path),SHA=sha(path)))
    plan=D/'train003';plan.mkdir(exist_ok=False)
    frozen=dict(kind='NEW_STOP_ONLY_CENTER_GATE_TRAIN_NO_H2_CHANGE',configs=configs,sources=sources,old_config_sources=templates,
        review_SHA=sha(P/'PRE_EXEC_REVIEW.json'),launcher_SHA=sha(__file__),gain_observer_startup_capture_unchanged=True,
        nominal_admission='complete26s_no_health_or_software_stop; original_skill_gate_reported_NOT_admission',
        no_retune_after_nominal=True,no_heldout_used=True,PH7_pending=True)
    dump(plan/'FROZEN_PLAN.json',frozen)
    keys=['complete','controls','physics_callbacks','stop_reason','proposed_gate_passed','transition_proposed_pass','xy_displacement_m','phase_metrics','tail_v_tracking_RMSE']
    n=launch(R,'r61_spin_decel_nominal1','run_spin_decel_gate_v1.py',configs[:1],dict(kind='R61_GATE_ONLY_NOMINAL_TRAIN'),keys,max_workers=1)
    nominal=n['rows'][0]
    if nominal['returncode']!=0 or not nominal.get('complete'):
        dump(plan/'DEFERRED_DR.json',dict(unstarted=[x[0]for x in configs[1:]],reason='nominal_admission_incomplete_or_software',nominal=nominal));return
    # A robot composite failure remains a failure, but a complete/healthy new
    # gate is allowed the two already-frozen matched diagnostic TRAIN episodes.
    for item in sources:assert sha(item['path'])==item['SHA']
    launch(R,'r61_spin_decel_paired2','run_spin_decel_gate_v1.py',configs[1:],dict(kind='R61_GATE_ONLY_MATCHED_TRAIN_NOT_HOLDOUT',baseline_not_replayed=True,old_seeds=[201,202]),keys,max_workers=2)
if __name__=='__main__':main()
