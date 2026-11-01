"""Prepare an update to the existing hourly heartbeat, preserving its identity."""
from pathlib import Path
import json,tomllib
N=Path(__file__).resolve().parent;R=N/'reports'
old=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
prompt='''每小时继续本聊天MOD4参考轨迹跟踪与定向修复。人类2026-11-01“新跟踪启动”“继续看收尾然后修复”，每轮完整保存安全退出后立即独立评测并真实姿态回放，按结果主动修复或继续，不等催促。保持ACTIVE/currentchat，不新Goal/重复automation；无变化或不可行动静默，只通知实质进展、失败、完成、资源/预算/网络问题和必需用户行动。

首先读取 C:/Users/lulu/Desktop/claude/mjcf/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/FINAL305_DIAGNOSTIC_NAME_RECOVERY_V307_20261102/reports/CURRENT_ACTUAL307_RECOVERED305_EVAL308_REPAIR_WORK_ORDER_V1.json。实际冻结源码/INDEX/ownreceipt/进程/消费once优先。305已完整结束，绝不能再称训练运行中或待评测。原normal305、CPU305、postround306已消费并退出；不再运行。305final32695597B SHA02b6de0af7da488ea459ef01da36e1cfec1cd72009ed9399e9e02f9646020958，Pi2724/Critic2724/newWM2756/total12468/2787controls/222960ownpairs，原fee3603.144765138626s，原closingbalance383272.1536028385s仅历史快照。ownchildrenwaited/原锁free/CNone。最终workerRC0/FINALpass，原node/collector把正常ACTUAL305_H32_PAIRED_REAL_WM_ERROR_BEFORE_PI.json误当致命错误，原qualifiedfalse/CPUKeyError0模型读/postround失败完整保留。

独立307首次formal传回并新CPU307v2完整解码通过609finite张量、actor103/critic106、Adam48257/5317/12468、EMA/teacher17Adam42940/STD/DR/norm/RNG/phase；CPU307v1语法失败保留。独立308已完成同固定edge.8/270平台、新9137DR/episode/80firstepisodes/400controls评测：0/80strict和cross，70姿态终止、10跑满8s，均寿命1.45675s，0closure/mimic/basecontact/lowbase，比30066姿态/14full8s退化。不能原样续305。真实viewer和记录bodypose渲染已打开且当前模型原生视觉看过，4casesx3时点在台阶远前早期倾倒/折腿，.26-.32s失败，无过沿。图在 RECOVERED305_TRACKING_REPLAY_EVAL_V308_20261102/RECORDED308_NATIVE_FRAMES/ACTUAL308_FINAL305_BODY_POSE_SEQUENCE.png。勿为归档/重复评测读模型。

当前定向诊断是新reference任务的物理起始分布：计划MuJoCo firststate和originalreset不同，尚无因果结论；不是291已证伪的35obs默认角ABI假说。309producerIndentationError0network/SDK/model；310共享finitevalidation锁拒绝，SDK/physics/model/GO0，全部once永久保留。新unused311根 REFERENCE_INITIAL_STATE_PHYSICS_PROBE_V311_20261102，run311_probe_once.py和TASK311_FROZEN.json，80env中40originalreset vs40fullplannedreference0reset，同plannedq/dqtarget64controls/512physics。两组仅同DR分布、非完全配对DR；记录实际初始root/q/dq。0模型/优化/账写，无GO，不克隆MPC力矩。先查311是否已CONSUMED/结果，消费后只读结果，不能重跑。

共享资源2026-11-02 01:15本地snapshot仍是W35任务占锁：F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/reports/W35_eval_snapshot_20261102_011546.json，job=/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_W35_FULLDR_EVAL_20261102_010506_1793552706521956800，parent1418833，worker1418842/create1793552711.6，GPU16828f91-2b45-b646-8dc0-9481138e2842，原finitevalidationEX。先读该任务最新本地terminal/release；不能以另一GPU空闲绕共享锁/干扰kill。仅freshLOCALexactCIM识别全部已知controller且serialleaseFREE后才新finiteSSH，已知close/evalcontroller活着只读本地；必要exact已知job的有限只读状态，禁止unknownPID/GPUscan。资源真实释放后执行唯一unused311，经原parent锁/权威准入；若资源仍忙推进本地准备/Git，不重复拒绝311/第二watcher。结果/回放审后按真实证据做同任务修复，不为利用GPU原样再训一小时。

FINAL_REPORT_CLASSIFICATION_REPAIR_V312_20261102已准备未来独立版本node/collector/worker源码并用实际305原诊断验证：只精确识别passedtrue、schema完整/finite的已知WMdiagnostic，其余真实/未知/损坏ERROR仍fatal；新worker诊断名用METRICS。0模型/SDK/网络，此修复尚未部署，原305冻结源/false不改。未来新实际训练版本须包含此修复，不把原305重分类回写历史。

仍是103actor35proprio+9currentdepth+59plannedreference/106critic，连续phase0..249/lookahead0/10/末段停稳pose，H32ownWM BPTT/PPO0/exp(-weightedtrackingcost/5)，Fudanfalse，非自主depth-only学生。MuJoCoMPC轨迹仅计划state参考，不可查询PhysX动作teacher、不力矩cloning。H32只起点已观测anchor+预测pose，episode可复用过去实测anchor，未来depth/GTmap不进actor/H32。305真实paired训练分布H32RMSE.06415m不是独立finalWM测量，也不把304重建context诊断当真实predictionerror。

既有400Nengineeringk2000/50policy100feedback400physics2.5msTGS32/4/fullD0whitev3D1-D7/闭链10mm单envreset/mimic.01rad，原唯一canonical3900/save3600/exit300，不增加预算/grant/copy/refund/clearactive/第二writer。读根AGENTS最新MOD4v1专家统一新资产/契约与注册表，本历史H1还需exactproducerjoin；不要静默改311物理或把它称新资产适配毕业。84x48暂定camera不是实机D435i标定/FPS。成功须核首次飞行越沿/整个轮脚印顶面接触/稳定.5s及接触manifold，loss/COM/腾空不是毕业。

遵根/repoAGENTS和polar-rl-train/docs/ALL_TRIALS_AND_REPORTS_GIT_POLICY.md：305晚收尾/原false、307恢复/语法失败/v2CPU、308评测与实际回放、309localfalse/310锁拒绝/311unused/312修复/所有本轮source/report/automation均归档为独立307phase，阶段IDmod4-final305-recovery-eval308-targeted-repair307；查Git实际recordreceipt与trial对象，已record不重record/retag，后续ordinary补充，push失败续已有objects。旧305tagobjectb81f3e4764d2de9a578840170cb2d588207ded3e/peel240e8ac77d9f06121e96d57e6bdc4a7f7d3a120b，300objectc7f856ecd4e90efbf0dd04b6e53f2c4c24690898/peel9f6381ada8c77b40ba0f5e9cf27154b3286ee7b8及全部旧tags/peels/lqr5848b45a99b8c32af02eb61b507c3f95ab39e4ad保护。PT/NPZ/USD/媒体只实际pathbytes已有SHA索引，不为Git读模型。凭据只沿原memory不输出入Git，SSHfinallyclosed/SESSIONrestored/全局serialFREE。postGit验证仅工具输出，不无限保存追HEAD报告。禁Luna/OpenRouter识图。'''
request=dict(mode='update',id=old['id'],kind=old['kind'],name=old['name'],prompt=prompt,rrule=old['rrule'],status=old['status'],targetThreadId=old['target_thread_id'])
if 'notification_policy' in old:request['notificationPolicy']=old['notification_policy']
for filename,data in [('AUTOMATION307_PRIOR_CONFIG.json',old),('AUTOMATION307_UPDATE_REQUEST.json',request)]:
    with (R/filename).open('x',encoding='utf8')as f:json.dump(data,f,indent=2,ensure_ascii=False)
print(json.dumps(request,ensure_ascii=False))
