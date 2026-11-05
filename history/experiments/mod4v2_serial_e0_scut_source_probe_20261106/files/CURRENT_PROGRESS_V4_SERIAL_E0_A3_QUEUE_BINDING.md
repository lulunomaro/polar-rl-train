# 当前仅E0串行归一化：A3实际GO，原生初始化待实证

用户明确‘一个一个，先训练E0归一化’，goal664已rev2 active/armed/max32；当前只E0/host72 GPU0/maxworkers1，自身native gate，不等第二卡、不启动H1或其他8角色、不访问86。整体后续九专家目标保留，但本窗不自动调度其他专家。原global两EX/singlewriter/charge_values仍保留，privateGPU仅GPU0；initial reserve+3900，3900/save3600/headroom300/preGO1800不改，无清锁/foreign signal/账复制/退款/扩预算。显存空闲不等于原全局lease。

正式E0源：`B/tasks/MOD4V1_POSTTRAIN_EIGHT_NOH1_PAIR1_V4_20261102_120158_1793592118216803700/roles/E0/production/model_final_complete.pt`（B=/home/lc01/Zonglin Li/zonglin2），14035411B/SHA6cdac1e4b84df407d41a38444b87eaa91309ed898af05fe95a6c80f6ac3fd693/iter32004/Adam17step641600/LR.0002562890625000001。完整actor/critic/learnedSTD/norm/17Adam/LR/计数在native之后一次physical/hash/CPUdecode/copy继承；旧v1母版/Registry未动，旧physicalDR/history/queue/phase/RNG CPU历史保留不应用，新v2sole fresh reset重建，不冒称PhysX整体精确resume。N20000/T24/原PPO/奖励/命令/fullD0D7/35-38-6/50policy100feedback/.0025/TGS32,4/closure.01per-env/mimic.01均保留。

## 实际失败与新用途（不当PPO成功）

- A5九角色队列原1800锁等待自然零GO结束，真实wait/结清/释放，所有scores null，新表示包尚未native实证。resource snapshot显示GPU0free24203/util0而GPU1另任务takeoff_velocity_final239_1h/pid1677968占16446MiB并持原canonical；没有以单卡空闲推定双卡准入。随后依用户新指令改单卡E0。
- E0首single root `MOD4V2_E0_SINGLE_FULL_LEARNER_MIGRATION_20261105_233933_1793893173422640300` owner1679732/controller1679725，verify_sources错误guard用了未定义es（真实变量entries），beforeOWNER_STARTED/lock/SDK/PT，outer实际rc1/reaped。旧源/错误保留；新owner_e0_single_v2仅更正变量。新增non-main verify_sources(实际OWNER_PLAN)预检所有stagedfile/manifest/target/localvalidation（非canonical账read/lock/SDK/PT）。[首错误](<F:/RMPOLAR-RL/mod4v2_expert_normalization_20261105/E0_SINGLE_PREMAIN_FAILURE_TRUTH.json>)。
- single A2 root `MOD4V2_E0_SINGLE_ADMISSION2_FULL_LEARNER_MIGRATION_20261105_234657_1793893617272790600` owner1679974/controller1679967/worker1680540，实际GO后SDK构造到D4 action_delay_sdk_adapter缺MOD4_RESUME_QUEUE_CONTROL_US而退出，NativeInitialized/learnerload均null，PPO0。原成功common_v1.py:348本来就设置20000us（50Hz .02s），非新超参。originalowner1793894709.6228497/outer1793894709.6362052全部ownwait/settle/释放true/rc0-reaped，workerfastclose rc0仍正确semantic false。[完整error文本](<F:/RMPOLAR-RL/mod4v2_expert_normalization_20261105/E0_SINGLE_A2_ACTUAL_FAILURE.txt>) / [闭合truth](<F:/RMPOLAR-RL/mod4v2_expert_normalization_20261105/E0_SINGLE_A2_QUEUE_FAILURE_TRUTH.json>)。
- 新worker_v4唯一增加original_environment中的MOD4_RESUME_QUEUE_CONTROL_US='20000'；v3与A2不改/不重放；无新DR/RNG/getter/physics/PPO改动。正式runtime必需环境与原成功worker/source已核读，不以缺键退出当训练。

