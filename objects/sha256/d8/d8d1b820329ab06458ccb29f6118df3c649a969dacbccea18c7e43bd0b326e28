# MOD4 传感器鲁棒性 DR 候选与安全续训

用户 2026-10-02 授权“你看着弄吧”，要求自主推进可靠 sim2real。
本包第一阶段补传感器误差，不同时扩大动力学 DR 或提高转速。

## 当前状态与真实证据

- 原主训练：`/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002`，4 rad/s 档，white_v1；原生产没有因候选构建而修改。
- 候选：`/home/egde/rl_candidates/MOD4_sim2real_sensor_dr_20261002`。
- `reports/sensor_readback.json`：实际 GPU 输入管线回读通过；名义 actor、critic、物理 root/q 精确不变；两次复位/实际动力学后参数回读通过。0.5 秒闭链最大约 0.0733 mm、mimic 0.001691 rad、无 NaN。这不是 15 秒技能毕业或实车认证。
- 第一版监督器状态写入重复关键字错误，在任何配对/交接之前退出；生产不受影响。错误保留，已修复为 retry1。
- 正在顺序做冻结 model14817（成熟 3 rad/s）、两 seed、站跑/自转、white_v1 传感器关闭/开启配对，共八份 15 秒评测。不得把“配对已启动”写成“DR 生产已开始”。最新状态看 `status.json` 与真实 `/proc`。

## sensor_v1 白名单（原始物理单位，缩放之前）

| 输入 | 每回合持久偏置 | 每控制步独立均匀噪声 |
|---|---:|---:|
| IMU 三轴角速度 | ±0.01 rad/s | ±0.03 rad/s |
| 重力方向三分量 | 无 | ±0.005，之后重新单位化 |
| 四主动腿编码器 | ±0.005 rad | ±0.002 rad |
| 四腿关节速度 | 无 | ±0.1 rad/s |
| 两主轮速度 | 无 | ±0.2 rad/s |

同一环境所有感知通道共用每回合保持的 0 或 1 个控制步滞后（0–10 ms）；约 20% 动力学名义样本保持干净输入与零滞后。动作延迟仍为零。

这些是保守的工程压力测试范围，尚非实物标定值，不能声称复制复旦范围就保证 sim2real。后续应依据真实传感器日志/编码器标定/总线时间戳调整。

不改变真实初始关节姿态，不破坏完整闭链。critic、奖励、指令、上次动作、网络输入维度保持原值。噪声和偏置使用独立 RNG；同 tick 重算不推进队列；复位用当前新回合包初始化所有历史，不串旧包或伪造零传感器。

## 保持的生产合同

20000 env ×24、solver16/4、native Plane z=0、真 root 目标0.25 m、直线±1.5 m/s、站10%/直线60%/纯自转30%、当前上限4 rad/s；详细 USD、六电机包络、3500 N/m预载弹簧、奖励系数/PPO、35D actor/38D critic/6动作/256-128-64网络不变。完整 actor/critic/optimizer/std/iteration 暖启动。

white_v1 保留：共同质量惯量0.95–1.05、主轮μ0.8–1.0、六电机输出0.95–1.05并执行原硬件包络再裁剪。legacy DR_OFF=1 保持。禁止只翻 legacy 开关。

## 自动验证与切换

