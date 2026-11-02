# mod4v1 新资产 fresh-DR 旁路 hook

仅新任务使用；不改旧源码、旧 PT、once、canonical。不自动部署或启动。

## 源码事实：旧恢复链没有“从 PT 装回旧绝对质量”的已知 bug

在 `MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101/package/payload/job0/runtime/isaac/mod4/`：

- `mild_dr.py:29–33` 在新构造 PhysX 中捕获 `MildDR.mass/inertia/com`；`:78–79` 每次 reset 用这些 nominal × episode factor 写参数。
- `sensor_resume_contract.py:38–45` 恢复 D0 named RNG（不是绝对 m/I），最后恰好一次 `env.reset()`。
- `chassis_com_pose_roundtrip_sdk_adapter.py:32,113–116` 在构造时捕获 `original_pose`；load 只恢复 COM delta/RNG，仍以本场景 nominal 为参考。
- W35 `adapter_v3/source_cache208_v3.py:34–41` 只向既有 restore 返回选定 source 的 deepcopy，不写机器人。`sensor_resume_contract208_v3.py:39–46` 同样恢复 RNG 再 reset。

本 hook 是新资产身份及缓存保护，不声称修复旧源码不存在的质量恢复问题。

## 新任务集成（只改独立新副本）

```python
from mod4v1_fresh_dr_guard import (
    bind_before_task_import, verify_task_module, configure_new_task,
    FreshDRNominalGuard,
)

# 新 worker 完成旧 RM_* 清理/恢复之后、runpy/import task 之前：
identity = bind_before_task_import(NEW_TASK_ASSET_DIR)
# 若 worker 之后又写 RM_MOD4_USD，必须仍指向该新目录；不能回指旧资产。

# 新 build_env 副本中，在 task 已导入、cfg 已生成而 env 尚未构造时：
import mod4_task
verify_task_module(mod4_task, identity)  # 包括 CONTRACT，避免 import cache 仍绑旧 JSON
configure_new_task(cfg, identity)       # closure .01m；mimic 必须原已为 .01rad
# env = 原 Mod4Env(cfg=cfg)，保留原场地/命令/自有 D0–D7 构造和初始 reset

# 新 main 副本中，build_env 返回后、runner.load/原完整 resume 前：
from mild_dr import tensor
nominal_guard = FreshDRNominalGuard(
    env, identity, torch_module=torch, tensor_converter=tensor,
)
with nominal_guard.around_original_fullstate_restore():
    # 原 runner.load 路径和原选源缓存作用域原样保留：
    with runner_source_load_scope():   # W35 原 source_cache208_v3 提供
        runner.load(warm)
    original_resume(runner, env, args.init_checkpoint, log_dir)
    # original_resume 自己执行一次 env.reset；本 hook 不新增 reset。

# 原代码自然取得 observations 后复用该对象，勿为 hook 多算一次传感器：
nominal_guard.check_observations(obs)
# receipt 返回 dict，不自动落盘；由新任务自己的完整证据保存路径接收。
nominal_receipt = nominal_guard.receipt()
# 继续原 Native24、完整保存/回放/评测/有限调度，不改其语义。
```

`identity` 需由新 worker 显式传入新 trainer，或在新 trainer 内用其实际新 asset 目录重新只读取得；不假定 `runpy` 自动共享 worker 局部变量。qualified240 若原本没有 `runner_source_load_scope`，保留其原 runner.load，不为了本 hook 引入 W35 的缓存模块。

实际原挂点：
- qualified240 `train_H1_ground_prelaunch_fullstate_v2.py:225–257`：build_env → runner.load → `resume_h1_new_episode` 别名。只在新副本包住原 load + resume。
- W35 `adapter_v3/train_full208_v3.py:221–253`：同样顺序，原 `runner_source_load_scope` + `checkpoint_cache208_v3.resume_e1_new_episode` 保持。
- E2/E3 若用不同入口，先在其完整原 resume 的唯一 `env.reset` 处绑定；不偷换 terrain/recovery bank、命令、effort-owner 或额外 reset。

## 保留与边界

- 只读/保护本场景已从新 USD 构造的四个确切缓存：`_mild_dr.mass/inertia/com`、`_chassis_com.original_pose`。若恢复路径改动它们，在 reset 前报出新 nominal 被覆盖；不推断字段、静默改值或重写 checkpoint。
- 前置固定 root SHA `2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3`、contract SHA `bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755`。部署位置可以不同，相对 USD 依赖必须完整；本 hook 不取代依赖清单/Native0PT。
- 必要新 nominal 质量/COM 与固定 contract 对照；raw inertia 直接捕获 SDK 数组后保护，不添加谱/FP64/新全局精度门槛，不猜 SDF 主轴到 SDK frame 转换。父端 Native0PT 仍需证明 v1 point-delta 惯量实际生效。
- 原 actor35/critic38/actions6、learned STD、17Adam、SI缩放/已有norm、全局/命令/各组件 RNG 恢复、控制队列 reset 由旧完整 helper 保持。本 hook 无 PT I/O、神经网络调用、额外随机抽样、物理积分或物理 setter。
- 使用原 MildDR auditor 和既有 SDK `get_masses/get_inertias` 验证 reset 后新 nominal × 本回合 factor。没有实测就不称目标 SDK、全部专家或全技能适配通过。
- 自有 D0 white_v3/D1–D7 保持原定义：D5=气弹簧 stiffness；D6=气弹簧 damping，**不是全部关节摩擦/硬件全覆盖**。
- 原 gas400 旧身份检查若固定旧 root/contract/“四标量差异”，需父为新 asset 创建独立 admission/Task/INDEX 并明确三 body 质量/COM/I DIFF；本 hook 不伪造旧通过标记、不绕过它。
- 不缩放/复制旧 per-env DR 状态以适配不同环境数。单 env Native0PT 无 PT；正式 20k fullrestore 仍走原 shape/RNG/队列检查。

## 本地检查范围

`test_mod4v1_fresh_dr_guard_synthetic.py` 用 NumPy API doubles 和固定新 JSON 做合成测试；只读取新 USD/JSON 字节核 SHA，不加载 USD Stage、Torch、PT、真实策略或 SDK。使用 `python -B`，不写测试报告/pycache。结果不代替目标 PhysX 验证。

该目录由父统一纳入新任务 Git/trial；本子任务没有 commit/push 或原 canonical 操作。
