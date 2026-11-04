# V19 — heightgate closed25质量实测

- goal-c490e4cc-b28b-440e-bde6-30ee956813f0 rev3 active/armed/round2/14，未完成，H1/其它专家/Registryv12/1cd保持。[实测报告](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_HEIGHTGATE_CLOSED25_QUALITY_RESULTS_V1.md>) / [完整决定](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_HEIGHTGATE_CLOSED25_QUALITY_DECISION_V1.json>)。
- W9 root /home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_E3_FUDAN_N20000_LOWTIMEOUT8_FRESH1CD25_HEIGHTGATE_W9_20261105_024613_1793817973423106300，controller1629746/parent1629753/worker1630734，GO1793819803.834791；实际25/两Adam500/24m，零继承，1200controls/9600physics/2400feedback，pending0，完整146247539B/bf824b1eae9eef1fd1a9041d124be298d0e98898b7372cb0b86ec4822277f2b2，全部inner+outer wait/cost/release/error[]闭环。训练observer4bc已completed0/output collected。
- 原N80 source bf824，V5_HEIGHTGATE实际parent qualified+collector全部true，原0/74/normal物理0/6，非graduation。名义MuJoCo十条completefinite，候选0/5、母版0/5；候选h/v/XY 0.195248/1.012090/7.844078，母版0.241437/0.038073/0.639393。三正项实际1/.2/.5及新pre-reset被动测量真实，不是联合接受率。
- CPUexport正确一次整bf824 CPU read/hash/decode，派生338873B/7085ea4c23c2440d2d4dded4557e17d61646100c8c8153ec31df60e3f530a780、本地F:\RMPOLAR-RL\e3_fudan_recovery_alignment_20261104\FDNHEIGHTGATE_PI_ONLY_EXPORT_20261105_034900_1793821740329490800\pi_export.pt，不是完整resume。原source/bad候选不为状态/Git开启。错误源CRLF格式检查发生于本地输入读取、mkdir前，V2只保留合法原byte且原close/math/resource完全相同，均保留。
- 决策KEEP_REGISTRY_V12_E3_1CD_NO_HEIGHTGATE_PROMOTION，full候选保留，原模型不晋升。独立多seed/native因果未建立，goal_completeFalse。当前Native/eval已收口，不重放旧stage/dispatch/collector/export/record。
- 最近源准入阶段已核验565c504fbe62649c31f9962c56d83f71fdac888a/tag trial-20261105-e3-fudan-lowheightgate-original-admission（537源；main只读f9837af03f8e704b05c28c16ca13c21bc3aa958a，未push/reset）。其后实际GO/首11proof/closed25/N80/CPUexport/MuJoCo/本报告需新意义阶段合并归档；原record全部校验+短2pathspec/fullstagedset，模型/raw/JSONL/geometry先跳再stat/read/hash，不为Git重跑物理。


# E3低位正tracking高度门控 / N20000×25：真实质量结果

## 结论

**25次真实PPO完整保存并收口；原N80执行资格通过，原首episode信用0/74。**

**KEEP_REGISTRY_V12_E3_1CD_NO_HEIGHTGATE_PROMOTION**。原1cd/Registryv12保持，完整bf824候选保留；H1/其它专家不动，总质量目标未完成。是否优于前一候选的严格联合信用按实测计算：False，normal物理终止增加：False。这是一次单seed/单五姿诊断，不自动建立多seed毕业或matched native因果。

原74请求与6normal分列：normal首episode物理终止0/6，不是normal接受率；请求组物理终止22/74。原稳定50 public ticks=0.5s=25控制，request300=3s，不拼后续reset。

## 真实训练和唯一干预

| PPO | 策略Adam | encoder Adam | 已优化转移 | 继承 |
|---:|---:|---:|---:|---:|
| 25 | 500 | 500 | 24,000,000 | 0 |

只对recipe>=13的3正tracking项乘clip((height-.1781)/(.23-.1781),0,1)。实际constructed weights：linear 1.0、tight 0.2、yaw 0.5；原std/params保持，三个wrapper标记true。旧fall/normal、负error/height/potential/命令/五姿/8s/400timeout、Fudan核心和物理/fullDR均保持。

重新1cd actor8+critic8 MLP warm、随机fresh encoder/latent列0/STD.5/两Adam-LR-private generator-计数fresh，与旧25pilot同seed和设置，不续坏246ac/205。原1cd14715029B一次physical/hash/CPUdecode，source_optimizer/DR/history/旧迭代不应用；source_iter43090不累计到新25。新N20000/一fresh reset/raw35×5，非PhysX位级resume。

Native 1200控制/9600physics/2400feedback/24,000,000真实转移；未优化pending0控制/0转移。全候选146,247,539B/SHA `bf824b1eae9eef1fd1a9041d124be298d0e98898b7372cb0b86ec4822277f2b2`。inner+outer实际wait、成本结清/释放/errors=[]，GO至outer约1884.380s为metadata解释，不改原账本。