1. 两 seed 同权重初始 root/q 精确配对，站跑与3 rad/s自转都通过原实验准入后才继续。
2. 暂停经身份验证的旧监督器启动权限；当前 trainer 在完整保存边界正常退出，所有旧权重保留；结清同一账本尾段。watchdog 在交接失败时恢复旧父，禁止双开。
3. 最新正式4 rad/s checkpoint补同权重传感器关闭/开启的15秒站跑和自转；未通过则恢复旧父，不能同时硬加新难度。
4. 无原20k生产/遗留评测后进行新20k短物理/材质/感知回读、128env两轮PPO、20k四轮PPO与吞吐检查。PPO预检扣原预算，权重弃用；短 combined 姿态警告与独立物理合同并列保留。
5. 从原最新正式 checkpoint 开45分钟 sensor_v1 试训。结束保存后两 seed、站跑/自转、传感器关闭/开启再次配对。
6. 通过才继续；失败保留所有新权重，在同一剩余预算精确恢复保留的4rad/s源与white_v1。保存选择按 trainer PID 绑定 receipt，不能用全局最高 iteration 找回滚权重。
7. 传感器档固定后，沿用原转速阶梯3→4→6→8→10→4π，两次当档通过和多 seed 名义/DR回归才晋级；不同时扩大 DR。

小规模冻结评测可在单一主训练旁运行；若原父启动已有回放，本候选只让出自己的探针，不停止生产。大规模20k和PPO预检绝不能并跑两个20k。

## 唯一预算与恢复

canonical `/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json`，总180000秒（50小时），两次20小时扩展早已应用；本次没有新预算。不得复制、重置charged、重复扩展或重复结账。冻结探针自身不做PPO；若与旧PPO并行，账本仍会合法增加，不能声称charged不变。独立冻结窗口不计PPO。

`supervise_sensor_dr.py` 是一次性交接入口。存在 `handover_completed.json` / `SENSOR_PRODUCTION_STARTED.json` 后不能盲重跑。重启先验证实际进程退出，核算 active_segment 到最后健康/日志/完整checkpoint/关机上界，保留误差披露，再实现安全恢复入口。父失败但 trainer 还活跃时不能双开。

实际启动入口 conda Python：`isaac/mod4/supervise_sensor_dr.py`，日志 `supervisor_sensor_dr_retry1.log`。仅首次失败尚未交接的 retry 允许；其它重跑必须审计。`SENSOR_TRIAL_ACCEPTED.json` 才证明试训多seed通过，`SENSOR_PRODUCTION_STARTED.json` 才证明正式部署。

## 下一阶段优先级

不要让剩余预算只叠纯自转。传感器试训和4rad/s真实技能稳定后，接续已有移动候选的实际 SDK/观测奖励/PPO/多周期验收：低速1–2rad/s自转时世界定向净移速0.15→0.3→0.5m/s，显式启停/反向，保留原纯转/站跑。数学CPU测试不等于技能；不得把body恒速绕圈当定向移动。高速原地120rpm与0.5m/s低速自转移动分别验收。

COM/PD/更宽动力学/云台负载分别验证实际参数后渐增，暂不本轮一起修改。实物300–700N气弹簧力行程未标定，不能开启或宣布通过。Rough完整地面/闭链reset/scan/airborne还需SDK接入与验收，不直接翻地形开关或加载RMUC。

保留0.5ms真实卸载/冲量/均载与10ms网格间隙/滑移近似、局部执行器裁剪和旧接触影子门槛。积分100%不是连续承重或学习进步；低力非腾空、滑移代理非PhysX流形、组均值非最坏。门槛为项目实验准入，不是SCUT/赛场/实车认证。

生产实际切换后自动替换Rich终端，新root/active_log/canonical，5秒只本地文件刷新。线程巡检仍每2小时，健康无实质变化安静。预算到点保存、名义/DR终验、停止、删除自动化。


## 2026-10-02 23:46 基线复用优化

首次重新执行的sensor-off/white_v1平地15秒基线与原model14817同seed20261002报告比较：全部per_environment数组、初始root/q、checkpoint/seed/seconds严格相同。由此保留该独立新基线，并复用另外三份原白名单无传感器扰动基线，未来off路径报告明确标注reused_frozen_baseline及原报告SHA；FROZEN_BASELINE_REUSE_RECEIPT.json保存证明，不能说这三份重新仿真。四份sensor-on报告仍必须新跑。复用避免重复占GPU；当前并行评测期间生产吞吐约22.5k是资源竞争快照，不是生产源码改动或训练崩溃。原4rad/s模型15025 CPU68浮点张量完整有限，两个root的源码指纹均匹配。预算仍180000秒，无新增；生产继续，DR尚未正式切换。


