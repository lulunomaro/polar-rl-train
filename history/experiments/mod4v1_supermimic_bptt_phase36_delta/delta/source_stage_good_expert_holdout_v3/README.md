# Good-expert holdout materializer V3 — SOURCE only

状态：`SOURCE_READY_FOR_PREFLIGHT_NOT_NATIVE`。本包只补齐已定位的 **materialization → typed runtime plan publication** 源码缺口；本轮没有执行实际 prepare/preflight/stage/main、parent、worker、controller 或 dispatcher，也没有运行 SSH、SDK、Torch、GPU、PT/raw、C ledger、锁、Git 或修改旧封件。实际 native binding、资源准入、外层实际等待与新质量结果仍为 `UNKNOWN`。

## 1. 最窄差异

继承完整 V2 CLI 47717 bytes / `f7638e1f24e416780d6124df5fea2492a63d5daac73984470b96a32132ca242d`。新 [CLI](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v3/stage_good_expert_holdout_v3.py>) 只改变原 `preflight_summary` 与 `stage` 两个函数；前者只有 SOURCE kind/version 标签变化，后者增加严格的最终运行 plan 派生与发布顺序。**V2 其余 28 个完整函数的源码与 AST 均保持相同**，包括 prepare、metadata_validate、main、put_once、全部 origin/retained 校验和资源相关边界。相对 V1 仍有原 22 个完整函数相同，旧三处差异集合没有扩大。

唯一新增 helper 的精确接口：

```python
def derive_materialized_runtime_plan(source_plan, source_plan_bytes,
                                    materials, observed, *,
                                    originals, preservation, required):
    ...
    return runtime_plan, runtime_bytes
```

它是无 IO 的 evidence-to-plan 纯函数，不接收 review/approved/GO 参数，不执行 admission、SDK、进程、锁或 native 操作，也不替代完整原 metadata guard。返回值是深拷贝后的新 plan 与其 UTF-8 bytes；它不改变 SOURCE plan 或原 encoded bytes。

helper 检查：
- SOURCE 的 enabled/staged/source_native_enabled/dispatched 均严格为 False；输入 bytes 与 SOURCE plan 的原 JSON 编码一致，仍满足原 262144-byte 上限。
- 严格独立 seed、对应 purpose、group identity、原 paired/holdout 协议、完整八角色 catalog 与两个 requested member 的 N80/750 元数据一致。
- observed 恰好覆盖全部 materials，bytes 为严格 int，SHA 与每一实际 materials 身份一致；不仅检查原来源子集，也检查新 overlay。
- 原 required27 身份集合及固定摘要保持，完整原 validate_preservation 继续核对独立 originals/input paths/read counts/retained 映射及实际 observed；只给出两份相同数组没有通过意义。
- installed 状态必须是原实际 stream 验证分支；planned/preflight 状态不产生运行 plan。

## 2. 两层状态，只有运行 plan 两字段变 True

| 对象 | enabled | staged | source_native_enabled | dispatched |
|---|---:|---:|---:|---:|
| SOURCE prepare/preflight plan | False | False | False | False |
| immutable SOURCE index/seal | False | False | False | False |
| 成功 materialize 后新运行 plan | True | True | False | False |
| SOURCE stage receipt | 未新增该字段 | False | False | False |

SOURCE stage receipt 的 `materialized=True` 只表示它完成文件物化与发布；其中 `staged=False` 沿用 SOURCE 层含义，不伪称 native/resource admission、GO 或已派发。真正交给原 native parent 的是 hash-bound 新运行 plan，只有原有 enabled/staged 两字段变 True，其他所有字段保持 SOURCE plan 的值。

旧 V2 会原样写 False plan，原 parent 随后在 main 之前要求 enabled/staged True。V3 消除这一确定的源码状态不相容；**没有执行 native parent 来证明实际启动通过**。原 parent、runtime、teacher/cache/freeze、物理条件和原判据没有改动。

## 3. 唯一未来发布顺序

未来实际 stage 的顺序由源码与 AST 回归绑定：

