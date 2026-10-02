# MOD4 远端 RL 审计与修复包

这是针对 4090 主机 `/home/egde/fangzhen_linux` 当前代码的**候选修复包**。原训练、检查点和资产未被修改，未启动额外 GPU 仿真。上传不等于应用。

先读 `CURRENT_STATUS.md`，再按 `TASK_LIST.md` 接管。`overlay/isaac/mod4/` 是实际修改后的 Python 文件，`patches/` 是逐文件 diff，`baseline_manifest.json` 绑定原始代码、滚动导轮 USD 与运行库的 SHA256。安装工具发现源文件变化会停止，不能强行覆盖另一个 AI 的更新。

已修正的逻辑：

1. 物理步、状态更新、奖励和自动重置的顺序；回合结束证据在 reset 前保存。
2. 路线课程按完整回合计数，并把路线索引映射为地形种类，移除错误的索引截断。
3. 独立导轮受力不再从底盘碰撞力中相减。
4. 历史编码器按观测项取最新样本；去掉使编码分支无法学习的双重清零。
5. 热启动严格检查策略和 critic 权重，拒绝未知语义的旧序列策略；纯 35 维策略可作为受控起点。
6. 蹲姿奖励不再奖励倒退；蹲下提前量与出生点前移量分开。
7. 新评测器按完整回合统计，新验收器对缺报告、错误分母、NaN、样本不足和技能退化返回失败。

**验证范围：**本地 CPU 单元测试、TorchScript 导出一致性及 Python 语法检查。尚未在目标 Isaac 运行新补丁；1→16→64 环境和 3 个种子的验收由接管 AI 在空闲窗口执行。此包不宣称狗洞已经通过，也不宣称可直接上实车。

只读核对（可以在训练期间执行；不创建候选）：

```bash
PKG=/home/egde/rl_repair_packages/MOD4_RL_FIX_20260913_1500
python3 "$PKG/tools/stage_candidate.py"
```

确认源码仍一致后，创建独立候选目录（由接管 AI 执行，不覆盖工作目录）：

```bash
python3 "$PKG/tools/stage_candidate.py" --create \
  --destination /home/egde/rl_candidates/mod4_repair_20260913_1500
```

候选复制代码，`incoming` 和 `cad` 以只读使用约定引用原资产；启动时必须设置 `PYTHONDONTWRITEBYTECODE=1`，禁止调用任何写回资产的工具。原始 USD 始终显式指定为 `incoming/mod4_rolling_20260913/.../robot.usd`，不得退回旧的固定导轮模型。

包没有修改旧的 `run_special_phases_v3.sh`。该脚本仍会吞掉部分评测失败，**不能把候选接回旧自动晋级流程并视为已经修好**。使用包里的 `run_nominal_suite.sh` 与 `repair_gate.py`，或按任务清单对接，并验证每个非零退出码能阻止晋级。

详细测试结果见 `evidence/tests.txt`。运行期验收完成前，状态应保持 `CANDIDATE_CPU_TESTED_RUNTIME_PENDING`。
