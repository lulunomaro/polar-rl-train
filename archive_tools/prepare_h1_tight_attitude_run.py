"""Prepare472: change only attitude scale, retaining the complete470 state."""
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
P=S/'runs/h1_wheel_planar_20261103'
N=S/'runs/h1_attitude_tight_20261103'
A=S/'analysis/20261103_wheelplanar471_vs455'
read=lambda p:json.loads(Path(p).read_bytes())
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not N.exists(),'New reward stage only; never replace a frozen run'
    final=read(P/'reports/ROOT470_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json')
    closed=read(P/'reports/ROOT470_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json')
    analysis=read(A/'analysis.json')
    assert final['passed']and(final['Pi'],final['totalWM'])==(43,63793)
    assert analysis['actual_all80']['strict']==analysis['actual_all80']['wholeclear']==0
    assert closed['owner_closed']['canonical_None']and closed['owner_closed']['shared_locks_free']
    prior=read(P/'TASK470_FROZEN.json')
    remote='/home/lc01/Zonglin Li/zonglin2/tasks/H1_ATTITUDE_TIGHT472_'+str(time.time_ns())
    protocol=dict(prior['reward_protocol'],attitude_scale_rad=.1)
    task=dict(prior,kind='ACTUAL_ONPOLICY_RESIDUAL_PPO_400N50_V472',
        run_id='ACTUAL_RESIDUAL_PPO472_'+str(time.time_ns()),source_SHA=final['SHA'],model_SHA=final['SHA'],
        source_parent_SHA=prior['source_SHA'],source_bytes=final['bytes'],model_bytes=final['bytes'],
        model_path=closed['roles']['jump_72']['formal']['path'],source_WM_updates=63793,
        window_start_world_updates=63793,source_actor_Adam_step=56848,source_Adam_step=56848,
        new_tracking_critic_Adam_step=13908,
        source_CPU_report_SHA=H(P/'reports/ROOT470_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json'),
        carrier_CPU_receipt_SHA=H(P/'reports/ROOT470_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json'),
        job_root=remote+'/tracker72',owner_root=remote+'/tracker72/control472',control_directory='control472',
        generation='FROZEN_BEFORE_GO_ATTITUDE_TIGHT472',planar_source_root=prior['job_root']+'/source',
        reward_protocol=protocol,reward_definition='Samecost+mapping; only geodesic reference attitude scale .2rad to .1rad, weight.5 unchanged',
        reward_scale_basis='Actual471 pitch21-22deg at.4s vs6.55deg reference; takeoffpitch30-33deg vs1.59deg',
        resume_scope='Exactfinal470 weights/threeAdamWM63793/teacherSTD/EMA/origin/RNG; freshphysicalDRqueue/replay',
        actor_objective='Actual128PPO; only reference attitude normalization scale changes',
        predecessor_actual='4710strict0wholeclear0leading0topforce; native8early4late andactualcurves reviewed',
        source_cpu_reuse='Final470CPU1735finite receipt; one necessary fullrestore continuation fixture',
        new_teacher_read_decode_purpose='Necessary final470 continuation for authorized attitude scale repair',
        offline_candidate_SHA=H(A/'ATTITUDE_SCALE472_OFFLINE_CANDIDATE.json'))
    task.pop('changed_learner_CPU_receipt_SHA',None)
    for folder in('source','control','reports','evaluation/source','evaluation/reports'):
        (N/folder).mkdir(parents=True,exist_ok=True)
    changes=[]
    def source_file(name,text,origin):
        path=N/'source'/name;write(path,text)
        changes.append(dict(path=str(path),bytes=path.stat().st_size,SHA=H(path),source=str(origin)))
    source_file('h1_tight_attitude_reward.py',(G/'project/train/h1_tight_attitude_reward.py').read_text('utf8'),G/'project/train/h1_tight_attitude_reward.py')
    learner=labels((P/'source/actual_transition_learner470.py').read_text('utf8'),[('470','472')])
    learner=replace_one(learner,'(56805, 13865, 58196)','(56848, 13908, 63793)')
    source_file('actual_transition_learner472.py',learner,P/'source/actual_transition_learner470.py')
    contract=labels((P/'source/teacher_task470.py').read_text('utf8'),[('470','472')])
    for a,b in[(prior['source_SHA'],final['SHA']),('35883815',str(final['bytes'])),('58196','63793'),('56805','56848'),('13865','13908')]:
        contract=contract.replace(a,b)
    contract=replace_one(contract,repr(prior['reward_protocol']),repr(protocol))
    source_file('teacher_task472.py',contract,P/'source/teacher_task470.py')
    worker=labels((P/'source/worker470.py').read_text('utf8'),[('470','472')])
    worker=worker.replace('ACTUAL_RESIDUAL_PPO468_COMPLETE','ACTUAL_RESIDUAL_PPO470_COMPLETE').replace('58196','63793')
    worker=replace_one(worker,"ck['actual_new_PPO_updates']==44","ck['actual_new_PPO_updates']==43")
    worker=replace_one(worker,"TASK['height_source_root']]","TASK['height_source_root'],TASK['planar_source_root']]")
    worker=replace_one(worker,'from h1_wheel_position_reward import tracking_cost_wheel_position as tracking_cost389,PROTOCOL as planar_protocol',
        'from h1_tight_attitude_reward import tracking_cost_tight_attitude as tracking_cost389,PROTOCOL as attitude_protocol')
    worker=replace_one(worker,"assert planar_protocol['scale_m']==reward_protocol['planar_scale_m'] and planar_protocol['weight']==reward_protocol['planar_weight']",
        "assert attitude_protocol['scale_rad']==reward_protocol['attitude_scale_rad'] and attitude_protocol['weight']==reward_protocol['attitude_weight']")
    worker=worker.replace('restoreexactfinal468/allAdamEMA_STD_WM63793','restoreexactfinal470/allAdamEMA_STD_WM63793')
    source_file('worker472.py',worker,P/'source/worker470.py')
    task['worker_SHA']=H(N/'source/worker472.py')
    for name in('model2050_240_finite_owner_authority72.py','model2050_240_fullstate_slot_node.py','three_slot_common_v1.py'):
        write(N/'control'/name,labels((P/'control'/name).read_text('utf8'),[('470','472')]))
    write(N/'control/teacher_task472.py',contract)
    shared=read(P/'SHARED_SOURCE_REFERENCES.json');shared['prior_run']=prior['run_id']
    shared['files'].append(dict(path=prior['job_root']+'/source/h1_wheel_position_reward.py',
        bytes=(P/'source/h1_wheel_position_reward.py').stat().st_size,SHA=H(P/'source/h1_wheel_position_reward.py'),local_path=str(P/'source/h1_wheel_position_reward.py')))
    shared['external_source_roots'].append(str(Path(prior['job_root']).parent).replace('\\','/'))
    write(N/'SHARED_SOURCE_REFERENCES.json',shared);write(N/'TASK472_FROZEN.json',task)
    paths=dict(read(P/'RUN_PATHS.json'),local_root=str(N),prior_reward_root=str(P),
               shared_planar_local_source=str(P/'source'),approval=task['human_authorization'])
    write(N/'RUN_PATHS.json',paths);write(N/'SOURCE_OVERRIDES.json',dict(files=changes,no_tree_copy=True))
    run=labels((P/'run.py').read_text('utf8'),[('470','472'),('471','473')])
    for a,b in[('[56805,13865,58196]','[56848,13908,63793]'),
        (".replace('36159','58196').replace('56634','56805').replace('13694','13865')",".replace('36159','63793').replace('56634','56848').replace('13694','13908')"),
        ("code.replace('455','472').replace('36159','58196')","code.replace('455','472').replace('36159','63793')")]:
        run=replace_one(run,a,b)
    run=replace_one(run,"str(PurePosixPath(task['mapping_source_root']).parent)]",
        "str(PurePosixPath(task['mapping_source_root']).parent),str(PurePosixPath(task['planar_source_root']).parent)]")
    run=run.replace('h1_wheel_planar|run472','h1_wheel_planar|h1_attitude_tight|run472')
    run=run.replace('Fullfinal468 restore; planar+height+attitude with unchangedreciprocalmapping tests','Fullfinal470 restore; attitude.1scale plus unchangedplanarheightmapping tests')
    write(N/'run.py',run)
    cpu=labels((P/'review_final_cpu.py').read_text('utf8'),[('470','472')])
    for a,b in[('58196','63793'),('56805','56848'),('13865','13908')]:cpu=cpu.replace(a,b)
    write(N/'review_final_cpu.py',cpu)
    fixture=(P/'cpu_restore_fixture.py').read_text('utf8')
    fixture=replace_one(fixture,'runs\\\\h1_reward_tail_20261103','runs\\\\h1_wheel_planar_20261103')
    fixture=fixture.replace('ROOT468_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL','ROOT470_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL')
    fixture=fixture.replace('ACTUAL_RESIDUAL_PPO468_COMPLETE','ACTUAL_RESIDUAL_PPO470_COMPLETE')
    fixture=replace_one(fixture,"carrier['actual_new_PPO_updates']==44","carrier['actual_new_PPO_updates']==43")
    fixture=labels(fixture,[('ActualTransitionLearner470','ActualTransitionLearner472'),('actual_transition_learner470','actual_transition_learner472'),('CPU470','CPU472')])
    for a,b in[('56805','56848'),('56806','56849'),('13865','13908'),('13866','13909'),('58196','63793')]:fixture=fixture.replace(a,b)
    fixture=fixture.replace('Necessary final468','Necessary final470')
    write(N/'cpu_restore_fixture.py',fixture)
    for before,after in[('contract471.py','contract473.py'),('target471_parent.py','target473_parent.py')]:
        write(N/'evaluation'/after,labels((P/'evaluation'/before).read_text('utf8'),[('470','472'),('471','473')]))
    evsrc=labels((P/'evaluation/source/evaluate471.py').read_text('utf8'),[('470','472'),('471','473')])
    evsrc=replace_one(evsrc,"TASK['geometry_source_root']]","TASK['geometry_source_root'],TASK['planar_source_root']]")
    evsrc=replace_one(evsrc,'from h1_wheel_position_reward import tracking_cost_wheel_position as tracking_cost389',
        'from h1_tight_attitude_reward import tracking_cost_tight_attitude as tracking_cost389')
    write(N/'evaluation/source/evaluate473.py',evsrc)
    ev=dict(read(P/'evaluation/TASK471_PENDING.json'),kind='FROZEN472_ACTUAL_RESIDUAL_PPO_EVAL473',
        source_run=task['run_id'],reward_source_root=task['job_root']+'/source',planar_source_root=task['planar_source_root'],
        reward_protocol=protocol,worker_SHA=H(N/'evaluation/source/evaluate473.py'),
        human_request='Actualfinal472 attitude.1scale; same270first80seed9137',
        distinct_evaluation_purpose='Evaluate one attitude scale repair afterfullsave safeclose')
    write(N/'evaluation/TASK473_PENDING.json',ev)
    write(N/'render_saved_evaluation.py',labels((P/'render_saved_evaluation.py').read_text('utf8'),[('470','472'),('471','473')]))
    # This single local timer performs only the unused launch after the exact
    # peer has finished both training and its original-owner independent eval.
    timer=(S/'runs/h1_reward_tail_20261103/start_after_original_release.py').read_text('utf8')
    timer=labels(timer,[('468','472')]);write(N/'start_after_original_release.py',timer)
    peer=read(Path('F:/RMPOLAR-RL/mod4_standing_step200_rlbptt_20261103/CURRENT_WORK_ORDER.json'))
    assert peer['run_id']=='MOD4_STANDING200_RLBPTT_V13_1793670990137789700'
    wait=dict(run_id=peer['run_id'],remote_job=peer['remote_job'],owner=peer['original_owner'],GO=peer['GO'],
              not_before_epoch=peer['GO']['nominal_end_epoch']+900,
              reason='Exact original standingV13 keepscanonical+finiteevaluation throughOWNER_EXIT; localtimeronly')
    write(N/'RESOURCE_WAIT_FROZEN.json',wait)
    for path in N.rglob('*.py'):ast.parse(path.read_text('utf8'),filename=str(path))
    spec=importlib.util.spec_from_file_location('prepared472contract',N/'source/teacher_task472.py')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);mod.validate_task(task)
    write(N/'reports/STATIC_PREPARED_ACTUAL.json',dict(passed=True,root=str(N),source_offsets=[56848,13908,63793],
        reward_protocol=protocol,sourcefiles_changed=4,sharedfiles=len(shared['files']),candidate_SHA=task['offline_candidate_SHA'],
        modelreads=0,network=0,SDK=0,physics=0,freeze_pending_CPU_fixture=True,launch_unused=True))
    print(json.dumps(dict(prepared=True,root=str(N),offsets=[56848,13908,63793],worker_SHA=task['worker_SHA'],waitpeer=wait['run_id'])))


if __name__=='__main__':main()