## 被动pre-reset描述，不是起身接受率

采样11,996,400低组状态，平均高度0.208249m，≥.23比例0.321068；已结束29,991低episode，峰值均值0.326453m，峰值≥.23比例0.997699。这是复用原phase.update的固定内存累计测量，无额外physics/传感/RNG，不把高度峰值当作姿态/静止/接触联合信用。训练信用0/29991单独保留，不是独立测试。旧run没有同一buffer，不用旧postreset .1781与此峰值推因果。

## 同五姿名义MuJoCo末态均值

| 指标 | 本候选bf824 | 前候选246ac（已发布） | 冻结1cd（本次实跑） |
|---|---:|---:|---:|
| 高度 m | 0.195248 | 0.198817 | 0.241437 |
| 倾斜 deg | 9.973 | 10.886 | 0.638 |
| 根速度 m/s | 1.012090 | 0.684080 | 0.038073 |
| 起终点平面位移 m | 7.844078 | 5.325706 | 0.639393 |
| 工程联合信用 | 0/5 | 0/5 | 0/5 |

双方五条均完整finite、400控制/8秒，同31体/30坐标/原限位、50策略/100PD/.0025物理、PD60,2/wheel.6/scales.5,10、400N-k2000-d3，无外力/yaw/动画。clean raw35/frame-major5，不是native fullDR/硬件/视频整腿同端姿态验收。严格信用还需h≥.23m、gravity_z<-.984807753、根速度<.03m/s、角速度<.2rad/s、双轮接触力各>1N/机身接触力<1N联合连续.5s；分项与联合条件分列。

## 执行、保存与IO边界

原唯一canonical/原charge_values/authority2EX/privateGPU_EX/trainSH-evalEX/reserve86412.86069250107/3900-3600-300/1800preGO保持，无外国signal/清锁/改账/扩预算/退款。CPUexport对新bf824仅一次整文件read/hash/CPUdecode、whole CPU根/未知字段保留，仅下载338,873B/14pi/82505派生，不是完整resume；本次正确EXCLUDED实际常量名且未重复旧import失败。原N80对相同新完整来源是另一真实用途的一次CPU缓存读取，不切片20k DR/history给80，不优化/安装训练gate。source-only旧生成器CRLF格式错误在输出mkdir前，旧源/错误及新V2 byte保持纠正已保留，未改原Appclose/actualwait。

## 完整证据与下一步

- [训练完整终态](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/reports/FDN_N20000_W9_LOWHEIGHTGATE_20261105_024651/CLOSED_RESULT.json>) / [实际原门控GO](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/reports/FDN_N20000_W9_LOWHEIGHTGATE_20261105_024651/FIRST_ACTUAL_ADMISSION.json>)。
- [原74 recipe与实际父资格](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDNHEIGHTGATE_FROZEN_ORIGINAL_SCOPE_RESULT.json>) / [同五姿十条完整物理案例](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_HEIGHTGATE_MUJOCO31_LOWRise_RESULT.json>)。
- [一次CPU派生收据](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDNHEIGHTGATE_PI_ONLY_EXPORT_STARTED_ONCE.json>) / [紧凑完整质量决定](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_HEIGHTGATE_CLOSED25_QUALITY_DECISION_V1.json>)。

不按25/205计数自动长跑或晋升。不把0信用等同零reward，不把瞬时高或100%峰值当起身成功。下一步依据真实联合失败分项和保持表现选择一项干预或确认性测试，原判据/分母/physics/DR保持；本报告及全部新成功失败下一有意义feature-only annotated trial归档，main只读。


## Archive boundary
Actual low-positive-tracking heightgate fresh1cd N20000 new25/dualAdam500/24m base0, original owner actualGO through save/SDKclose/inner+outer wait/cost/leases all closed. Full146247539B candidate bf824 kept, native1200/9600/2400/pending0. Allcore/physics/DR/commands/oldfall-normal/negative-reward/acceptance unchanged; actual constructed positive1/.2/.5 weights with installed gate proven. Immutable first11 evidence plus passive pre-reset11996400 low samples/29991 episodes distinguish peaks from reset height;99.77percent above-height peaks are not skill credit. Original N80 actual V5_HEIGHTGATE+matching collector qualified0of74, normal physical0of6; MuJoCo10 finite cases both0of5, candidateheight.195248/speed1.01209/XY7.844078 versus mother.241437/.038073/.639393, nominal only not fullDR/hardware or causalnative proof. CPU export correct names, wholeCPU once and338873B14pi artifact only, no source model for status or Git. Preserve source-only AppV6 validCRLF rejection before output and newV2 byte-preserving correction, unchanged7dependencies/3metadata adapter source. KEEP original1cd/Registryv12, no bf824 promotion or goal completion; all full candidates retained. Alltext success/failure/code/reports included; original recorder validation/redaction/hashes unchanged, only2 short exact git-add scopes+full stagedset, feature-only mainreadonly, no model/raw/JSONL/geometry stat-read-hash for Git and no once/physical replay.
