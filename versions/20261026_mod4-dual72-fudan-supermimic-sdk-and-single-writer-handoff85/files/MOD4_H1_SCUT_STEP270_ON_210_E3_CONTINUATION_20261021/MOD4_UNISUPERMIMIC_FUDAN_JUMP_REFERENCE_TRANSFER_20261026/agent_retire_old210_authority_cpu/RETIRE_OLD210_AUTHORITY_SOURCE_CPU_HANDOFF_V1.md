# 旧210 Linux记账权永久fence：已准备，尚未实际执行

本helper仅准备源码并运行本机合成CPU测试。没有SSH、GPU、模型、Git、生产canonical或72运行中owner访问。root现已报告firstPi finite observer返回；真实报告已落盘，之后仅stdout摘要TypeError，不影响那份真实报告。以下动作供root随后**单路串行**在旧source210执行；本helper没有执行它。

## 固定边界

- 旧C：`/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json`
- 原C精确SHA：`fa47cf989898d9c771f35dcaa1e25330456694fda044502aaf82a5887b205bb1`
- 原83B closing：`595256.8240613937`；原total2268000、9条budget_extensions、显式active_segment=None。任何不匹配立即停，不改字段来凑数。
- 旧owner1493851/create1792994651.61；仅额外检查其已知source210 node1493856、worker1494050的存在/creation身份。PID重用不kill；身份未知/可能仍是旧进程则停。旧cohort全部children退出仍引用原83B实际收尾凭据，不声称扫清整机进程。
- 两把**原**fcntl：`/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/native_floor_supervisor.lock`、`/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock`。只打开既有文件，非阻塞独占；不创建、删锁或改权限。
- 新唯一权威：72的`/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json`，generation `MOD4_SINGLE_WRITER72_20261026`。此路径在helper中仅作为tombstone数据，从不打开。72已恢复finite限制；临时unlimited授权的时限结束不撤销永久sole-writer迁权，helper不改任何预算模式。
- 已批准的人类原授权raw SHA：`fc029e1ec254bf64b86a0428be6695a564c23fbc67794daaea0b13b6adcd04cf`，实际来源N85M/reports/HUMAN_SINGLE_WRITER72_TEMPORARY_UNLIMITED_AUTHORIZATION_ACTUAL.json。

## 精确动作与失败保护

Linux-only executor先校验上述授权raw和root串行clearance，再只查三个已知旧PID身份，取得两原fcntl后重复检查身份和旧C完整性。原C必须是预期真实路径、普通文件且无symlink；不满足就拒绝，不自动找替身。没有“改权限后继续”的分支。

在两锁持有期间，用同目录`renameat2(RENAME_NOREPLACE)`把原C移动为：

`TRAINING_BUDGET_10H.RETIRED_SOURCE210_SHA256_fa47cf989898d9c771f35dcaa1e25330456694fda044502aaf82a5887b205bb1.json`

这是原inode/原字节的原子rename，不复制、不JSON重写、不修改费用。随后fsync目录，准备仅含退休声明、新72唯一路径/generation、源SHA、授权SHA、历史路径和真实退休时间的tombstone；fsync后再次以no-replace原子rename安装到旧C路径。故意没有active_segment、active、authorized_training_seconds、remaining_training_seconds、budget_extensions或completed_segments。

Linux不支持no-replace原子rename时直接停，没有覆盖式fallback。若rename后进程中断，原始字节仍在明确RETIRED_SOURCE历史，旧C缺失使典型旧owner拒绝；恢复时必须重新核授权/进程/两锁/历史SHA，才续装tombstone。若间隙出现未知新C，绝不覆盖；保留原history和prepared partial。已有精确tombstone+精确history重复观察只返回ALREADY_RETIRED，不改日期/内容。C与history同时像原账本、既有历史不符等歧义状态均拒绝，不删文件猜修复。

## 旧schema拒绝证明

CPU测试隔离执行真实`budget_authority.validate_budget`函数，tombstone因缺少authorized_training_seconds而KeyError。另隔离执行真实旧`three_slot_finite_owner_v1.owner`必需的`c['active_segment']`表达式，tombstone同样KeyError；旧owner的首个准入读取在GO/写C之前就依赖该字段。没有启动owner、HTTP服务器、线程、PPO或物理。此证明覆盖这两个已读真实旧消费者，不虚称证明所有未知旧脚本。

## 给root wrapper的CODE/args接口

将`retire_old210_authority_core_v1.py`、`retire_old210_authority_local_executor_v1.py`与授权raw部署到root自己选定的、未使用的source210 helper目录。不要把ledger复制过去。root根据已返回observer事实写实际clearance，schema与模板相同，`root_serial_execution_on_source210=true`；模板自身该值false，不能直接授权生产动作。

唯一实际入口：

`<source210 python> -u -B retire_old210_authority_local_executor_v1.py --authorization-file <exact-authorized-raw.json> --serial-clearance-file <ROOT_SERIAL_SOURCE210_RETIREMENT_CLEARANCE_ACTUAL.json> --execute`

不带`--execute`仅dry review。无需传旧C、新C、SHA或锁路径，均已硬固定；没有override参数。标准输出只返回receipt路径/status/SHA。每次实际执行或拒绝均在该helper目录`retirement_receipts/OLD210_AUTHORITY_RETIREMENT_<真实ns>.json`保存；原错误/partial保留。root收集报告和历史/tombstone的path/bytes/SHA索引即可，不需传回完整原账本字节。source helper会原样保留全部旧账历史；既有Git历史也不改写。

11/11 CPU测试通过，涵盖授权与原C字段拒绝、无锁/干跑不写、原inode/bytes/权限保留、旧真实schema拒绝、rename中断续装、不覆盖间隙新C、幂等和历史损坏拒绝、PID重用区分、first-observer串行边界。所有文件事务均为本目录内合成fixture；原source210的fcntl/process/renameat2路径仍由root现场串行执行确认。

72 owner477414及H1真实Fudan native训练/E3训练不被访问、暂停或改动；private GPU锁、收费sum-once、有限预算限制、物理/完整保存与技能门槛均保持。此fence不增加预算、不退款、不补造history。
