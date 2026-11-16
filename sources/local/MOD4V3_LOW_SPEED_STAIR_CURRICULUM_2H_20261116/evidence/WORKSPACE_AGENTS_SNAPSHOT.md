## 2026-11-16 最新训练：逐环境低速单台阶课程

2026-11-16逐环境低速单台阶课程两小时已实际开训：2026-11-16T12:00:05.874203+08:00，预计最后完整迭代结束约2026-11-16T14:00:05.874203+08:00。从当前采用c874/iter25362完整PPO和17项Adam续训；819环境从5cm独立升到7/9/11/13/15/17/19/20cm，实际入阶速度与双轮接触/车身越边/0.4s稳定合格才升级。3次失败降级、15%低级复习；1229保留平地/崎岖环境由当前c874教师约束，课程环境无旧高速台阶/高站姿BC。每5分钟完整PT与固定回放；2mm仅诊断、不reset、不整轮停训，沿用TGS32/4与原有数值保护；7200s上限，无自动延长/晋升。见sources/local/MOD4V3_LOW_SPEED_STAIR_CURRICULUM_2H_20261116/README.md。

## 2026-11-16 最新人类纠偏：SCUT主线取消2mm门控，先读原对话

用户于2026-11-16再次明确旧2mm限制早已抛弃，要求按原对话更新约束。已直接核对`查看目标主机训练进展`原始用户消息：北京时间2026-11-09 00:43:15“2mm不要重置环境…华南虎没有限制这个”，2026-11-10 01:28:08“2mm门控早没了”。后续SCUT代码实际为`enforce_closure_reset=False`：2mm只作诊断，不进奖励、不触发episode reset、不触发整轮停训；保留框架原有非有限/数值/mimic保护及>1m灾难性分离的单环境reset。11月1日10mm说明也比上述SCUT更新更早，不能再将它当最新规则重新门控。下方所有旧2mm/10mm条目与旧试验源保留为历史，不能覆盖本条对当前MOD4v3 SCUT PPO的约定。

当前俯仰模型仍是用户认可的五分钟c874a1af/iter25362，学生和保留教师均用此SHA；MOD4v3、35/78/6、电机、完整DR、物理2.5ms、腿100Hz/轮400Hz/策略50Hz及原已用TGS32/4维持。本次AI误加的“2mm零触发整轮门禁”与128/8、255/4求解器试验已撤回；原始失败并列保留，不能改写为通过。逐环境5→7→9→11→13→15→17→19→20cm课程已实现，但在本次核对时尚无PPO启动，两小时预算7200s未使用；用户要求先看原对话，不应在核对期间继续盲目扫求解器或擅自开训。证据：`sources/local/MOD4V3_LOW_SPEED_STAIR_CURRICULUM_2H_20261116/evidence/CONTRACT_CORRECTION_20261116.json`。

## 2026-11-16：华南虎与当前模型同条件俯仰补测已完成

当前采用模型仍是11月16日俯仰较低模型/c874a1af/iter25362。新冻结评测统一地形、接触材料(mu1、solref.02)、50Hz策略及起停时间，独立校准实际入刹速度；24项请求中得到11组严格同速配对，另有16组同指令配对全部完成。前进急停6组中我们4组角度更小、2组接近；后退急停5组均更大，高站姿0.6m/s约2.5倍。11组中我们的急停角速度均更大；前进高站姿低角度伴随更长制动路程。没有取得双方2.0m/s有效配对，不作同高速结论。

旧SCUT实际接触mu5.5、MOD4v3为0.9，接触硬度也不同；旧同地形/指令结果不能当作同接触条件。两者本体、质量和配套控制/物理频率仍不同，入刹匹配不等于全状态相同。全部校准/失败/较硬接触早期重置保留，详见`sources/local/MOD4V3_SCUT_MATCHED_PITCH_COMPARE_20261116/REPORT.md`。无PPO更新、无权重或默认变更。

## 2026-11-16 最新采用：11月16日俯仰较低模型

用户已明确采用两小时俯仰训练的5分钟检查点：`scut_pitch_brake_2h_20261116_005m` / iteration25362 / SHA256 `c874a1afa9adc33c3fa806d098fc135a76d3e9ecdf411d0ca4ab879696b18617`。当前综合默认及后续综合续训入口改为`deliveries/MOD4V3_LOW_PITCH_20261116/model_full_ppo.pt`，统一指针为`deliveries/CURRENT_COMPREHENSIVE_MODEL.json`。旧11月13日db6保留回退基线；历史“不自动晋升”记录是本次用户采用前的状态。

