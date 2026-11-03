# Phase1 capture materializer V4 — sealed SOURCE-only propagation

## 交付状态与界限

本目录是封存 V3 的最窄 NEW SOURCE 派生，不是已 preflight、已 stage 或已 native 验证的运行目录。最终 worker4 pins 来自父 agent 交付，已读取实际封件/索引并核对完整 13 成员；派生文件不使用浮动值。原 V3、good holdout V2 和所有旧封件保持原字节。

技能 catalog 仅 Office/ACL，与本 RL SOURCE 任务无匹配；采用 FS read/glob/grep、stdlib、fake 和 AST 方法。当前交付未读取 actual reports，未使用 SSH、Torch CPU、SDK、PT/raw/GPU、C ledger、锁、Git，也未调用 actual prepare/preflight/stage/dispatch、worker 或 parent。

[TEST_REPORT.json](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_materializer_v4/TEST_REPORT.json>)：**44/44 PASS**，一次完整 NEW 回归耗时 39.164 s。保留原 42 个完整 SOURCE 案例，新增 2 个 Source8 只读闭包案例；模型 stat/lstat/open、native imports、real raw reads、process/network/lock、escaped writes 五项 audit 全为 0。fake 静态树中的 NPZ/NPY 标记只是测试文件，不是真实 raw。实际静态树、原银行/vendor7 的现场完整性尚未由本交付测得。

```text
source_native_enabled = False
materialized = staged = dispatched = False
actual_prepare_calls = actual_preflight_calls = stage_calls = 0
native_worker_or_parent_calls = 0
actual_native_binding = UNKNOWN
actual_V3_flags_shape_dtype_device = UNKNOWN
gate1 = UNKNOWN
capture_interface_passed = exact = stage2_GO = False
```

## 1. 固定输入和完整字节投影

[最终 worker4 索引](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_worker_v4/CAPTURE_SOURCE_INDEX.json>)：134423 bytes / `75e36c0255a3b354dd0efeec33600f9b38d51ca28484de2dbed55db865fc7b2d`。

[最终 worker4 seal](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_worker_v4/SOURCE_SEAL.json>)：2919 bytes / `ba3409a5450e378ea97eac64f0fec4c3409ac974a4c3378d0c6e6a6cfc405180`；完整 13 root：

```text
758dc867cc4040a6f1eb9f587cc88f69a3866e03a9553290128a1681cda039e8
```

[最终 worker](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_worker_v4/worker_passive_interface_v1.py>)：16326 bytes / `25fa00939694f9558c8aa1a9af73a40bf9b6b1cae666e1e636c70e6e8ab2f7e9`。整个 worker 与封存 V3 bytes 的精确投影仅为：

```diff
-boundary=core().OriginalEpisodeBoundary(torch,env.device,n=80)
+boundary=core().OriginalEpisodeBoundary(torch,bridge.device,n=80)
```

原 separate `state.terminated/state.truncated`、原 bool 转换、原 N80/shape/device 检查、`first | previous(term | trunc)`、canonical boundary API 均保持。其余四 candidate 完整 bytes 与 V3 相同：contract `7910d7f3…`、observer `8a6faa66…`、runtime `490dcb8f…`、parent `d5575ff2…`。未添加 SDK getter、reset、tick、噪声抽样或新的 plant 行为。

原 canonical 构造器直接保存 device 参数；既有 native bridge 构造器已经执行 `torch.device(env.device)`。因此这里只传播已有规范 device 对象，不重写原 predicate。父 agent 的独立真实 Torch CPU 结果属于父方独立证据；本 SOURCE 封件既不读取该 actual report，也不将其设置为镜像/运行硬依赖。实际 V3 flags 的类型、shape、device 仍为 UNKNOWN，CPU fixture 不是 SDK 现场定因。

## 2. 最窄 materializer 差异

唯一派生基准是 [封存 V3 entry](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_materializer_v3/stage_phase1_capture_v3.py>) 全文：42437 bytes / `2a4213d95939216f3a91db6c1739a443907aadf33c4f615aa897eace5a915425`。

