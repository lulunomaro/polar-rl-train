# Phase1 capture materializer V3 — SOURCE only

状态：`SOURCE_READY_FOR_PARENT_REVIEW_NOT_NATIVE`。本目录仅准备 V3 来源传播、完整文本闭包与原 B2 源码重建校验；未执行真实 prepare/preflight/stage/dispatch。`source_native_enabled/materialized/staged/dispatched=False`，`Gate1=UNKNOWN`、`exact=False`、`capture_interface_passed=False`、`stage2_GO=False`。

## 1. 最窄变更与不变项

入口为 [stage_phase1_capture_v3.py](<stage_phase1_capture_v3.py>)，从完整 sealed [V2 入口](<../source_phase1_capture_materializer_v2/stage_phase1_capture_v2.py>) 派生。[derive_materializer_v3.py](<derive_materializer_v3.py>) 固定旧入口 bytes/SHA 后仅更改最终 worker V3 / B2 来源、`load_sources`、三个必要 SOURCE kind/version 标签，新增 `normalize_B2_source_paths` 与 `verify_B2_source_closure` 两个源码校验函数。正式白名单由 [WHITELIST_DIFF.json](<WHITELIST_DIFF.json>) 给出。

以下保持完整原 AST / bytes：

- 全部 17 个原完整 stdlib helper；[static_source_helpers_v1.py](<static_source_helpers_v1.py>) 为 10078 bytes，SHA256 `11f43dad3d0f29f0fb1b54995c16d3bf2000586481dda7870dd68af6bc9f50c2`。
- `prepare` 的完整 8 role runtime / bank / asset / dependency 遍历，原 27 文件集合及完整 vendor7：`7 / ddf9d6e1744c050fd5298805d125a611673ff22ade52c5177fb02c488ff8f0c0`。这里没有以 SOURCE overlay 或 AST 子集代替实际静态树。
- `native_boundary` 的原真实闭合元数据条件；独立 pre-overlay 输入实际 bytes / input_path / readbytes / logical-tree 摘要；同 alias 不同内容时的 retained-original 命名空间；实际 stage 流式读取后的 observed hashes 校验。
- `metadata_validate` 的原完整 AppV6 → dc4Base / canonical7a092 及同一个真实 worker bootstrap；全模块 storage/capacity file/spec/function-code/PIN/cache 证明，不 stub，不调用 storage/capacity/SDK 构造。
- 原 parent 的 private GPU EX + global finite EX / C-readonly、空 GPU≥23500MiB / util0、RAM>96GiB、disk>25GiB、wait1800 / ready900 / deadline2400、实际 `p.wait` 后语义判定、finally 等待子进程后释放 EX。
- N80、seed20260928、原 physics/DR、E3-only、64 或128个 control、显式 synthetic zero6、PT0 / trainFalse / qualityFalse。此任务不是 PPO / BPTT / 技能质量评测。

V3 五个 candidate 生产 Python 文件与 sealed worker V2 **逐字节一致**；只把 sensor 三个依赖替换为最终 B2，并传播其完整来源证据。未重写 B2 strict reset-chain verifier、没有新审批 bool / C writer / controller / executor。

## 2. 最终上游来源

| 来源 | 固定身份 |
|---|---|
| [worker V3 seal](<../source_phase1_capture_worker_v3/SOURCE_SEAL.json>) | 13 members；2920 bytes；SHA256 `80b27d160b68cc67d38fe406b3507f2df10621a054ab237e758fd6e1af1061da`；root `b1b6ec96f93561d201c307cab9b17fbdc8591c6e362cef45a29ee63419f87963` |
| [worker V3 index](<../source_phase1_capture_worker_v3/CAPTURE_SOURCE_INDEX.json>) | 124202 bytes；SHA256 `bdeea3f057fb922bd9ae2670dcbf19188f651ca64ab2cbb0331f56a5a1124797` |
| [B2 seal](<../source_phase1_passive_sensor_capture_v2/SOURCE_SEAL.json>) | 完整13 members；2909 bytes；SHA256 `be538a07c8ccfb785023422ace6985e1fde0bd5b885266124e430527c1ec558a`；该 seal 原本没有 content-root 字段，不添加虚构值 |
| [B2 manifest](<../source_phase1_passive_sensor_capture_v2/SOURCE_API_MANIFEST.json>) | 336133 bytes；SHA256 `2801135d1ff028f09a5eb7cd571cc3ca90694b60340d17e62374a42cbe60eaca` |