两小时PPO已于2026-11-16T03:30:17+08:00结束，实际7209.351秒，全部25组检查点评估及原轮次归档已完成。选中5m的名义MuJoCo固定评测：崎岖急停13.562°、平地13.370°，平地60/60、正向两阶5/5、实际斜向1/20、下阶5/5。尚无此新SHA的原生完整DR毕业证据，不继承旧db6的分数；没有新增训练或部署。MOD4v3、35/78/6接口与硬件合同保持。详见`deliveries/MOD4V3_LOW_PITCH_20261116/README.md`。

# 当前模型与时间线更新（用户2026-11-15确认）

2026-11-16新独立两小时俯仰修复已实际开训：2026-11-16T01:30:08.102419+08:00，预计完整迭代结束约2026-11-16T03:30:08.102419+08:00；从冻结db6/iter25331完整恢复，新增SCUT稠密姿态、水平速度奖励修复和训练期急停轮协调示范。每5分钟完整PT与固定回放，默认不自动晋升。见sources/local/MOD4V3_SCUT_PITCH_BRAKE_2H_20261116/README.md。

当前项目使用最新 **MOD4v3 / MOD4V3_HW300N60_R3**。本条覆盖下方2026-09-10旧模型路径的“唯一live plant”描述；不要据旧e91 pin把当前MOD4v3工作退回9月模型。当前训练资产以`_mod4v2_src_20261106/sources/local/MOD4V3_PITCH_RATE_SQUARE_40M_20261115/PLAN.json`的`asset_identity`及新的同源试验读回为准：MJCF SHA256 `77904c001262d53bdb5ec59b270dc24588b7c1aee8c9ba59d8c85074720c8d8f`，USD SHA256 `e057969b136fd75613bb8d77985d43d043f54faae62dc060afb718ebabbe1c1c`。原11月13日iteration25331/db6保留为历史冻结基线；当前综合默认已按2026-11-16用户指令采用本页顶部的5分钟低俯仰模型。

查询进展先按对话时间读取最新消息和实际运行状态，不能把旧总览当实时记忆。MOD4v3的PPO六动作顺序是`left_front1_joint,left_rear1_joint,right_front1_joint,right_rear1_joint,left_wheel_joint,right_wheel_joint`，现有播放器通过`[0,2,1,3,4,5]`映射到模型关节顺序；不要套用下方旧模型的名字。35维actor、78维critic、6动作和现有电机包络保持。新模型不得混用旧模型检查点。retired rm2025_fixed仍不可恢复。

俯仰修复当前试验：`_mod4v2_src_20261106/sources/local/MOD4V3_PITCH_CAUSAL_REPAIR_40M_20261115`，独立40分钟，无自动延长；继承上一轮2mm闭链episode guard，本次不改变物理容差。


当前40分钟俯仰试验在2026-11-16确认20ms奖励窗口时序错位后分段修复：第一段`MOD4V3_PITCH_CAUSAL_REPAIR_40M_20261115`已安全保存，实际1019.2484555s；第二段`MOD4V3_PITCH_CAUSAL_TIMING_R2_20261116`只使用剩余1380s，不是新增40分钟。回放所有原始成功/失败保留，默认综合权重尚未晋升。


本次俯仰训练已于2026-11-16T00:29:14.977693+08:00完整保存结束，PPO两段合计2401.152479s（40分1.15秒），最终iteration25716，最终权重SHA256 930fb0ec09428f92a5f403beed6c74b59cf807bbcd17344a29f449f516b6c18d。训练未自动延长，综合默认未晋升；俯仰效果待本轮所有固定回放完整报告判定。最终报告位于R2/COMBINED_REPORT.md。


全量回放与零更新梯度核查已完成：最终40m rough急停20.396度、平地17.805度、正向两阶3/5，未形成稳定俯仰修复。R2实验候选为累计20m（平地60/60、正向5/5、下阶5/5、实际斜向0/20）；默认仍是db6，未晋升。别把20ms时序bug修好等同于姿态控制已修好。综合结论与因果数据见R2/COMBINED_REPORT.md、PROJECT_OVERVIEW.md。

---

# Agent rules for this workspace (RM2026 wheel-legged robot)

Read this before you touch the robot model, launch training, or export a policy.
These rules exist because 2026-09-10 two AI runs trained on a retired plant and on a
plant that did not match the deployment firmware.

## 1. The only live robot plant is MOD4

* MuJoCo / mjlab plant: `incoming/rm2025_mod4/robot_hifi.xml`, pinned by
  `incoming/rm2025_mod4/PLANT_PROVENANCE.json` (sha256 `e91ce284..`).
* Isaac Lab / PhysX asset: `incoming/chassis_mod4_mjcf_usd_20260910/chassis_mod4/isaac/robot.usd`
  plus the `import_contract.json` next to it. Do NOT regenerate that USD with a generic
  MJCF importer - the closed loops and the 1:1 chain couplings are authored into it.
