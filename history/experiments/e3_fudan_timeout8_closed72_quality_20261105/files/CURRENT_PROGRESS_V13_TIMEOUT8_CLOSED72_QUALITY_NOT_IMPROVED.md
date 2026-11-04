# V13 — timeout8真实closed72；原范围0/74；仍保留1cd

- 当前goal goal-c490e4cc-b28b-440e-bde6-30ee956813f0 rev3 active/armed/max14；目标是质量，不标complete/pause/blocked。
- [完整实测报告](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_TIMEOUT8_CLOSED72_QUALITY_RESULTS_V1.md>)与[紧凑选择](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_TIMEOUT8_CLOSED72_QUALITY_DECISION_V1.json>)已发布。本窗72真实PPO/两Adam各1440/69,120,000优化转移；累计205/4100/147,942,912，原始4096×64不能冒充N20000。完整保存48个未优化控制。
- 完整新候选SHA 3e64ebca251b0457409fe83521da69c99378f4fedd7726c7d5761c6a39ac868e，1204253399B；母版1cd、4096祖先47937、上窗8af4与pi-only93753各自独立。完整learner续接实际CPU一次，环境/DR/history流切断fresh。所有原训练wait/cost/release闭环/errors空，无本任务native训练剩余。
- 原N80实际父1623792/worker1623801/controller1623785，单N80/160/seed20260928/fullDR/原74首episode+6normal。父actual qualification原本为true；collector忘改kind导致仅reader误报false，旧文件保留，新metadata-only reprocess已纠正，不重跑SDK/模型/父资格。结果0/74，normal物理终止0/6。
- MuJoCo相同5姿每条400control/8s全finite。新候选均值高度0.182897、速度0.391495、位移3.020520；母版0.241437/0.038073/0.639393；严格信用双方0/5，但母版确实抬高了身。不能称全DR/硬件/视频同端姿态成绩或native因果退化。
- Decision KEEP_REGISTRY_V12_E3_1CD_NO_3E64_PROMOTION，所有候选保留，H1/其它专家不动。下一步单一质量干预源分析尚未形成部署，不按205步数盲续。
- 原训练observer009、原N80observer895均completed0并已收输出；CPUexport和MuJoCo命令均完成0。旧once/roots不可重放，不为状态/Git开模型或raw。
- 最近已验证archive cce218551eba7d527e4b611a41bc6536c1f75039 / trial-20261104-e3-fudan-n20000-timeout8-real-fullresume-native，tagobj ede4f6dd6cd2a8aea2e087c04a2904f562662733。原record WinError206已在同一record短pathspec续完并归档，不重放record。本次72闭环、reader false+纠正、MuJoCo与质量决定等待下一有意义合并阶段archive；新archive务必使用短directory pathspec适配原record，避免Windows argv过长。feature-only/main只读。
