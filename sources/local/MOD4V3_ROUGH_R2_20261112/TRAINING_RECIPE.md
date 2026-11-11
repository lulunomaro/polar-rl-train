# R2 首轮实际训练配方

## 接续身份与调用

父为R1第二轮005m，iteration22959，SHA `0dcc15f5ecfca08107dba8b1a1d80de57c777218b5f3a928c094be66c73a644f`。完整恢复actor/critic/STD/Adam与RNG，接续R1各地形levels/types/offsets/累计计数；物理episode重新开始。该课程接续使用4096环境，不把少环境探针当成完整课程恢复。

本轮实际调用：`launch.py train040m_rough_r2_r1 --kind train --num-envs 4096 --seconds 2400`，训练模块profile为`rough_r2`。完整参数、远端Python/support/package路径见[PLAN](PLAN.json)和[evidence/TRAIN_LAUNCH_OUTPUT.json](evidence/TRAIN_LAUNCH_OUTPUT.json)。执行时参数原件见[evidence/TRAIN_PLAN_AS_LAUNCHED.json](evidence/TRAIN_PLAN_AS_LAUNCHED.json)；后续PLAN只纠正继承的预算/混合分布文字。

PPO：LR3e-5 fixed、clip0.1、3epochs、4mini-batches、rollout24步、seed66；一次2400秒训练窗，每300秒原子保存完整PT，下载核SHA后作固定权重检查。轮末固定权重评测不做optimizer update。

## 本轮新增的落地内容

采用ScutRoughR2Env继承原ScutRoughR1Env。平地或已有R0类型level0–1的reset有30%替换为air；中级正反阶不作air出生，继续原R1混合训练。实际全体air比例依地形和reset频率变化。其余normal/ground分布保留；被替换的ground样本取消其0.2秒零力矩期和1.5秒指令覆盖。

air姿态取原MOD4闭链可行站姿bank，根高度设为当地raycast地面＋bank站姿根高度＋随机0.05–0.10m；原生SDK四元数，roll/pitch±0.03rad、yaw±pi，初始rootXY速度±0.1m/s、其余root速度和全部关节速度0。观测/动作延迟历史按既有reset语义刷新。额外落高不是绝对worldz，也不是主动跳高成绩。

复用本项目已保存的SCUT Flatv1 airborne状态机与airborne奖励系数。低落高air reset内部force-enter，使5cm下落也参与奖励；自然进入条件仍是body离地>0.30m、双轮净空>0.08m且持续0.02s。退出参考轮接触>20N持续0.3s、base接触>5N持续0.25s或最长1s。内部高度奖励target保留bias0.12m/max0.36m；landing trajectory关闭。只有内部奖励分段，actor末7个control-mode槽仍固定`[1,0,0,0,0,0,0]`。

airborne权重沿用已保存Flatv1：joint_pos_limits−10、wheel_heading_x_centering+10、air_wheel_zero_torque_exp+20、precontact_wheel_directional_speed+10、其shortfall−10；MOD4无SCUT rear机械止挡对，原适配器仍不给虚构的止挡奖励。air内部分项倍率沿用参考undesired_contact25、termination6、flat_orientation_y_v0、track_height_square0；普通段保持原配方。准确配置由scut_rough_r2_env.py的configuration_r2及同目录scut_flat_rewards.py的configuration_v1共同确定，实际生效权重见STARTUP。

## 保留的任务和物理

原−1.5e²前进对称平方惩罚、指数速度权重1.2、其余normal奖励；35actor/78critic/6action，动作仍为原始策略动作记忆。20%名义/80%完整DR、20%平地/80%R1地形独立交叉，已有质量/COM/材质/摩擦/气弹簧阻尼/增益/输出倍率/外力力矩/速度推扰/噪声/物理时间延迟范围保留。

训练plant、闭链与mimic、原电机速度力矩包络保持；物理2.5ms、PD10ms、策略20ms、TGS32/4、2mm单环境闭链重置。实际USD根文件SHA `e057969b136fd75613bb8d77985d43d043f54faae62dc060afb718ebabbe1c1c`；wrapper和contract读回记录见[evidence/TRAIN_SOURCE_MANIFEST.json](evidence/TRAIN_SOURCE_MANIFEST.json)。

## 结果从哪里查

[evidence/training_round](evidence/training_round)为每次保存收据、SHA核对和名义MuJoCo固定回放。MuJoCo采用既有5ms传感器/动作延迟口径，与PhysX名义0延迟分列。轮末所有8个5分钟保存点及父模型在相同初态下比较落地、Flat原任务和R1 level0/3；落地成绩只计首次物理episode，reset后的站姿不给成绩。

本轮只适应5–10cm额外落高。现有模型主动起跳高度未测，华南虎参考pose z不能直接当作MOD4已完成的跳高或落高。
