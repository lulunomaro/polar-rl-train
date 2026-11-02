"""Prepare468 as a small reward-mapping overlay on complete466 state."""
from pathlib import Path
import ast
import hashlib
import importlib.util
import json
import time

from prepare_h1_attitude_run import write
from prepare_h1_wheel_height_run import labels

G = Path(__file__).resolve().parents[1]
S = Path('F:/RMPOLAR-RL/mjcf_mod4_h1_archive_01a1967f_20261102')
P = S/'runs/h1_wheel_height_20261103'
N = S/'runs/h1_reward_tail_20261103'
read = lambda p: json.loads(Path(p).read_bytes())
H = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def replace_one(text, before, after):
    assert text.count(before) == 1, before
    return text.replace(before, after)


def main():
    assert not N.exists(), 'Preparation only; never replace a frozen run'
    final = read(P/'reports/ROOT466_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json')
    closed = read(P/'reports/ROOT466_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json')
    analysis = read(S/'analysis/20261103_wheelheight467_vs455/analysis.json')
    candidate = read(S/'analysis/20261103_wheelheight467_vs455/RECIPROCAL468_OFFLINE_CANDIDATE.json')
    assert final['passed'] and (final['Pi'],final['totalWM']) == (43,52554)
    assert analysis['actual_all80']['strict'] == analysis['actual_all80']['wholeclear'] == 0
    assert closed['owner_closed']['canonical_None'] and closed['owner_closed']['shared_locks_free']
    for folder in ('source','control','reports','evaluation/source','evaluation/reports'):
        (N/folder).mkdir(parents=True,exist_ok=True)
    prior = read(P/'TASK466_FROZEN.json')
    remote = '/home/lc01/Zonglin Li/zonglin2/tasks/H1_REWARD_TAIL468_'+str(time.time_ns())
    protocol = dict(prior['reward_protocol'],kind='RECIPROCAL_TOTAL_TRACKING_COST_V1',
                    cost_kind=prior['reward_protocol']['kind'],mapping='1/(1+cost/5)',denominator=5.)
    task = dict(prior,kind='ACTUAL_ONPOLICY_RESIDUAL_PPO_400N50_V468',
        run_id='ACTUAL_RESIDUAL_PPO468_'+str(time.time_ns()),source_SHA=final['SHA'],model_SHA=final['SHA'],
        source_parent_SHA=prior['source_SHA'],source_bytes=final['bytes'],model_bytes=final['bytes'],
        model_path=closed['roles']['jump_72']['formal']['path'],source_WM_updates=52554,
        window_start_world_updates=52554,source_actor_Adam_step=56761,source_Adam_step=56761,
        new_tracking_critic_Adam_step=13821,
        source_CPU_report_SHA=H(P/'reports/ROOT466_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json'),
        carrier_CPU_receipt_SHA=H(P/'reports/ROOT466_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json'),
        job_root=remote+'/tracker72',owner_root=remote+'/tracker72/control468',
        control_directory='control468',generation='FROZEN_BEFORE_GO_REWARD_TAIL468',
        height_source_root=prior['job_root']+'/source',reward_protocol=protocol,
        reward_definition='1/(1+(unchanged attitude464 plus wheelheight466 cost)/5)',
        reward_mapping_source='h1_tracking_reward.py',
        reward_scale_basis='Same zero-cost optimum, monotone ordering and local slope; slower tail preserves larger-error signal',
        resume_scope='Exactfinal466 weights/threeAdamWM52554/teacherSTD/EMA/origin/RNG; freshphysicalDRqueue/replay',
        actor_objective='Actual128PPO; only scalar reward mapping changes from exponential to reciprocal',
        predecessor_actual='4670strict0wholeclear0leading0topforce; native8early6late andactualcurves reviewed',
        source_cpu_reuse='Final466CPU1645finite receipt; one necessary fullrestore continuation fixture',
        new_teacher_read_decode_purpose='Necessary final466 continuation for authorized reward mapping repair',
        offline_candidate_SHA=H(S/'analysis/20261103_wheelheight467_vs455/RECIPROCAL468_OFFLINE_CANDIDATE.json'))
    task.pop('changed_learner_CPU_receipt_SHA',None)
    changes = []
    def source_file(name,text,origin):
        path=N/'source'/name
        write(path,text)
        changes.append(dict(path=str(path),bytes=path.stat().st_size,SHA=H(path),source=str(origin)))
    source_file('h1_tracking_reward.py',(G/'project/train/h1_tracking_reward.py').read_text('utf8'),G/'project/train/h1_tracking_reward.py')
    learner=labels((P/'source/actual_transition_learner466.py').read_text('utf8'),[('466','468')])
    learner=replace_one(learner,'(56718, 13778, 46967)','(56761, 13821, 52554)')
    source_file('actual_transition_learner468.py',learner,P/'source/actual_transition_learner466.py')
    contract=labels((P/'source/teacher_task466.py').read_text('utf8'),[('466','468')])
    for a,b in [(prior['source_SHA'],final['SHA']),('36327877',str(final['bytes'])),
                ('46967','52554'),('56718','56761'),('13778','13821')]:
        contract=contract.replace(a,b)
    contract=replace_one(contract,repr(prior['reward_protocol']),repr(protocol))
    source_file('teacher_task468.py',contract,P/'source/teacher_task466.py')
    worker=labels((P/'source/worker466.py').read_text('utf8'),[('466','468')])
    worker=worker.replace('ACTUAL_RESIDUAL_PPO464_COMPLETE','ACTUAL_RESIDUAL_PPO466_COMPLETE')
    worker=worker.replace('46967','52554')
    worker=replace_one(worker,"ck['actual_new_PPO_updates']==42","ck['actual_new_PPO_updates']==43")
    worker=replace_one(worker,"TASK['attitude_source_root']]","TASK['attitude_source_root'],TASK['height_source_root']]")
    worker=replace_one(worker,'from h1_wheel_height_reward import tracking_cost_wheel_height as tracking_cost389,PROTOCOL as reward_protocol',
        "from h1_wheel_height_reward import tracking_cost_wheel_height as tracking_cost389\n from h1_tracking_reward import tracking_reward,PROTOCOL as mapping_protocol\n reward_protocol=TASK['reward_protocol'];assert mapping_protocol['formula']==reward_protocol['mapping']")
    worker=replace_one(worker,'return torch.exp(-cost/5.)','return tracking_reward(cost)')
    source_file('worker468.py',worker,P/'source/worker466.py')
    task['worker_SHA']=H(N/'source/worker468.py')
    for name in ('model2050_240_finite_owner_authority72.py','model2050_240_fullstate_slot_node.py','three_slot_common_v1.py'):
        write(N/'control'/name,labels((P/'control'/name).read_text('utf8'),[('466','468')]))
    write(N/'control/teacher_task468.py',contract)
    shared=read(P/'SHARED_SOURCE_REFERENCES.json')
    shared['prior_run']=prior['run_id']
    shared['files'].append(dict(path=prior['job_root']+'/source/h1_wheel_height_reward.py',
        bytes=(P/'source/h1_wheel_height_reward.py').stat().st_size,
        SHA=H(P/'source/h1_wheel_height_reward.py'),local_path=str(P/'source/h1_wheel_height_reward.py')))
    shared['files'].append(dict(path=prior['job_root']+'/independent467/source/wheel_geometry220.py',
        bytes=(P/'evaluation/source/wheel_geometry220.py').stat().st_size,
        SHA=H(P/'evaluation/source/wheel_geometry220.py'),local_path=str(P/'evaluation/source/wheel_geometry220.py')))
    shared['external_source_roots'].append(str(Path(prior['job_root']).parent).replace('\\','/'))
    write(N/'SHARED_SOURCE_REFERENCES.json',shared)
    write(N/'TASK468_FROZEN.json',task)
    paths=dict(read(P/'RUN_PATHS.json'),local_root=str(N),prior_reward_root=str(P),
               shared_height_local_source=str(P/'source'),approval=task['human_authorization'])
    write(N/'RUN_PATHS.json',paths)
    write(N/'SOURCE_OVERRIDES.json',dict(files=changes,no_tree_copy=True))
    run=labels((P/'run.py').read_text('utf8'),[('466','468'),('467','469')])
    for a,b in [('[56718,13778,46967]','[56761,13821,52554]'),
        (".replace('36159','46967').replace('56634','56718').replace('13694','13778')", ".replace('36159','52554').replace('56634','56761').replace('13694','13821')"),
        ("code.replace('455','468').replace('36159','46967')","code.replace('455','468').replace('36159','52554')")]:
        run=run.replace(a,b)
    run=replace_one(run,"str(PurePosixPath(task['attitude_source_root']).parent)]", "str(PurePosixPath(task['attitude_source_root']).parent),str(PurePosixPath(task['height_source_root']).parent)]")
    run=run.replace('h1_attitude|run468','h1_attitude|h1_wheel_height|h1_reward_tail|run468')
    run=run.replace('Fullfinal464 restore; wheelworldheight+attitude reward tests','Fullfinal466 restore; reciprocalmapping sameheight+attitudecost tests')
    write(N/'run.py',run)
    cpu=labels((P/'review_final_cpu.py').read_text('utf8'),[('466','468')])
    for a,b in [('46967','52554'),('56718','56761'),('13778','13821')]:cpu=cpu.replace(a,b)
    write(N/'review_final_cpu.py',cpu)
    fixture=(P/'cpu_restore_fixture.py').read_text('utf8')
    fixture=replace_one(fixture,"runs\\\\h1_attitude_20261103","runs\\\\h1_wheel_height_20261103")
    fixture=fixture.replace('ROOT464_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL','ROOT466_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL')
    fixture=fixture.replace('ACTUAL_RESIDUAL_PPO464_COMPLETE','ACTUAL_RESIDUAL_PPO466_COMPLETE')
    fixture=replace_one(fixture,"carrier['actual_new_PPO_updates']==42","carrier['actual_new_PPO_updates']==43")
    fixture=labels(fixture,[('ActualTransitionLearner466','ActualTransitionLearner468'),('actual_transition_learner466','actual_transition_learner468'),('CPU466','CPU468')])
    for a,b in [('56718','56761'),('56719','56762'),('13778','13821'),('13779','13822'),('46967','52554')]:fixture=fixture.replace(a,b)
    # A scalar mapping changes critic targets. Relabel only CPU fixture rewards;
    # observations repeat from savedrows and latents are synthetic as before.
    fixture=replace_one(fixture,'row=deepcopy(actual[i%len(actual)])',
        "row=deepcopy(actual[i%len(actual)])\n        row['reward']=1./(1.-row['reward'].clamp(1e-30,1.).log())")
    fixture=fixture.replace('Necessary final455','Necessary final466').replace('Necessary final455 fullrestore','Necessary final466 fullrestore')
    write(N/'cpu_restore_fixture.py',fixture)
    for before,after in [('contract467.py','contract469.py'),('target467_parent.py','target469_parent.py')]:
        write(N/'evaluation'/after,labels((P/'evaluation'/before).read_text('utf8'),[('466','468'),('467','469')]))
    evsrc=labels((P/'evaluation/source/evaluate467.py').read_text('utf8'),[('466','468'),('467','469')])
    evsrc=replace_one(evsrc,"TASK['attitude_source_root']]","TASK['attitude_source_root'],TASK['height_source_root'],TASK['geometry_source_root']]")
    evsrc=replace_one(evsrc,'from h1_wheel_height_reward import tracking_cost_wheel_height as tracking_cost389',
        'from h1_wheel_height_reward import tracking_cost_wheel_height as tracking_cost389\n from h1_tracking_reward import tracking_reward')
    assert evsrc.count('torch.exp(-cost/5.)')==2
    evsrc=evsrc.replace('torch.exp(-cost/5.)','tracking_reward(cost)')
    write(N/'evaluation/source/evaluate469.py',evsrc)
    ev=dict(read(P/'evaluation/TASK467_PENDING.json'),kind='FROZEN468_ACTUAL_RESIDUAL_PPO_EVAL469',
        source_run=task['run_id'],reward_source_root=task['job_root']+'/source',height_source_root=task['height_source_root'],
        geometry_source_root=prior['job_root']+'/independent467/source',
        shared_geometry_SHA=H(P/'evaluation/source/wheel_geometry220.py'),reward_protocol=protocol,
        worker_SHA=H(N/'evaluation/source/evaluate469.py'),human_request='Actualfinal468 reciprocalreward; same270first80seed9137',
        distinct_evaluation_purpose='Evaluate one reward mapping repair afterfullsave safeclose')
    write(N/'evaluation/TASK469_PENDING.json',ev)
    renderer=labels((P/'render_saved_evaluation.py').read_text('utf8'),[('466','468'),('467','469')])
    write(N/'render_saved_evaluation.py',renderer)
    for path in N.rglob('*.py'):ast.parse(path.read_text('utf8'),filename=str(path))
    spec=importlib.util.spec_from_file_location('prepared468contract',N/'source/teacher_task468.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.validate_task(task)
    write(N/'reports/STATIC_PREPARED_ACTUAL.json',dict(passed=True,root=str(N),
        source_offsets=[56761,13821,52554],reward_protocol=protocol,sourcefiles_changed=4,
        sharedfiles=len(shared['files']),candidate_SHA=task['offline_candidate_SHA'],
        modelreads=0,network=0,SDK=0,physics=0,freeze_pending_CPU_fixture=True))
    print(json.dumps(dict(prepared=True,root=str(N),offsets=[56761,13821,52554],worker_SHA=task['worker_SHA'])))


if __name__=='__main__':
    main()
