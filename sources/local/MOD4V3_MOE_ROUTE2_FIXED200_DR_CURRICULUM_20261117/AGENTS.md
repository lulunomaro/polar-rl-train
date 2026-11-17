## 2026-11-17 22:20 人类新授权40分钟：0DR→DR课程已实际PPO开训

最新人类“开始40分钟ppo训练”覆盖旧22:30绝对截止，本次独立2400秒从实际PPO起点2026-11-17T22:20:06.147919+08:00计时，2026-11-17T22:59:06.147919+08:00停算保存，2026-11-17T23:00:06.147919+08:00硬截止，不自动延长/训练后重启/晋升。实验MOD4V3_MOE_ROUTE2_FIXED200_DR_CURRICULUM_20261117，job=train_fixed200_dr_curriculum_40m_r2，PID3593510/守护3593511。首次启动遗留7200秒断言在0PPO/0Adam时安全退出，全部证据留evidence/startup40_failed_r1，勿混作训练；本次预算不额外扣旧326.837s历史短轮。

起点v1/a55eeaed；2048/819全20cm，E1先真0DR center→0DR五起点/速度→成功后原fullDR环境占比10/25/50/75/100%，E0真c874及normal原fullDR。首轮1PPO/12真实Adam，E1 head/encoder/独立STD/critic均实际更新，E0 actor/STD/critic变化和梯度0。沿用600步已通过预检的课程/奖励/物理，只改40分钟计时与审计字段，原预检/代码哈希和差异保留。

每5m完整PT，5/10/20m独立E1五点+E0flat60，最后完整冻结回归与1x视频；正式<=.6和fullDR毕业不能拿0DR宽速成功冒充。本地monitor与heartbeat mod4v3-0dr-40已启用，只监测/评测/归档，无新训练授权。默认c874/CURRENT、原010m/8391、旧失败目录和物理/PD/电机/78critic/6动作/2mm仅诊断不变。见本目录LAUNCH_REPORT_40M.md和evidence/LAUNCH40M_VERIFICATION.json。

最新人类允许E1先0DR学轨迹、干净多起点泛化后逐步恢复原fullDR范围。E0真c874冻结与原normal fullDR不变。当前仅零更新真实0DR预检，未达起步门槛不得启动PPO；不得把0DR成绩称fullDR毕业。200mm单高、正式≤.6、原物理PD频率/78critic/6动作/2mm只读、保护原件不变。原22:30:31.928145截止和40m无完成止损暂保留，不擅自延长/再重启/晋升。
