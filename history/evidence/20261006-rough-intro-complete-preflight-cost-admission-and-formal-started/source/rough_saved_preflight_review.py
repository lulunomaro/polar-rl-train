"""Review saved, complete rough PPO execution; throughput is a cost diagnostic.

This module does not execute PPO, change the canonical ledger or alter any
original rejection. It is deliberately bound to the named R preflight runs.
"""
import math,re
from pathlib import Path
VERSION='rough_complete_bounded_PPO_throughput_diagnostic_v1'
SOURCE_SHA='2f82374fe07a849dbbaeabbf8dd34b20d0df8da789f2ebc2be3e688a1b24498a'
ERROR_MARKERS=('Traceback (most recent last)','Traceback (most recent call last)','PhysX error:','simulation will miss interactions','buffer overflow','cooking failure','Unable to create triangle mesh','BV4 tree failed','CUDA out of memory','OutOfMemoryError','non-finite','nan detected')

def execution_contract(record,count,iterations,env,sha_map):
    m=record['manifest'];latest=record['latest'];saved=record['checkpoint'];times=record['iteration_seconds']
    assert record['source_sha256']==SOURCE_SHA and m['init_checkpoint_sha256']==SOURCE_SHA
    assert m['num_envs']==count and m['additional_iterations_arg']==iterations and m['start_iteration']==23509
    assert len(times)==iterations and all(math.isfinite(x) and x>0 for x in times)
    assert record['total_steps']==count*24*iterations
    assert latest['pid']==record['expected_pid'] and latest['checkpoint']==saved['path']
    assert latest['iteration']==saved['iteration_stored']==23509+iterations-1 and saved['finite_tensors']==68
    assert record['owner_exited'] and record['settled_segment_count']==1 and record['segment_seconds']>0
    assert record['segment_seconds']<=600.25 and record['errors']==[] and record['normal_shutdown']
    actual=dict(m['env']);actual.pop('RM_RESCUE_DEADLINE',None);assert actual==env
    assert env['RM_KEEP_STD']=='1' and env['RM_MILD_DR_PROFILE']=='white_v3'
    assert record['run_freeze']['sha256']==sha_map
    assert m['actual_rough_intro']['actual_plane_removed'] and not m['actual_rough_intro']['scan_in_observation']
    assert m['actual_rough_intro']['complete_joint_reset']==30
    assert m['actual_rough_intro']['body_vx_range']==[-.3,.3] and m['actual_rough_intro']['yaw_range']==[0.,0.]
    rate=count*24/(sum(times)/len(times))
    return dict(execution_complete=True,discarded_weights=True,requested_full_iterations=iterations,environment_policy_steps_per_second=rate,old_23000_throughput_contract_pass=count!=20000 or rate>=23000,throughput_is_cost_diagnostic_for_this_rough_lesson=True,version=VERSION)

