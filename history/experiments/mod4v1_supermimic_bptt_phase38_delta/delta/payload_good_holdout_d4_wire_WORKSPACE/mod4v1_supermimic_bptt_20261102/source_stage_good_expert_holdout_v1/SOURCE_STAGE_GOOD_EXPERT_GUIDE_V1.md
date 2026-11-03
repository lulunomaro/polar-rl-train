# Good-expert holdout 最小 SOURCE materializer V1

## 当前结论与边界

这是下一阶段的**静态源码准备工具**，不是新 native 版本，也不是训练器/执行器。当前全部 `enabled=False`、`source_native_enabled=False`、`staged=False`、`dispatched=False`。本回合执行了自己的 stdlib/fake/完整模块/AST 回归；**没有执行 `stage()`，没有执行 CLI `--stage`，没有对真实 group/native inputs 运行 preflight**。无 SSH、checkpoint stat/lstat/open/hash/decode、真实 raw/NPZ/NPY、Torch/SDK/GPU、canonical budget/锁、Git、parent/worker main、自动 GO/dispatch。

保留原母策略是主目标。CURB_PROTECTED878/SLOPE135 的 Admission2 容器是 actual0-update full fresh capture，embedded 原 teacher mean 可作为保持 baseline；fresh WM、optimizer0 和容器保存不等于训练。未新增实测质量或改善结论。原 seed20260928 只作已发布历史，不重标为 holdout。

