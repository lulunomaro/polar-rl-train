"""Prepare one approved H1 reward change as a small overlay on frozen455."""
from pathlib import Path
import ast
import hashlib
import io
import json
import time
import tokenize

S = Path('F:/RMPOLAR-RL/mjcf_mod4_h1_archive_01a1967f_20261102')
T = S/'workspace/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021'
G = Path(__file__).resolve().parents[1]
P = T/'RL_ACTUAL128_RETURN_PPO_PRODUCTION_V455_20261102'
N = S/'runs/h1_attitude_20261103'
H = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
read = lambda p: json.loads(Path(p).read_bytes())


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) if not isinstance(value, str) else value
    with path.open('x', encoding='utf8', newline='\n') as stream:
        stream.write(raw)


def labels(source, substitutions):
    """Change identifiers/report labels, never numeric literals."""
    rows = []
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.type in (tokenize.NAME, tokenize.STRING, tokenize.COMMENT):
            text = token.string
            for old, new in substitutions:
                text = text.replace(old, new)
            token = token._replace(string=text)
        rows.append(token)
    result = tokenize.untokenize(rows)
    ast.parse(result)
    return result


def main():
    assert not N.exists(), 'Existing run must be resumed, never prepared twice'
    approval = read(S/'analysis/20261103_route456_vs446/HUMAN_REWARD_APPROVAL.json')
    assert approval['quote'] == '同意这项姿态奖励修复并继续RL验证'
    proof = read(P/'reports/ROOT455_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json')
    closed = read(P/'reports/ROOT455_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json')
    assert proof['passed'] and proof['totalWM'] == 41575 and proof['Pi'] == 42
    assert closed['owner_closed']['canonical_None'] and closed['owner_closed']['shared_locks_free']
    N.mkdir(parents=True)
    (N/'reports').mkdir()
    (N/'source').mkdir()
    (N/'control').mkdir()
    prior = read(P/'TASK455_FROZEN.json')
    jobbase = '/home/lc01/Zonglin Li/zonglin2/tasks/H1_ATTITUDE464_'+str(time.time_ns())
    task = dict(prior)
    task.update(kind='ACTUAL_ONPOLICY_RESIDUAL_PPO_400N50_V464',
                run_id='ACTUAL_RESIDUAL_PPO464_'+str(time.time_ns()),
                source_SHA=proof['SHA'], model_SHA=proof['SHA'], source_parent_SHA=prior['source_SHA'],
                model_path=closed['roles']['jump_72']['formal']['path'],
                model_bytes=proof['bytes'], source_bytes=proof['bytes'],
                source_WM_updates=41575, window_start_world_updates=41575,
                source_actor_Adam_step=56676, new_tracking_critic_Adam_step=13736,
                source_Adam_step=56676, source_CPU_report_SHA=H(P/'reports/ROOT455_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json'),
                carrier_CPU_receipt_SHA=H(P/'reports/ROOT455_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json'),
                generation='FROZEN_BEFORE_GO_ATTITUDE464', job_root=jobbase+'/tracker72',
                owner_root=jobbase+'/tracker72/control464', control_directory='control464',
                shared_source_root=prior['job_root']+'/source',
                shared_control_root=prior['job_root']+'/control455',
                shared_reference_path=prior['job_root']+'/reference389.npz',
                shared_feedforward_path=prior['job_root']+'/feedforward389.json',
                human_authorization=approval,
                reward_definition='exp(-cost/5), only rotation=(geodesic(R,Rref)/.2rad)^2, existing weight.5; all other terms unchanged',
                reward_protocol=dict(kind='GEODESIC_REFERENCE_ATTITUDE_V1', scale_rad=.2, weight=.5),
                source_cpu_reuse='final455 complete CPU1258 receipt reused; necessary changed-learner CPU fixture recorded separately',
                resume_scope='Fullfinal455actorcriticSTDallAdamEMAoriginWM41575;freshphysicalDRrollout;savedCUDAresidualRNGrestored',
                policy_rollback='none; restoreexactfinal455allstate', actual_reward_unchanged=False,
                predecessor_actual='4560strict0wholeclear/17orientation63full8s; native eight earlyviews and alignedcurves reviewed',
                actor_objective='Actual128controlPPO unchanged; approved attitude scale only',
                new_teacher_read_decode_purpose='Necessary final455 fullstate continuation for human-approved attitude reward scale')
    for key in list(task):
        if key.startswith('CPU') or key in ('CPU389_new_required', 'CPU383_new_required'):
            del task[key]
    overrides = []

    def source(name, text, origin):
        path = N/'source'/name
        write(path, text)
        overrides.append(dict(relative='source/'+name, local_path=str(path), bytes=path.stat().st_size, SHA=H(path), original=origin))

    reward_path = G/'project/train/h1_attitude_reward.py'
    source('h1_attitude_reward.py', reward_path.read_text('utf8'), str(reward_path))
    learner = (P/'source/actual_transition_learner454.py').read_text('utf8')
    learner = labels(learner, [('ActualTransitionLearner454', 'ActualTransitionLearner464'), ('ACTUAL454_', 'ACTUAL464_')])
    learner = learner.replace('(56634, 13694, 36159)', '(56676, 13736, 41575)')
    learner = learner.replace('actor_model_gradient=False,actual_reward_unchanged=True,', 'actor_model_gradient=False,actual_reward_unchanged=False,')
    source('actual_transition_learner464.py', learner, str(P/'source/actual_transition_learner454.py'))
    protocol = labels((P/'tracking_task455.py').read_text('utf8'), [('455', '464')])
    for old, new in [('056410f592d07ff63c3acc6adac4d1ebb0357bc154e817568bec56ba155f18ed', proof['SHA']),
                     ('34229331', str(proof['bytes'])), ('36159', '41575'), ('56634', '56676'), ('13694', '13736')]:
        protocol = protocol.replace(old, new)
    protocol = protocol.replace("assert t['run_id'].startswith", "assert t['reward_protocol']==dict(kind='GEODESIC_REFERENCE_ATTITUDE_V1',scale_rad=.2,weight=.5)\n assert t['run_id'].startswith")
    source('teacher_task464.py', protocol, str(P/'tracking_task455.py'))
    worker = labels((P/'source/worker455.py').read_text('utf8'), [('455', '464')])
    worker = worker.replace("ck['kind']=='ACTUAL_RESIDUAL_PPO445_COMPLETE' and ck['total_WM_updates']==36159 and ck['actual_new_PPO_updates']==169", "ck['kind']=='ACTUAL_RESIDUAL_PPO455_COMPLETE' and ck['total_WM_updates']==41575 and ck['actual_new_PPO_updates']==42")
    worker = worker.replace('36159', '41575').replace('final445', 'final455')
    worker = worker.replace('from actual_transition_learner454 import ActualTransitionLearner454', 'from actual_transition_learner464 import ActualTransitionLearner464')
    worker = worker.replace('ActualTransitionLearner454(', 'ActualTransitionLearner464(')
    worker = worker.replace('from tracking_reference389 import Reference389,tracking_cost389', 'from tracking_reference389 import Reference389\n from h1_attitude_reward import tracking_cost_attitude as tracking_cost389,PROTOCOL as reward_protocol')
    worker = worker.replace("P=a.task.resolve().parent;TASK=json.loads(a.task.read_bytes());validate_task(TASK)", "P=a.task.resolve().parent;TASK=json.loads(a.task.read_bytes());validate_task(TASK)\nsys.path[1:1]=[TASK['shared_source_root'],TASK['shared_source_root']+'/code',TASK['shared_source_root']+'/kernel']")
    worker = worker.replace("str(Path(__file__).resolve().parent/'kernel')", "str(Path(TASK['shared_source_root'])/'kernel')")
    # The first import path setup precedes TASK; keep that harmless local path.
    worker = worker.replace("str(Path(TASK['shared_source_root'])/'kernel')]\nfrom teacher_task", "str(Path(__file__).resolve().parent/'kernel')]\nfrom teacher_task", 1)
    worker = worker.replace("P/'reference389.npz'", "Path(TASK['shared_reference_path'])")
    worker = worker.replace("P/'feedforward389.json'", "Path(TASK['shared_feedforward_path'])")
    worker = worker.replace("state=dict(kind='ACTUAL_RESIDUAL_PPO464_COMPLETE',", "state=dict(kind='ACTUAL_RESIDUAL_PPO464_COMPLETE',reward_protocol=reward_protocol,")
    worker = worker.replace("learner=ActualTransitionLearner464(wm,carrier,reference,real,wmbinding,TASK['carrier_CPU_receipt_SHA'],put)", "learner=ActualTransitionLearner464(wm,carrier,reference,real,wmbinding,TASK['carrier_CPU_receipt_SHA'],put)\n assert reward_protocol['scale_rad']==TASK['reward_protocol']['scale_rad']\n put('ACTUAL464_APPROVED_REWARD_PROTOCOL.json',dict(reward_protocol,other_terms_unchanged=True))")
    source('worker464.py', worker, str(P/'source/worker455.py'))
    task['worker_SHA'] = H(N/'source/worker464.py')
    # One control directory serves both owner and node; unchanged control modules
    # are imported from their pinned original location, rather than recopied.
    for name in ('model2050_240_finite_owner_authority72.py', 'model2050_240_fullstate_slot_node.py', 'three_slot_common_v1.py'):
        text = labels((P/'control455'/name).read_text('utf8'), [('455', '464')])
        bootstrap = "import sys\nsys.path.append("+repr(task['shared_control_root'])+")\n"
        text = bootstrap+text
        if name == 'model2050_240_fullstate_slot_node.py':
            text = text.replace('f=J/row["relative"];assert f.resolve().is_relative_to(J.resolve())', 'f=Path(row["path"]);assert any(f.resolve().is_relative_to(Path(root).resolve()) for root in spec["allowed_source_roots"])')
        write(N/'control'/name, text)
    write(N/'control/teacher_task464.py', protocol)
    # Shared sources are referenced by their existing deployed SHA identities.
    deployed = read(P/'reports/ROOT455_ACTUAL_TASK_MANIFEST_READY_SCHEDULE.json')
    shared = []
    overridden_names = {Path(row['relative']).name for row in overrides}
    for row in deployed['manifest']['files']:
        if row['relative'].startswith('source/') and Path(row['relative']).name in overridden_names:
            continue
        if row['relative'] == 'TASK455.json':
            continue
        shared.append(dict(path=prior['job_root']+'/'+row['relative'], bytes=row['bytes'], SHA=row['SHA'],
                           local_path=str(P/row['relative'])))
    write(N/'SHARED_SOURCE_REFERENCES.json', dict(prior_run=prior['run_id'], files=shared,
                                               no_tree_copy=True, external_source_roots=[prior['job_root']]))
    write(N/'SOURCE_OVERRIDES.json', dict(files=overrides, changed_files_only=True))
    write(N/'TASK464_FROZEN.json', task)
    write(N/'RUN_PATHS.json', dict(scope=str(S), task_root=str(T), prior_root=str(P), repo=str(G),
                                  local_root=str(N), shared_local_source=str(P/'source'), approval=approval))
    for path in [*N.glob('source/*.py'), *N.glob('control/*.py')]:
        ast.parse(path.read_text('utf8'), filename=str(path))
    print(json.dumps(dict(prepared=True, root=str(N), new_source_files=len(overrides),
                          shared_source_references=len(shared), worker_SHA=task['worker_SHA'],
                          source_offsets=[56676,13736,41575], model_reads=0, network=0)))


if __name__ == '__main__':
    main()
