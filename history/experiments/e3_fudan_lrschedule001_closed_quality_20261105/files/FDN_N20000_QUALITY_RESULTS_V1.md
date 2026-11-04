# E3 Fudan / N20000 实测结果

## 结论

**N20000 真实训练与独立原范围评测均完成，但尚无起身质量改善证据；本候选不替换冻结母本。**

- 原 E3 首 episode 稳定恢复计分：**0/74**。原口径的6个正常案例另列，物理终止 **0/6**，不并入恢复分母。
- 31体 MuJoCo 的5个固定合法低姿、每姿8秒对照中，候选与母本按完整工程联合条件均 **0/5**。这不是原 E3 整专家毕业判定，也不是 native/fullDR 成绩。
- MuJoCo 母本确实抬高了车身；候选反而维持低位并明显后退。不给“两个都0，所以行为相同”的解释。
- **保留 Registry v12 的 E3 `1cd99995…`；保存 `8af4e04c…` 完整候选与所有失败证据，不推广。H1 和其他专家不变。**

## 实际训练量

| 阶段 | 环境数 | 实际 PPO 更新 | 策略 Adam | 编码器 Adam | 已优化 transitions |
|---|---:|---:|---:|---:|---:|
| 已关闭的前窗 | 4096 | 64 | 1280 | 1280 | 12,582,912 |
| 本窗新增 | **20000** | **69** | **1380** | **1380** | **66,240,000** |
| 完整 learner 累计 | 分阶段 | 133 | 2660 | 2660 | 78,822,912 |

累计133步不是133步 N20000。新窗实际控制 3360 次、physical callbacks 26880、feedback callbacks 6720；完整保存的 **48 个控制/960,000 个 transitions 尚未优化**，不冒充第70次更新。

本窗恢复了模型、critic、STD、LR、两套 Adam 与 learner 私有 generator；N20000 环境/DR/历史为新初始化，没有把旧4096环境状态裁切成20000。原 inner/outer wait、计费结算、租约释放均完成，errors为空。按 GO→原终态元数据算得约 3600.874 expert-seconds；它是派生说明，不是新账本或退款。

## MuJoCo 名义行为：5姿平均8秒末

| 指标 | 新候选 | 冻结母本 |
|---|---:|---:|
| 车身高度 m | 0.182898 | 0.241437 |
| 倾斜 deg | 7.560 | 0.638 |
| 根速度 m/s | 0.308785 | 0.038073 |
| 起点至终点平面位移 m | 2.396440 | 0.639393 |
| 完整、finite案例 | 5/5 | 5/5 |
| 工程联合条件计分 | 0/5 | 0/5 |

工程条件仍为高度≥0.23m、重力/线速度/角速度、双轮接触及车身脱地连续0.5秒的联合条件。母本末速度约0.038m/s，超过0.03m/s门；不能把母本的0/5解释成没有抬起。候选的名义高度和漂移较差，但这不是跨 backend 的 native 因果退化证明。

这是新31体/30坐标模型的真实 MuJoCo 仿真，50Hz策略/100Hz PD/0.0025s物理；使用名义参数与 clean raw35，非 native 噪声/延迟/完整DR。五个姿势保持既有关节范围，**没有覆盖参考视频中整腿同端的姿态**。没有外部抬升、yaw辅助或姿态动画。

## 完整产物与证据

- 完整候选：1,204,250,903 bytes，SHA256 `8af4e04c3a2b7dff8e805eb28a47caee442ae2f9c9ac25d08369e25d4aa6ca78`；保留于原远程 production。
- 派生部署文件：338,617 bytes，只含14个 actor+encoder 张量、82,505个标量；**不是完整训练 resume**。原完整输入仅为实际导出目的读取/哈希/CPU解码各一次，未下载1.2GB完整输入。
- [训练原始闭环](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/reports/FDN_N20000_W5_20261104_205335/CLOSED_RESULT.json>)
- [原 E3 N80 outcome 与实际父等待资格](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDNN20000_FROZEN_ORIGINAL_SCOPE_RESULT.json>)
- [MuJoCo十条真实案例](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_N20000_MUJOCO31_LOWRise_RESULT.json>)
- [紧凑选择与算术结果](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_N20000_CLOSED69_QUALITY_DECISION_V1.json>)

## 下一步

已准备[单一低趴8秒timeout干预源](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/source_task_runtime_v2_lowtimeout8/e3_fudan_task_runtime_v1.py>)：只缩短低趴episode，旧fall/normal、奖励及PPO不动。默认20秒episode与8秒请求的差别是待验证的采样假说；原全局配置可被ENV覆写，下一运行会记录实际值，不把默认当作本次实测。源码通过一次AST/compile与差异检查，**尚未准入或训练**。下一完整learner承接需绑定8af4/N20000/Base133，而非旧47937/N4096/Base64模板。不按133这个数字盲续；[完整下一窗计划](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/NEXT_SINGLE_INTERVENTION_LOWTIMEOUT8_PLAN_V1.md>)保留原74/normal、物理、DR、H1及冻结母本。本次总质量目标仍在推进，未标完成。
