"""Record this completed round and its actual native visual review; no physics."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import time

N = Path(__file__).resolve().parent
A = N / 'env20000_scut_stairs_1h_20261104/attempt07'
R = A / 'reports'
G = Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
D = G / 'history/reviews/20261103-mod4v1-scut-native-training'
read = lambda p: json.loads(Path(p).read_bytes())
write = lambda p, v: Path(p).write_text(json.dumps(v, ensure_ascii=False, indent=2)+'\n', encoding='utf8', newline='\n')
facts = read(R / 'POSTROUND_FULL_RETURNED.json')['files']
telemetry = read(R / 'ACTUAL_PATCH07_FINAL_TELEMETRY.json')
logs = read(R / 'FINAL_COMPLETE_LOG_ACTUAL.json')
final = facts['production/FINAL.json']
result = facts['evaluation/RESULT.json']
rows = facts['evaluation/ALL80.json']['first_episodes']
assert final['passed_execution'] and facts['TRAIN_CLOSED.json']['passed_execution']
assert all(not value for value in logs['actual_error_lines'].values())
assert not logs['exact_owner_alive'] and facts['OWNER_EXIT.json']['original_leases_released']
assert all(row['SHA_verified'] for row in read(R/'POSTROUND_FORMAL_TRANSFERS.json')['files'])
renders = [read(A / 'evaluation' / sub / 'RENDER_REPORT.json')
           for sub in ['recorded_native', 'recorded_native_late']]
images = [path for render in renders for path in render['media']]
assert len(images) == 4 and all(Path(p).is_file() for p in images)
assert all(render['NN'] == render['physics_steps'] == 0 for render in renders)
stamp = datetime.now(timezone(timedelta(hours=8))).isoformat()
report = dict(epoch=time.time(), captured_at=stamp,
    status='TRAINING_CLOSED_VALID_FINAL__INDEPENDENT80_AND_ALL4_NATIVE_IMAGES_REVIEWED',
    root=str(A), final=final, actual_onpolicy_samples=final['PPO_updates']*480000,
    Adam_steps=facts['production/LATEST_PROGRESS.json']['gradient']['steps'],
    actual_train_closed=facts['TRAIN_CLOSED.json'], owner_exit=facts['OWNER_EXIT.json'],
    formal_transfers=str(R/'POSTROUND_FORMAL_TRANSFERS.json'),
    exact_original_identities=read(R/'POSTROUND_FULL_RETURNED.json')['exact_original_identities'],
    independent80=dict(recovered=result['scut_stair_recovered'],
        bothup=result['scut_stair_both_up'], anyup=result['scut_stair_any_up'],
        **telemetry['all80'],
        stable_duration_counts={str(t):sum(row['longest_stable_seconds']>=t for row in rows)
                                for t in [.025, .1, .25, .5]},
        both_support_duration_counts={str(t):sum(row['longest_valid_top_seconds']>=t for row in rows)
                                      for t in [.025, .1, .25, .5]},
        recovered_environments=[dict(env=row['env'], longest_stable_seconds=row['longest_stable_seconds'],
            longest_both_support_seconds=row['longest_valid_top_seconds'])
            for row in rows if row['scut_stair_recovered']],
        seed=9137, controls_cap=400, optimizer_operations=0,
        metric_scope='Project observation includes standing/heading/special commands; not an upstream graduation or270mm criterion'),
    current_model_view_image=True, all4_actual_images_reviewed=True,
    images=images, saved_pose_order='wxyz',
    visual_findings=[
        'All four selected bodies settle from spawn during0.02-0.30s; no quaternion reordering applied.',
        'env0 receives zero motion command and remains near the birth centre through8s; this is not evidence of a failed requested traverse.',
        'env1 moves toward negative x and reaches the first visible rising ground late in the episode; continuous raised dual support is only0.0075s.',
        'env40 moves to the positive-x rising ground by0.8-2s and leaves the narrow birth-centred frame; native all80 gives0.3075s bothsupport/0.1825s stable.',
        'env41 travels beyond the narrow birth-centred frame by2s and reaches the actual global boundary at6.48s; its final pose is a boundary timeout, not a completed stable traverse.'
    ],
    complete_logs=dict(report=str(R/'FINAL_COMPLETE_LOG_ACTUAL.json'),
        files={k:{field:row[field] for field in ['path','bytes','SHA']}for k,row in logs['logs'].items()},
        actual_error_lines=logs['actual_error_lines'],
        production_error_present='production/ERROR.json' in logs['files'],
        evaluation_error_present='evaluation/ERROR.json' in logs['files']),
    baseline=dict(source_SHA='0fdd9463205f739daff8713ade26d937846c832fba25392af4e515edc8904f86',
        recovered=2,bothup=56,anyup=60,
        protocol_limit='Earlier source diagnostic lacked restored global boundary timeout; same80/seed/course distribution but not a perfectly matched causal experiment'),
    checkpoint_evidence=dict(format=final['checkpoint']['format'],
        serializer_source=str(G/'project/isaac/mod4v1_scut/checkpoint.py'),
        serializer_fields='actor/critic/STD/Adam/LR/iteration,components,command/physical/globalRNG,queues,counters',
        transfer_SHA_verified=True, independent_native_actor_interface_checked=True,
        final_checkpoint_CPU_deserializations_this_review=0,
        physical_nominals='New constructor nominals remain protected; no old absolute mass/inertia restore'),
    reader_issues=[
        'First final-log reader refused before network because a newly opened local FPS MuJoCo player matched RMPOLAR; rawCIM/error retained.',
        'Inspected player.py/runtime.py; narrow exactPID48896/create17:14:26.364359/pythonw/argv/sourceSHA exception only; no process stopped.',
        'Second read rejected launch-time bash exe versus actual OWNER_STARTED Python exe before reading logs. Corrected reader expectation to exact returned OWNER_STARTED; original PID/create still mandatory.',
        'Recovered only incomplete read; full WORKER/EVAL logs returned, no production launch, physics, modeldecode orcanonicalwrite.'
    ],
    decision=dict(training_execution_valid=True, robust_stair_skill_demonstrated=False,
        clear_improvement_demonstrated=False,
        reason='53 raisedboth at leastonce but only10 maintain dualsupport.5s and2 satisfy complete stablemetric; source diagnostic also2. Hiptarget upperhits remain94.69%/59.47%.',
        next='Keep validfinalffce and inspect actual support interruptions and hiptarget saturation against commands/height before selecting a targeted change; do not repeat an unchanged failed hour.',
        new_training_authorized=False, original_hour_complete=True,
        original_save_deadline=1793782945.8450963, original_nominal_end_epoch=1793783245.8450963,
        no_extension_refund_or_budget_grant=True),
    PT_reads=0,new_physics=0,new_training_launches=0)
review_path=R/'ACTUAL_PATCH07_FINAL_NATIVE_REVIEW.json'
assert not review_path.exists()
write(review_path,report)

# Preserve old dynamic snapshots explicitly while publishing actual closed state.
for path in [N.parents[1]/'admin/CURRENT_STATE.json',D/'WORK_ORDER.json']:
    state=read(path)
    state.setdefault('scut_stair_attempt07_first_running_snapshot',dict(
        current_training=state.get('current_training'), next=state.get('next'),
        scut_stair_training=state.get('scut_stair_training')))
    state['scut_stair_attempt07_closed_native_review']=report
    state['epoch']=report['epoch']
    state['current_training']='SCUT_STAIRS_PATCH07_CLOSED_VALID_FULLV4__80_EVALUATED_ALL4_IMAGES_REVIEWED__NO_LIVE_CONTROLLER'
    state['status']=report['status']
    state['next']='Original authorizedhour complete. Validfinalffce/fullstate preserved; independent80=53bothup/63anyup/2stable, no clear improvement. Analyze existing support interruptions/hiptarget saturation before targetedrepair. No automatic newtrainingwindow orproductiononce replay.'
    current=state.get('scut_stair_training',{})
    current.update(epoch=report['epoch'],status=report['status'],local_controller=None,
        local_role='completed; no live controller',collector_bound=False,
        collector_completed=True,training_completed=True,evaluation_completed=True,
        native_pose_visual_review=True,valid_training=True,final=final,
        owner_exit=facts['OWNER_EXIT.json'],independent80=report['independent80'],
        pending_human_new_window_answer=False,original_hour_complete=True,
        closed_review=str(review_path),robust_stair_skill_demonstrated=False)
    state['scut_stair_training']=current
    if path.name=='WORK_ORDER.json':
        state.update(captured_at=stamp,root=str(A),remote=read(A/'PLAN.json')['remote_root'],
            local_controller=None,local_controller_role='completed; no live controller',
            owner_exit=facts['OWNER_EXIT.json'],final=final,training_completed=True,
            evaluation_completed=True,native_pose_visual_review=dict(completed=True,images=images),
            independent_evaluation=report['independent80'],trained_skill=False,
            actual_samples=report['actual_onpolicy_samples'])
    write(path,state)

markdown='''# attempt07完整保存、原生80评测与接续决定

2026-11-04 17:03已完成训练、安全退出、独立80首局及正式传回；当前已原生查看全部早晚侧顶4图，collector59804与原owner1605308均结束。当前没有本聊天活controller。

本轮20,000环境实际31次PPO、14,880,000 onpolicy样本、5,952physics ticks、620Adam；FULL_V4 final37,849,545B，SHA `ffce8d5ad2662a8981d971906e4b30bba13da38debbf42b6bc68284345f66d8c`。模型、actual400Hz和pose均由原collector核SHA后传回。完整WORKER.log115,474B与EVAL.log15,451B已有限读回，actualerrorlines均0，无production/evalERROR。原owner ownwait/settled/released，未增加预算或延长原SAVE17:02:25.845096/NOMINAL17:07:25.845096。FULL_V4原serializer保存完整学习/RNG/组件/队列/计数器；本次评审不为归档重读PT。

独立80为seed9137/newDR/最多400controls/8s/actual400Hz/0optimizer：53局至少一次双轮升阶、63局至少一轮升阶，只有2局满足连续.5s完整稳定观测指标（env49为1.8275s，env74为.675s）。78局8s评测cap、2局真实globalboundarytimeout、0接触姿态终止；closure/mimic/数值/raw异常重置均0，mean7.97975s。仅10局双轮更高支持连续.5s，说明短暂升阶接触不能替代持续支持。该指标是本项目观察，评测含standing/heading/special命令，不冒充上游毕业或270mm成功。

所有目标/CAD差值合规。四腿motor target MAE约.102/.076/.098/.082rad，左/右hip目标上限命中94.69%/59.47%。第一轴执行clip约.003%，此前100%饱和已不再是当前现象。height平方平均加权项-.01337与其它分项已完整记录；原SCUT的observed_height本来是world root z，再在奖励减raycast ground，不能仅因其负值误判高度错误。当前证据不足以把hip饱和或稳定不足归结为唯一奖励原因。

原生审图：env0命令全零，在出生中心附近停留；env1逐步驶向负x坡阶，连续双轮更高支持仅.0075s；env40在.8–2s驶向正x升阶后离开窄画框，all80确认连续双轮支持.3075s/稳定.1825s；env41至2s离框，6.48s触发globalboundarytimeout。离框不算成功，也不算无故消失。保存pose已是wxyz，未换序，渲染0NN/0新physics。

原有效0fdd来源诊断为56bothup/60anyup/2恢复，本轮53/63/2，没有明确技能提升；旧诊断尚无globalboundarytimeout，比较不当作完全匹配的因果实验。当前已解决20k原生碰撞缓存执行失败，不能因此宣布稳定上阶学成。保留本轮有效final与完整状态，下一步围绕既有400Hz支持中断、命令/高度与hip限位饱和定向分析后选择修复；不原样再开失败小时。人类本次一小时已消费完，新训练窗尚未获授权。

最终日志读者的两次错误均保留：新本地FPS MuJoCo viewer被RMPOLAR宽匹配在网络前拒绝；检查源码后只按确切PID/create/exe/argv/SHA分类。随后读者错误拿launch时bash身份与原owner exec后的Python比较而拒绝，改读returned OWNER_STARTED确切身份后成功。没有重启生产、重跑评测、改canonical或kill其它进程。详见ACTUAL_PATCH07_FINAL_NATIVE_REVIEW及原错误报告。
'''
target=D/'SCUT_STAIRS_ATTEMPT07_FINAL_REVIEW.md'
assert not target.exists()
target.write_text(markdown,encoding='utf8',newline='\n')
launchdoc=D/'SCUT_STAIR_NATIVE_AND_IDLE_GPU_LAUNCH.md'
with launchdoc.open('a',encoding='utf8',newline='\n')as stream:
    stream.write('\n\n## 17:03完整关闭、80评测与原生审图覆盖\n\n'+markdown.split('\n\n',1)[1])
readme=G/'project/isaac/mod4v1_scut/README.md'
text=readme.read_text(encoding='utf8')
heading,rest=text.split('\n',1)
readme.write_text(heading+'\n\n2026-11-04 17:03最新实际：attempt07已完整保存安全退出并正式传回，31PPO/14.88M样本/620Adam，FULL_V4 final SHAffce8d5ad2662a8981d971906e4b30bba13da38debbf42b6bc68284345f66d8c。完整训练/评测日志actualerrorlines0，原owner与collector均结束。独立80为53bothup/63anyup/2连续稳定指标，78评测cap/2boundarytimeout、0闭链/mimic/数值异常；早晚4图已由当前模型原生审看。对比原来源同为2恢复，没有明确技能提升；左/右hip目标上限命中94.69%/59.47%仍待按曲线定向分析。原授权小时已结束，不自动再开窗。详见history/reviews/20261103-mod4v1-scut-native-training/SCUT_STAIRS_ATTEMPT07_FINAL_REVIEW.md。以下各时间段为历史。\n'+rest,encoding='utf8',newline='\n')
print(json.dumps(dict(report=str(review_path),status=report['status'],result=dict(
    PPO=final['PPO_updates'],samples=report['actual_onpolicy_samples'],recovered=2,bothup=53,anyup=63),
    new_physics=0,PT_reads=0)))