## 当前single A3

root **B/tasks/MOD4V2_E0_SINGLE_ADMISSION3_FULL_LEARNER_MIGRATION_20261106_001831_1793895511281001300**；stage295 shared非PT+472完整E0 runtime/lib/staticNPZ+新包，Linux实际verify_sources preflight rc0，sourcePT/SDK/GPU/GO/C0。dispatch1793895643.6918783/controller1681986，唯一observer **pwsh-b53ffb58285f402d**。最新已收epoch1793895919.3574848 **E0 GOtrue/NativeBeforePTfalse/learnerfalse/update null/无workererror/无parentwait**，原生初始化中；不可把GO当已训练。此后实际状态从该purpose own metadata/observer继续。

目标包 **HW300N60_PHYSX_REPR_V2**：USD47be6619a1ec78e7c1514aab673996f545feedb24fda05da3f359d69f4a4be7f、contract5cf79932fb1f11edebcfa7e35ff63ed658bbfdf1dd56706ad201b3c4fd3141a1、adapter405391d463980c1628532274709ea0e64c8a220a7de718b2ba6b860cfa3990dd。A4实测10个被动CAD有限端全±FLT_MAX，因此新包仅原None的passive反端给±π backend表达，CAD端/8active+follower无限/gas140–200mm300N/k2000d3/target.170639441/31体MCI闭链277meshes不改。canonical q[-π,π)集合包含证明不是全3D/任意unwrapped winding；hardware/native分开存。local24+pxr构建不算nativePASS。v4仍用同一zero control后读gas（原step事件preload先写target），检查20k实际limits/gas/closure与8physics2feedback成功才开正式源；旧1e-6门未放宽。

## 已备但未运行的单E0评测

`E0_SINGLE_FROZEN_parent.py/stage.py/dispatch_once.py/collect_once.py`与`worker_mod4v2_frozen_eval_e0_single_v3.py`已静态生成并全部AST/compile；显式migration factory v4，stage frontdoor仅接受上面A3真实singleton关闭allwait/结算/释放/semanticq与latest完整新candidate（实际producer路径/SHA/bytes/iter/17Adam/LR，不推算、不用旧6cd）。当前还没有该资格，不能stage或宣称已评测。新parent保持原privateEX+finiteEX/ownerNone/reserve/23500empty-util0/RAM96/disk25/1800/ready900/worker2400和实际wait/ownPIDcleanup；singleE0 N80/1000ctrl/seed20260928/fullDR/单reset/mean+norm/clip6，不调20k_native_initialized或额外zero。实际workerwait+FINAL/intent/taskSHA/PIDs/无ERROR/真实GPUsettle后才executionqualified，E0完整二元grader/fullgraduation仍null。

评测preparer首次basename断言忽略doc+guard有2处、第二次原supervisor finally缩进锚点3vs实际2失败，均在任何输出前停；旧preparer保留，finish_v3用实际缩进、精确双替换/反向bytes并校验全部5新源AST后才独占写。没有重跑SDK/旧worker/测试farm。输出main示例pointer已A3；入口stage --closed传真实closed路径或pointer，必须先核实际资格。

最近Git9c2dcd2e3a06ffc03105fed9329d758700b2938e/tag trial-20261105-mod4v2-physx-stop-representation-repair远端核验，之后用户串行新政策/A5实际timeout/single初失败+A2失败/A3新源实测/本报告与pipeline静态修复待下一meaningful feature-only归档。main只读，不为Git/状态重开权重/raw或重放old once/physics，不造无限验证链。暂无新E0完整candidate或技能通过；其余8未调度。