def review_saved(ctl,prior):
    prior=Path(prior);P=ctl.P;w=ctl.w;base=ctl.base
    freeze=w.read(prior/'reports/SOURCE_FREEZE.json')['sha256']
    for n,h in freeze.items():assert base.sha(prior/n)==h,n
    env=w.read(prior/'isaac/mod4/env.json');b=base.budget_state()
    assert b['active_segment'] is None and not ctl.ctl.S.get('active_training')
    info=base.checkpoint(Path(w.read(prior/'reports/ROUGH_INTRO_STARTED.json')['source']['path']))
    assert info['sha256']==SOURCE_SHA and info['finite_tensors']==68 and info['iteration_stored']==23509
    phase=w.read(prior/'reports/ROUGH_INTRO_COLLISION_COST_STATE.json')
    assert phase['phase']=='repair_hold' and 'Excessive overhead; discard and roll back' in phase['reason']
    records=[]
    for label,count,n,pid in (('auto_0317_rough_collision_cost_128_discard_cap12.5664_white_v3',128,2,500016),('auto_0318_rough_collision_cost_20k_discard_cap12.5664_white_v3',20000,4,500311)):
        log=P/(label+'.log');txt=log.read_text();runs=list((P/'autonomy_preflight_logs').glob('*_'+label));assert len(runs)==1
        run=runs[0];latest=w.read(run/'latest_complete.json');manifest=w.read(run/'run_manifest.json')
        assert manifest['init_checkpoint']==info['path'] and base.sha(Path(manifest['init_checkpoint']))==SOURCE_SHA
        segments=[x for x in b['completed_segments'] if x.get('pid')==pid]
        assert len(segments)==1
        identity=ctl.helpers.identity(pid)
        record=dict(log_path=str(log),log_sha256=base.sha(log),run=str(run),manifest=manifest,latest=latest,checkpoint=base.checkpoint(Path(latest['checkpoint'])),expected_pid=pid,source_sha256=SOURCE_SHA,iteration_seconds=[float(x) for x in re.findall(r'Iteration time:\s*([0-9.]+)s',txt)],total_steps=int(re.findall(r'Total steps:\s*(\d+)',txt)[-1]),owner_exited=not identity or identity['state']=='Z',settled_segment_count=len(segments),segment_seconds=segments[0]['ended_epoch']-segments[0]['started_epoch'],settled_segment=segments[0],errors=[line for line in txt.splitlines() if any(s.lower() in line.lower() for s in ERROR_MARKERS)],normal_shutdown='[INFO]: SimulationContext cleared' in txt,run_freeze=w.read(run/'rolling_source_freeze.json'))
        record['decision']=execution_contract(record,count,n,env,freeze);records.append(record)
    assert not records[1]['decision']['old_23000_throughput_contract_pass']
    paths=[]
    for number,kind,count,steps in ((315,'task_readback',10,300),(316,'fullscale_physical',20000,120)):
        path=P/'reports'/f'auto_{number:04d}_rough_intro_collision_cost_{kind}_cap12.5664_white_v3.json'
        raw=w.read(path);engine=w.read(path.with_name(path.stem+'_engine_error_review.json'))
        assert raw['pass_'] and raw['actual_task_resets']==0 and not raw['nonfinite'] and raw['steps_completed']==steps and raw['alive_count']==count
        assert raw['max_closure_m']<=.002 and raw['max_mimic_rad']<=.01 and raw['all_30_joint_writeback_error']==0
        assert raw['ground_reward_readback_max_error']==raw['ground_height_fresh_query_max_error']==0
        assert raw['initial_parameters']['actual_parameters_pass'] and raw['final_parameters']['actual_parameters_pass']
        assert engine['pass_'] and raw['physical_contact_callback_ticks']>=steps*20
        assert [raw[k] for k in ('actor_obs_dim','critic_obs_dim','action_dim')]==[35,38,6]
        assert raw['exact_collision_partition']['pass_'] and raw['exact_collision_partition']['max_faces_per_collider']==25000
        assert raw['actual_authored_triangle_f32_sha256']=='81348d8b3be401698b7c6b5ca5aecbc95372741ddc051e99b5d2c0df2877c8d5'
        paths.append(dict(path=str(path),sha256=base.sha(path),steps=steps,num_envs=count,max_closure_m=raw['max_closure_m'],max_mimic_rad=raw['max_mimic_rad'],physics_callback_ticks=raw['physical_contact_callback_ticks'],task_resets=0,engine_pass=True,actual_parameters_initial_final_pass=True))
    return dict(pass_=True,admission_version=VERSION,source=info,physical_readbacks=paths,preflights=records,old_rejection_preserved=dict(path=str(prior/'reports/ROUGH_INTRO_COLLISION_COST_STATE.json'),sha256=base.sha(prior/'reports/ROUGH_INTRO_COLLISION_COST_STATE.json'),old_throughput_pass=False),new_PPO_or_probe_executed=False,budget_operations=0,weights_from_preflight_never_used=True,throughput_actual=records[1]['decision']['environment_policy_steps_per_second'],reason='Fixed throughput expectation classified a slower complete valid rough task as an overhead failure. Use measured cost under the same finite deadline and sole canonical budget, while retaining actual task/model/data contracts.',full_target_skill_not_claimed=True)
