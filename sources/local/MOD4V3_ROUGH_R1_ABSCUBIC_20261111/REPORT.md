# R1绝对三次项接续记录

平方2.0段015m完整PT已核SHA后SIGINT退出，无FINAL/SAFE_CLOSED。父iter23027；旧段numerical10、mimic1、closure3659/episodes24597，原始保留。

目标改动：仅速度项−2e²→−2e²(1+|e|/1m/s)。其余完整DR/地形/PPO/接口与门槛不变，课程等级累计计数保存，新物理episode；剩740s计入原40min，未额外开一轮。实际启动/回放结果待补。

已启动2026-11-11 19:04:48 Asia/Shanghai，PID1272268。STARTUP公式−2e²(1+|e|/1m/s)、vref1；RESTORE确认父iter23027/17项Adam、4096env、R1localsteps4104。首次更新iter23028，完整PT SHA34bb4a5b8566b22496811df586bfe1fb9e263b7e9c11592ef24b80f1f548af39。REWARD_VALIDATION实际方法核对对称性、原门控、pitch投影、原standstilldeadzone；无新增观测或solver变更。

三次叠加项005m：MuJoCo名义cmd2→2.46907、2.2→2.76098，仍各0/10；后退−1.50001、旋转和双高度各10/10，全任务reset0。此点未压住MuJoCo超速，保留实际结果，PhysX同源尚待评测。

三次叠加项010m：MuJoCo名义cmd2→2.40069、2.2→2.66329，各0/10；后退/旋转/高身10/10，但低身0.2指令平均0.22113m，超过±.02m判据，低身0/10，无reset。新出现低身精度损失，不能称所有旧技能保持。

轮末已完成2400.031s总PPO与三组同批评测；结论、原始失败和保存范围见FINAL_REPORT.md与DECISION.md。三次项未解决fullDR速度，原Flat1.5_020m保留回退；R1_010m和三次005m只读存档实验候选，未晋升。全11份R1分段PT实体归档。
