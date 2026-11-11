# MOD4v3 实车电控调试完整包

交付日期：2026-11-12，Asia/Shanghai。

**主模型：R1第二轮005m，iteration22959。** 这是当前选择记录中的综合均衡候选，已覆盖完整DR、平地/浅地形/中级阶梯和专项起身测试；本包为它导出并验证了可集成的推理与控制代码。它仍是电控调试候选，**没有实车标定和实车验收通过记录**。原Step6/Step7主冻结没有被覆盖。

模型SHA256：`0dcc15f5ecfca08107dba8b1a1d80de57c777218b5f3a928c094be66c73a644f`。

## 电控先看这些

1. [电控接口、35维观测、六路电机顺序和50Hz/100Hz时序](docs/电控接口.md)
2. [实车标定和上车调试步骤](docs/上车调试.md)
3. [机器可读部署合同](config/deployment_contract.json)
4. [待填的实体标定表](config/hardware_calibration.template.json)
5. [16组实际训练环境金样](examples/golden_vectors.json)

**本包严格绑定随包MOD4v3 HW300N60 R3 plant。** 动作顺序是左曲柄、左髋、右曲柄、右髋、左轮、右轮；策略50Hz，PD100Hz。旧模型/旧100Hz策略入口及泛用资产runtime中的另一种动作排列不可直接套用。本包保留对应MJCF、实际PhysX USD及其subLayer，模型身份和SHA都可核对。

## 包内内容

| 目录 | 内容与用途 |
|---|---|
| model/policy.onnx | 车端/上位机CPU推理，float32 `[batch,35] -> [batch,6]`，输出已clip[-6,6] |
| model/policy_actor.ts | 同一策略的TorchScript版本，供已有PyTorch/C++集成 |
| model/training_checkpoint.pt | 未改写的完整PPO原始检查点，含训练恢复信息；车端不需要加载critic |
| firmware/ | 无动态分配的纯C策略、35维组观测、动作/目标映射、PD和电机包络，含完整固定权重 |
| bin/windows-x64/ | 编译通过的DLL、命令行示例及导入库 |
| bin/linux-x64/ | Linux x64共享库和命令行示例；ARM/MCU使用源代码构建 |
| runtime/control.py | NumPy+ONNX Runtime CPU参考实现，分开50Hz策略和100Hz PD |
| runtime/infer.py | 文件/JSON-lines离线桥接示例，打印动作/目标/Nm，不直接发电机报文 |
| runtime/replay_mujoco.py | 随包模型的独立ONNX回放，可开GUI，无需训练仓库或PyTorch |
| config/ | 固定部署合同、待实测标定模板 |
| plant/ | 当前训练配套MJCF+全部STL、PhysX USD及subLayer、机械/语义参数、reset bank |
| evidence/ | 原评测、起身失败、800份原环境接口样本、导出与C对齐、ONNX闭环结果 |
| tools/ | 离线预检、验证/导出源码、打包流程和生成证据的脚本 |

C网络结构35→256→128→64→6，ELU；50,758个float32参数约198.3KiB，临时推理数组约2KiB。它能编进MCU固件，但是否满足具体板上20ms预算需上板实测。

## 先离线运行

使用有对应CPU轮子的Python环境安装：

```sh
python -m pip install -r requirements-debug.txt
python tools/preflight.py
python runtime/infer.py --state examples/bench_input.json
python runtime/replay_mujoco.py --vx 0.3 --height 0.28 --seconds 8 --viewer
```

`bench_input.json`是CAD默认角的接口输入样例，不是实车稳态姿态，也不保证策略输出或力矩为零。预检只读包文件，不发电。完整性清单在 `SHA256SUMS.txt`。

`requirements-debug.txt`为本次实测版本；只做ONNX集成需要NumPy和ONNX Runtime，不必安装Isaac Lab或PyTorch。重新导出才用 `requirements-export.txt`。实际测试环境版本保存在 `evidence/VERSIONS.json`。

### C / 固件接入

将 `firmware` 四个C/头文件编进现有工程。50Hz调用 `mod4_policy_tick`，100Hz调用 `mod4_pd_torque`，更快执行环可用 `mod4_limit_torque`按当前速度重限。保留电控现有电机使能与急停/BSP接口。API返回失败时清除目标有效状态，不发送旧目标。

Linux/ARM主机编译：

```sh
cmake -S firmware -B build
cmake --build build
./build/mod4_stdio
```

已提供的x64程序不是STM32固件。H7/其他MCU只集成纯C实现与常量，CAN报文、编码器、IMU、使能沿用电控已有硬件层，并按随包合同转换。

## 标定与实车接管

先阅读[上车调试](docs/上车调试.md)。模板中的CAN ID、方向、编码器零偏、原始报文单位/电流换算及IMU安装旋转没有测量依据，保持空值和 `verified=false`。复制成 `config/hardware_calibration.json` 后按实测填写，再运行：

```sh
python tools/preflight.py --real-enable --hardware-calibration config/hardware_calibration.json
```

这只核验标定配置，不发送电机指令，也不替代实车验收。当前未填模板应按预期返回阻断。旧项目 `sim2real/preflight_deploy.sh` 也实际执行过，因实体标定未确认而阻断，记录见 `evidence/LEGACY_DEPLOY_GATE.json`；没有绕过旧门或把它写成PASS。

初次接管从正常支承姿态、零速、高度0.28m开始，再按文档逐步试低速。当前模型尚不能保证任意摆腿都可靠起身，R2腾空落地也没有训练完成。

## 已完成的验证与已知结果

- **接口对齐PASS**：800份原冻结R1环境样本中，Python/C的35维观测、动作目标与160份名义PD样本均与原实现吻合；ONNX/C与原PyTorch动作误差约1e-5内。另有4096组随机网络输入验证。
- **ONNX独立闭环8项**：正常站立、0.3/2.0/2.2前进、后退、旋转、低身、高身均运行5.2秒，无2mm闭链/非有限安全终止。最大闭链约0.487mm。
- **速度偏差如实保留**：0.3指令约0.320；2.0/2.2指令约2.418/2.721m/s，名义MuJoCo高速前进仍超速。这不是实车速度保证，电控先从低速调试。
- **起身未全适应**：8种随机摆姿的名义6/8、完整DR25/32达高度/姿态保持；逐帧接触严格统计6/8、19/32。真实卡住、翻倒和准备期闭链保护记录都在evidence，未删失败。
- **没有新训练、没有改模型**：导出的是同一完整PT的actor。未修改资产、奖励或DR，没有针对实车偷偷调观测缩放和PD。

详细文件：`NUMERICAL_PARITY.json`、`ONNX_CLOSED_LOOP.json`、`MODEL_SELECTION.md`、`R1_FINAL_REPORT.md`、`GROUND_STAND_REPORT.md`。`capture01_failure.log`保留采样工具最初因Kit独立目录名不符合既有启动器要求而退出的记录；改为合法独立目录后的capture02才产生800份接口样本，没有重训或改物理。
