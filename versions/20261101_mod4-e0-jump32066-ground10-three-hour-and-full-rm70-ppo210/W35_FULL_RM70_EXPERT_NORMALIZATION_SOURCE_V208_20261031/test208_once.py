"""NEW208 synthetic CPU contract purpose, never a robot/model/WM experiment."""
import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
from pathlib import Path
import ast, copy, hashlib, json, math, sys, time, traceback
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
SRC = HERE / 'source'
REPORTS = HERE / 'reports'
sys.path.insert(0, str(SRC))
TRIAL = 'NEW208_CPU_COMPLETE_CYCLE_CAD_LAYOUT_DATA_ABI_V1'


def main():
    purpose = json.loads((REPORTS / 'CPU208_PURPOSE_FROZEN.json').read_text())
    assert purpose['ID'] == TRIAL and purpose['control_steps'] == 360 and purpose['envs'] == 8
    for row in purpose['source_rows']:
        raw = Path(row['path']).read_bytes()
        assert len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['SHA']
    with (REPORTS / 'CPU208_ONCE_CONSUMED.json').open('x', encoding='utf8') as f:
        json.dump(dict(ID=TRIAL, epoch=time.time(), consumed=True), f)
    import torch as t
    assert not t.cuda.is_initialized()
    t.set_num_threads(1)
    groups = []; negative = []
    for path in SRC.glob('*.py'):
        compile(ast.parse(path.read_bytes(), filename=str(path)), str(path), 'exec')
    groups.append('complete_new_source_graph_syntax_no_SDK_import')
    from course_math208 import layout_origins, route_for_env, outside_course_xy, COURSE_X, COURSE_Y, ROAD_X
    origins = layout_origins(8)
    assert len({tuple(v) for v in origins}) == 8
    assert abs(route_for_env(0)['spawn_ground_xy'][0] - 5.85) < 1e-7
    assert abs(route_for_env(1)['spawn_ground_xy'][0] - 9.15) < 1e-7
    assert all(not outside_course_xy(x, 6.45) for x in (5.85, ROAD_X[0], ROAD_X[1], 9.15))
    assert outside_course_xy(COURSE_X[0] - .001, 6.45)
    assert outside_course_xy(7., COURSE_Y[1] + .001)
    assert layout_origins(20000)[0][2] == 0
    # Source must reference original complete CAD, not scale the old35mm heights.
    field_source = (SRC / 'field208.py').read_text()
    assert 'assets/arena_collision.usdc' in field_source and 'SetInstanceable(True)' in field_source
    assert 'normalized_height' not in field_source and 'sin(' not in field_source
    groups.append('original_CAD_reference_translation_layout_and_full_route_extent')

    import w35_base208
    class MemoryRows:
        def __init__(self, directory, name, schema, maximum_bytes=0):
            self.rows = []; self.schema = schema; self.closed = False
        def append(self, row):
            self.rows.append(dict(row)); return True
        def finish(self):
            self.closed = True
            return dict(path='MEMORY_ONLY_SYNTHETIC208', rows=len(self.rows), bytes=0,
                        SHA=None, schema=self.schema, retention_limited=False,
                        actual_robot_raw_saved=False)
    w35_base208.TypedRows = MemoryRows
    from skill_cycle208 import FullWorldCycle208
    n = 8
    env = SimpleNamespace(_e1_episode=t.zeros(n, dtype=t.long), _sim_step_counter=0)
    cmd = SimpleNamespace(_env=env, num_envs=n, device='cpu',
        command=t.zeros(n, 3), direction=t.zeros(n), signed_yaw=t.tensor([-2.,2.,2.,-2.,2.,2.,2.,2.]),
        time_left=t.full((n,), 14.), family=t.zeros(n,dtype=t.long),
        is_standing_env=t.tensor([False]*7+[True]), linear=t.zeros(n,dtype=t.bool),
        linear_vx=t.zeros(n), moving=t.tensor([True]*7+[False]),
        eligible_flat=t.ones(n,dtype=t.bool))
    cmd.command[:,2]=cmd.signed_yaw
    book = FullWorldCycle208(t,n,'cpu',HERE)
    book.adopt_observed_initial_packet(dict(term=cmd,ids=t.arange(n),tick=0))
    xy=t.zeros(n,2); heading=t.zeros(n)
    actual_yaw=t.tensor([-2.,2.,2.,-1.,2.,2.,2.,0.])
    speeds=t.tensor([.5,.5,.5,.5,.60,.5,.5,0.])
    for control in range(360):
        env._sim_step_counter=8*control
        if control==50:
            # Natural resampling breaks an incomplete same-UID span. Its old
            # angular credit cannot be credited to the next UID.
            ids=t.tensor([6]); book.original_event('AFTER_ORIGINAL_RESAMPLE',cmd,ids,
                original_prior_timer=t.zeros(1),within_original_reset=False)
        command=cmd.command.clone(); command[:,0]=t.cos(heading)
        command[7]=0
        ctx=dict(control=control,profile_key=w35_base208.profile_key(t,cmd),command=command,
            moving=cmd.moving.clone(),eligible=cmd.eligible_flat.clone(),direction=cmd.direction.clone(),
            signed_yaw=cmd.signed_yaw.clone(),heading=heading.clone(),before_root_xy=xy.clone())
        book.begin(cmd,ctx)
        xy[:,0]+=speeds*.02; xy[2,1]+=.08*.02; heading+=actual_yaw*.02
        terminated=t.zeros(n,dtype=t.bool); truncated=t.zeros_like(terminated)
        if control==157:
            terminated[5]=True
        reasons=dict(base_contact=terminated.clone(),time_out=truncated.clone())
        env._sim_step_counter+=8
        book.observe208(ctx,xy.clone(),heading.clone(),[t.zeros(n) for _ in range(3)],
            terminated,truncated,physics_end_tick=env._sim_step_counter,termination_reasons=reasons)
        if control==157:
            ids=t.tensor([5]); book.original_event('BEFORE_ORIGINAL_RESET',cmd,ids)
            env._e1_episode[ids]+=1
            book.original_event('AFTER_ORIGINAL_RESAMPLE',cmd,ids,
                original_prior_timer=t.ones(1),within_original_reset=True)
    value=book.finish()
    complete=[r for r in book.cycle_records.rows if r['complete_sampled_span']]
    partial=[r for r in book.cycle_records.rows if not r['complete_sampled_span']]
    assert complete and partial
    def first(env_id):
        return next(r for r in complete if r['env_id']==env_id)
    assert first(0)['original_strict_cycle_observed_pass']
    assert first(1)['original_strict_cycle_observed_pass']
    assert first(0)['actual_signed_yaw_increment_rad'] < 0
    assert first(0)['original_commanded_signed_yaw_integral_rad'] < 0
    assert not first(2)['original_strict_cycle_observed_pass']
    assert first(2)['actual_world_cross_speed_m_s'] > .05
    assert not first(3)['original_strict_cycle_observed_pass']
    assert first(3)['signed_yaw_error_rad_s'] > .2
    assert not first(4)['original_strict_cycle_observed_pass']
    terminal=first(5)
    assert terminal['non_timeout_before_reset'] and terminal['original_terminal_reason_base_contact']
    assert terminal['command_uid']==1 and terminal['original_episode_uid']==0
    assert any(r['env_id']==6 and r['command_uid']==2 and r['first_control']>=50 for r in complete)
    assert not any(r['env_id']==7 for r in complete)
    groups.append('360x8_synthetic_natural_UID_cross_signedyaw_terminal_partial_and_resample')

    from transition208 import MeasuredClock208, validate_natural_pair
    clock=MeasuredClock208(0,0,8,(10000,20000),tuple(range(1,9)))
    dims=dict(s=127,s1=127,a=6,xi=31,original_policy35=35,original_teacher_raw6=6,
              original_critic38=38,auxiliary_before54=54,auxiliary_terminal54=54)
    pair={k:t.arange(n*d,dtype=t.float32).reshape(n,d)*.001 for k,d in dims.items()}
    pair.update(episode_uid=t.arange(n),command_uid=t.ones(n,dtype=t.long),
        terminated_before_reset=t.zeros(n,dtype=t.bool),timeout_before_reset=t.zeros(n,dtype=t.bool),
        eight_processed_targets6=t.arange(n*8*6,dtype=t.float32).reshape(n,8,6)*.001,
        all_original_reason_masks={'closure':t.zeros(n,dtype=t.bool)})
    assert validate_natural_pair(t,pair,clock,n)
    cases=[]
    bad=dict(pair);bad.pop('auxiliary_terminal54');cases.append(('missing_dynamic54',bad,clock))
    bad=dict(pair);bad['xi']=t.zeros(n,30);cases.append(('wrong_static31',bad,clock))
    bad=dict(pair);bad['eight_processed_targets6']=t.zeros(n,7,6);cases.append(('missing_substep',bad,clock))
    bad=dict(pair);bad['episode_uid']=t.zeros(n);cases.append(('wrong_UID_dtype',bad,clock))
    bad=dict(pair);bad['s1']=pair['s1'].clone();bad['s1'][0,0]=float('nan');cases.append(('nonfinite_terminal',bad,clock))
    cases.append(('100Hz_not_50Hz',pair,MeasuredClock208(0,0,4,(10000,20000),tuple(range(1,5)))))
    cases.append(('feedback_clock_wrong',pair,MeasuredClock208(0,0,8,(5000,15000),tuple(range(1,9)))))
    for name,bad,c in cases:
        try:validate_natural_pair(t,bad,c,n)
        except ValueError:negative.append(name)
        else:raise AssertionError('Expected negative rejection '+name)
    groups.append('strict127_54_31_6_eighttargets_feedback_and_original_UID_ABI')
    assert not t.cuda.is_initialized()
    report=dict(ID=TRIAL,passed=True,epoch=time.time(),groups=groups,
        negative_refusals=negative,synthetic_control_steps=360,synthetic_envs=n,
        synthetic_population_control_pairs=360*n,synthetic_cycle_events=len(complete),
        synthetic_partial_events=len(partial),synthetic_counts=value['full_world208'],
        original_model_opens=0,original_JSONL_opens=0,NPZ_or_USD_opens=0,
        SDK_imports=0,remote_calls=0,neural_updates=0,CUDA_initialized=False,
        actual_W35_skill_accepted=False,actual_RM70_scene_or_training_admitted=False,
        full_SuperMimic_conversion=False,Git_status='PENDING_ROOT_UNIQUE208_ARCHIVE')
    with (REPORTS/'CPU208_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
    print(json.dumps({k:report[k] for k in ('ID','passed','groups','negative_refusals','synthetic_cycle_events')},ensure_ascii=False))


if __name__=='__main__':
    try:main()
    except BaseException:
        with (REPORTS/('CPU208_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:
            json.dump(dict(ID=TRIAL,traceback=traceback.format_exc(),robot_failure=False),f,indent=2)
        raise