[NEW entry](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_materializer_v4/stage_phase1_capture_v4.py>)：45850 bytes / `f3059d24444c40873f2d55aeb22fd82e32284e761db96250ec985314080c6507`。

仅 4 个既有函数变化：

- `load_sources`：最终 worker4 folder/seal/index/root/source_version 传播；按最终索引新增的实际 `boundary_device_source_contract` 接口核对完整只读 Source8、seal、三条原来源引用。它不是新增 runtime dependency。
- `metadata_validate`：只变 SOURCE kind/version，沿用相同 whole-module bootstrap 与完整 metadata 接口。
- `preflight_summary`：只变 SOURCE kind/version。
- `stage`：仅 SOURCE kind V3→V4；整个实际 stream/read/hash/written/retained/installed metadata 逻辑未改。

其余 **10 个完整函数 AST 不变**，无新增 runtime/闭包 helper。特别保留 `normalize_B2_source_paths`、`verify_B2_source_closure`、`native_boundary`、`prepare`、`retain_originals`、`validate_preservation`、`main`。完整原 [17 helpers](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_materializer_v4/static_source_helpers_v1.py>) 全文 10078 bytes / `11f43dad3d0f29f0fb1b54995c16d3bf2000586481dda7870dd68af6bc9f50c2`，与原 bound stager 的完整函数 AST 对照不变。

[WHITELIST_DIFF.json](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_materializer_v4/WHITELIST_DIFF.json>) 保存完整证据，不以函数名清单代替 AST 相等检验。

## 3. 原闭包全部保留，新增 Source8 只是证据

完整保留：原 17 runtime/source 映射、新 5 candidate、原 5 dependency mappings，共 **27 active mappings**；原 B2/C8/adapter10/partition9 sealed dependency 集合不变；C 原 182 个 source pins 不变；原 bootstrap 两个实际完整模块及 `__file__/spec.origin/function/globals/cache` 检查不变。

B2 原闭包仍是 **435 refs / 155 个完整 Python + 4 个实际 E1 routing JSON + diagnostic final / 4 references = 164 个独立来源输入**：

1. 先核对完整原 manifest raw SHA，再做派生比较；
2. 调用未修改的原 `source_api.build_manifest(root=actual_source_mirror_root)`；
3. 只正规化 `source_path` 中明确的原 R/实际 mirror 根；镜像嵌套在 R 时优先实际 mirror 根；
4. SHA/module/qualname/code pin/数字/status 均保持；拒绝外根、dot/traversal、猜 suffix 或把 hash 变化正规化为通过；
5. 隔离完整 mirror 加载时禁止回读原 R；四个 routing JSON 任缺其一、改变完整 Python、丢失诊断引用均失败。

新增声明来自实际最终索引，不猜字段。[Source8 seal](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_boundary_device_contract_v1/SOURCE_SEAL.json>)：1570 bytes / `c9fae49e96b7042863372e7fb681c7c93fd8ce733646908222c9af6f7d306bdc`，8-member root `5b4d0134e8ec0d828adef1fae8156d195ede032eacea2476457a403162e9e106`。

- 完整 8 members 加 seal 共 9 文本逐字节、成员集合和 canonical root 全核对；Python 仅 AST parse。
- sealed source pins / source receipt 的整个 `source_contract` 与最终 worker index 严格相等；三条原 canonical/bridge/V3 worker 来源逐字节核对并作为只读 proof 保留。
- 元数据保留 `read_only_fixture_source_not_runtime_dependency=True`、`parent_CPU_result=NOT_REPRESENTED_BY_THIS_SOURCE_SEAL`。fixture/CPU 模块 **0 import、0 execution**，没有父 actual CPU report 依赖。
- 新增回归对这 9 个文本逐个做缺失、篡改，共 18 个负例 subcase；真实原文件不动，仅修改 NEW 临时 mirror 副本。

