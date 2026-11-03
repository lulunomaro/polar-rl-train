"""Prepare474: reward executed leg-target limit excess, keep action/physics."""
from pathlib import Path
import ast
import hashlib
import importlib.util
import json
import time

from prepare_h1_attitude_run import write
from prepare_h1_wheel_height_run import labels
from prepare_h1_reward_tail_run import replace_one

G=Path(__file__).resolve().parents[1]
S=Path('F:/RMPOLAR-RL/mjcf_mod4_h1_archive_01a1967f_20261102')
P=S/'runs/h1_attitude_tight_20261103'
N=S/'runs/h1_target_limit_20261103'
A=S/'analysis/20261103_tightattitude473_vs455'
read=lambda p:json.loads(Path(p).read_bytes())
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not N.exists(),'New reward stage only; never replace frozen sources'
    final=read(P/'reports/ROOT472_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json')
    closed=read(P/'reports/ROOT472_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json')
    analysis=read(A/'analysis.json')
    assert final['passed']and(final['Pi'],final['totalWM'])==(45,69534)
    assert analysis['actual_all80']['strict']==analysis['actual_all80']['wholeclear']==0
    assert closed['owner_closed']['canonical_None']and closed['owner_closed']['shared_locks_free']
    prior=read(P/'TASK472_FROZEN.json')
    remote='/home/lc01/Zonglin Li/zonglin2/tasks/H1_TARGET_LIMIT474_'+str(time.time_ns())
    protocol=dict(prior['reward_protocol'],target_limit_scale_rad=.1,target_limit_weight=1.,
                  target_lower_rad=[-1.2,-.5,-1.2,-.5],target_upper_rad=[.9,.5,.9,.5])
    task=dict(prior,kind='ACTUAL_ONPOLICY_RESIDUAL_PPO_400N50_V474',
        run_id='ACTUAL_RESIDUAL_PPO474_'+str(time.time_ns()),source_SHA=final['SHA'],model_SHA=final['SHA'],
        source_parent_SHA=prior['source_SHA'],source_bytes=final['bytes'],model_bytes=final['bytes'],
        model_path=closed['roles']['jump_72']['formal']['path'],source_WM_updates=69534,
        window_start_world_updates=69534,source_actor_Adam_step=56893,source_Adam_step=56893,
        new_tracking_critic_Adam_step=13953,
        source_CPU_report_SHA=H(P/'reports/ROOT472_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json'),
        carrier_CPU_receipt_SHA=H(P/'reports/ROOT472_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json'),
        job_root=remote+'/tracker72',owner_root=remote+'/tracker72/control474',control_directory='control474',
        generation='FROZEN_BEFORE_GO_TARGET_LIMIT474',tight_source_root=prior['job_root']+'/source',
        reward_protocol=protocol,reward_definition='Add meanfourlegs((processedpositiontarget-executablejointinterval distance)/.1rad)^2 weight1; existingcost+reciprocal unchanged',
        reward_scale_basis='Actual473 right-hip target beyond.5rad allfirst20controls; meanrighttarget1.02rad. Oldabs(action)>6overflow0.',
        reward_measurement='Same pre-reset endpoint actual robot joint_pos_target in leftcrank/lefthip/rightcrank/righthip order; wheelbodypositions minusenvorigin',
        resume_scope='Exactfinal472 weights/threeAdamWM69534/teacherSTD/EMA/origin/RNG; freshphysicalDRqueue/replay',
        policy_rollback='none; restoreexactfinal472allstate',
        actor_objective='Actual128PPO; only add executed leg-target limit cost',
        predecessor_actual='4730strict0wholeclear0leading5singlelefttopticks0both; native8early2late+curves reviewed',
        source_cpu_reuse='Final472CPU727finite receipt; one necessary fullrestore continuation fixture',
        new_teacher_read_decode_purpose='Necessary final472 continuation for authorized processedtargetlimit reward repair',
        offline_candidate_SHA=H(A/'TARGET_LIMIT474_OFFLINE_CANDIDATE.json'))
    task.pop('changed_learner_CPU_receipt_SHA',None)
    for folder in('source','control','reports','evaluation/source','evaluation/reports'):
        (N/folder).mkdir(parents=True,exist_ok=True)
    changes=[]
    def source_file(name,text,origin):
        path=N/'source'/name;write(path,text)
        changes.append(dict(path=str(path),bytes=path.stat().st_size,SHA=H(path),source=str(origin)))
    source_file('h1_target_limit_reward.py',(G/'project/train/h1_target_limit_reward.py').read_text('utf8'),G/'project/train/h1_target_limit_reward.py')
    learner=labels((P/'source/actual_transition_learner472.py').read_text('utf8'),[('472','474')])
    learner=replace_one(learner,'(56848, 13908, 63793)','(56893, 13953, 69534)')
    source_file('actual_transition_learner474.py',learner,P/'source/actual_transition_learner472.py')
    contract=labels((P/'source/teacher_task472.py').read_text('utf8'),[('472','474')])
    for a,b in[(prior['source_SHA'],final['SHA']),('42093152',str(final['bytes'])),('63793','69534'),('56848','56893'),('13908','13953')]:
        contract=contract.replace(a,b)
    contract=replace_one(contract,repr(prior['reward_protocol']),repr(protocol))
    source_file('teacher_task474.py',contract,P/'source/teacher_task472.py')
    worker=labels((P/'source/worker472.py').read_text('utf8'),[('472','474')])
    worker=worker.replace('ACTUAL_RESIDUAL_PPO470_COMPLETE','ACTUAL_RESIDUAL_PPO472_COMPLETE').replace('63793','69534')
    worker=replace_one(worker,"ck['actual_new_PPO_updates']==43","ck['actual_new_PPO_updates']==45")
    worker=replace_one(worker,"TASK['planar_source_root']]","TASK['planar_source_root'],TASK['tight_source_root']]")
    worker=replace_one(worker,'from h1_tight_attitude_reward import tracking_cost_tight_attitude as tracking_cost389,PROTOCOL as attitude_protocol',
        'from h1_target_limit_reward import tracking_cost_target_limit as tracking_cost389,PROTOCOL as target_protocol')
    worker=replace_one(worker,"assert attitude_protocol['scale_rad']==reward_protocol['attitude_scale_rad'] and attitude_protocol['weight']==reward_protocol['attitude_weight']",
        "assert target_protocol['scale_rad']==reward_protocol['target_limit_scale_rad'] and target_protocol['weight']==reward_protocol['target_limit_weight']\n assert target_protocol['lower_rad']==reward_protocol['target_lower_rad'] and target_protocol['upper_rad']==reward_protocol['target_upper_rad']")
    worker=replace_one(worker,'wheel_position=tensor(robot.data.body_pos_w)[:,learner.wheelbodies,:]-real.scene.env_origins[:,None,:])',
        'wheel_position=tensor(robot.data.body_pos_w)[:,learner.wheelbodies,:]-real.scene.env_origins[:,None,:],leg_target=tensor(robot.data.joint_pos_target)[:,learner.legs])')
    worker=worker.replace('restoreexactfinal470/allAdamEMA_STD_WM69534','restoreexactfinal472/allAdamEMA_STD_WM69534')
    source_file('worker474.py',worker,P/'source/worker472.py')
    task['worker_SHA']=H(N/'source/worker474.py')
    for name in('model2050_240_finite_owner_authority72.py','model2050_240_fullstate_slot_node.py','three_slot_common_v1.py'):
        write(N/'control'/name,labels((P/'control'/name).read_text('utf8'),[('472','474')]))
    write(N/'control/teacher_task474.py',contract)
    shared=read(P/'SHARED_SOURCE_REFERENCES.json');shared['prior_run']=prior['run_id']
    shared['files'].append(dict(path=prior['job_root']+'/source/h1_tight_attitude_reward.py',
        bytes=(P/'source/h1_tight_attitude_reward.py').stat().st_size,SHA=H(P/'source/h1_tight_attitude_reward.py'),local_path=str(P/'source/h1_tight_attitude_reward.py')))
    shared['external_source_roots'].append(str(Path(prior['job_root']).parent).replace('\\','/'))
    write(N/'SHARED_SOURCE_REFERENCES.json',shared);write(N/'TASK474_FROZEN.json',task)
    paths=dict(read(P/'RUN_PATHS.json'),local_root=str(N),prior_reward_root=str(P),
               shared_tight_local_source=str(P/'source'),approval=task['human_authorization'])
    write(N/'RUN_PATHS.json',paths);write(N/'SOURCE_OVERRIDES.json',dict(files=changes,no_tree_copy=True))
    run=labels((P/'run.py').read_text('utf8'),[('472','474'),('473','475')])
    for a,b in[('[56848,13908,63793]','[56893,13953,69534]'),
        (".replace('36159','63793').replace('56634','56848').replace('13694','13908')",".replace('36159','69534').replace('56634','56893').replace('13694','13953')"),
        ("code.replace('455','474').replace('36159','63793')","code.replace('455','474').replace('36159','69534')")]:
        run=replace_one(run,a,b)
    run=replace_one(run,"str(PurePosixPath(task['planar_source_root']).parent)]",
        "str(PurePosixPath(task['planar_source_root']).parent),str(PurePosixPath(task['tight_source_root']).parent)]")
    run=run.replace('h1_attitude_tight|run474','h1_attitude_tight|h1_target_limit|run474')
    run=run.replace('Fullfinal470 restore; attitude.1scale plus unchangedplanarheightmapping tests','Fullfinal472 restore; targetlimitcost plus unchangedattitudeplanarheightmapping tests')
    write(N/'run.py',run)
    cpu=labels((P/'review_final_cpu.py').read_text('utf8'),[('472','474')])
    for a,b in[('63793','69534'),('56848','56893'),('13908','13953')]:cpu=cpu.replace(a,b)
    write(N/'review_final_cpu.py',cpu)
    fixture=(P/'cpu_restore_fixture.py').read_text('utf8')
    fixture=replace_one(fixture,'runs\\\\h1_wheel_planar_20261103','runs\\\\h1_attitude_tight_20261103')
    fixture=fixture.replace('ROOT470_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL','ROOT472_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL')
    fixture=fixture.replace('ACTUAL_RESIDUAL_PPO470_COMPLETE','ACTUAL_RESIDUAL_PPO472_COMPLETE')
    fixture=replace_one(fixture,"carrier['actual_new_PPO_updates']==43","carrier['actual_new_PPO_updates']==45")
    fixture=labels(fixture,[('ActualTransitionLearner472','ActualTransitionLearner474'),('actual_transition_learner472','actual_transition_learner474'),('CPU472','CPU474')])
    for a,b in[('56848','56893'),('56849','56894'),('13908','13953'),('13909','13954'),('63793','69534')]:fixture=fixture.replace(a,b)
    fixture=fixture.replace('Necessary final470','Necessary final472')
    write(N/'cpu_restore_fixture.py',fixture)
    for before,after in[('contract473.py','contract475.py'),('target473_parent.py','target475_parent.py')]:
        write(N/'evaluation'/after,labels((P/'evaluation'/before).read_text('utf8'),[('472','474'),('473','475')]))
    evsrc=labels((P/'evaluation/source/evaluate473.py').read_text('utf8'),[('472','474'),('473','475')])
    evsrc=replace_one(evsrc,"TASK['planar_source_root']]","TASK['planar_source_root'],TASK['tight_source_root']]")
    evsrc=replace_one(evsrc,'from h1_tight_attitude_reward import tracking_cost_tight_attitude as tracking_cost389',
        'from h1_target_limit_reward import tracking_cost_target_limit as tracking_cost389')
    evsrc=replace_one(evsrc,'wheel_position=tensor(robot.data.body_pos_w)[:,wheel_ids,:]-real.scene.env_origins[:,None,:])',
        'wheel_position=tensor(robot.data.body_pos_w)[:,wheel_ids,:]-real.scene.env_origins[:,None,:],leg_target=tensor(robot.data.joint_pos_target)[:,leg_ids])')
    write(N/'evaluation/source/evaluate475.py',evsrc)
    ev=dict(read(P/'evaluation/TASK473_PENDING.json'),kind='FROZEN474_ACTUAL_RESIDUAL_PPO_EVAL475',
        source_run=task['run_id'],reward_source_root=task['job_root']+'/source',tight_source_root=task['tight_source_root'],
        reward_protocol=protocol,worker_SHA=H(N/'evaluation/source/evaluate475.py'),
        human_request='Actualfinal474 processedlegtargetlimitcost; same270first80seed9137',
        distinct_evaluation_purpose='Evaluate one processedlegtargetlimit reward repair afterfullsave safeclose')
    write(N/'evaluation/TASK475_PENDING.json',ev)
    write(N/'render_saved_evaluation.py',labels((P/'render_saved_evaluation.py').read_text('utf8'),[('472','474'),('473','475')]))
    for path in N.rglob('*.py'):ast.parse(path.read_text('utf8'),filename=str(path))
    spec=importlib.util.spec_from_file_location('prepared474contract',N/'source/teacher_task474.py')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);mod.validate_task(task)
    write(N/'reports/STATIC_PREPARED_ACTUAL.json',dict(passed=True,root=str(N),source_offsets=[56893,13953,69534],
        reward_protocol=protocol,sourcefiles_changed=4,sharedfiles=len(shared['files']),candidate_SHA=task['offline_candidate_SHA'],
        modelreads=0,network=0,SDK=0,physics=0,freeze_pending_CPU_fixture=True,launch_unused=True))
    print(json.dumps(dict(prepared=True,root=str(N),offsets=[56893,13953,69534],worker_SHA=task['worker_SHA'])))


if __name__=='__main__':main()
