"""Prepare update of existingmod4-10 after actual416FIRST/sole417timer; no newautomation."""
from pathlib import Path
import json
P = Path(__file__).resolve().parent
R = P / 'reports'
read = lambda path: json.loads(path.read_bytes())
prior = read(R / 'AUTOMATION419_FINAL389_EVAL_FAIL_ACTUALPPO416_STAGED418_REQUEST.json')
work = read(R / 'CURRENT_ACTUAL421_LIVE_PPO416_FIRST_AND_POSTROUND417_WORK_ORDER_V1.json')
assert work['postround417']['started'] and work['actual416']['FIRST_UPDATED_consumed']
prompt = '''每小时继续本聊天MOD4跳270mm。人类明确“我需要的是rl上台阶”，交付为RL实际跳台并稳定；传统MPC成功不是交付。人类已授权新跟踪启动/继续看收尾然后修复。每轮完整保存安全退出后立即独立RL评测与真实姿态回放，按实际证据主动定向修复或合理续训，不等催促。ACTIVE/currentchat，不新Goal/chat/重复automation；无变化或不可行动静默，只通知实质进展、失败、完成、资源/预算/网络问题和必需用户行动。

首先读 C:/Users/lulu/Desktop/claude/mjcf/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/FINAL305_DIAGNOSTIC_NAME_RECOVERY_V307_20261102/reports/CURRENT_ACTUAL421_LIVE_PPO416_FIRST_AND_POSTROUND417_WORK_ORDER_V1.json。实际冻结source/INDEX/ownreceipt/确切进程和结果优先。旧419的416staged/418unused/Pair4active已过时，原报告与原416拒绝保留。418已唯一执行且成功创建原owner/node，416真实GO/FIRST已发生，绝不再launch416/run418/FIRST/bind或重造namespace。

实际416 run=ACTUAL_RESIDUAL_PPO416_1793602132213517800，root=C:/Users/lulu/Desktop/claude/mjcf/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/RL_ACTUAL_RESIDUAL_PPO_PRODUCTION_V416_20261102。原ownerPID1470022/create1793606832.48，node1470031/create1793606832.9，worker1470045/create1793606839.05，完整exe/argv/controlcwd/jobroot见工作单和原launch/snapshot。GPU-c27eecbd-6838-7290-1cd2-37e34522213d。GO2026-11-02T16:07:16.449378+08:00，SAVE17:07:16.449378，NOMINAL17:12:16.449378，normal最早16:57:16.449378。原3900/save3600/exit300/唯一canonicalstrictreserve不改。冻结INDEX416SHAb1e843c8fa3b3e091857a61bc669296a14a0ef5a98ff8076945d429e5e95caeb，workerSHA4257ba795a62542db8951234244d5a8664f2a2691bc8fa96aa267505d3516c0a。健康不restart/hotpatch/重跑startup资源或模型验证。

416是真实actualonpolicy残差PPO，35proprio+9currentdepth+59plannedreference的actor103/critic106；固定347processed50Hz电机前馈+1*tanh(actor-origin)残差，无在线MPC/接管/力矩cloning，非自主depth-only。完整恢复final389SHAc760f8c2e3441756e1d4f6912d019c6bcdaafa456bdf6e48a9ce152395776f99，actorAdam56144/critic13204/WM20419、三Adam/STD/teacher17Adam42940/EMA/normRNG/savedorigin，不resetAdam或回退网络。latentGaussianstd.15固定且原learnedSTD冻结，32controls/2560onpolicy样本/oneepoch/PPOclip.2 gamma.99 GAE.95，实际reward=原exp(-weightedtrackingcost/5)和done直接入actor；WM仍H32独立训练但无actorWMgradient。futureactualdepth/GTmap不进imagination。freshphysicalDRqueue/replay明确，physics/DR/reward/验收保持。

真实FIRST64controls/5120ownpairs/512physics/128feedback，PPO=Pi=critic1，newWM33total20452；actualPPO2560samples actorgrad8.793684005737305/critic28.80631446838379有限非零，terminalbootstrap0/actualdoneGAEtrue/actorWMgradfalse，native24通过。首完整32803321B SHAfb884227d0a45a5fd7eb90c610631ac7953af697a869453ce51222921f74e347，actorAdam56145/critic13205/WM20452，teacher17Adam42940。后续FIRSTsnapshot242controls/19360pairs/PPO6/WM20630/270orientation为训练多episode事件，不是独立80评测，FIRST不是FINAL或技能毕业。后续latestcomplete231controls/PPO6/WM20619已保存，模型原件不为归档再读。

唯一localpostround417已绑定启动：PID18704/create2026-11-02T16:10:30.469554+08:00，script C:/Users/lulu/Desktop/claude/mjcf/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/RL416_SINGLE_PROCESS_POSTROUND_V417_20261102/postround417_close_actual416_eval_once.py，完整exactCIM见421。INDEX417SHA3ff915d8fbd52673b48df98af0a7cb83273b001ef493dbfd31c7ff419d04e912。BIND417/POSTROUND417_ONCE已消费。它localtimer至原normal900，若其它knowncontroller忙只localwait，然后同一localprocess经runpy唯一normal416完整保存/安全退出/fullformaltransfer、新fullCPU offsets56144/13204/20419，再独立417同final一次actor+origin读取、80firstepisodes/400controls8s/seed9137新DR/同fixededge.8/270，actual400Hzcontactmanifold与有限记录bodypose原生渲染。原预算窗不改。

先读417waiter/children/CONSUMED/results；活着不第二watcher/normal/CPU/eval/新SSH，close/eval期间仅本地直至controller释放。结果=C:/Users/lulu/Desktop/claude/mjcf/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/RL_ACTUAL_RESIDUAL_PPO_PRODUCTION_V416_20261102/reports/POSTROUND416_RL_REPLAY_EVAL_DECISION.json。evalroot=C:/Users/lulu/Desktop/claude/mjcf/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/RL416_FINAL_INDEPENDENT_EVAL_V417_20261102，图RECORDED417_NATIVE_FRAMES/ACTUAL417_RL_BODY_POSE_SEQUENCE.png。结果出来当前模型必须view_image原生审真实pose/核manifold，再按真实RL误差/寿命/整轮越台/稳定执行针对性修复或合理续训，不能只报结束或原样重复退化任务。失败保留原false/source/once，独立版本修，不重放已消费once。

历史389已完整保存关闭，normal399/CPU389618finite已消费，final32801003B/c760f8c2…完整。404实际评测0/80strict/0wholeclear/6leading/77orientation3full8s/mean1.375s，407实际40matchedDRpairs full0strict/0wholeclear/36orientation4full8s/mean1.7055，quarter0strict/1wholeclear/39orientation1full8s/mean1.121。两图已原生审，quarter不是修好，不再称待评测。389actor旧imaginedH8只有trackinggradient，真实done只入critic且无actor末值；416修的是actualreward/done进入actor。CPU409只是一次必要恢复/无step准入。旧396/400/403/410/414/416authorityrace与全部原失败保留，345仍unused不启动，传统MPC不算RL毕业。

Pair4训练及retention已实际关闭且本地knowncontroller释放后才run418；418freshCNone/stagedmanifestexact/noowner-node-GO/private共享准入/secondCNone通过，原owner取得唯一canonical。期间localRMPOLAR r26是另scopeCPU任务，未因它绕CIM。新finiteSSH必须freshLOCAL广范围exactCIM含MOD4_H1/RMPOLAR/watch/run_once_after_resume/E1collect/prepare_archive/single_gpu/collect_nine/collect_generic/PAIR及任何新collector并serialFREE；parent再freshCNone/private共享准入。活controller只读本地，不抢锁/清active/kill/第二writer/unknownPID或GPUscan。每次finallySSHclosed/SESSIONrestored/FREE，凭据只原memory不输出Git。历史余额不当实时余额。

成功必须首次飞行整轮rearfootprint越沿、双轮真实400Hz台顶manifold、无回地面/退沿，vxy/vz<=.03m_s、rollpitch<=10deg/yaw<=.2rad连续>=.5s。loss/COM/腾空/leadingedge不毕业。400Nengineeringk2000/policy50feedback100physics400/2.5msTGS32-4/fullD0whitev3D1-D7/10mm单envclosure/.01mimic/原PD/DCclip/queue/solver/historicalH1exactproducer资产保持，不暗换newMOD4v1也不冒称适配毕业。84x48camera暂定非D435i实机标定FPS。唯一原canonical3900save3600exit300strictreserve不grant/copy/refund/clearactive/第二writer。禁Luna/OpenRouter，仅当前模型原生视觉。

全部source/report/rawfalse/once/实际418启动/FIRST/417timer/421handoff/automation按根/repoAGENTS与polar-rl-train/docs/ALL_TRIALS_AND_REPORTS_GIT_POLICY.md进入Git。同phase mod4-final389-eval404-actual-ppo416-repair已record420：main/peel412d5d5dcc12d725502849c0dc109367c61452bc，trialobject111385802593206df921feeadd119824ff6949a1。查supplement422实际commit与远端，已commit不重record/retag，push失败续existingobjects。保护全部历史tagobjects/peels与lqr5848b45a99b8c32af02eb61b507c3f95ab39e4ad。PT/NPZ/USD/media仅actualpathbytes已有SHA，不为归档读模型/跑physics。postGit验证只工具输出，不追HEAD循环。'''
request = dict(prior, prompt=prompt)
assert request['id'] == 'mod4-10' and request['mode'] == 'update'
assert request['status'] == 'ACTIVE' and request['kind'] == 'heartbeat'
assert request['targetThreadId'] == '01a1967f-0f8f-73b1-8ca8-2a26ae7d9697'
path = R / 'AUTOMATION421_LIVE_REALPPO416_SOLE417_UPDATE_REQUEST.json'
with path.open('x', encoding='utf8') as stream:
    json.dump(request, stream, indent=2, ensure_ascii=False)
print(json.dumps(dict(passed=True,request=str(path),existing_automation_only=True)))
