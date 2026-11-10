# 原 Step7 父权重：增强速度误差平方惩罚

> 授权更新（2026-11-11）：用户明确允许开训，并要求一轮40分钟、每5分钟完整检查点和检查。此前“暂不开训”段落记录的是奖励实现验证阶段；下述训练启动状态取代该运行边界，原验证结果保留。

日期：2026-11-11，Asia/Shanghai。用户要求开始修复前进退化，并提出速度指令追踪平方惩罚。沿用原父权重884cd07b与上一版集中修复后的DR环境，新增一个独立奖励profile和必要的调用/记录。此前暂不开训练边界保留：本轮只改奖励并做4环境实际执行验证，没有PPO、优化器或权重更新，不宣称前进速度已经恢复。

## 为什么这样改

实际调用的平方项不是表面权重-0.1直接乘原始误差平方，而是：

```python
e = tracking_command[:, 0] - root_lin_vel_b[:, 0] * cos(pitch)
term = (e * cfg.lin_vel_xy_square_sigma) ** 2
reward_step = cfg.rewards['track_lin_vel_xy_square'] * term * step_dt
```

旧配置weight=-0.1、sigma=.25，因此实际每秒项为`-.00625 e²`；指数项是`1.2 exp(-clip(e,-1,1)²/.5)`。当误差幅度大于1m/s，指数项已因clip不再区分更大误差，旧平方项仍非零但很弱，不能描述为“所有速度优化信号归零”。

新配置只调整同一平方项的两个表示参数：weight=-.5、sigma=1，实际每秒项为`-.5e²`。有效系数为旧平方项80倍，不等于总奖励或PPO梯度增强80倍。无新增奖励键，不再叠加另一份误差平方，指数项/其它奖励保持。

采用-.5是本轮可检验的起点，未宣称最优或已证明能解决退化。对低速、后退、站立漂移、超速都按误差平方对称计入；不添加只奖前进或只罚欠速的方向性激励。此处速度保持原来的水平前向投影定义，不混用轮速。

| 速度误差幅度m/s | 旧平方惩罚/秒 | 新平方惩罚/秒 | 新平方惩罚/20ms |
|---|---:|---:|---:|
| .15 | .000140625 | .01125 | .000225 |
| .6 | .00225 | .18 | .0036 |
| 1.2 | .009 | .72 | .0144 |
| 2.2 | .03025 | 2.42 | .0484 |

符号是负奖励；表中为惩罚幅度。数学上较大误差会更昂贵，超速与欠速同幅同罚。奖励曲线对测量速度的导数不是actor参数梯度；PPO还依赖采样return、优势与策略概率，不能仅凭曲线证明学习效果。

历史stage2b_speed_preserve检查点a58f8923同时改了指数、tight、平方和abs四项，名义MuJoCo2.2曾跑到2.44793；它不是此次单一平方项的因果验证，不复用为此项已成功的证据。

## 代码与范围

- 唯一父权重SHA256：`884cd07b3942df9c8484b905994e302906c84151f6f9c5d079a417ec98158f24`，iteration20838。路径沿用PLAN记录。
- 新支持文件：`support/mod4v3_ppo_v1/scut_flat_forward_square_env.py`，继承上一版`ScutFlatPhysicalDelayEnv`，只覆盖奖励factory。
- 新profile：`flat_forward_square`；scut_flat_train的选择/clip/checkpoint格式分支同步支持，STARTUP记录平方sigma及有效系数，未来checkpoint保存完整reward_recipe避免仅凭文件名恢复错误配方。
- `launch.py`绑定新profile、原父权重SHA与修正版目录，未来显式train运行默认短窗300秒；本轮没有调用train或会更新PPO的probe模式。
- DR质量/COM/摩擦/噪声、0/5ms物理时序、100HzPD、电机包络、35/6/78维、solver和原任务判据均沿用集中修复版，不扩大到fullDR、不改命令采样。
- 旧目录只读保留。新增的profile及调用在独立目录，没有覆盖原奖励配置或其它AI未提交文件。

远端目录：`/mnt/mod4_linux_durable_20261013/mod4v3_scut_target_native_20261107/step7_forward_square_20261111_r1`。

## 实际执行验证

`reward_probe_r1`：4个环境，24个策略步（.48s模拟），冻结父actor均值动作。命令分别2.2、2.0、-1.5、0m/s，高度.28，原DR开启。没有构造PPO或优化器。

已核对：
- 完整配置只diff两个字段：rewards.track_lin_vel_xy_square、lin_vel_xy_square_sigma；其它奖励逐项相等。
- 逐步用原生状态/同一姿态公式重算e²，raw项最大绝对误差9.5367e-7。
- 加权项与`-.5e²*.02`最大绝对误差7.4506e-9，未重复乘dt或重复叠加。
- 全部奖励项求和与返回total最大误差0。
- numerical=0，reset/timeout事件0，最大闭链.30919mm；obs/reward有限、actor35维和critic78维。
- 父权重前后SHA一致，最终支持源本地/远端SHA一致；CLI help接受新profile，未启动模拟做该CLI检查。

这是奖励执行验证，不是新训练成绩。冻结actor不会因为奖励改动而立即跑得更快；未重新跑已完成280/4096任务组，也没有把4环境短测当数值规模准入或能力毕业。上一版固定权重前进未通过的结果仍有效，未改写。

## 保留的失败与版本区别

`local-profile-setup-r1`：本地补丁预期行使用getattr(...,None)，实际源码是float(getattr(...,0.0))，因此assert失败。失败发生在写入train模块前，无远端任务或训练；读实际源后r2完成。SETUP_ATTEMPTS.json保留记录。

实际reward探针执行一次成功，无模拟器重试。probe后补了未来checkpoint的reward_recipe记录：只影响保存的metadata，不改已实测reward实现；实测时train文件全文保存在evidence/train_before_recipe_metadata.py，最终train文件另经语法/CLI检查和远端hash读回。缺失ERROR在下载前stat确认，未创建空占位文件。

## 当前结果与下一步

已把速度误差平方惩罚按真实SI误差增强，并在现有环境实际验证。没有证据要求从零重训；也没有证据保证-.5最优。下一次若进入适应训练，应继续原父884cd07b与这版环境，用既有前进2.0/2.2、后退、yaw、高度科目对比更新前后，不能用新总奖励升高替代速度误差改善。当前PPO未启动，GPU已释放。

## 证据

PLAN、BASELINE_SOURCES、REWARD.diff、REWARD_MATH记录版本/公式/边界；reward_probe.py与evidence保存实际调用、RESULT/LAUNCH/log/SAFE_CLOSED，REMOTE_READBACK与FINAL_SOURCE_READBACK记录文件状态、父权重和源SHA。FILE_INDEX索引所有落盘文件。原权重不提交实体。

外部一手资料仅用于区分奖励曲线与PPO优化机制：Schulman等《Proximal Policy Optimization Algorithms》，arXiv:1707.06347；实际项目公式与验证以本报告源码和回执为准。
