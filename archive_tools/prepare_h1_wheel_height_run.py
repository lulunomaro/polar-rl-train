"""Prepare a small466 reward overlay; share455 code and464 attitude source."""
from pathlib import Path
import ast
import hashlib
import importlib.util
import json
import re
import time

from prepare_h1_attitude_run import labels as label_tokens, write

G = Path(__file__).resolve().parents[1]
S = Path('F:/RMPOLAR-RL/mjcf_mod4_h1_archive_01a1967f_20261102')
T = S/'workspace/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021'
P = S/'runs/h1_attitude_20261103'
OLD = T/'RL_ACTUAL128_RETURN_PPO_PRODUCTION_V455_20261102'
N = S/'runs/h1_wheel_height_20261103'
read = lambda p: json.loads(Path(p).read_bytes())
H = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def labels(source, substitutions):
    hashes = {}
    def protect(match):
        key = '__PINNED_SHA_'+str(len(hashes))+'__'
        hashes[key] = match.group()
        return key
    transformed = label_tokens(re.sub(r'\b[0-9a-f]{64}\b', protect, source), substitutions)
    for key, value in hashes.items():
        transformed = transformed.replace(key, value)
    return transformed


def main():
    assert not N.exists(), 'Prepare only once; do not replace a frozen task'
    source = read(P/'reports/ROOT464_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json')
    complete = read(P/'reports/ROOT464_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json')
    analysis = read(S/'analysis/20261103_attitude465_vs455/analysis.json')
    assert source['passed'] and source['Pi'] == 42 and source['totalWM'] == 46967
    assert analysis['actual_all80']['strict'] == analysis['actual_all80']['wholeclear'] == 0
    assert complete['owner_closed']['canonical_None'] and complete['owner_closed']['shared_locks_free']
    N.mkdir(parents=True)
    for name in ('source', 'control', 'reports', 'evaluation', 'evaluation/source', 'evaluation/reports'):
        (N/name).mkdir(exist_ok=True)
    prior = read(P/'TASK464_FROZEN.json')
    remote = '/home/lc01/Zonglin Li/zonglin2/tasks/H1_WHEEL_HEIGHT466_'+str(time.time_ns())
    reward_protocol = dict(kind='REFERENCE_WHEEL_WORLD_HEIGHT_V1', scale_m=.05, weight=1.,
                           attitude_scale_rad=.2, attitude_weight=.5)
    task = dict(prior, kind='ACTUAL_ONPOLICY_RESIDUAL_PPO_400N50_V466',
                run_id='ACTUAL_RESIDUAL_PPO466_'+str(time.time_ns()),
                source_SHA=source['SHA'], model_SHA=source['SHA'], source_parent_SHA=prior['source_SHA'],
                source_bytes=source['bytes'], model_bytes=source['bytes'],
                model_path=complete['roles']['jump_72']['formal']['path'],
                source_WM_updates=46967, window_start_world_updates=46967,
                source_actor_Adam_step=56718, source_Adam_step=56718, new_tracking_critic_Adam_step=13778,
                source_CPU_report_SHA=H(P/'reports/ROOT464_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json'),
                carrier_CPU_receipt_SHA=H(P/'reports/ROOT464_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json'),
                job_root=remote+'/tracker72', owner_root=remote+'/tracker72/control466',
                control_directory='control466', generation='FROZEN_BEFORE_GO_WHEEL_HEIGHT466',
                attitude_source_root=prior['job_root']+'/source',
                reward_protocol=reward_protocol,
                reward_definition='exp(-(attitude464cost+mean(((actual wheelworldz-reference wheelworldz)/.05)^2))/5)',
                reward_measurement='Actual current wheel body centers from same pre-reset endpoint, subtract environment origin z; no future depth or GT map',
                reward_scale_basis='Selected465 wheelbottom shortage .050-.069m; .05m gives one cost unit per5cm perwheel, mean two wheels',
                human_authorization=dict(date='2026-11-03', quote='开始修奖励，奖励都能改', scope='Evidence-directed reward repair; physics/270 acceptance/originalcanonical unchanged'),
                resume_scope='Exactfinal464actorcriticallAdamWM46967STDteacherEMAoriginRNG;freshphysicalDRqueue/replay',
                actor_objective='Actual128PPO unchanged; retain attitude464 and add one worldwheelheight trackingterm',
                source_cpu_reuse='Completefinal464CPU1042 receipt; necessary466fullrestore fixture once',
                predecessor_actual='4650strict0wholeclear/29orientation51full8s; eightnativeearlyviews and6curves reviewed',
                new_teacher_read_decode_purpose='Necessary final464 continuation for authorized worldwheelheight reward',
                deterministic_eval_formula_unchanged=True)
    task.pop('changed_learner_CPU_receipt_SHA', None)
    changes = []
    def source_file(name, text, origin):
        path = N/'source'/name
        write(path, text)
        changes.append(dict(path=str(path), bytes=path.stat().st_size, SHA=H(path), source=str(origin)))
    source_file('h1_wheel_height_reward.py', (G/'project/train/h1_wheel_height_reward.py').read_text('utf8'), G/'project/train/h1_wheel_height_reward.py')
    learner = labels((P/'source/actual_transition_learner464.py').read_text('utf8'), [('464', '466')])
    learner = learner.replace('(56676, 13736, 41575)', '(56718, 13778, 46967)')
    learner = learner.replace('actor_WM_gradients=False,new_reward=False', 'actor_WM_gradients=False,new_reward=True')
    source_file('actual_transition_learner466.py', learner, P/'source/actual_transition_learner464.py')
    protocol = labels((P/'source/teacher_task464.py').read_text('utf8'), [('464', '466')])
    for before, after in [(prior['source_SHA'], source['SHA']), ('38120237', str(source['bytes'])),
                          ('41575', '46967'), ('56676', '56718'), ('13736', '13778')]:
        protocol = protocol.replace(before, after)
    protocol = protocol.replace("dict(kind='GEODESIC_REFERENCE_ATTITUDE_V1',scale_rad=.2,weight=.5)", repr(reward_protocol))
    source_file('teacher_task466.py', protocol, P/'source/teacher_task464.py')
    worker = labels((P/'source/worker464.py').read_text('utf8'), [('464', '466')])
    worker = worker.replace("ck['kind']=='ACTUAL_RESIDUAL_PPO455_COMPLETE' and ck['total_WM_updates']==41575", "ck['kind']=='ACTUAL_RESIDUAL_PPO464_COMPLETE' and ck['total_WM_updates']==46967")
    worker = worker.replace('41575', '46967').replace('final455', 'final464')
    worker = worker.replace("TASK['shared_source_root']+'/kernel']", "TASK['shared_source_root']+'/kernel',TASK['attitude_source_root']]")
    worker = worker.replace('from h1_attitude_reward import tracking_cost_attitude as tracking_cost389,PROTOCOL as reward_protocol', 'from h1_wheel_height_reward import tracking_cost_wheel_height as tracking_cost389,PROTOCOL as reward_protocol')
    worker = worker.replace("reward_protocol['scale_rad']==TASK['reward_protocol']['scale_rad']", "reward_protocol['scale_m']==TASK['reward_protocol']['scale_m']")
    target = "previous_action,frame['actions'][:,[0,1,3,4,2,5]])"
    assert worker.count(target) == 1
    worker = worker.replace(target, "previous_action,frame['actions'][:,[0,1,3,4,2,5]],wheel_height=tensor(robot.data.body_pos_w)[:,learner.wheelbodies,2]-real.scene.env_origins[:,None,2])")
    source_file('worker466.py', worker, P/'source/worker464.py')
    task['worker_SHA'] = H(N/'source/worker466.py')
    for name in ('model2050_240_finite_owner_authority72.py', 'model2050_240_fullstate_slot_node.py', 'three_slot_common_v1.py'):
        write(N/'control'/name, labels((P/'control'/name).read_text('utf8'), [('464', '466')]))
    write(N/'control/teacher_task466.py', protocol)
    shared = read(P/'SHARED_SOURCE_REFERENCES.json')
    shared['files'].append(dict(path=prior['job_root']+'/source/h1_attitude_reward.py',
                                bytes=(P/'source/h1_attitude_reward.py').stat().st_size,
                                SHA=H(P/'source/h1_attitude_reward.py'), local_path=str(P/'source/h1_attitude_reward.py')))
    shared['external_source_roots'].append(str(Path(prior['job_root']).parent).replace('\\', '/'))
    write(N/'SHARED_SOURCE_REFERENCES.json', shared)
    write(N/'TASK466_FROZEN.json', task)
    paths = dict(read(P/'RUN_PATHS.json'), local_root=str(N), prior_reward_root=str(P),
                 shared_attitude_local_source=str(P/'source'), approval=task['human_authorization'])
    write(N/'RUN_PATHS.json', paths)
    write(N/'SOURCE_OVERRIDES.json', dict(files=changes, no_tree_copy=True))
    run = labels((P/'run.py').read_text('utf8'), [('464', '466'), ('465', '467')])
    run = run.replace('[56676,13736,41575]', '[56718,13778,46967]')
    run = run.replace(".replace('36159','41575').replace('56634','56676').replace('13694','13736')", ".replace('36159','46967').replace('56634','56718').replace('13694','13778')")
    run = run.replace("code=code.replace('455','466').replace('36159','41575')", "code=code.replace('455','466').replace('36159','46967')\n    code=code.replace('import sys;sys.path.insert(0,str(C));from report_classification312 import classify_error_reports',\"import sys;classifier=Path(v['spec']['shared_control_root'])/'report_classification312.py';assert hashlib.sha256(classifier.read_bytes()).hexdigest()=='50223444323c1898af61b34821f486d9b6e524425ef5cef191dce87c7d69e78f';sys.path[:0]=[str(C),str(classifier.parent)];from report_classification312 import classify_error_reports\")")
    run = run.replace("allowed_source_roots=[J,str(PurePosixPath(task['shared_source_root']).parent)]", "allowed_source_roots=[J,str(PurePosixPath(task['shared_source_root']).parent),str(PurePosixPath(task['attitude_source_root']).parent)]")
    run = run.replace("Fullfinal455 restore; changed attitude reward known-angle tests", "Fullfinal464 restore; wheelworldheight+attitude reward tests")
    write(N/'run.py', run)
    # Prepare exact CPU reader from the established455 reader, just as run.py does.
    cpu = (OLD/'review455_new_final_full_CPU_once.py').read_text('utf8')
    cpu = cpu.replace('455', '466').replace('36159', '46967').replace('56634', '56718').replace('13694', '13778')
    cpu = cpu.replace('from tracking_task466 import', 'from teacher_task466 import').replace('sys.path.insert(0,str(N));', "sys.path.insert(0,str(N/'source'));")
    cpu = cpu.replace("and s['actual_reward_unchanged']", "and not s['actual_reward_unchanged']")
    write(N/'review_final_cpu.py', cpu)
    for before, after in [('contract465.py', 'contract467.py'), ('target465_parent.py', 'target467_parent.py')]:
        write(N/'evaluation'/after, labels((P/'evaluation'/before).read_text('utf8'), [('464','466'),('465','467')]))
    evaluation = labels((P/'evaluation/source/evaluate465.py').read_text('utf8'), [('464','466'),('465','467')])
    evaluation = evaluation.replace("TASK['reward_source_root']]", "TASK['reward_source_root'],TASK['attitude_source_root']]")
    evaluation = evaluation.replace('from h1_attitude_reward import tracking_cost_attitude as tracking_cost389', 'from h1_wheel_height_reward import tracking_cost_wheel_height as tracking_cost389')
    endpoint = "previous_action,frame['actions'][:,[0,1,3,4,2,5]])"
    assert evaluation.count(endpoint) == 1
    evaluation = evaluation.replace(endpoint, "previous_action,frame['actions'][:,[0,1,3,4,2,5]],wheel_height=tensor(robot.data.body_pos_w)[:,wheel_ids,2]-real.scene.env_origins[:,None,2])")
    write(N/'evaluation/source/evaluate467.py', evaluation)
    # Helper is a pinned shared file, loaded by the existing evaluator path.
    helper = P/'evaluation/source/wheel_geometry220.py'
    write(N/'evaluation/source/wheel_geometry220.py', helper.read_text('utf8'))
    ev = dict(read(P/'evaluation/TASK465_PENDING.json'), kind='FROZEN466_ACTUAL_RESIDUAL_PPO_EVAL467',
              source_run=task['run_id'], reward_source_root=task['job_root']+'/source',
              attitude_source_root=task['attitude_source_root'], reward_protocol=reward_protocol,
              worker_SHA=H(N/'evaluation/source/evaluate467.py'),
              human_request='Actualfinal466wheelworldheight reward; unchangedstrict270first80seed9137',
              distinct_evaluation_purpose='Evaluate authorized wheelheight466 afterfullsave safeclose')
    write(N/'evaluation/TASK467_PENDING.json', ev)
    renderer = labels((P/'render_saved_evaluation.py').read_text('utf8'), [('465','467'),('464','466')])
    write(N/'render_saved_evaluation.py', renderer)
    # CPU fixture preserves all source weights/Adam; new latent samples are synthetic only.
    fixture = (P/'cpu_restore_fixture.py').read_text('utf8')
    fixture = fixture.replace("S=C/'source'", "S=C/'source';A=Path("+repr(str(P))+')')
    fixture = fixture.replace("[str(S),str(N/'source')", "[str(S),str(A/'source'),str(N/'source')")
    fixture = fixture.replace("proofpath=N/'reports/ROOT455_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json'", "proofpath=A/'reports/ROOT464_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json'")
    fixture = fixture.replace('ACTUAL_RESIDUAL_PPO455_COMPLETE', 'ACTUAL_RESIDUAL_PPO464_COMPLETE')
    for before, after in [('ActualTransitionLearner464','ActualTransitionLearner466'),('actual_transition_learner464','actual_transition_learner466'),('CPU464','CPU466'),('ACTUAL464','ACTUAL466'),('56676','56718'),('56677','56719'),('13736','13778'),('13737','13779'),('41575','46967')]:
        fixture = fixture.replace(before, after)
    write(N/'cpu_restore_fixture.py', fixture)
    for path in N.rglob('*.py'):
        ast.parse(path.read_text('utf8'), filename=str(path))
    modspec=importlib.util.spec_from_file_location('prepared466protocol',N/'source/teacher_task466.py')
    module=importlib.util.module_from_spec(modspec);modspec.loader.exec_module(module);module.validate_task(task)
    write(N/'reports/STATIC_PREPARED_ACTUAL.json', dict(passed=True, root=str(N), source_offsets=[56718,13778,46967],
          reward_protocol=reward_protocol, sourcefiles_changed=4, sharedfiles=len(shared['files']),
          modelreads=0, network=0, SDK=0, physics=0, freeze_pending_CPU_fixture=True))
    print(json.dumps(dict(prepared=True,root=str(N),source_offsets=[56718,13778,46967],worker_SHA=task['worker_SHA'])))


if __name__ == '__main__':
    main()