1. 原完整 material copy/hash/fsync 循环，逐项积累实际 written observations；循环完整 AST 与 V2 相同。
2. 原独立 origin/retained 校验对照实际 written；保留 proof sidecar，不扩展原 plan 262144-byte schema。
3. 调用唯一纯 helper，获得只改变两个 flags 的新 runtime_plan/runtime_bytes。
4. 核对运行 group_id 等于实际新 root.name；运行**完整、未修改的 metadata_validate(runtime_prepared, actual_root=root)**，针对新 True plan 验证两角色/seed/producer/source aliases 等。
5. 上述步骤全部成功之后，才由原 put_once 写 GROUP_PLAN 的精确 runtime_bytes，并执行其原 flush/fsync。
6. 写原静态文件记录与 SOURCE COMPLETE receipt，绑定这次新 GROUP_PLAN 的 bytes/SHA。

任何 copy/hash/fsync、独立原来源、retained/observed、seed/purpose/root 或完整 metadata guard 失败，沿原异常分支退出，前述 GROUP_PLAN 发布语句不会被执行。回归用自己的内存 emit probe 验证无输出，并用实际 stage 的 AST 验证顺序；**没有调用 stage，即使 fake IO 也没有执行其入口**。

## 4. 父 / CFF 精确消费接口

COMPLETE 文件名不变：

```text
STAGE_COMPLETE_GOOD_EXPERT_HOLDOUT_V1.json
```

成功 SOURCE receipt：

```text
kind = SOURCE_MATERIALIZED_GOOD_EXPERT_HOLDOUT_NOT_NATIVE_STAGE_V3
source_derivation_version = 3
materialized = True
source_native_enabled = False
staged = False
dispatched = False
GROUP_PLAN_bytes = len(runtime_bytes)       # 严格 int
GROUP_PLAN_SHA256 = SHA256(runtime_bytes)   # 精确原始 UTF-8 bytes
original_plan_SHA = 原闭合 V8 GROUP_PLAN SHA
```

相对 V2 **只新增 GROUP_PLAN_bytes / GROUP_PLAN_SHA256 两个 binding 字段**，其余 receipt 字段继承；没有新增审批/admission/SDK 字段。`original_plan_SHA` 仍是旧 V8 的 `54172e4ff8fcd502602d60dfa3c35c9ed5acc02d871691e231637e59123795a0`，不是新运行 plan 的 hash。

新 binding hash 对应成功传给原 flush/fsync writer 的精确 bytes，不是对一个裁剪或重新序列化投影计算的 hash。本包未运行目标端实际写入、目标端独立 readback、controller 或 collector。后续消费者应对实际读取的完整 GROUP_PLAN 原始 bytes 校验长度与 SHA，并与 stage receipt、root/group_id/seed/purpose/GPU_UUID 和 parent source pins 绑定；完整内部 wait/EX 结果也不替代独立 outer actual-parent Popen.wait 证据。

### root 规则没有固定 PREFIX

原 prepare/main 的规则保持：
- 显式传入绝对、尚不存在、非 symlink 的 new_root。
- lexical new_root.name 必须等于 group_id，且 group_id 不是原 V8 group id。
- group_id 匹配 `[A-Za-z0-9_]+`，并包含该严格 seed 的十进制字符串；seed 只取 20260929 或 20260930。
- GPU_UUID 原正则为 `GPU-[0-9a-f-]+`。
- new_root 与输入 roots 双向不重叠。

本链没有 ROOT_PREFIX 常量；controller 不应添加一个未在原源码声明的固定前缀。只有给定 root 和 plan identity 满足原完整 guard 才有后续意义。

## 5. 完整依赖闭包与保持项

[镜像清单](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v3/SOURCE_MIRROR_INPUTS.json>) 必须保留旧 V2 的全部 67 个 WORKSPACE-relative 文本成员，逐行相同 bytes/SHA；并增加实际用于推导的完整 V2 九成员＋seal、已持久化 operational-gap MD/JSON。清单按真实去重输入计算，不设置未来固定上限。当前 SOURCE 包成员与新 seal 单独携带。

镜像布局继续在任意实际 WORKSPACE 下保留 R 与 T 两个具名 sibling project trees。`F:/RMPOLAR-RL/` 只作为严格 provenance prefix 映射，不依赖原盘回退。不能把两个 sibling 树压平为一个 R 目录。完整 V2 stdlib manifest module 以固定全文件 bytes 导入，仅复用其读/hash/AST helpers；没有调用它的旧 main、metadata_products 或文件写入函数。

[索引](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v3/SOURCE_INDEX.json>) 保持原 flat complete20 mapping、原27依赖/25真实文本＋2 asset metadata、原 supervisor、三处实际 E1 alias 冲突的原字节 namespace、vendor7、原 wire 与资源字段。

