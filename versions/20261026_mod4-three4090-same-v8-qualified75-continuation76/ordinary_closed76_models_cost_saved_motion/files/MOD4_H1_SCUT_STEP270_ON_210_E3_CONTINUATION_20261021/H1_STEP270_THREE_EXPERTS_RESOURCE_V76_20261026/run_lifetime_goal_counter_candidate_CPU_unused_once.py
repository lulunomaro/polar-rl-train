"""Synthetic20k CPU candidate accounting checks; not installed or simulation evidence."""
from pathlib import Path
import hashlib,json,sys,time,traceback
import numpy as np
N=Path(__file__).resolve().parent;R=N/'reports';D=N/'diagnostic_goal_counter_candidate';sys.path.insert(0,str(D))
from lifetime_goal_counter_CPU_candidate_v1 import LifetimeGoalCounter,EVENTS
try:
    n=20000;initial={k:np.zeros(n,dtype=np.int64) for k in EVENTS};cross=np.zeros((n,2),dtype=bool)
    c=LifetimeGoalCounter(initial,cross)
    def row():return {**{k:np.zeros(n,dtype=np.int64) for k in EVENTS},'done':np.zeros(n,dtype=bool),'step_wheel_crossed':np.zeros((n,2),dtype=bool)}
    a=row();a['takeoff_count'][0]=1;a['done'][0]=True;a['step_wheel_crossed'][0]=True
    snapshot={k:v.copy() for k,v in a.items()};assert c.complete(a) and all(np.array_equal(v,a[k]) for k,v in snapshot.items())
    b=row();b['takeoff_count'][0]=1;b['landing_count'][0]=1;b['step_wheel_crossed'][0]=True;assert c.complete(b)
    z={k:v.copy() for k,v in b.items()};z['recovery_count'][0]=1;assert c.complete(z)
    assert c.snapshot()['events']=={'takeoff_count':2,'landing_count':1,'recovery_count':1} and c.snapshot()['both_leading_edges_cross_event_count']==2
    assert c.complete(z) and c.snapshot()['events']=={'takeoff_count':2,'landing_count':1,'recovery_count':1}
    assert all(not x.any() for x in initial.values()) and not cross.any()
    valid=c.snapshot();assert valid['diagnostic_valid'] and valid['complete_control_rows']==4
    bad={k:v.copy() for k,v in z.items()};bad['done']=np.zeros(2,dtype=bool);assert not c.complete(bad) and not c.snapshot()['diagnostic_valid']
    neg=LifetimeGoalCounter({'takeoff_count':np.ones(n,dtype=np.int64),'landing_count':initial['landing_count'],'recovery_count':initial['recovery_count']},cross);assert neg.complete(row()) and neg.snapshot()['negative_counter_envframes']==n and not neg.snapshot()['diagnostic_valid']
    outdir=D/'synthetic_output';outdir.mkdir();good=LifetimeGoalCounter(initial,cross);good.complete(a);good.save(outdir);good.complete(b);good.save(outdir)
    saved=json.loads((outdir/'CONTROL_LIFETIME_GOAL_EVENTS_ACTUAL.json').read_bytes());assert saved['events']['takeoff_count']==2 and not (outdir/'CONTROL_LIFETIME_GOAL_EVENTS_ACTUAL.json.partial').exists()
    result={'epoch':time.time(),'passed_synthetic_CPU_candidate':True,'environments':n,'cases':['reset_before_next_row','repeated_event_with_new_episode','landing_recovery_once','unchanged_row_no_duplicate','input_arrays_unchanged','invalid_shape_diagnostic_false_without_training_gate','negative_counter_diagnostic_false','atomic_updated_text_snapshot'],
            'valid_synthetic_snapshot':valid,'module_SHA':hashlib.sha256((D/'lifetime_goal_counter_CPU_candidate_v1.py').read_bytes()).hexdigest(),
            'candidate_only_no_trace_hook_installed_or_runtime_payload_prepared':True,'future_hook_must_use_existing_CPU_copied_rows_and_one_initial_counter_read':True,
            'no_actor_reward_command_physics_reset_RNG_model_GPU_or_remote_action':True}
    with (R/'LIFETIME_GOAL_COUNTER_UNINSTALLED_CANDIDATE_SYNTHETIC_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(result,f,indent=2)
    print(json.dumps({'passed_synthetic_CPU_candidate':True,'cases':len(result['cases']),'not_installed':True}))
except BaseException:
    with (R/('LIFETIME_GOAL_COUNTER_CANDIDATE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump({'epoch':time.time(),'error':traceback.format_exc(),'no_same_once_replay':True},f,indent=2)
    raise
