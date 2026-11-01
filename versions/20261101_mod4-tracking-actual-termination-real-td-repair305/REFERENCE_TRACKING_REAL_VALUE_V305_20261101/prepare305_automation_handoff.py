from pathlib import Path
import hashlib,json,time,tomllib
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
def put(p,x):
 with p.open('x',encoding='utf8')as f:json.dump(x,f,indent=2,ensure_ascii=False,allow_nan=False)
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
w=json.loads((R/'CURRENT_ACTUAL305_REPAIR_WORK_ORDER.json').read_bytes());waiter=json.loads((R/'POSTROUND306_WAITER_LAUNCH.json').read_text('utf-8-sig'))
assert json.loads((R/'POSTROUND306_ONCE_CONSUMED.json').read_bytes())['pid']==waiter['pid']and not(R/'POSTROUND306_LOCAL_STDERR.log').read_text('utf8')
w.update(epoch=time.time(),postround_waiter=waiter)
put(R/'CURRENT_ACTUAL305_REPAIR_WORK_ORDER_V2.json',w)
config=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'));put(R/'AUTOMATION305_PRIOR.json',config)
prompt=f'''每小时继续本聊天MOD4参考轨迹跟踪/修复。人类2026-11-01“新跟踪启动”且“继续看收尾然后修复”。持续流程：每轮完整保存/安全退出后立即真实姿态回放、独立评测，依据结果主动继续或定向修复，不等催促。ACTIVE/currentchat，不新Goal/重复automation；无变化静默，仅完成、失败、实质进展、资源/预算/网络问题或必需用户行动通知。

首先读 {R.as_posix()}/CURRENT_ACTUAL305_REPAIR_WORK_ORDER_V2.json。当前305run REFERENCE_TRACKING305_1793547655904296600，唯一原72owner PID1414841/create1793547867.41，node1414850/create1793547867.83，完整exe/argv/jobroot/controlcwd见原launch/binding。GPU-c27eecbd-6838-7290-1cd2-37e34522213d。GO2026-11-01 23:44:31.365921+08，SAVE2026-11-02 00:44:31.365921+08，NOMINAL00:49:31.365921+08，normal最早00:34:31.365921+08。唯一canonical原3900/save3600/exit300不改，严禁健康重启/hotpatch/重复startupcard检查。

前轮300已正常收尾，完整32593725B SHAe700e546e3cada81dee7cdd6ed1aa59d51eb0d0d1932f0dfda928799de7812a8，Pi2593/Critic2593/newWM2625total9712，601finiteCPU全树通过，原fee3603.3367319107056s，ownchildren/锁全free/CNone，原余额snapshot386875.29836797714s。独立303已实际评测0/80越台成功/越沿，66姿态终止，14跑满8s，不待评测。303真实viewer开启但被关闭在截图前，且旧kind判断把平台藏了；原source/错误保留，独立304只用已记录303bodyposes渲染4casesx3时点且平台可见，当前模型原生视觉已看过：前倾卡台前/早期倾倒，无过沿。304图在 TRACKING300_FAILURE_DIAGNOSIS_V304_20261101/RECORDED303_NATIVE_FRAMES/ACTUAL303_FINAL300_BODY_POSE_SEQUENCE.png。

304诊断一次必要新final300CPU读：轮通道raw最大9.27/9.84存在饱和，重建cleanABI critic均39.33但不是实际delayedobs；重建场景context WM诊断不能称真实predictionerror。明确代码缺陷：实际bad_orientation角.75rad=>Rzz约.73169，而旧imagined存活sigmoid阈值Rzz.45（约63deg），且critic只用imaginedrewardlabels。末bootstrap可自强化，不能称唯一失败原因。

305独立修复：完整恢复300actor103/critic106/STD/三套Adam/norm/RNG/WM9712，不回退2135actor；actorAdam45533+新Pi、criticAdam2593+新critic、原teacher17Adam42940冻结。imaginedsurvival改sigmoid((Rzz-cos(.75))/.025)，真实物理终止阈值不改。critic改实际own r/done/nextcritic/currentdepth一步TD+Huber，done无bootstrap；EMA.01 targetcritic随完整保存，actor末值用target并clip0..100。exp(-trackingcost/5)权重/参考/物理仍原300跟踪任务，PPO0/Fudan目标false。新CPU305一次必要source读验证全部Adam/权重准确恢复和H32不更新，终止TDtarget=.6、survival(.5,.75,1rad)=[.9971,.5,.000473]；无伪造模型进步。
实际305 FIRST64controls/5120ownpairs/512physics/128feedback，Pi1/Critic1/WM+33total9745。实际trackinggrad20.4879/terminal70.1752/combined74.9077均有限非零；完整32695597B SHA296e267af8d8809a5a8caa3b93efbf8a319f906e1693ddfbde3b673ee4af4a47，actorAdam45534/critic2594。后续73controls/Pi10critic10WM9754/28姿态终止，不技能毕业。新增真正实际连续转移配对H32报告：one-step位置RMSE.008502956m/RzzMAE.0105025，H32位置RMSE.0641504m/RzzMAE.0312084，mask30313；当时WM9744、训练中分布不是独立技能评测。真实pair报告见binding/files/ACTUAL305_H32_PAIRED_REAL_WM_ERROR_BEFORE_PI。不能把重建304rollout混称这个实际测量。

唯一localpostround306 PID20404/Start2026-11-01 23:48:11.040444+08，完整path/argv见POSTROUND306_WAITER_LAUNCH。它只localtimer至原normal900，再调用唯一normal305完整收尾/fullformaltransfer/新CPU305校验，独立306seed9137/80reference首episodes/400controls评测，实际姿态可视回放与有限原生渲染序列（无需新物理或NN推理），落盘POSTROUND305_REPLAY_EVAL_DECISION.json。冻结INDEX306_POSTROUND_FOR305 SHA4ff36b74f075eeaacb81933f80742dac9bd6d4c22bf11bda067600c6f1ce6020。先查waiter/children/CONSUMED/results，活着不重复normal/CPU/eval，不第二watcher；close/eval期间只读本地直到controller释放。evalroot {T.as_posix()}/REFERENCE_TRACKING305_POSTROUND_EVAL_V306_20261101；samefixededge.8/270平台，仅独立DR/episode seed9137，不虚称heldout地形。viewer现已正确显示reference270平台且提前截图。回放/误差/终止审后主动决定并执行续训或修复，不能原样重复退化任务或只报结束。候选成功必须核首次腾空越沿/整轮footprint顶面/稳定.5s及实际接触manifold，loss/COM/腾空不是毕业。

继续103actor=35proprio+9currentdepth+59plannedreference，106critic；连续episodephase clamped249、lookahead0/10、末段教师停稳。计划参考跟踪器尚非自主depth-only学生，MuJoCoMPC轨迹仅计划state不是可查询PhysX动作teacher，不力矩cloning。H32只起点真实观察anchor+预测pose，episode可复用过去观测支持，未来实际depth/GTterrain不进actor/H32。相机84x48/暂定前置mount不等实机D435i标定/FPS。

400N工程k2000/50policy100feedback400physics2.5msTGS32/4/fullD0white_v3D1-D7/闭链10mm单envreset/mimic.01rad保持。原singlecanonical预算、无grant/clearactive/copy/refund/第二writer。新finiteSSH前freshLOCALexactCIM识别全部已知controller、serialleaseFREE后连接，finallySSHclosed/SESSIONrestored/FREE。不unknownPID/GPU-PIDscan/kill。旧2920/72stairs6/8ground、297空criticAdam保存失败、286/289/290/291默认q/dq全0反证及全部consumedonce保留且永不重放。

遵根/repoAGENTS与polar-rl-train/docs/ALL_TRIALS_AND_REPORTS_GIT_POLICY.md：所有失败/raw/false/source/report/automation/验证入Git；305新实际repairphase唯一annotatedtrial，后续ordinary补充不重record/retag，push失败续objects。300phase标签trial-20261101-mod4-reference-tracking-bptt-save-repair300 objectc7f856ecd4e90efbf0dd04b6e53f2c4c24690898 peel9f6381ada8c77b40ba0f5e9cf27154b3286ee7b8保护。PT/NPZ/USD/媒体只实际pathbytesSHA索引不为归档读模型；凭据仅原memory不输出入Git；保护全部旧tagobject/peels和lqr5848b45a99b8c32af02eb61b507c3f95ab39e4ad。postGit验证留工具输出，不追HEAD报告循环；禁止Luna/OpenRouter识图。'''
request=dict(mode='update',id=config['id'],kind=config['kind'],name=config['name'],prompt=prompt,rrule=config['rrule'],status=config['status'],targetThreadId=config['target_thread_id'])
if 'notification_policy'in config:request['notificationPolicy']=config['notification_policy']
put(R/'AUTOMATION305_UPDATE_REQUEST.json',request)
print(json.dumps(dict(passed=True,request=str(R/'AUTOMATION305_UPDATE_REQUEST.json'))))