上游 [holdout V1 seal](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/GOOD_EXPERT_HOLDOUT_SOURCE_SEAL_V1.json#L8>) 保持 `032c431b844aedc02bffad76549b9516f92e5cfd06cce6194e47d5f4451c7534`；其原封文件保持稳定。

## 唯一 CLI

[stage_good_expert_holdout_v1.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v1/stage_good_expert_holdout_v1.py>) 为单一 stdlib CLI；从完整旧 embedded stager 派生，原 helper 通过 AST 白名单核对。没有新增执行框架、进程启动器、资源管理器或 enable 状态机。

必填参数：

| 参数 | 精确含义 |
|---|---|
| `--original-group-root` | 原 N80V8 group 根；basename 必须等于 `MOD4V1_NINE_N80_SINGLE_GPU_PARALLEL_V8_20261102_101426_1793585666425343700`，读取真实 `GROUP_PLAN.json` 与原 `worker_files` |
| `--source-dir` | 二十个 pinned source 的 **flat basenames**；按上游 index 的 `path` basename 取文件，不沿 Windows provenance 绝对路径读文件 |
| `--source-index` | 封存的上游 holdout index；固定 bytes21075 / SHA256 `6f2fb9a4c3ad145620e1bb1b9748ae3848ef1287129aa5970dacee22502a128e` |
| `--native-root` | 原 Admission2 根；basename 固定 `MOD4V1_A1_RAW35_V6_ADMISSION2_20261102_231937_1793632777470828000`；只读真实闭合 owner/producer metadata 与 Python source |
| `--new-root` | 绝对路径、当前不存在、与所有输入互不包含；每个 seed 独立一次性 root |
| `--group-id` | 等于 new-root basename，仅字母/数字/下划线，并含该 seed 的十进制 token，避免跨 seed 复用 root 名 |
| `--gpu-uuid` | 显式 `GPU-[0-9a-f-]+` 字符串；这里只是 metadata，不查询 GPU |
| `--seed` | 仅整数 `20260929` 或 `20260930`；历史 `20260928` 被排除 |
| 模式 | 必须且只选 `--preflight-only` / `--stage`；没有隐式 stage |

以下只是后续父代理 review 后的**接口示例，本回合未运行**。路径为调用方供给，不进行 SSH/下载/SDK 操作：

```text
python3 -B stage_good_expert_holdout_v1.py \
  --original-group-root ORIGINAL_GROUP_ROOT \
  --source-dir FLAT_TWENTY_SOURCE_DIR \
  --source-index GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V1.json \
  --native-root ADMISSION2_NATIVE_ROOT \
  --new-root /PARENT_SELECTED_ROOT/GOOD_EXPERT_SOURCE_SEED20260929_V1 \
  --group-id GOOD_EXPERT_SOURCE_SEED20260929_V1 \
  --gpu-uuid GPU-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee \
  --seed 20260929 --preflight-only
```

第二 seed 必须另取不存在的 `...SEED20260930...` root/group-id，使用 `--seed 20260930`。两者 purpose 分别严格为 `GOOD_EXPERT_HOLDOUT_C878_S135_SEED20260929_V1` 与 `GOOD_EXPERT_HOLDOUT_C878_S135_SEED20260930_V1`；不是一个 group 混两 seed，也不是原 seed 重评。

## prepare / preflight 的精确检查顺序

1. 先检查 seed、新 root absent/绝对/不重叠、seed-tagged group-id 和显式 GPU 字符串。已有或失败消费过的 root 一律换新 root，不覆盖。
2. 复用原 `native_boundary()`：原 owner exit/cohort 的所有 GO row 必须原 actual wait terminal、rc0、semantic success、原 cost/leases 已闭合、H1 excluded、无原 error。选中两 role 的 own job 必须在原 native-root/roles/role，`PARENT_WAITED_ACTUAL` 与 cohort row 相等，FINAL 与 waited/semantic FINAL 相等。FINAL 用同一份字节做一次读取及 SHA。
3. 二十 source 逐项 byte/SHA 验证、全模块 AST parse；JSON contract 做完整对象读取。canonical `a1_frozen_eval_runtime_v2.py` **仍为 37927 / 7a092364cf63e9621481dc0a5554b56a22e4412cf89870c3db9a124864074b2e**，NEW runtime 独立 alias，避免循环。
4. 原 group 的全部 `worker_files` source/asset 集合与上游 index 的 24 inherited source + 两 pinned asset 精确集合/identity 核对。完整 `worker_sources`、`pinned_assets` 递归保留；不是按 import 切片。原源文件即使被 NEW alias 覆盖，也保留其声明/provenance，实际 verification list 绑定目标 overlay 后的 bytes。
5. 仅从原 group/`runtimes/CURB_PROTECTED878` 与 `runtimes/SLOPE135` 收集**完整 permitted static tree**，包括非 Python 文件、静态 NPZ/NPY、USD/native extensions/banks/deps。原 runtime_origin/worker 与封存 source-index 相等，E1 canonical JSON 的 role 相等；不凭另一个目录存在推断 active 链。其他六角色仅 deferred catalog metadata，无 runtime tree、env、worker 或 H1 构造。
6. 复用原 `tree()` 排除操作/训练产物目录与 checkpoint 后缀；排除发生在 DirEntry classification 前，保留其余所有 bytes，不裁 N20k history/banks。模型 PT/PTH/CKPT/SAFETENSORS/ONNX/PT2/PKL/PICKLE 不 stat/open/hash；symlink/special files 被拦截。
7. 完整原 vendor7 来自原 native-root/roles/E3/worker_sources/supermimic_vendor_v2，tree SHA 必须为 `ddf9d6e1744c050fd5298805d125a611673ff22ade52c5177fb02c488ff8f0c0`；七个完整 Python 模块均做 AST parse，原 initializer 仅 docstring，不改写、不 stub。三条 overlay import 不是 vendor 全体。
8. 对两 actual0 producer 重新验证原 TASK、INSTALL_MANIFEST、FINAL 与完整 worker17704/`7c42986077de62278e33a49f560f22602c9ba4d4e69b058f5f5f8f0893c099c7`、bridge13125/`8211964c2ce3dd78fdb9fee6603ee4a4dcfbca6fa9d7df44f20d3ddb7aaead29`，用同一上游 producer guard 检查全部 teacher state snapshot/torch.equal 保存前与成功 FINAL 前机制。没有 caller boolean fallback。容器路径与原 mother identity 分开；两容器的 actual_BPTT/all9counts/iteration 必须0。
9. 合并二十精确 overlay；原 source/static/vendor 依赖 union 保持完整。plan 保留八角色 catalog，selected2/deferred6/H1 absent，两个 requested role 各 N80/750 control、原 27/27/26 ascending/descending/standing 条件与物理 D0D7 不变。
10. 在 disposable import view 实 import 完整 metadata-safe closure：NEW runtime、canonical core、producer guard、reference helper、frozen helper、pose adapter、AppV6/Base、E1 worker/bridge/factory/endpoint；只执行 module top-level，不调用 native main。验证原 AppV6 bytes27769/`3d2d75196fb98fdb45c80a79b5b8bb69873e7c0c2c0b0f6f6610eb11a8c63c39` → Base22337/`dc4bc67193457a4fb72b125d23fa482cd3d686363bd1a93eb07268f4e4e26cb7`，`app._base is actual base`。
11. 使用实际 `select_requested_roles()` / `make_task()` / `_validate_batch_members()` 检查2 role、当前seed、原6000 physics/1500 feedback，跨seed task/paired pose负例与历史seed负例。FD101/102只是在内存中的 task-producer interface placeholders，没有打开/继承/验证真实 FD，也不是资源准入。

preflight 会读取/hash **真实的完整允许 static inputs**，但不写输入、不创建 new-root、不产生 GO。temporary import view 只复制完整文本 alias；这不是替代完整 tree 收集或最终 materialization。当前 SOURCE 回归只使用 synthetic marker banks，不触及真实 NPZ/NPY。

## metadata 与 native 的准确分层

- **实 import 层**：完整已 pin 的 metadata-safe 原模块，不做 AST crop，不以 stub 冒充原模块。AppV6→Base 是实际完整 import。
- **保留/PIN/AST 层**：native parent、原 native Torch bridge、完整 vendor7/source tree。它们的完整 source/bytes 被保留核验，但不 import/执行 Torch、psutil/fcntl、SDK、GPU、actor/reset/step。
- **未来原 admission 层**：本工具不承担。原 parent close、实际 `p.wait()` 后 semantic、private GPU EX+finite EX、canonical read-only、empty23500MiB/RAM96GiB/disk25GiB、wait1800/ready900/deadline2400 的原实现保存在上游 sealed parent，不改其 AST。SOURCE 工具不打开预算账本或锁。
- **证据层**：只有未来实际独立 seed evaluation 才产出质量样本；统计仍 conditional per-direction/standing，不池化成整个技能90，也不制造 E0/S50 predicates 或 improvement。

## 后续静态 materialization 的输出契约（本回合未执行）

显式 `--stage` 未来只做静态 materialization：再确认 root absent，创建一次性 root，按 `prepared.materials` **所有项** streaming copy/full size+SHA，写 source plan 和完整 static manifest，再对目标实际 alias 运行相同完整安全 metadata validation。

成功文件名固定为 `STAGE_COMPLETE_GOOD_EXPERT_HOLDOUT_V1.json`。它声明 `materialized=True`，但仍 `source_native_enabled=False/staged=False/dispatched=False`，`parent_launches=0`，`resource_admission=None`，`actual_frozen_evaluation=None`。上游 parent entry 对 `enabled/staged` 的原 gate 保持，SOURCE materialization 不宣称 native staged，也不自动越过 gate。

失败留 `STAGE_ERROR_GOOD_EXPERT_HOLDOUT_V1.json`，该 root 已消费，禁止同根续写/覆盖，另建新 root。无 parent Popen、环境启动、native预算访问、GPU查询或自动 dispatch。

## 当前回归：18/18，准确的覆盖与未覆盖

[test_stage_good_expert_stdlib_v1.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v1/test_stage_good_expert_stdlib_v1.py>) 覆盖：真实二十 source/JSON PIN、坏PIN先失败、synthetic closed owner/actual producer 完整 source guard、坏wait/FINAL/source guard、两 seed 完整真实安全 import+task/跨seed负例、真实 Base 缺件失败、旧 helper AST 白名单、synthetic NPZ/NPY/非Python static tree整取、PT name在stat前跳过、路径/escape保护、prepare/stage全体AST机制、preflight summary不写输入/不建root、上游 sealed V1与所有原 indexed bytes 不变。

审计：model/stat/lstat/open0、native imports0、process/network/lock0、`stage_function_calls=0`、`CLI_stage_calls=0`。4次 NPZ/NPY open 仅用于本测试自己写入并逐项标记的 `FAKE_STATIC_MARKER...`，不是原 raw/静态 banks。

测试中的 producer/owner/FINAL 为显式 synthetic metadata，不是实际 parent wait、actual admission 或质量证据。为了 fake own-job containment，仅对测试中新 import 的 runtime `BASELINE_IDENTITIES[*].source_path` 做内存 fixture 替换；不改源文件/SHA，不改 teacher/source guard，不创建 checkpoint，不给 production CLI 增加 pin override。

**未覆盖且留未来父代理 review/preflight：**真实原 group 的 pinned assets、完整 role runtime/banks/deps、完整 vendor7 tree 的实际文件完整性，以及对真实 inputs 的完整 `prepare()` / CLI preflight / 静态 materialization。当前测试不伪称这些已过；本机保留的是未来严格检查这些 inputs 的完整 SOURCE。父代理当前优先论文/BPTT方法审计，再择下一 native 版本。