原17、C8 / 原182来源、adapter10、partition9、AppV6→dc4Base、canonical7a092 均继续逐项验证。上游 tests 只作为已封元数据读入，不重放其脚本。

## 3. 真正的 SOURCE 闭包，而非“155个 py 已足够”

原 B2 manifest 有 **435 个 source pin 引用 / 155 个唯一完整 Python 文件**。新增 loader 对全部文件实际读 bytes、核 SHA、完整 AST parse，不 import plant 文件。随后完整导入原 sealed B2 [source_api.py](<../source_phase1_passive_sensor_capture_v2/source_api.py>)，原样调用 `build_manifest(root=实际source_mirror_root)`；此调用是源码 read / AST / compile，不运行 reset / adapter / SDK 构造。

原 API 还实际读取四个 E1 entry-routing JSON；它们不在 worker V3 已封155-py列表中，因此本 NEW materializer 明确追加 SOURCE pins，不修改旧 index：

| R-relative 路由 JSON | bytes | SHA256 |
|---|---:|---|
| `discovery/reward_command_audit_v1/CURB_PROTECTED878/E1_CANONICAL_SOURCE_METADATA.json` | 4814 | `671f77ddef5fbd79de8dafc54213ff754cfc70ac5a9d9611680e9c76c021cfc5` |
| `discovery/reward_command_audit_v1/CURB_INDEPENDENT113/E1_CANONICAL_SOURCE_METADATA.json` | 4873 | `b906aaacefe79f29e001bee015de1d4c8ee930bf936a9996f79f0a72ee103fd3` |
| `discovery/reward_command_audit_v1/SLOPE135/E1_CANONICAL_SOURCE_METADATA.json` | 5390 | `f9a0a42c6b1390e38013a410e454da4a9d63569d47f014c3b6f6ea4ca7615b41` |
| `discovery/reward_command_audit_v1/SLOPE_INDEPENDENT50/E1_CANONICAL_SOURCE_METADATA.json` | 4834 | `8ccc2f890c90eeeea652b8b10cd8a96518ba996b52294b20d2f525ea72f716e7` |

另外逐项固定诊断 final handoff 与4个 reference 文件，仅读取，不执行诊断脚本。155 py +4 JSON + final/4 refs =164个 B2 源码证据输入；这些通过只读 proof aliases 保留，不成为新的 active plant/runtime 路由。

比较前先核原 sealed manifest 原始 bytes/SHA。派生比较**只**把 `source_path` 的显式原 `F:/RMPOLAR-RL/<R_NAME>/` 或调用者给定实际 mirror 根转为 R-relative；不采用后缀猜测，不接受点段/越界来源。测试 mirror 若嵌套于原 R，给定的实际 mirror 根优先于较短 provenance 根。其余全部字段、SHA、module、qualname、codepin、数值、status 均保持精确；路径正规化不修复 changed SHA。原 manifest/index/Root 不改。

完整外部文本镜像行数据由 [SOURCE_MIRROR_INPUTS.json](<SOURCE_MIRROR_INPUTS.json>) 实算；读取其 `file_count`，不硬编码旧263。它包括真实 loader 输入、原182 C来源、全部155py/4JSON/诊断引用，以及实际旧派生输入。另完整带上本目录11个封件成员与 [SOURCE_SEAL.json](<SOURCE_SEAL.json>)；mirror清单不递归包含自身封件，从而没有循环 hash。