* **Everything under `incoming/rm2025_fixed/` is RETIRED (0908 and 0910).** There is no
  `robot_hifi.xml` there any more; the 0910 file was renamed to `robot_hifi_0910.xml` so
  nothing can select it by default. Read `incoming/rm2025_fixed/DO_NOT_USE.md` before you
  even think about it, and never wire it back into `names.py`. If something asks for
  `incoming/rm2025_fixed/robot_hifi.xml`, the correct answer is "that plant is retired",
  not "restore the file".
* `train/rmvehicle/src/rmvehicle/robot_cfg.py` raises for any plant path that resolves
  inside `rm2025_fixed/`; `scripts/check_model_identity.py` refuses to train when the
  plant hash or a pinned number disagrees with the provenance file.

## 2. Entry points

| purpose | entry point |
|---|---|
| production RL (mjlab, MuJoCo-Warp, MOD4 MJCF) | `migration/linux/run_closed_chain_training.sh` |
| plant identity gate | `scripts/check_model_identity.py --task RM2025-Later-CC-Flat-v0` |
| Isaac Lab training (PhysX, MOD4 USD) | `isaac/mod4/train_mod4_ppo.py` |
| Isaac Lab physics acceptance | `incoming/chassis_mod4_mjcf_usd_20260910/chassis_mod4/isaac/smoke_test.py` (must print `PASS_RUNTIME_BOUNDED`) |
| deployment gate | `sim2real/preflight_deploy.sh` with the exported ONNX |

`migration/linux/run_allterrain_training.sh`, `run_skills_training.sh`, `run_training.sh`,
`run_final_*.sh`, `run_teacher_view.sh`, `run_spin_pure.sh`, `supervise_*.sh` and
`finalize_refine.sh` are the retired 0908/0910 serial-teacher pipeline. They now exit 2
unless `ALLOW_RETIRED_TEACHER=1` is set, and their checkpoints were never deployable.

## 3. Contracts you may not silently change

* Policy interface: 35-D observation, 6-D action in the exported order
  `[left_crank, left_hip, right_crank, right_hip, left_wheel_spin, right_wheel_spin]`
  (`train/deploy/contract_rm2025_later.json`). The passive knee is never an action.
* Motor envelope (plateau / stall / no-load): legs 40 / 53.333 / 16.755,
  wheels 5.7759 / 28.185 / 55.3557. Training and deployment must use the same numbers;
  `scripts/check_model_identity.py` reads them back out of the compiled model.
* Closed-chain guard: the six loop-closure anchors must stay within 2 mm in any engine
  (mjlab/MuJoCo and Isaac/PhysX both enforce this). If the guard fires, stop and fix the
  plant or the solver - do not raise the tolerance.
* A model swap voids every existing checkpoint, ONNX and sim2sim contract. Retrain and
  re-run the gates; never re-label old artefacts.

## 4. Isaac Lab notes that cost hours on 2026-09-10

* Isaac Lab 3.0/6.x uses (x, y, z, w) quaternions (identity `[0, 0, 0, 1]`); 2.x used
  (w, x, y, z). Code that hard-codes the 2.x order reports phantom geometry errors - the
  delivered `RuntimeGuard`/`smoke_test.py` did exactly that (a fake 0.36 m closure error).
  Use `isaaclab.utils.math.quat_apply` instead of hand-rolled quaternion maths.
* `SimulationCfg.physics` is `None` by default; solver settings only exist once you
  assign a `PhysxCfg` (`isaaclab_physx.physics`).
* Kit tears the interpreter down inside `app.close()` and can swallow a traceback, leaving
  an exit code of 0 with no error text. Always wrap the entry point, write the traceback to
  a file, then close (`isaac/mod4/train_mod4_ppo.py` and `isaac/mod4/probe_physx.py` show
  the pattern).
* Do not spawn terrain via the packaged "plane"/grid assets on a machine without Nucleus
  access; build a local collider instead.
* Local Isaac Lab venv: `.venv-isaaclab` (Isaac Sim 6.0.1, Isaac Lab 6.1.14, rsl-rl 5.x).
  Run scripts with `.venv-isaaclab\Scripts\python.exe`.

## 5. Where the evidence lives

* `docs/ISAACLAB_MOD4_20260910.md` - Isaac Lab / PhysX MOD4 bring-up, training task, DR list.
* `docs/SCUT_ALIGNMENT_AND_DEPLOY_20260909.md` - the SCUT/华南虎 randomization list.
* `docs/MODEL_0910_VS_CURRENT.md`, `docs/AUDIT_0910_ADOPTION_RM2025.md` - why 0908/0910
  were retired.
* `incoming/chassis_mod4_mjcf_usd_20260910/chassis_mod4/reports/` - the delivery evidence.
