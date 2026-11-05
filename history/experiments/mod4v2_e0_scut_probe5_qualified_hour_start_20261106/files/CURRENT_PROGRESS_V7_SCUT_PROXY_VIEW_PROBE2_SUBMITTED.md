# E0 SCUT第二独立probe：严格ProxyArray视图适配，仍未验收

## 当前目标与边界
Goal664 rev5 active/armed；按华南虎真实registered V14Flat-v0源串行九专家，当前只有E0。未开hour/其他8专家/86，不改旧母版或Registry。仍N20000/T24，仅1次原PPO更新的必要native/U000/one-update/U001准入；这不是用户要求的一小时训练完成。保留300N/60mm/140–200mm、D6连续传动、原几何/限位/.0025/50–100Hz/fullD0D7、原单writer/charge_values/reserve86412.86069250107/3900-save3600-headroom300/preGO1800/实际inner+outerwait成本结算释放。

## 第一次probe真实失败/闭合
`MOD4V2_E0_SCUT_PROBE_FULL_LEARNER_MIGRATION_20261106_043618_1793910978054991000` controller1693216/owner1693224。reward_v2.bind→_RewardState._inputs报`Unexpected robot tensor shape: joint_acc`。其type和shape原为合取报错，不能说实际shape错。native-before-PT、learner loaded、U000 acceptance未发布，新增PPO0；owner已实际allwait/结算/释放，outer1793911530.0575306 rc0/reaped。semantic qualified=false，fastclose rc0未当通过，旧purpose/源/失败不覆盖。

## 已证实的当前SDK源码ABI与最小新源
source-only SFTP获取`articulation_data` factory明确imports的真实PhysX/base；`sdk_scut_joint_data_abi_source_v2/physx_articulation_data.py:950–988` joint_vel/joint_acc返回ProxyArray，joint_acc967标Torch形状(N,J)，不是原Tensor。base aliases同类。`sdk_scut_tensor_math_abi_source_v1/utils/warp/proxy_array.py:122–148`明确`.torch`为缓存zero-copy view；`utils/math.py:444–477`当前euler与实际native均xyzw，`quat_apply_inverse`也同序，无重新排序/猜单位。

新`scut_v14_flat_reward_adapter_v3.py` SHA c82aa2d0eb3e249afad9f439c1d8a7e5d54b628257fbb3914e802347b916fe31，只增加原Torch或实际SDK ProxyArray.torch严格view桥并保持原shape/dtype/数值门；未知类型Unknown，不reshape/cast/造Tensor/填0，shape错报observed/expected。物理9字段/command/height/contact历史/termination/raw-action均按原字段一次读取，额外没有step/obs.compute/getter/RNG。原37有序weights/26active/11zero、raw公式/dt/sanitize/sum、step ABI/reset/history完全反向字节一致；这只是静态检查，不是runtime PASS。

首preparer针对想当然的value循环锚点AssertionError（实际fields字典）在任何输出/SSH/AST13前停止；源保留。`prepare_scut_probe_admission2_tensor_view_v2_once.py`改成已read的fields字典锚点与shapes[key]诊断，再一次发布所有新代码AST/compile、recipe_inverse_exact。未执行CPU模拟/测试农场。

## 第二独立purpose已暂存及提交
原scope保持E01update，`worker_e0_scut_v14_probe_v2.py`只更新新reward模块名和真实SHA；原v1/v2失败源都保留。stager_v2只更新共享文件名；owner资源/计费/实际wait/初始actor-norm验收门不变。stage guard要求第一probe真实close/wait/结算/释放、无源learner加载/PPO0及原错误。297共享nonPT+E0472完整runtime/lib/staticNPZ；Linux verify_sources实际preflight0，不是SDKpass。

新root：`/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V2_E0_SCUT_PROBE_ADMISSION2_FULL_LEARNER_MIGRATION_20261106_051947_1793913587868886200`。
2026-11-06 05:19:47 +08:00暂存，dispatch1793913685.692319/controller1695092，首snapshot1793913688.9410706 E0 GO=true/native=false/learner=false/update=null/error=false/parentwait=null。唯一observer **pwsh-b4806f80b7a04487** running，未见native/U000/真实oneupdate/U001/actualwait资格，不能宣称训练入场或完成。不得重放stage/dispatch/collector/权重，等原自有JSON闭合，若错误保真停止。

## Git已完成与待下一阶段
前阶段原recorder跨午夜旧日期git-add guard在write-record后、暂存前失败，保留其preparedrecord/INDEX/失败入口；`finish_prepared_serial_e0_scut_trial_once.py`续同一record，逐文件复核原hash/redact与精确短scope stagedset，追加失败说明/finisher/真实闭合probe JSON，不重跑recorder或GPU。已真实远端核验commit **83d9178063bc6901da670fc3f1fa94cc13667e95**，annotated tag **trial-20261106-mod4v2-serial-e0-scut-source-probe**，对象 **e7e557c1b416f229b3894dea055842ddb3e813ec**，296条目/clean，remote branch-tag-peeled一致，main只读 **79ea28c7d82924d6a7cf06d4fedf4807fd23140a**，未push/reset。job82df7bfd2ab446fe completed0/fulloutput collected。
本新view源码/SDK math getter source/第一preparer失败/第二purpose stage/GO及本报告，待下一meaningful实际结果一起归档；不造无限核验文件链。原U000 actor/critic/norm/STD/Adam17/LR/iter exact和原p.wait/ERROR/FINAL-intent/gas/native门均未豁免。总目标、E0健康/技能与original fullgrader仍未通过，缺完整grader仍null。
