# 小陀螺两转每秒目标：逐档提速续训

2026-10-02用户明确授权小陀螺目标2转/秒，觉得成熟就提高；既有边转边走0.5m/s和自主加DR/地形要求仍有效。目标2rev/s=12.566370614rad/s=120rpm。不可把当前2rad/s说成2转/秒，也不可把目标登记说成已经实现。

## 生产与预算

隔离root为 /home/egde/rl_candidates/MOD4_scut_spin_rate_20261002。本机同名大写目录保存代码与报告。只用原canonical /home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json，总180000秒50小时，两次72000秒扩展均已应用，不新增、不复制、不清零charged。冻结无PPO不计有效预算，所有PPO预检计预算，场景加载计入各PPO段。旧spin/轻DR/平地目录与所有权重保留。

只调整yaw课程范围，初档1–3rad/s，后续上限3→4→6→8→10→4π。保留站10%、直线60%（±1.5m/s）、纯自转30%、左右均衡、4–8s重采样；不加自转平移，不同时改变DR范围或硬件。20k×24、solver16/4、nativePlane、root.25m、现有USD/6电机/3500N/m预载弹簧、奖励PPO与35/38D观测/256-128-64网络保持，完整恢复actor/critic/optimizer/std/iter。现有white_v1质量惯量.95–1.05、主轮μ.8–1、六电机输出.95–1.05/硬件再裁剪、20%名义保持。未标定的300–700N弹簧DR不启用。

## 一次性安全入口

supervise_spin_rate.py等待MOD4_AUTO_DIFFICULTY_20261002两seed×nominal/white的15s spin+flat收据通过，且reviewer已经结束恢复原parent；只在原训练自然完成完整保存、trainer退出、active_segment=None的冻结窗口暂停经身份核验的旧parent1239785启动权限。已有评测结束后先22env×300步3s的±1/±2/±3及ramp/站跑物理安全检查，新3rad/s跟踪未学会不算物理故障。短验收失败就恢复旧parent，不开新PPO。独立watchdog在接管前异常恢复旧parent，不能同时停住reviewer和两个父进程。

短验收通过后结束旧parent、取得同一个canonical lock、验证账本charged未变化，完整14141候选（以实时receipt为准）CPU回读68浮点张量有限；旧source保存。新owner登记后才20k×120步1.2s实际材料/法向/闭链/有限数验收，128env×2轮完整PPO计原预算且权重弃用，然后从正式source暖启动45分钟3rad/s试训。不是从预检model续训，不重置std。首次试训后和后续最长2h训练段均完整保存，顺序80env15sflat回归、88env15s rate回放。

rate_probe保留±1/±2低速自转，加入±当档上限及其启停反向；旧skill门槛不变，报告100Hz轮速/执行器局部真实裁剪和扭矩峰值（不称子步峰值）。两次连续当档技能+站跑通过后，再用同一候选两seed各nominal/white的spin+flat、精确相同root/q配对。全部通过才增加一个档，并在下档先3s物理、20k1.2s全量及128env2轮PPO预检；下档不安全回退当档命令，从保存的正式权重继续，所有拒绝报告保留。当前档安全但yaw跟踪未过可以继续学习，不因单次奖励波动重启。

原三种接触影子统计保留；子步卸载/冲量/均载、控制采样网格间隙/滑移近似、速度/倾斜/真实高度、action差分、导轮底盘载荷、闭链<=2mm/mimic<=.01、停车均核查。低力非腾空，滑移近似非PhysX流形，积分100%非连续承重或学习进步，项目门槛非SCUT/赛场/实车认证。脚本不修改奖励权重或以新统计掩盖失败。

## 高速与移动的可达性

现USD合同neutral wheel中心±.2188m，delivery contract却保留half_track=.235854m，两个数分别披露；实际姿态下还需轮中心读回。按半径合同.0625m推算，原地2rev/s需要约44rad/s（420rpm）轮速；按delivery半轮距则47.4rad/s（453rpm）。当前软件电机包络拐点44.01rad/s、空载55.36rad/s；这说明原地目标在建模转速范围内，但不证明有负载/热余量或稳定性。不得拿空载极限当比赛可用转速。

原先0.5m/s平均世界定向移动的cos投影方案需机身瞬时峰1m/s；叠加2rev/s时理想轮需求约60rad/s，超过当前软件空载包络。因此高速原地自转与低速自转移动分开验收，不能承诺此方案在120rpm同时达到0.5净移速。移动先维持1–2rad/s、.15→.3→.5m/s独立课程；若要高速也移动，必须重新测余量/可达净进度，不能抬电机上限或虚报速度。rate课程不替代该后续需求；自动巡检看到3/4rad/s成熟后应优先完成准备好的移动课程，再按真实余量安排高速专家/地形。

## 进程恢复与交接

一次性main已有handover receipt后不能重复。--resume仅用于真实trainer/评测退出、owner仍此root、canonical active_segment已经依据日志/checkpoint/shutdown证据结清后的恢复；不能把它当重启记账工具。若trainer还活跃但supervisor失败，先修父，不双开。NaN/OOM/Xid保留日志、完整权重和账本，先隔离诊断。fallback使用原root绝对train脚本及旧2rad/s配置，在新fallback_logs内继续同预算，保留新rate权重。

阶段切换后UbuntuRich必须跟随新root/status/active_log，显示目标120rpm与当档/实测rpm，不能继续误看旧2rad/s窗口。每两小时线程巡检、健康无实质变化安静；新阶段、故障修复、明显变化或完成通知。预算到点完整保存、final_flat/final_rate_mild/final_rate_nominal冻结终验，明确达到转速和失败项，更新终端后删除mod4-10自动化，不自动追加预算。下一AI先读实际status/reports/进程身份，不只信本文件的历史PID或目标。
