# R0 第一轮启动与当前状态

2026-11-11 用户授权“按照r0开始推进训练”。本轮独立40分钟，4096环境，父square1_030m；完整PPO恢复已由RESTORE回读，原冻结不变。

80env×200步与4096env×48步均不更新优化器，numerical0、rawaction槽误差0。4096探针810次episode事件中closure564，最大3.08mm，2mm单envreset有效，未把numerical0写成无物理重置。80env探针后将课程路径累计改为指令方向净位移，原探针源与原结果保留。

R0完整DR、20%名义/80%DR，20%平地交叉分配，实际四组164/655/655/2622。7地形族（含平地），不含中级台阶、air reset或高级落差。4个浅等级，最低出生，失败降级、净位移2m且地面变化至少3mm无失败升级；地形边界单列timeout。

真实启动15:36:57 Asia/Shanghai、PID1152439。STARTUP确认2.5ms物理/20ms策略、TGS32/4、−1.0e²、35D/78D/6D。FIRST_UPDATE首完整PT已取回并核SHA；每5分钟检查点与评测待逐次补入。

评测计划：周期MuJoCo名义Flat回归保留，轮末在相同PhysX DR/初态/扰动配对父与本轮8检查点，分别检查Flat固定任务和level0六类浅地形正反向越障。各地形10初态、20s，2m净位移和至少3mm实测地面变化作为越障诊断，不把站在出生平台算成功。

当前训练未结束，不宣称R0通过或自动进入R1。

{
  "status": "running",
  "launch_local_time": "2026-11-11 15:36:57 Asia/Shanghai",
  "pid": 1152439,
  "job": "train040m_rough_r0_r1",
  "probe80_numerical": 0,
  "probe4096_numerical": 0,
  "probe4096_closure": 564,
  "probe4096_episode_events": 810,
  "probe4096_closure_peak_m": 0.0030804581474512815,
  "first_complete_sha256": "e8235ef8443de1a7b49904e1676039c6a7f02c267105388313fb49c1ed1a4374",
  "next": "check/download unique fullPT every5min; localMuJoCo replay; final samebatchFlat andRough evaluations",
  "all_probe_reports_preserved": true
}

## 5分钟补充

model_005m / iter22660 / SHA b914bd2a29898b6270350d20ec3ec6e9086c31795ab12f3c93e41c64a84e3531，完整PT与课程状态已取回。MuJoCo名义2.0→2.26540、2.2→2.54904，原速度容差0/20；后退/旋转/两高度各10/10、reset0。此回放不替代同源PhysX fullDR评测。训练仍在运行，numerical0，closure和地形boundary均照实保留。

## 10分钟补充

完整model_010m / iter22702 / SHA87925dd405b84c2a54aecc927f25bbc2db8247a2769fcaa43f5768f9f1db6b43已取回、PPO和课程状态完整。MuJoCo名义2.0→2.2805、2.2→2.5875，前进原精度0/20；后退/旋转/两高度各10/10、所有reset0。训练numerical0；完整DR同源效果等轮末配对，当前不晋升。

## 15/20分钟补充

15m前进名义回放2.2241/2.5302；20m为2.1844/2.4792，超速逐步减少但原速度容差仍0/20。四项其它正式技能各10/10，所有reset0。15m、20m完整PPO及课程状态均取回；训练仍numerical0，closure事件保留。20m的完整PT SHA64affb5794f5518f2b84611ab7d3904aef95b7e1ea660e1efd87820102cc14d6。

## 25/30分钟补充

25m前进MuJoCo名义2.17705/2.48537；30m2.13395（10/10）/2.41392（0/10），原精度不改。后退/旋转/两高度在两个检查点均各10/10，无reset。30m完整PT / iter22868 / SHA9316106bb24142475aaf3566bf836001d347a1077e7f2566c9377a0fa6231d4f，权重和课程状态已取回。训练numerical仍0，最终R0和Flat配对未完成。
