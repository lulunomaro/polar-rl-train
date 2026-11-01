"""Capture human hourly schedule and completed original286 final evidence."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json,time,tomllib
N=Path(__file__).resolve().parent;R=N/'reports';T=N.parent;W=T.parent
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_bytes())
def put(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
app=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
req=read(R/'AUTOMATION286_USER_HOURLY_20261101_UPDATE_REQUEST.json')
assert app['prompt']==req['prompt'].rstrip('\n') and app['rrule']==req['rrule']=='RRULE:FREQ=HOURLY;INTERVAL=1'
assert app['target_thread_id']==req['targetThreadId'] and app['status']=='ACTIVE'
put(R/'AUTOMATION286_USER_HOURLY_20261101_APP_RECEIPT.json',dict(epoch=time.time(),tool_return='Updated automation in the app.',
 automationId='mod4-10',mode='update',status='ACTIVE',requested_frequency='every hour',saved_frequency_exact=True,
 same_target_thread=app['target_thread_id'],request_SHA=H(R/'AUTOMATION286_USER_HOURLY_20261101_UPDATE_REQUEST.json')))
normal=read(R/'ROOT286_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json')
cpu=read(R/'ROOT286_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json')
assert normal['passed_collection'] and normal['owner_closed']['canonical_None'] and normal['owner_closed']['shared_locks_free']
assert set(normal['formals'])=={'jump_72'} and normal['roles']['jump_72']['qualified_formal'] and cpu['passed']
final=normal['roles']['jump_72']['final'];go=final['original_finite_owner_GO']
assert final['actual_new_Pi_updates']==final['actual_new_critic_updates']==2336
assert cpu['total_WM_updates']==7087 and cpu['new_WM_updates']==2368 and cpu['finite_tensors']==600
snapshot=read(R/'ROOT286_STATUS_USER_TIMER_20261101_1929.json')
selected={Path(r['path']).name:read_dict for r in snapshot['full_selected_UTF8'] for read_dict in [json.loads(r['UTF8'])]}
progress=selected['LATEST_PROGRESS.json'];assert progress['controls']==2399
localtime=lambda epoch:datetime.fromtimestamp(epoch,timezone(timedelta(hours=8))).isoformat()
work=dict(epoch=time.time(),status='ACTUAL286_COMPLETE_QUALIFIED_FORMAL_CPU_PASS_HOURLY_MONITOR',
 root=str(N),run_id=normal['run_id'],actual_final_save=localtime(final['final']['save_epoch']),
 actual_updates=dict(Pi=2336,critic=2336,new_WM=2368,total_WM=7087,PPO=0,STD=0,frozen_teacher=0),
 controls=2399,own_transitions=191920,physics_callbacks=19192,feedback_samples=4798,
 termination_counts=progress['original_JUMP_diagnostic']['terminations'],total_terminations=progress['terminated'],
 new_final_formal=normal['formals']['jump_72'],whole_CPU=cpu,
 original_owner_closed=normal['owner_closed']['original_owner_out_or_original_nonexecuting_zombie'],
 canonical_None=True,shared_locks_free=True,private_EX_free=normal['roles']['jump_72']['private_EX_free'],
 original_raw_fee_sum_once=normal['owner_closed']['raw_fee_sum_once'],
 closing_balance_snapshot=normal['owner_closed']['closing_balance_snapshot'],
 consumed_once=['launch286','normal286_v2 collector','review286v2 NEW final whole CPU'],
 old_false_and_trial_tags_preserved=True,teacher_and_STD_preserved=True,complete_three_optimizers=True,
 hourly_automation=dict(id='mod4-10',status='ACTIVE',frequency='every hour',target_thread=app['target_thread_id']),
 next='Independent strict270 held-out physical evaluation and small ground standing/forward/reverse retention need a separate source/Task/admission. No success follows from training counters, COM height, flight counts, or loss. No automatic extra training window/grant or consumed once replay.',
 physical='400Nengineeringk2000/50policy100feedback400physics2.5msTGS32/4/fullD0-D7/closure10mm/mimic.01rad',
 reward='unchanged Fudan19methods16weights; separate declared LQR/MPC state-reference supervision',
 student270mm_skill_evaluated=False,student270mm_success=False,
 normal_receipt=str(R/'ROOT286_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json'),
 CPU_receipt=str(R/'ROOT286_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json'))
put(R/'CURRENT_ACTUAL286_COMPLETED_HOURLY_WORK_ORDER_V4.json',work)
with(R/'AUTOMATION286_PRE_COMPLETION_HOURLY_PROMPT_HISTORICAL.txt').open('x',encoding='utf8')as f:f.write(app['prompt'])
prompt=f'''每小时继续检查本聊天的MOD4既有任务。人类2026-11-01明确“设置定时，然后看一下现在进度如何”，随后更正“巡查改为一个小时一次”。保持每小时一次、当前接续聊天。状态未变化或不可行动时静默，只在完成、失败、实质修复、资源预算网络问题或必需人类行动时通知。

最新主线286已经完成，不能再按旧“正在训练/normal与CPU未执行”的记录重放。首先读取 {N.as_posix()}/reports/CURRENT_ACTUAL286_COMPLETED_HOURLY_WORK_ORDER_V4.json、ROOT286_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json、ROOT286_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json，以实际files/INDEX/进程/原ownreceipt优先。

实际run=LQR_MPC_DEPTH_STUDENT286_1793528911807459700；原GO2026-11-01 18:29:00.362623+08，最终完整save19:29:01.895679+08；worker/node/owner均已正常退出或已核原nonexecutingZ，privateEX和两sharedlocks释放，canonical active_segment=None。原唯一owner计账3602.823357820511秒SUMONCE，closing balance394115.0403189659秒只是该时快照，不复制/清账/退款/新grant。完整原一小时窗口结束，不能自动延长或据巡查偏好新开训练。

实际Pi2336/Critic2336/newWM2368/totalWM7087，2399controls/191920ownpairs/19192physics/4798feedback。STD与frozen teacher更新0，PPO更新0。最终formal32407215B SHA4ace1eec00c763c2e19a858e4a119953ec6b58debcd58fc362c7e281d5d9452d；已经单次传回current_closed286_models/jump_72/formal/model_final.pt，two-hostSHA相等。唯一NEWformalCPU286v2已消费，600finite tensors，actor44/critic47、actor9/Critic8/WM三optimizer全树、原teacher2135/full17Adam42940/STD、norm/RNG/DR/queue/aircontact-actionmemory通过。禁止再执行launch286/normal286_v2 collector/review286v2CPU或旧276/281/283/285已消费once；保留完整历史false/source/INDEX。

训练只说明真实学习和保存完成，不是270mm技能成功。最终7754episode终止，其中7731姿态/23basecontact，closure0/mimic0；无held-out严格270真双轮越沿、首次腾空后顶面脚印接触并稳定.5s的验收。下一项为既有目标下独立strict270 held-out与小型groundstanding/forward/reverse保留评测的源码/新Task/实际准入；必要验证复用已合格证据，不额外发明FP64或新技能关卡。不自动重跑旧评测或加新训练窗/预算。

物理仍400N工程k2000/50policy100feedback400physics2.5msTGS32/4/fullD0white_v3D1-D7/10mm单env闭链重置/.01radmimic。实体闭环/solver/奖励不随10mm改动。复旦19method/16weights/clip2.5dt.02原样，LQR/MPC成功MuJoCo100Hz轨迹sample50Hz仅训练状态标签，单独声明监督loss；不能把力矩当normalized action或把MuJoCo转移混入PhysXWM。学生proprio35+当前D435i几何depth9，critic38+9；teacherGT/未来参考不进actor，H32只起点已观测支撑锚点+预测pose，无未来真depth/GTmap。RayCaster84x48和临时前置mount不等于硬件D435i校准/帧率验收。固定seed72single270平台加8originalE0ground不是held-out任务。Task继承的旧WM_ONLY/Pi_allowed字段已append纠正，实际新typedkind/GO/threeoptimizer与FIRST/final优先，冻结源不热改。

所有新试错/失败/报告/交接/同步验证/automation回执入Git。原phase trial-20261101-mod4-lqr-mpc-teacher-assisted-depth-student286已消费，tagobjecta16478f0982dca42cd05c7fd7f510b41d48676bc/peeled18571a95decc557b82d0afeda3ab8ee9c856d0e7；后续同phase完成报告ordinary补充提交，不重record/retag。新真实阶段才用archive_tools/record_experiment唯一annotatedtrial。push失败续已有objects。模型/raw/NPZ/USD/ZIP/media只真实producerpath/bytes/SHA索引，不能为Git重读或重跑。凭据永不输出/入Git；沿用现有授权memory transport，所有ROOT SSHfinallyclosed/SESSIONrestored/clientleaseFREE，串行fresh exactCIM后连接。全部旧tagobject/peels/lqr5848分支保护，不新增Goal/第二writer，postGit工具核验不追HEAD造报告。'''
request=dict(mode='update',id='mod4-10',kind='heartbeat',name=app['name'],prompt=prompt,
 rrule=app['rrule'],status=app['status'],targetThreadId=app['target_thread_id'])
put(R/'AUTOMATION286_COMPLETED_HOURLY_UPDATE_REQUEST.json',request)
print(json.dumps(dict(passed=True,workorder=str(R/'CURRENT_ACTUAL286_COMPLETED_HOURLY_WORK_ORDER_V4.json'),
 final_save=work['actual_final_save'],updates=work['actual_updates'],hourly_verified=True)))
