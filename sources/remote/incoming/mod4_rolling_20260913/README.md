# MOD4 滚动导轮植物修复包 (2026-09-13)

本目录是 MOD4 串联腿底盘"狗洞穿不过去"问题的**独立修复包**。不改 STEP/SolidWorks，不覆盖
交付资产、日志或 checkpoint：交付件 `incoming/mod4_fixed_20260912/.../robot.usd` 仍是
sha256 `1d437847778ad04ddc3e1e936878e31cf3cc2917e8e105078e5e95daa0d862b4`。

## 1. 两个真实缺陷

**一、8 个导轮被刚性焊在一个刚体上。** 交付 USD 用单个刚体 `/Robot/links/guide_rollers`
（`/Robot/joints/chassis_guide_rollers_fixed` 固定关节）承载 8 个圆柱碰撞体，PhysX 里等价于
8 个固定滑块。唯一能塞进 247.2 mm 洞口的低姿态下（root≈0.178 m）主轮离地约 1.8 mm，
全部载荷落在这些滑块上，机器人被接触阻力刹停。实车是轴承上的惰轮——必须做成被动的
转动关节，把"滚动阻力"交给关节而不是靠把碰撞摩擦改成 0。

**二、腿位置环刚度不足。** 用交付契约 PD（`leg_kp=60`）时机构在蹲姿重力矩下垂约 0.13 rad：

| 指令 hip | 实现 hip | root | CAD 包络 | 判定 |
| ---: | ---: | ---: | ---: | --- |
| +0.4702 (KP=60) | +0.3221 | 0.2067 m | 273.7 mm | 比洞口高 26 mm |
| +0.4702 (KP=1500) | +0.4666 | 0.1796 m | 246.5 mm | 勉强 |
| +0.4702 (KP=2500) | +0.4671 | 0.1791 m | **246.0 mm** | 通过（余量 1.2 mm） |

这不是模型错：用 CAD 硬限位关节解对**交付 USD 自身**做前向运动学，6 条 spherical closure 残差
全部 `0.00000 m`（`migration/linux/check_usd_closure_consistency.py`），交付模型闭链几何与 CAD
完全一致，姿态可达。用户 MuJoCo 验证用的是带积分的位置环（KP=320/KD=10/**KI=90**），只看比例项
会低估所需力矩。

## 2. 产物

| 产物 | 说明 |
| --- | --- |
| `chassis_mod4/isaac/robot.usd` | 8 个导轮各自独立刚体 + 被动转动关节（轴向=车体 Y），旧的固定关节与合体刚体删除。sha256 `7b4d853563551755…` |
| `chassis_mod4/isaac/import_contract.json` | 从新 USD 重算：31 bodies / 30 树关节(22+8) / 6 closures / 0 fixed / 34 碰撞体 / 277 视觉 / 6 执行关节 / 8 个 roller_joints |
| `tools/build_rolling_rollers_usd.py` | 生成器（幂等 / `--dry-run`）；质量 0.0025 kg/个 = 交付 0.02÷8（派生值非实测），实心圆柱惯量，轴承阻尼 1e-4 N·m·s/rad **TO BE CALIBRATED** |
| `tools/make_rolling_contract.py` | 从新 USD 重算契约（不照抄旧数字） |
| `migration/linux/patch_guide_sensor_regex.py` | `guide_contact` 改为匹配 8 个独立刚体 |
| `migration/linux/patch_leg_pi.py` | 腿位置环积分项 + `RM_LEG_KP/KD/KI` 运行时旋钮（默认=交付行为） |

导轮碰撞摩擦按用户要求设 0.9（滚动来自轴承），且不再做 `chassis_force - guide_force` 相减。

## 3. 证据（真实 PhysX）

* 闭链一致性（离线 FK）：6/6 closure 残差 `0.00000 m`
* 低姿态扫描：KP 60→2500，包络 273.7→246.0 mm（`docs/probe_crouch_kp*.log`）
* 穿越试验 `isaac/mod4/probe_tunnel_cross_pi.py`（新植物 + `RM_LEG_KP=2500 RM_LEG_KD=10`）：

| 速度 | 最远 x | 完整越过 x>1.45 | 洞内最小净空 | 顶板接触步数 | 主轮承载时间比 | 主轮平均法向力 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.12 m/s | 1.354 | 25% | -0.6 mm | 0 | 55% | 35.5 N |
| 0.18 m/s | 1.522 | 50% | -1.0 mm | 0 | 61% | 34.7 N |
| 0.25 m/s | 运行中 | — | — | — | — | — |

对照用户 MuJoCo：0.12–0.25 m/s 全通过、顶板 0 接触、主轮平均 41 N。Isaac 静态余量 1.2 mm
（MuJoCo 1.57 mm），**洞高/轮胎压缩/装配误差/俯仰随机化仍是放行前提**。

## 4. 用法

```bash
# 训练（一次只跑一个任务）
RM_MOD4_USD=$PWD/incoming/mod4_rolling_20260913/chassis_mod4/isaac/robot.usd \
RM_LEG_KP=2500 RM_LEG_KD=10 \
  bash migration/linux/start_mod4_stage_fixedplant.sh mixed <checkpoint> 512 700

# 穿越探针
OMNI_KIT_ACCEPT_EULA=YES RM_MOD4_MAP=rmuc2026 RM_MOD4_TERRAIN=field RM_DR_OFF=1 \
RM_ROUTE_KINDS=tunnel_cross \
RM_MOD4_USD=$PWD/incoming/mod4_rolling_20260913/chassis_mod4/isaac/robot.usd \
RM_LEG_KP=2500 RM_LEG_KD=10 \
  /home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python isaac/mod4/probe_tunnel_cross_pi.py \
  --num_envs 4 --speeds 0.12,0.18,0.25
```

## 5. 待标定 / 未决（不得当实测值）

1. 导轮轴承阻尼 1e-4 N·m·s/rad（无台架数据）；导轮质量 2.5 g 来自交付 0.02 kg÷8。
2. Isaac 目前用纯 PD `KP=2500` 等效 MuJoCo 的 PI 环；`RM_LEG_KI` 旋钮已接好但积分通路
   待逐位复核（下一步接上后重测穿越）。
3. 真机洞口净高 250 mm vs 最低蹲姿视觉包络的历史冲突：本包用小幅展开姿态
   （hip +0.470170 / crank -0.595844 / root 0.1787 m，包络 245.634 mm）解决，静态余量仅 1.5 mm
   量级，真机需顶面降矮或洞口复测。
4. 域随机化未开（质量/质心/摩擦/执行器/编码器/延迟/电池电压/地形摩擦）。

## 6. 验收状态

* `tunnel_roll` / `tunnel_cross`：**物理阻塞已解除**（探针 0.12/0.18 m/s 通过、顶板零接触），
  可进入课程训练；完整门禁（complete_rate ≥0.60、underpass ≥0.80、roof_hit≈0、每路线 ≥100
  episode、3 固定种子）仍待训练 + 逐 episode 评测。
* 其他路线沿用 v3 链的分阶段训练与逐路线评测。