## 4. 保留原 wire / controller 接口

下列 API 仍是 V1，这是有意保留，不把 SOURCE 版本传播变成 controller 重构：

```text
ROOT_PREFIX = MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_
completion receipt = STAGE_COMPLETE_PHASE1_CAPTURE_V1.json
purpose = NEW_PASSIVE_INTERFACE_PROBE_NO_TRAIN
parent launch count in completion receipt = 0
plan/task/purpose/inventory aliases = original V1 typed contract
```

未来由父侧单独 review / CPU / 真实 preflight / stage / dispatch；新 root 必须不存在且使用新的唯一 suffix，例如 `B2_FIX_V3_<UNIQUE>`，旧 consumed V1/V2 root 保持完整。下面仅记录 CLI 接口，本任务没有运行这些操作：

```powershell
python -B stage_phase1_capture_v3.py --original-group-root ORIGINAL_GROUP_ROOT --source-root SOURCE_ONLY_R_MIRROR --native-root CLOSED_NATIVE_ROOT --new-root ABSENT_NEW_ROOT --group-id NEW_ROOT_BASENAME --gpu-uuid GPU_UUID --controls 64 --preflight-only
python -B stage_phase1_capture_v3.py --original-group-root ORIGINAL_GROUP_ROOT --source-root SOURCE_ONLY_R_MIRROR --native-root CLOSED_NATIVE_ROOT --new-root ABSENT_NEW_ROOT --group-id NEW_ROOT_BASENAME --gpu-uuid GPU_UUID --controls 64 --stage
```

`--source-root` 是保留 R-relative 路径的文本镜像，不是 flat27目录，也不是实际 native runtime/static trees。真实原始闭合 root、8份完整静态 runtime/banks/assets、vendor7、capacity helper、原 EX/C/资源准入仍是父侧未来实际输入；这里的 SOURCE 回归不证明它们已实测。

## 5. 本地验证与证据边界

[test_materializer_stdlib_v3.py](<test_materializer_stdlib_v3.py>) 是 NEW 回归源码；由 [derive_regressions_v3.py](<derive_regressions_v3.py>) 从固定 V2 源码派生而来，没有 import / 执行旧 test 脚本。42项覆盖：

- 全13/17/B2/C/adapter/partition完整 bytes，原17 helpers完整AST、5个 candidate bytes相等、原parent资源块不变；
- 完整 fake8静态树、3个同alias冲突、原bytes保全、伪造两个相等列表/丢失origin/input_path/stream观测负例；
- 完整真实 stdlib AppV6/Base/core API、64/128 make_task、storage/capacity 同一完整模块 bootstrap 及缺件/错PIN/缓存/function/spec/decoy负例；
- 实际复制的隔离 R 文本镜像：禁止任何回读原 R，实际原B2 API完整重建435/155相等；每个routing JSON缺失、改完整py、缺诊断引用均失败；
- 只有 `source_path` 发生精确根替换的正负例，changed SHA / module / qualname / 数值 / status 不被吸收。

[TEST_REPORT.json](<TEST_REPORT.json>)：42/42 PASS，audit五项全0。真实 prepare / preflight / stage / worker / parent 调用全0；模型 stat/lstat/open、真实 raw、native/resource import、进程/网络/锁、越目录写入全0。fake NPZ/NPY 只是测试自身创建的静态标记，不是真 raw。实际 SDK / reset-chain binding / RuntimeRoot / Gate1 均仍 UNKNOWN；源码重建相等不构成 native 证据。

封件后只读核验入口：

```powershell
python -B build_source_manifest_v3.py --verify
```

封件内容稳定后保留；后续变化使用 NEW 版本。good holdout V2 仍是独立、尚未封的后续 SOURCE 工作，本目录没有改其角色、teacher、seed或原物理条件。
