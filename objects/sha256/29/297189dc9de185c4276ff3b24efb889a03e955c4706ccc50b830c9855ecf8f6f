# MOD4 当前状态与协调单 (2026-09-13 20:00 CST)

## 正在跑的东西（单任务，勿抢占 GPU）
- 链路：`migration/linux/run_special_phases_v3.sh`（PID 838044），阶段序列
  `smoke(64env×250it) → tunnel → terrain → spin → fly → jump`，每阶段 512env×700it + 逐路线评测 + 版本门禁
- 当前：smoke（训练 PID 838103，日志 `logs/isaac_mod4/stage_mixed_fixedplant_20260912_194609.log`）
- 植物/控制器（已写进 run_manifest）：
  - `RM_MOD4_USD=incoming/mod4_rolling_20260913/chassis_mod4/isaac/robot.usd`（sha `7b4d853563551755`，8 个被动转动导轮）
  - `RM_LEG_KP=2500 RM_LEG_KD=10 RM_LEG_KI=0`
  - 调参文件 `migration/linux/tunnel_tuning.env`
- smoke 健康：closure session max 0.4 mm、mimic 1.7 mrad、closure/mimic 终止 0、无 NaN/OOM。

## 关键结论（不要再用旧结论）
1. **交付 USD 的闭链几何与 CAD 完全一致**：CAD 硬限位关节解 → 6/6 spherical closure 残差 `0.00000 m`
   （`migration/linux/check_usd_closure_consistency.py`）。所谓"Isaac 蹲不到 0.178 m"不是模型错。
2. **真凶是腿位置环刚度**：交付 PD `leg_kp=60` 下垂 0.13 rad → 包络 273.7 mm；`RM_LEG_KP=2500`
   时 246.0 mm（洞口 247.2 mm）。用户 MuJoCo 验证用的 PI 环是 KP=320/**KI=90**，纯比例等效需要更高刚度。
3. **导轮必须能转**：旧的单刚体焊接 = 8 个滑块，会让低姿态锁死。新植物 0.12/0.18 m/s 穿越：
   顶板接触 0 步、主轮平均 35 N（MuJoCo 41 N）。
4. 旧的 `tunnel_probe_20260912_181236.txt`（hip=0.35/diff=-1.06、wheel cmd=0、只跑到 0.25 m/s）
   结论作废——方法学错误，不代表真实低姿态。

## 禁止事项
- 训练运行期间不得修改 `isaac/mod4/*.py`、USD、JSON、奖励配置（v3 链每阶段核冻结哈希，不一致 exit 4）
- 不得启动第二个训练；不得 kill 正在跑的链（它是单次相位序列器，不做自动重启）
- 真机放行前必须完成 DR 最差样本净空评估；静态余量只有 1.2–1.6 mm

## 交付物位置
- 修复包：`incoming/mod4_rolling_20260913/`（README.md / TASK_LIST.md / chassis_mod4/isaac/{robot.usd,import_contract.json} / tools/）
- 证据日志：`docs/probe_crouch_kp*.log`、`docs/probe_tunnel_cross_pi.log`、`logs/isaac_mod4/chain_v3b_run.log`