完整 8 runtime/static-bank/deps、完整原 27 worker files、完整 vendor7、AppV6→dc4Base、canonical7a092 独立 alias，均沿原 AST 保持。独立 pre-overlay input_path/readbytes/hash 原树库存、冲突 namespace 原字节保全、实际 stream observations 与 installed 校验继续是硬证据；两份自报相同列表不构成原树证明。source overlay/proof 不冒充完整 SDK/静态树。

## 4. 原 wire / parent / 资源保持

```text
ROOT_PREFIX = MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_
COMPLETE_NAME = STAGE_COMPLETE_PHASE1_CAPTURE_V1.json
purpose = NEW_PASSIVE_INTERFACE_PROBE_NO_TRAIN
wire_API_version = 1
requested = E3 only
num_envs = 80
controls = 64 or 128
seed = 20260928
policy = EXPLICIT_SYNTHETIC_ZERO6_NOT_POLICY_QUALITY
PT reads = 0
```

完整 8-role catalog、其余 deferred、H1 不构造；没有训练/好专家质量结论。typed plan/task、controller receipt API、原 parent、close/p.wait/finally、private GPU EX + finite EX/C readonly、empty GPU 23500 MiB / RAM 96 GiB / disk 25 GiB / wait 1800 / ready 900 / deadline 2400 保持。原训练/预算逻辑未触碰。

## 5. 文件、复核和未来 CLI

- [SOURCE_INDEX.json](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_materializer_v4/SOURCE_INDEX.json>)：固定来源、scope、wire、false flags 与独立证据。
- [SOURCE_MIRROR_INPUTS.json](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_materializer_v4/SOURCE_MIRROR_INPUTS.json>)：按本次真实文件重算唯一 R-relative 文本输入；不套旧 313 上限。完整 NEW 11-member bundle 加 seal 与这些输入分开传递。
- [test_materializer_stdlib_v4.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_materializer_v4/test_materializer_stdlib_v4.py>)：NEW 原42+2回归；从固定旧测试文本派生，未 import/replay 旧 one-shot 测试脚本。
- [derive_materializer_v4.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_materializer_v4/derive_materializer_v4.py>) 和 [derive_regressions_v4.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_materializer_v4/derive_regressions_v4.py>)：固定完整旧输入的可复核派生器；封存后保持不变。
- [build_source_manifest_v4.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_materializer_v4/build_source_manifest_v4.py>)：生成或只读核对 [SOURCE_SEAL.json](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_materializer_v4/SOURCE_SEAL.json>)。`--verify` 不写文件，不调用 preflight/stage。

只读封件复核：

```powershell
python -B build_source_manifest_v4.py --verify
```

以下只是未来父方评审后的调用接口，当前交付没有执行。`SOURCE_R_MIRROR` 是完整保留 R-relative 来源布局的 source 根，不是单独平铺几个 candidate；`ORIGINAL_GROUP_ROOT` 是未裁剪的原 8-runtime/static tree，`NATIVE_ROOT` 是原 native dependency/source 证据根，`NEW_ROOT` 是独立未消费且符合原 V1 prefix 的新目录。

```powershell
python -B stage_phase1_capture_v4.py `
  --original-group-root ORIGINAL_GROUP_ROOT `
  --source-root SOURCE_R_MIRROR `
  --native-root NATIVE_ROOT `
  --new-root NEW_ROOT `
  --group-id GROUP_ID `
  --gpu-uuid GPU_UUID `
  --controls 64 `
  --preflight-only
```

真正物化时仅将互斥模式替为 `--stage`，输出原 V1 completion/controller 接口。preflight PASS 也不是 stage 或 native PASS；SOURCE PASS 同样不证明现场 flags、binding、actor35、physical readback 或 Gate1。原 parent 的 READY/GO、资源票据、实际 child/outer wait 与随后严格采集应由父方独立执行、独立报告。本封件没有自动 stage/dispatch，也没有新增审批布尔、C writer、dispatcher 或泛化执行框架。
