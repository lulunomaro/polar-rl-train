# MOD4 Rough隔离适配：2026-10-02 13:10最新交接

当前生产仍为 `/home/egde/rl_candidates/MOD4_mild_dr_trial_20261001` 的平地轻DR。
本目录已运行两类隔离验收，但尚未部署Rough训练或地形复位。
没有停止主训练，未修改其USD、物理、奖励、PPO或预算。

唯一canonical账本为
`/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json`。
总有效PPO108000秒，用户20小时扩展ID `USER_ADD20H_20261001_2341` 已应用一次。
13:06时余35641秒、截止约23:00:14；数字会过期，必须读实际账本。
不能复制预算、重新应用扩展、重置charged或重复结账。

## 已完成的证据

- 固定SCUT提交 `b8ff79f3df855faf9dc92f4a282bd80c42649466` 的11类活动配方已映射。
  `upstream_v1`保留11类，`intro_v1`明确是5类入门子集，不是完整一比一；尚未选定生产课程。
  上游部分台阶起点15cm，tiny_step才2–6cm。没有在起伏下放无限Plane。
- `TERRAIN_RUNTIME_VERIFICATION.json`：实际TerrainImporter collider
  `/World/ground/terrain/mesh` 上81条射线，80命中、1条边界外miss；
  Warp/CPU/PhysX命中语义一致，最大高度误差2.90e-7m和2.98e-8m。
  只验收2×5诊断地形的几何/射线，不代表机器人接触、复位或技能验收。
- `rough_reset_geometry.py`读取实际生产USD关节帧，生成完整FK及34碰撞体表面采样库。
  实际资产 **31 bodies / 30 tree joints / 6 closures / 4 mimics / 34 colliders**。
  8个自由转动导轮带来8个额外刚体/关节，旧22关节描述不能直接用于当前资产。
  原库133姿态显式记录20个腿/被动/mimic关节，2轮和8导轮角补0；输出全部30关节q。
  生产高度范围内74姿态，qd仍需完整清零。
- `MOD4_RESET_COLLISION_BANK.npz`已在本机与目标机：133姿态，每姿态25200采样点。
  CPU闭链最大残差2.33e-10m，mimic残差0。**表面采样不是连续实体非穿透保证。**
  必须加入实际支撑、净空、边缘和独立动态接触验收后才可安装reset。
- `ROBOT_FK_RUNTIME_VERIFICATION.json`：实际PhysX31刚体/30关节，7个合法库姿态
  加非零轮/导轮角，与CPU FK对照通过；最大位置误差2.43e-7m，旋转矩阵误差9.55e-7，q回读误差0。
  仅独立探针关闭重力、根高2m、sim.forward()运动学核对，未证明动态承重或地形复位安全。
- USD SHA256 `694e9d5414401972d9186c44baef25aa785e1e07409ce9acf1ef553b9279dd87`；
  合同SHA256 `cbcdacdf2b15d6a5fb1e5650e418443ff376ee23334e47e1ef36fcb79c32719f`。
  当前生产源与旧候选快照的哈希复核见 `HEARTBEAT_20261002_1244.json`。
  新组件源冻结见 `CANDIDATE_SOURCE_FREEZE_v2.json`；原始manifest保留作为历史。

## 隔离探针修复记录

首次Kit未继承既有EULA接受标志导致bootstrap EOF；隔离进程沿用生产已设置同名标志后启动。
另一次PhysX射线探针未开启scene_query_support导致全部miss及空normal统计异常。
仅在该独立探针的SimulationCfg/PhysxCfg启用场景查询，三方对照随后通过。
Kit关闭可能使报错脚本退出码仍0，故保留error.json、各retry日志，以显式带时间戳pass报告为准。
这些是隔离探针程序问题，不是生产故障，未修改生产或增加预算。两类探针均已退出。

## 必须继续实现

1. 接入实际地形、root/body/wheel/forward scan，替换候选Plane/RMUC查询；miss显式失败。
   校验环境原点、collision group和坡面高度语义。现在没有完整可训练的Rough任务。
2. 用实际30关节库实现完整q/qd/root地形复位，检查坡顶坡底平台、台阶边缘、双轮支撑、
   底盘/导轮净空及动态接触。空中与落地复位分开验收；不能删除flat guard后仅移高root。
3. 映射上游地形指令覆盖、扫描、airborne/预接触状态机、边界、奖励和课程。
   保留35D actor/38D critic/6动作、256/128/64网络与完整optimizer/std。
   尺寸、云台、电机、弹簧用MOD4映射并明确差异；新增观察维度须先验证权重迁移。
4. 先小规模动态物理、闭链、真实地面、同权重平地回归和地形冻结基线。
   不重复现有自动回放；同验收探针不再重复。
5. 真切换时核实PID/cwd/start ticks，关闭旧父重启/评测权限，STOP_AFTER_SAVE保存退出，
   确认无遗留评测，结清同一账本和锁。128env两轮PPO、20k材质/有限数预检不能与20k生产并跑。
   PPO预检计预算、弃用权重；正式从最新完整actor/critic/optimizer/std/iter继续。
   失败恢复保留轻DR与同一剩余预算，全部检查点保留。
6. 同步Rich终端及自动化；预算不足安全切换则只准备，到点保存终验停止。
   不翻terrain flag直接开训、不加载RMUC、不自动扩±2m/s。
   当前3500N/m预载弹簧不变，300–700N实物力行程未标定不得称鲁棒通过。
   后续才Rough v0、小陀螺、飞坡、跳跃和狗洞。

## 本轮生产复核

supervisor83478/trainer83510/TUI58640实际cwd/cmdline正常。
model13100 CPU回读68浮点张量完整有限，SHA256
`39589ac134d962a8ff0293502760e975fd14d189b3b9e05cf9d047e8819add17`。
现有例行12950回放64个已训练样本全部存活、各组实验准入通过。
最差已训练样本峰tilt7.15°、平均高度误差3.94mm、控制采样轮间隙1.45mm、双轮低载14ms；
均值不可冒充最坏样本，低力不可直接解读腾空，网格间隙/滑移不是实际接触流形。
正确执行器诊断已运行 `actuator_local_order_v1`：腿真实裁剪0，轮最差约0.379%；
旧腿错配shadow最高1.0，不能再据此宣称真实饱和。力矩采样10ms，不当子步峰值。
旧strict_pass_window仍false保留，试验准入不等于旧门槛毕业或实车认证。
12725曾有一项+1.5m/s间隙超标，7/8仍达该组80%准入，12950恢复；不得掩盖历史最坏样本。
继续每两小时巡检；现有监督器自动回放不要重复，短期波动不重启。
