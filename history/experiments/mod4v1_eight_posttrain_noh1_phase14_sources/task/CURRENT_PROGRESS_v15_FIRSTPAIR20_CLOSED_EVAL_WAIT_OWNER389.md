# 最新接续 v15：首批2x20已实跑闭合，原资源被另一个canonical任务使用，复评尚未开模型

以本页覆盖[v14](<CURRENT_PROGRESS_v14_FIRSTPAIR_TRAIN20_CLOSED_RETENTION_WAIT.md>)的job/Git/资源待收项；具体源/规范与复评派发仍查v14和[v13](<CURRENT_PROGRESS_v13_EIGHT_POSTTRAIN_NOH1_PAIR1_ACTIVE.md>)。用户Goal revision8 **active/armed，roundsStarted2/max12** 已再次get_goal证实；id `goal-1348948b-8b3e-4e93-85ec-317e88962347`。不另建/不完成/未到3轮不blocked。H1一直冻结，八范围2条完成首窗但未技能复评，后六E2/E3/W35/Curb113/S135/S50未消费。

## 两个真实20updates与完整终末

[已核真实汇总](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/reports/PAIR1_ACTUAL_FULLSTATE_TRAINING_CLOSED_SUMMARY_V1.json>)已生成，job `pwsh-93fe64ada9bd4c1b`完成且已收。两者均RC0/各原source byteopen1 decode1/完整save/currentlive+oldunknownroot不丢；原parent1457086已12:23:29全部wait/成本结算/原私EX两卡+finiteSH+authorityEX释放，errors[]；不再启动旧once。E0真实20/400optsteps/960万transitions/iter32004/17Adam641600/LR.0002562890625/SHA6cdac1e4...；Curb真实20/原lastlooplabel32959（delta19不是19update）/17Adam660800/LR7.59375009996e-05/SHA db3d5a6a...，各完整候选都未覆盖母本。原producer时间戳派生成本 E01146.7129719257355 + Curb1272.1442589759827 = **2418.8572309017183 expertseconds**，非账本复制/新加计费。**技能仍pending**，20PPO不代表pass。

## 复评唯一派发与collector

root `/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_PAIR1_POSTTRAIN_RETENTION_N80_V3_20261102_123301_1793593981516967400`，parent1458948，12:33:06派发，originalboundedwait1800s（约13:03耗尽）。两候选原fresh80 E0 20s1000/Curb15s750/同seed20260928、原factory/DR/physics/skill界，无PPO/GO/canonicalwriter，整20krootCPUcache不apply/slice历史。Source只改精确2memberbarrier+新actualsourcepin；原V8不改。

**唯一相关仍在跑的后台job `pwsh-48098626586548ec`**：[collector](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/collect_pair1_retention_v3_once.py>)15s看publishedmetadata/phase变化才打印，4500s上限，模型/raw/SDK/C操作0。最后job_output仍running/no新phase，当前还未ACTUAL_GROUP_ADMISSION/CHILDREN/barrier/modelRead；不是技能失败。先收此job，不开第二次评测/不复用once。成功/等待耗尽均会收原exit/error/closed；若耗尽等资源真实改变后才新目的/新root重试。

## 已实际只读归因：不是本组锁泄漏，另一个项目任务正在用原authority+GPU1

[12:45:34只读诊断](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/reports/PAIR1_RETENTION_ORIGINAL_LOCKHOLDER_DIAGNOSIS_ONCE.json>)来自project原C最小状态、原锁fuser引用与授权GPU snapshot，**无取锁/信号/模型/SDK/预算写**：

- 原C当前active_owner **1458549**，kind **Linux_LQR_MPC_DEPTH_STUDENT389_1793593791143544998**，started1793593791.143538（约12:29:51）。不是我们已闭合1457086；budgetremaining **369023.2153682709**，reserve86412.86069250107，预算本身充足。
- 原GPU1私锁文件由该关联worker **1458558**打开（fuser只显示引用PID，勿把它误当独立flock权限证据）；GPU1free19653MiB/util13%，GPU0free24203MiB/util0%。原finite_env锁fuser返回1未见引用。但原eval还要求**C.active_segment=None**，所以即使GPU0看起来空，换GPU0也不绕过当前canonicalactiveowner gate。
- 因此保留原锁等待、不清锁、不改共享/独占、不kill foreign/不接管那个owner、不启动第二canonicalwriter。不是需要重新打开本组sourcePT/改目标asset，也不是预算不足。别以“找空闲卡”为由绕过原uniqueowner。

## Git状态（均实际push+remote feature/tag/peeled验证）

phase12 **6d04141cb75c83220c60033c7e56b4f8174e507a** / trial-20261102-mod4v1-eight-posttrain-noh1-firstpair-phase12 / annobj5d5eafba36df03e226fd2a4c78ffc8258512bbfc。
phase13 **22b88b8a1c92ca7bf8f09dd168ed0696c5ff0de2** / `trial-20261102-mod4v1-firstpair-train20-closed-retention-wait-phase13` / annobj **d03b0f2201c194b04c5c41a0adebc986bed1cbcb** / peeled22b88b8a，11696sourceentries11662texts，feature mod4v1-experts-fulldr-rm70 clean。pushjob `pwsh-b292a3969a964ada`已完成已收。phase13包含2x20闭合与summary、v14、新复评source/两本地source错误/真实dispatch与早期锁等待，**不含之后这条12:45锁归因脚本/报告与v15（待phase14）**。

Main独立又前进到 **938b9ee8458f09a47e369995c8bfb1064b052a1f**，这是phase13 verifier只读实际值，不再4b571但正常，没pushmain。继续只核当前readonly40hex，不能再硬绑历史值误报push失败。不为Git重跑GPU/开PT/raw，晚生成复评error/技能结果append nextphase。

## 下一步

1. 保持原复评collector，收实际resourcewait结束/actualrun/close。资源尚被389使用时无新的PPO/SDK动作，做未消费6角色源/元数据准备即可；允许wait不等于blocked/完成。
2. 若成功回放，按原scope与V8 baseline比较E0诊断MAE/noordinaryfall与Curbup22/27down27/27stand26/26，保best/退化留回滚源；无E0全局毕业阈值不发明。若仅WAIT耗尽，新候选模型仍未评，不把它叫失败/通过。
3. 在原canonical无owner/私EX+finiteSH实际准入后推进新pair2 E2+Curb113、pair3 E3+S135（stager源已生成未执行，尤其S135handoff schema需先检查），pair4 W35最新8d+S50尚需sourcePlan集成，绝不重跑已完成E0/Curb20窗作调试。
4. 新source/真实错误/等待/技能/接续报告phase14继续归档。Goal保持active，八专家后训练+评测实证前不宣全完成。当前没有别的运行后台job；两sourcechildren已inactive，所有训练/归档/diagnosis jobs都已读终末。