这里的八角色是**完整 catalog**：仅 CURB_PROTECTED878 / SLOPE135 请求执行，其余六角色 deferred，H1 不构造。原 prepare 对两个 selected E1 runtime 的完整非禁止静态树、banks/依赖保留逻辑保持；没有通过新增字段虚称复制六个 deferred runtime。实际目标端完整树/asset/vendor bytes 仍须原实际 preflight/stage 证据。

保持项包括：canonical7a092 单独 alias、AppV6→dc4Base、原 one-byte-stream/hash/decode/wholepi/STD/Norm/freeze/physical N80 包含性、母 teacher reopen0、原 privateGPU_EX＋global finite_EX/Creadonly、empty23500/RAM96/disk25/wait1800/ready900/deadline2400、actual worker p.wait 及 finally wait-before-unlock。没有训练/optimizer/teacher 更新，没有新资源 ledger 或 dispatcher。

## 6. NEW 32 SOURCE 回归

[回归源码](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v3/test_good_holdout_v3_source.py>) / [结果](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v3/TEST_REPORT.json>)：32/32 PASS，audit 五项均 0。没有导入/执行旧测试脚本，没有写旧 receipt；所有 scratch 和本轮结果只在 NEW 目录。

保留原18个 SOURCE 要点并补齐：
- 两个 seed 的新 True plan 均通过**完整原 metadata_validate**，不是 AST 裁剪、stub 或伪 schema；SOURCE plan 和 encoded bytes 原样不变。
- wrong seed/purpose/member/paired pose/root、observed 缺失/多出、实际 copy hash/count/布尔 count 篡改、origin/retained/相同数组伪造、required asset identity 缺失/篡改、旧 planned 状态、SOURCE flags 已变、超界/不一致 JSON bytes：自己的内存 probe 均无 emit。
- producer checkpoint SHA 不符由原完整 metadata guard 在 emit 前拦下；没有把 runtime 会从 producer 覆盖的冗余 row source_SHA 当成有效攻击该 guard 的字段。
- 原完整 copy/hash/fsync loop AST、28＋22 原函数、父 gate/hash/close 与两个 binding 字段通过结构核对。

两 asset 只读取允许的固定 SOURCE plan 中身份元数据；测试中的路径是未创建、未 stat/open 的符号路径。observed/status 在 pure helper fixture 中是明确的**合成数据**，不是实际 stage 完成证明。实际 full static banks、vendor7、GPU、PT/raw、native flags、资源、外层等待与质量没有被本轮回归测量。

## 7. 仅供父后续使用的命令模板，本轮均未执行

`--source-dir` 与 `--source-index` 必须指向原 sealed complete20 overlay 目录及它原有的 GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V1，而不是本 materializer 的 SOURCE_INDEX。后者是本包说明和 pins，不是原 runtime source-index 输入 schema。

```bash
python -B stage_good_expert_holdout_v3.py \
  --original-group-root /ABS/ORIGINAL_CLOSED_V8_ROOT \
  --source-dir /ABS/WORKSPACE/mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1 \
  --source-index /ABS/WORKSPACE/mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V1.json \
  --native-root /ABS/ORIGINAL_NATIVE_SOURCE_ROOT \
  --new-root /ABS/HOLDOUT_RUN_20260929 \
  --group-id HOLDOUT_RUN_20260929 --gpu-uuid GPU-EXACT_UUID --seed 20260929 \
  --preflight-only
```

只有原全部未来前提满足时，父才按原流程使用 `--stage`，并给另一 seed 独立的 root/group/purpose；这里不生成 controller 或执行命令。上例 GPU 值是占位符，实际值须满足原正则。

## 8. 封存与证据边界

[差异证据](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v3/WHITELIST_DIFF.json>) / [immutable seal](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v3/SOURCE_SEAL.json>) 由 SOURCE metadata builder 生成；封后只读 `--verify` 比较所有原 bytes，不修复或覆写差异。新目录稳定后保持 sealSHA。

旧 holdout V1/V2、Phase1 V1–V4、runtime/parent/source overlay 与两份历史 review 均保持原样。这个补丁不替代 CFF 独立 per-seed outer-wait / 双角色 collector 的 SOURCE review，也不把内部 grade 当 outer wait。质量统计仍是每个独立 seed 的 conditional ascending/descending/standing；不合并为整个技能90、不声称改进/noninferiority、新质量已测或 SM 训练。CURB878/S135 保持原 teacher mean，无再次训练；H1 冻结。
