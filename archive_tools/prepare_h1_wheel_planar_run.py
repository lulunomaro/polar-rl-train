"""Prepare470: one planar wheel-position reward overlay on complete468."""
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
P=S/'runs/h1_reward_tail_20261103'
N=S/'runs/h1_wheel_planar_20261103'
A=S/'analysis/20261103_rewardtail469_vs455'
read=lambda p:json.loads(Path(p).read_bytes())
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not N.exists(),'Prepare once, never replace a frozen run'
    final=read(P/'reports/ROOT468_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json')
    closed=read(P/'reports/ROOT468_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json')
    analysis=read(A/'analysis.json')
    assert final['passed']and(final['Pi'],final['totalWM'])==(44,58196)
    assert analysis['actual_all80']['strict']==analysis['actual_all80']['wholeclear']==0
    assert closed['owner_closed']['canonical_None']and closed['owner_closed']['shared_locks_free']
    prior=read(P/'TASK468_FROZEN.json')
    remote='/home/lc01/Zonglin Li/zonglin2/tasks/H1_WHEEL_PLANAR470_'+str(time.time_ns())
    protocol=dict(prior['reward_protocol'],cost_kind='REFERENCE_WHEEL_PLANAR_PLUS_HEIGHT_V1',
                  planar_scale_m=.1,planar_weight=1.,planar_reduction='sum xy then mean two wheels')
    task=dict(prior,kind='ACTUAL_ONPOLICY_RESIDUAL_PPO_400N50_V470',
        run_id='ACTUAL_RESIDUAL_PPO470_'+str(time.time_ns()),source_SHA=final['SHA'],model_SHA=final['SHA'],
        source_parent_SHA=prior['source_SHA'],source_bytes=final['bytes'],model_bytes=final['bytes'],
        model_path=closed['roles']['jump_72']['formal']['path'],source_WM_updates=58196,
        window_start_world_updates=58196,source_actor_Adam_step=56805,source_Adam_step=56805,
        new_tracking_critic_Adam_step=13865,
        source_CPU_report_SHA=H(P/'reports/ROOT468_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json'),
        carrier_CPU_receipt_SHA=H(P/'reports/ROOT468_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json'),
        job_root=remote+'/tracker72',owner_root=remote+'/tracker72/control470',control_directory='control470',
        generation='FROZEN_BEFORE_GO_WHEEL_PLANAR470',mapping_source_root=prior['job_root']+'/source',
        reward_protocol=protocol,reward_definition='1/(1+(existingcost+mean_wheels(sum_xy((actual-planned)/.10m)^2))/5)',
        reward_mapping_source='shared468/h1_tracking_reward.py',
        reward_scale_basis='Observed wheel x lag17-32cm before takeoff; add only planar tracking at10cm scale',
        resume_scope='Exactfinal468 weights/threeAdamWM58196/teacherSTD/EMA/origin/RNG; freshphysicalDRqueue/replay',
        actor_objective='Actual128PPO; only planar wheel reference tracking cost added',
        predecessor_actual='4690strict0wholeclear0leading0topforce; native8early4late andactualcurves reviewed',
        source_cpu_reuse='Final468CPU988finite receipt; one necessary fullrestore continuation fixture',
        new_teacher_read_decode_purpose='Necessary final468 continuation for authorized planar wheel reward repair',
        offline_candidate_SHA=H(A/'WHEEL_PLANAR470_OFFLINE_CANDIDATE.json'))
    task.pop('changed_learner_CPU_receipt_SHA',None)
    for folder in('source','control','reports','evaluation/source','evaluation/reports'):
        (N/folder).mkdir(parents=True,exist_ok=True)
    changes=[]
    def source_file(name,text,origin):
        path=N/'source'/name;write(path,text)
        changes.append(dict(path=str(path),bytes=path.stat().st_size,SHA=H(path),source=str(origin)))
    source_file('h1_wheel_position_reward.py',(G/'project/train/h1_wheel_position_reward.py').read_text('utf8'),G/'project/train/h1_wheel_position_reward.py')
    learner=labels((P/'source/actual_transition_learner468.py').read_text('utf8'),[('468','470')])
    learner=replace_one(learner,'(56761, 13821, 52554)','(56805, 13865, 58196)')
    source_file('actual_transition_learner470.py',learner,P/'source/actual_transition_learner468.py')
    contract=labels((P/'source/teacher_task468.py').read_text('utf8'),[('468','470')])
    for a,b in[(prior['source_SHA'],final['SHA']),('41341082',str(final['bytes'])),('52554','58196'),('56761','56805'),('13821','13865')]:
        contract=contract.replace(a,b)
    contract=replace_one(contract,repr(prior['reward_protocol']),repr(protocol))
    source_file('teacher_task470.py',contract,P/'source/teacher_task468.py')
    worker=labels((P/'source/worker468.py').read_text('utf8'),[('468','470')])
    worker=worker.replace('ACTUAL_RESIDUAL_PPO466_COMPLETE','ACTUAL_RESIDUAL_PPO468_COMPLETE').replace('52554','58196')
    worker=replace_one(worker,"ck['actual_new_PPO_updates']==43","ck['actual_new_PPO_updates']==44")
    worker=replace_one(worker,"sys.path[1:1]=[TASK['shared_source_root']","sys.path[1:1]=[TASK['mapping_source_root'],TASK['shared_source_root']")
    worker=replace_one(worker,'from h1_wheel_height_reward import tracking_cost_wheel_height as tracking_cost389',
        'from h1_wheel_position_reward import tracking_cost_wheel_position as tracking_cost389,PROTOCOL as planar_protocol')
    worker=replace_one(worker,"assert reward_protocol['scale_m']==TASK['reward_protocol']['scale_m']",
        "assert planar_protocol['scale_m']==reward_protocol['planar_scale_m'] and planar_protocol['weight']==reward_protocol['planar_weight']")
    worker=replace_one(worker,'wheel_height=tensor(robot.data.body_pos_w)[:,learner.wheelbodies,2]-real.scene.env_origins[:,None,2]',
        'wheel_position=tensor(robot.data.body_pos_w)[:,learner.wheelbodies,:]-real.scene.env_origins[:,None,:]')
    worker=worker.replace('restoreexactfinal464/allAdamEMA_STD_WM58196','restoreexactfinal468/allAdamEMA_STD_WM58196')
    source_file('worker470.py',worker,P/'source/worker468.py')
    task['worker_SHA']=H(N/'source/worker470.py')
    for name in('model2050_240_finite_owner_authority72.py','model2050_240_fullstate_slot_node.py','three_slot_common_v1.py'):
        write(N/'control'/name,labels((P/'control'/name).read_text('utf8'),[('468','470')]))
    write(N/'control/teacher_task470.py',contract)
    shared=read(P/'SHARED_SOURCE_REFERENCES.json');shared['prior_run']=prior['run_id']
    shared['files'].append(dict(path=prior['job_root']+'/source/h1_tracking_reward.py',
        bytes=(P/'source/h1_tracking_reward.py').stat().st_size,SHA=H(P/'source/h1_tracking_reward.py'),local_path=str(P/'source/h1_tracking_reward.py')))
    shared['external_source_roots'].append(str(Path(prior['job_root']).parent).replace('\\','/'))
    write(N/'SHARED_SOURCE_REFERENCES.json',shared);write(N/'TASK470_FROZEN.json',task)
    paths=dict(read(P/'RUN_PATHS.json'),local_root=str(N),prior_reward_root=str(P),
               shared_mapping_local_source=str(P/'source'),approval=task['human_authorization'])
    write(N/'RUN_PATHS.json',paths);write(N/'SOURCE_OVERRIDES.json',dict(files=changes,no_tree_copy=True))
    run=labels((P/'run.py').read_text('utf8'),[('468','470'),('469','471')])
    for a,b in[('[56761,13821,52554]','[56805,13865,58196]'),
        (".replace('36159','52554').replace('56634','56761').replace('13694','13821')",".replace('36159','58196').replace('56634','56805').replace('13694','13865')"),
        ("code.replace('455','470').replace('36159','52554')","code.replace('455','470').replace('36159','58196')")]:
        run=replace_one(run,a,b)
    run=replace_one(run,"str(PurePosixPath(task['height_source_root']).parent)]",
        "str(PurePosixPath(task['height_source_root']).parent),str(PurePosixPath(task['mapping_source_root']).parent)]")
    run=run.replace('h1_reward_tail|run470','h1_reward_tail|h1_wheel_planar|run470')
    run=run.replace('Fullfinal466 restore; reciprocalmapping sameheight+attitudecost tests','Fullfinal468 restore; planar+height+attitude with unchangedreciprocalmapping tests')
    write(N/'run.py',run)
    cpu=labels((P/'review_final_cpu.py').read_text('utf8'),[('468','470')])
    for a,b in[('52554','58196'),('56761','56805'),('13821','13865')]:cpu=cpu.replace(a,b)
    write(N/'review_final_cpu.py',cpu)
    fixture=(P/'cpu_restore_fixture.py').read_text('utf8')
    fixture=replace_one(fixture,'runs\\\\h1_wheel_height_20261103','runs\\\\h1_reward_tail_20261103')
    fixture=fixture.replace('ROOT466_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL','ROOT468_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL')
    fixture=fixture.replace('ACTUAL_RESIDUAL_PPO466_COMPLETE','ACTUAL_RESIDUAL_PPO468_COMPLETE')
    fixture=replace_one(fixture,"carrier['actual_new_PPO_updates']==43","carrier['actual_new_PPO_updates']==44")
    fixture=labels(fixture,[('ActualTransitionLearner468','ActualTransitionLearner470'),('actual_transition_learner468','actual_transition_learner470'),('CPU468','CPU470')])
    for a,b in[('56761','56805'),('56762','56806'),('13821','13865'),('13822','13866'),('52554','58196')]:fixture=fixture.replace(a,b)
    # Saved468 rewards already use the reciprocal map. These repeated coordinates
    # and generated latents are synthetic, solely a continuation/algorithm fixture.
    fixture=replace_one(fixture,"        row['reward']=1./(1.-row['reward'].clamp(1e-30,1.).log())\n",'')
    fixture=fixture.replace('Necessary final466','Necessary final468')
    write(N/'cpu_restore_fixture.py',fixture)
    for before,after in[('contract469.py','contract471.py'),('target469_parent.py','target471_parent.py')]:
        write(N/'evaluation'/after,labels((P/'evaluation'/before).read_text('utf8'),[('468','470'),('469','471')]))
    evsrc=labels((P/'evaluation/source/evaluate469.py').read_text('utf8'),[('468','470'),('469','471')])
    evsrc=replace_one(evsrc,"sys.path[1:1]=[TASK['shared_source_root']","sys.path[1:1]=[TASK['mapping_source_root'],TASK['shared_source_root']")
    evsrc=replace_one(evsrc,'from h1_wheel_height_reward import tracking_cost_wheel_height as tracking_cost389',
        'from h1_wheel_position_reward import tracking_cost_wheel_position as tracking_cost389')
    evsrc=replace_one(evsrc,'wheel_height=tensor(robot.data.body_pos_w)[:,wheel_ids,2]-real.scene.env_origins[:,None,2]',
        'wheel_position=tensor(robot.data.body_pos_w)[:,wheel_ids,:]-real.scene.env_origins[:,None,:]')
    write(N/'evaluation/source/evaluate471.py',evsrc)
    ev=dict(read(P/'evaluation/TASK469_PENDING.json'),kind='FROZEN470_ACTUAL_RESIDUAL_PPO_EVAL471',
        source_run=task['run_id'],reward_source_root=task['job_root']+'/source',mapping_source_root=task['mapping_source_root'],
        reward_protocol=protocol,worker_SHA=H(N/'evaluation/source/evaluate471.py'),
        human_request='Actualfinal470 planarwheeltracking; same270first80seed9137',
        distinct_evaluation_purpose='Evaluate one planar wheelposition reward repair afterfullsave safeclose')
    write(N/'evaluation/TASK471_PENDING.json',ev)
    write(N/'render_saved_evaluation.py',labels((P/'render_saved_evaluation.py').read_text('utf8'),[('468','470'),('469','471')]))
    for path in N.rglob('*.py'):ast.parse(path.read_text('utf8'),filename=str(path))
    spec=importlib.util.spec_from_file_location('prepared470contract',N/'source/teacher_task470.py')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);mod.validate_task(task)
    write(N/'reports/STATIC_PREPARED_ACTUAL.json',dict(passed=True,root=str(N),source_offsets=[56805,13865,58196],
        reward_protocol=protocol,sourcefiles_changed=4,sharedfiles=len(shared['files']),candidate_SHA=task['offline_candidate_SHA'],
        modelreads=0,network=0,SDK=0,physics=0,freeze_pending_CPU_fixture=True))
    print(json.dumps(dict(prepared=True,root=str(N),offsets=[56805,13865,58196],worker_SHA=task['worker_SHA'])))


if __name__=='__main__':main()
