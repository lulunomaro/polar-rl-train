"""Prepare a small H1 continuation overlay from a closed, reviewed run."""
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
P=S/'runs/h1_target_limit_20261103'
N=S/'runs/h1_target_limit_cont_20261103'
read=lambda p:json.loads(Path(p).read_bytes())
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not N.exists(),'Never overwrite a frozen or consumed continuation'
    final=read(P/'reports/ROOT474_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json')
    closed=read(P/'reports/ROOT474_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json')
    review=read(S/'analysis/20261103_targetlimit475_vs455/ALL80_MANIFOLD_AND_TARGET_LIMIT_REVIEW.json')
    assert final['passed']and(final['Pi'],final['totalWM'])==(44,75210)
    assert review['all80']['strict']==review['all80']['wholeclear']==0
    assert review['all80']['both_wheels_top_active_ticks']==166
    assert closed['owner_closed']['canonical_None']and closed['owner_closed']['shared_locks_free']
    prior=read(P/'TASK474_FROZEN.json')
    remote='/home/lc01/Zonglin Li/zonglin2/tasks/H1_TARGET_LIMIT_CONT476_'+str(time.time_ns())
    task=dict(prior,kind='ACTUAL_ONPOLICY_RESIDUAL_PPO_400N50_V476',
        run_id='ACTUAL_RESIDUAL_PPO476_'+str(time.time_ns()),
        source_SHA=final['SHA'],model_SHA=final['SHA'],source_parent_SHA=prior['source_SHA'],
        source_bytes=final['bytes'],model_bytes=final['bytes'],
        model_path=closed['roles']['jump_72']['formal']['path'],source_WM_updates=75210,
        window_start_world_updates=75210,source_actor_Adam_step=56937,source_Adam_step=56937,
        new_tracking_critic_Adam_step=13997,
        source_CPU_report_SHA=H(P/'reports/ROOT474_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json'),
        carrier_CPU_receipt_SHA=H(P/'reports/ROOT474_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json'),
        job_root=remote+'/tracker72',owner_root=remote+'/tracker72/control476',control_directory='control476',
        generation='FROZEN_BEFORE_GO_SAME_REWARD_CONTINUATION476',
        target_source_root=prior['job_root']+'/source',
        resume_scope='Exactfinal474 allnetworks/threeAdamWM75210/teacherSTD/EMA/origin/RNG; freshphysicalDRqueue/replay',
        policy_rollback='none; restoreexactfinal474allstate',
        actor_objective='Actual128PPO; continue exact474reward after improved475contact/targetlimits',
        predecessor_actual='4750strict0wholeclear2leading79airborne;42top7bothenvs166both-ticks;native8early2late reviewed',
        source_cpu_reuse='Final474CPU1294finite receipt; one necessary fullrestore continuation fixture',
        new_teacher_read_decode_purpose='Necessary exactfinal474 continuation with unchanged targetlimit reward',
        reward_changed_since_source=False,
        reward_definition=prior['reward_definition'],
        continuation_decision='Targetlimitcost decreased28-51percent on selectedcases; topcontact expanded from1env5ticks to42env1439ticks,7env166both. Retain reward one window; strict0 notsuccess, full8s decreased.')
    for folder in('source','control','reports','evaluation/source','evaluation/reports'):
        (N/folder).mkdir(parents=True,exist_ok=True)
    changes=[]
    def source_file(name,text,origin):
        path=N/'source'/name;write(path,text)
        changes.append(dict(path=str(path),bytes=path.stat().st_size,SHA=H(path),source=str(origin)))
    def offsets(text):
        for a,b in [('56893','56937'),('13953','13997'),('69534','75210')]:text=text.replace(a,b)
        return text
    learner=offsets(labels((P/'source/actual_transition_learner474.py').read_text('utf8'),[('474','476')]))
    learner=learner.replace('new_reward=True','new_reward=False')
    source_file('actual_transition_learner476.py',learner,P/'source/actual_transition_learner474.py')
    contract=offsets(labels((P/'source/teacher_task474.py').read_text('utf8'),[('474','476')]))
    contract=contract.replace(prior['source_SHA'],final['SHA']).replace('33719905',str(final['bytes']))
    source_file('teacher_task476.py',contract,P/'source/teacher_task474.py')
    worker=offsets(labels((P/'source/worker474.py').read_text('utf8'),[('474','476')]))
    worker=worker.replace('ACTUAL_RESIDUAL_PPO472_COMPLETE','ACTUAL_RESIDUAL_PPO474_COMPLETE')
    worker=replace_one(worker,"ck['actual_new_PPO_updates']==45","ck['actual_new_PPO_updates']==44")
    worker=replace_one(worker,"TASK['tight_source_root']]","TASK['tight_source_root'],TASK['target_source_root']]")
    worker=worker.replace('restoreexactfinal472','restoreexactfinal474')
    source_file('worker476.py',worker,P/'source/worker474.py')
    task['worker_SHA']=H(N/'source/worker476.py')
    for name in('model2050_240_finite_owner_authority72.py','model2050_240_fullstate_slot_node.py','three_slot_common_v1.py'):
        write(N/'control'/name,labels((P/'control'/name).read_text('utf8'),[('474','476')]))
    write(N/'control/teacher_task476.py',contract)
    shared=read(P/'SHARED_SOURCE_REFERENCES.json');shared['prior_run']=prior['run_id']
    shared['files'].append(dict(path=prior['job_root']+'/source/h1_target_limit_reward.py',
        bytes=(P/'source/h1_target_limit_reward.py').stat().st_size,SHA=H(P/'source/h1_target_limit_reward.py'),
        local_path=str(P/'source/h1_target_limit_reward.py')))
    shared['external_source_roots'].append(str(Path(prior['job_root']).parent).replace('\\','/'))
    write(N/'SHARED_SOURCE_REFERENCES.json',shared);write(N/'TASK476_FROZEN.json',task)
    write(N/'RUN_PATHS.json',dict(read(P/'RUN_PATHS.json'),local_root=str(N),prior_reward_root=str(P),
        shared_target_local_source=str(P/'source')))
    write(N/'SOURCE_OVERRIDES.json',dict(files=changes,no_tree_copy=True,reward_source_shared=True))
    run=offsets(labels((P/'run.py').read_text('utf8'),[('474','476'),('475','477')]))
    run=replace_one(run,"str(PurePosixPath(task['tight_source_root']).parent)]",
        "str(PurePosixPath(task['tight_source_root']).parent),str(PurePosixPath(task['target_source_root']).parent)]")
    run=run.replace('h1_target_limit|run476','h1_target_limit|h1_target_limit_cont|run476')
    run=run.replace('Fullfinal472 restore; targetlimitcost plus unchangedattitudeplanarheightmapping tests',
        'Fullfinal474 restore; same474reward retained; existing targetlimit tests reused')
    write(N/'run.py',run)
    write(N/'review_final_cpu.py',offsets(labels((P/'review_final_cpu.py').read_text('utf8'),[('474','476')])))
    fixture=(P/'cpu_restore_fixture.py').read_text('utf8')
    fixture=replace_one(fixture,'runs\\\\h1_attitude_tight_20261103','runs\\\\h1_target_limit_20261103')
    fixture=fixture.replace('ROOT472_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL','ROOT474_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL')
    fixture=fixture.replace('ACTUAL_RESIDUAL_PPO472_COMPLETE','ACTUAL_RESIDUAL_PPO474_COMPLETE')
    fixture=replace_one(fixture,"carrier['actual_new_PPO_updates']==45","carrier['actual_new_PPO_updates']==44")
    fixture=labels(fixture,[('ActualTransitionLearner474','ActualTransitionLearner476'),('actual_transition_learner474','actual_transition_learner476'),('CPU474','CPU476')])
    fixture=offsets(fixture).replace('56894','56938').replace('13954','13998').replace('Necessary final472','Necessary final474').replace('new_reward=True','new_reward=False')
    write(N/'cpu_restore_fixture.py',fixture)
    for before,after in [('contract475.py','contract477.py'),('target475_parent.py','target477_parent.py')]:
        write(N/'evaluation'/after,labels((P/'evaluation'/before).read_text('utf8'),[('474','476'),('475','477')]))
    evsrc=labels((P/'evaluation/source/evaluate475.py').read_text('utf8'),[('474','476'),('475','477')])
    evsrc=replace_one(evsrc,"TASK['tight_source_root']]","TASK['tight_source_root'],TASK['target_source_root']]")
    write(N/'evaluation/source/evaluate477.py',evsrc)
    ev=dict(read(P/'evaluation/TASK475_PENDING.json'),kind='FROZEN476_ACTUAL_RESIDUAL_PPO_EVAL477',
        source_run=task['run_id'],reward_source_root=task['target_source_root'],target_source_root=task['target_source_root'],
        worker_SHA=H(N/'evaluation/source/evaluate477.py'),
        human_request='Actualfinal476 same474reward continuation; same270first80seed9137',
        distinct_evaluation_purpose='Evaluate same-reward continuation afterfullsave safeclose')
    write(N/'evaluation/TASK477_PENDING.json',ev)
    write(N/'render_saved_evaluation.py',labels((P/'render_saved_evaluation.py').read_text('utf8'),[('474','476'),('475','477')]))
    for path in N.rglob('*.py'):ast.parse(path.read_text('utf8'),filename=str(path))
    spec=importlib.util.spec_from_file_location('prepared476contract',N/'source/teacher_task476.py')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);mod.validate_task(task)
    write(N/'reports/STATIC_PREPARED_ACTUAL.json',dict(passed=True,root=str(N),source_offsets=[56937,13997,75210],
        reward_changed_since_source=False,reward_tests_reused=str(P/'reports/REWARD_UNIT_CHECKS_ACTUAL.json'),
        sourcefiles_changed=3,sharedfiles=len(shared['files']),modelreads=0,network=0,SDK=0,physics=0,launch_unused=True))
    print(json.dumps(dict(prepared=True,root=str(N),offsets=[56937,13997,75210],worker_SHA=task['worker_SHA'])))


if __name__=='__main__':main()