## 2026-10-03 最新状态优先

完整sensor_v1在最新15150的+1.5m/s回归只有75%通过，含25.76度短时倾角，已安全拒绝正式切换，原4rad/s生产自动继续。成熟3档配对通过不能冒充最新4档通过。当前只启动同15150/同seed噪声与延迟的两份受控消融，无PPO/交接。详读 SENSOR_REJECTION_AND_ABLATION_20261003.md 与 reports/sensor_ablation_model15150_20261003/status.json。不得盲重跑旧sensor main或重复结账。


## 2026-10-03 对照已完成（本段为最新）

同15150、seed20261002、相同初始root/q和RNG的两个80env15秒冻结消融已完成，comparison.json已下载为本机ABLATION_COMPARISON_20261003.json。noise-only已训练64个样本全部通过原实验准入，最坏峰tilt6.283deg，无所核查指标违规。delay-only虽然各组87.5%或100%满足原80%组门槛、原admission布尔仍true，但存在真实严重异常：env75@+1.5峰29.541deg、双轮低载20ms、间隙2.013mm；env53@1m峰22.811deg；env4@-1.5 delta.2086、滑移代理.2045/.1521。不能以组通过率掩盖这些样本，或声称10ms延迟已安全适应。

本组受控对照指向延迟引起的鲁棒性不足，仍仅针对该checkpoint/seed，不冒称所有阶段/实车的普遍原因。先选择sensor_noise_v1（偏置/噪声且lag0）作为下一候选；10ms延迟需独立逐步适应/验证，当前不原样强切full sensor_v1。噪声档尚未生产部署，需要同最新成熟策略两seed站跑/自转配对、实际参数回读、完整PPO及保存边界接管。延迟消融的原true与失败样本都保留，不改门槛。

主root model15583第二次4rad/s技能和flat回归通过，当前原父1577904正在顺序执行同候选两个seed nominal/white的原定多seed复核（实际eval2199662只是读取时定位）。这是监督器主动保存后的冻结评测，无trainer是计划内，不是故障；不要抢发重复探针或重复启动。4档多seed最终结果未齐，完成后可能按既定规则到6，先读实际cap/状态再重基新DR候选。读取时canonical剩66606.55s约18h30min，无active_segment，冻结评测不扣PPO。本次没有新增预算。


## 2026-10-03 03:15 最新正式晋级结果

model15583的4rad/s两个seed20261002/20261003、nominal/white_v1、flat/spin全部8份15秒回放已完成，四对初始root/q严格相同，父receipt rate4p0_model15583_multiseed.json pass=true。纯4档四报告实际+3.9903至+3.9958、−4.0176至−4.0260rad/s，全部纯4组8/8技能与存活通过，最坏峰tilt1.2542deg。原window影子未改，非实车认证。

原父已把候选上限改为6并开始rate4p0_model15583_next_short.log的短物理预检，当前eval2208477仅定位；没有正式6档trainer时不能说6档已经学会/开训。只有新档短/全量物理和完整PPO预检通过后才从正式15583暖启动，预检权重弃用。white_v1保持，新增sensor_noise_v1仍未部署，不能同时升yaw和加传感器DR。继续查父实际stage/cap/receipt。

传感器候选env仍旧4档，仅15150噪声消融证据，不能冒充最新6档兼容性。后续按当前成熟cap重基噪声首档，做最新正式权重两seed回归/实际回读与安全接管；不要盲启动旧sensor one-shot。移动0.5m/s目标保持，需接续真实SDK/多周期净进度/PPO适配，不能所有剩余预算只提高pureyaw。读取时原账本余66606.55秒约18h30min（冻结期间不扣），无新预算。
