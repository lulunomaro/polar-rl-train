# C2 real-CPU fixture：DISABLED / SOURCE 准备

`enabled:false`。本机仅 stdlib 字节派生、AST 与 compile-without-exec；未 import Torch/任务模块，未执行 real CPU fixture，无 SSH/SDK/model/GPU/C/Git、训练或旧件修改。技能 catalog 的 Office/ACL 与任务无匹配，使用 FS read/glob/grep 及本地 stdlib。

## 完整复用，不绕旧 pin

[原 fixture:1–359](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_actuation_real_cpu_fixture_v1/real_cpu_fixture.py#L1-L359>) 的 TAP pin 固定 C1，因此另存完整 [real_cpu_fixture_c2.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_c2_real_cpu_fixture_v1/real_cpu_fixture_c2.py>)：原字节仅替换 module docstring 首行与第12行 TAP_SHA256 为 C2 `ec10b09b77548c560611e641d685e2cee029c9778ff8c8852a8bf070243bd95d`，LF 原样保留。原 QUEUE pin、所有函数/类/返回结构均原样；11个完整顶层定义及26个完整函数/类 AST（含循环内 spy）一致。17行 [完整派生 diff](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_c2_real_cpu_fixture_v1/ORIGINAL_TO_C2_FIXTURE_DIFF.patch>) 与 [DERIVE_AST_PROOF.json](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_c2_real_cpu_fixture_v1/DERIVE_AST_PROOF.json>) 给出精确证明。未修改旧常量、monkeypatch 旧 module/class，亦未裁取原函数。

## 94行薄 wrapper / caller 注入

[c2_cpu_fixture_wrapper.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_c2_real_cpu_fixture_v1/c2_cpu_fixture_wrapper.py>) 只有一个外部 callable，无 imports/loader/driver：

```python
run_c2_cpu_fixture(torch_module, PhysicsActionQueue, tap_module, derived_fixture, *, seed=20261103)
```

四个对象由父的独立 CPU purpose 注入，并保持 Python assertions 启用（非 `-O`）。wrapper 先严格检查完整派生文件 SHA；原 `run_fixture` 仍执行未改的 source/Q/Torch/tap 检查。无旧 pin/global/class 改写或 fallback。

1. N2、N3 各完整调用原 `run_fixture`，原9-lag/reset/idempotence/overflow及各项 totals 原样放入 `original_fixture_by_n`。原字段 `normal_apply_ticks` 应各432、合计864；不把新 setter probes 算进去，也不重定义该计数。
2. 每个 N 另建同一个原 PhysicsActionQueue 类、同 seed 的 base/observed 两队列。复用 FakeEnv；安装 C2 前为每个 env 的两 term 绑定同一个 NEW fake AssetProbe。它仅在 `_write` 记录参数/次数及注入显式 synthetic RuntimeError，继承的两原 FakeAsset setter 函数对象不变。它不是 SDK asset；新 case 的 probe=None 因为只调用 setter，不调用 term process/apply。
3. 新 case 用 counter=0/17 × position/velocity × 正常/异常，共每 N **8 observed NON_TERM events**。每个 asset 原 setter 调用8次；检查 target/joint_ids 原对象、成功返回对象、原异常 identity 与一次调用。joint_ids 是 synthetic Torch CPU 参数，不是原 plant DOF 身份。
4. 检查 raw stored counter、group UNKNOWN、physics tick NOT_APPLICABLE、parent None、scope NON_TERM_SETTER；检查 CPU target/kwargs joint-id owned clones，先逐 byte 对比，再修改捕获 clone 并验证输入未变。每 N 的计划计数为正常4/异常4、owned tensors16、full queue/RNG rounds8，单独放入 `non_term_setter_by_n`。
5. 通过原 `_full_state`/`_equal` 核对两队列全状态及各自 saved 状态、private RNG 和 global Torch CPU RNG 均未变；[原 Queue:80–81](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/W35/runtime/isaac/mod4/action_delay_physics_queue.py#L80-L81>) 的 state_dict 明确含 private RNG bytes。检查 tap close/restoration/idempotence。没有添加 RNG reset、SDK getter 或 GPU 数据比较；对象与 tensors 明示 cpu。

以上数字是**源码中的预期断言，不是实际 CPU PASS**。本次仅完成 SOURCE/AST/语法检查；真实结果为 null，由父另行实际执行后产生。

## 证据边界与唯一下一步

原 core 调用局部离线 helper 的语义与范围完全不变；新增 non-term 子流不调用旧 helper/pure，不给完整 NEW schema 签发 PASS。same-asset、方法名、kwargs/source IDs 均不等于实际 DOF/target 组身份或物理 readback；不推导 SDK/技能/训练收益/真实失败 cause。runtime binding、DOF identity、physical readback、Gate1 为 UNKNOWN；exact=false、Stage2=false。

父下一独立 CPU purpose 可注入严格绑定的原 Queue、真实 Torch CPU、C2 tap 及完整派生模块，调用薄 wrapper 并分别保存两类 receipt。本目录不含 stager/launcher，不自行执行。C1/C2/oldFixture/旧真实 receipts 保留；精确文件/输入 pins、旧 seal 成员核验与内容根集中在 [SOURCE_SEAL.json](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_c2_real_cpu_fixture_v1/SOURCE_SEAL.json>)。
