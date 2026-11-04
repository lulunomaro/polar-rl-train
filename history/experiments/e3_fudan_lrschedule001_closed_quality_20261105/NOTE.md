# V24 — 主LR日程×.01有限25真实质量结果

- goal-c490e4cc-b28b-440e-bde6-30ee956813f0 rev3 active/armed/round4/14，质量未完成；H1/其它专家/Registryv12/1cd不变。[实测报告](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_LRSCHEDULE001_CLOSED_QUALITY_RESULTS_V1.md>) / [完整决定](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_LRSCHEDULE001_CLOSED_QUALITY_DECISION_V1.json>)。
- W12 root /home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_E3_FUDAN_N20000_LOWTIMEOUT8_FRESH1CD25_LRSCHEDULE001_W12_20261105_065201_1793832721176405000，GO1793833088.400895；实际25PPO/两Adam各500/24,000,000已优化转移，base0/无旧计数拼接；1200native controls/physics9600/feedback2400/pending0，完整146247985B/55afa784423b5af3d3e3300932628d4d213756c3d2b6c4edaaba2e66b1aaabd7，inner+outer wait/cost/release/error[]全闭环。
- 原N80 V7_LRSCHEDULE001真实父及collector全qualified；原0/74，normal物理0/6。名义MuJoCo十条completefinite，新候选5/5与母版0/5；候选h/v/XY 0.241784/0.032465/0.596205，母版0.241437/0.038073/0.639393；非硬件/fullDR/video验收。
- 名义5/5是8秒内曾连续.5s达全部旧工程门限，终点credited_and_stable_at_end仍0/5，五条终点v略高于.03，勿解读为终点保持或原E3接受。第25次update KL.0050813306/actualLR2.562890625e-6；与首1点KL22.888443/min1e-7分开、不当因果。passive11996400低样本joint_good2437872=.203217/speed2826581=.235619/训练连续信用4/29991仍仅训练描述。下一[冻结确认计划](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/NEXT_LRSCHEDULE001_FROZEN_CONFIRMATION_PLAN_V1.md>)仅文字、未部署新source/准入/GPU，优先同原门限的独立low80/fullDR/3seed+终点保持确认，不加训练/不续坏cc41/不修改原74。
- 本轮唯一受控handoff job pwsh-bd58147566b04531 completed0/output collected，训练observer/独立eval/CPUexport/十名义case/publication全部顺序闭环；没有额外observer/Native剩余。原native controller1639584/parent1639591/worker1639602；outerwait1793834291.269021到eval父创建回执1793834307.0811164约15.812s。原eval root FDNLR001_FROZEN_ORIGINAL_N80_20261105_071819_1793834299559872300/controller1640340/parent1640347，实际common barrier/close/wait/cleanup/releases/父V7全qualified。未读取或虚构eval workerPID。CPU导出完整source55afa一次physical/hash/CPU decode、whole20kCPU根保留，派生338873B/2626cb5fbbd95c1c43744d47a489f03bbf850aa3073f42e165fc46fdfd29e980，仅小artifact下载，非fullresume，无旧模型状态/Git开销；各物理用途分别一次、不重放。Bridge不是只读observer，不改原父资源/预算/SDK，不automatic retry。所有旧失败/false/timeout保留。
- 实际init mainLR1e-5/min1e-7/max1e-4，STD0.05/encoderLR.001不改、tracking无heightgate；passive七项保留原阈值/联合good，不当独立信用。完整候选保留，决策RETAIN_LRSCHEDULE001_CANDIDATE_FOR_CONFIRMATORY_SCOPED_TEST_KEEP_REGISTRY_V12_UNCHANGED，goal_completeFalse；原source/current坏候选不为状态/Git开启，旧once不重放。
- 上一阶段已核验feature f50e04481bc476934e671d23f094d259a11d5101/tag trial-20261105-e3-fudan-lowstd005-admission2-closed-quality，696源，main只读6ed42f20e48636660993f2138649dcde35f378f4。当前新native-LR源/原父准入/真实训练闭环/即时独立评测/CPUexport/MuJoCo/本报告待新意义quality归档；所有原失败保留，main只读，模型/raw/JSONL/geometry先跳再stat/read/hash，不为Git重跑物理或旧once。


# E3主LR日程整体×0.01 / N20000有限25：真实质量结果

## 结论

**实际25次PPO/两Adam各500次/24,000,000已优化转移，完整收口。原N80执行资格通过，首episode恢复信用0/74。**

**RETAIN_LRSCHEDULE001_CANDIDATE_FOR_CONFIRMATORY_SCOPED_TEST_KEEP_REGISTRY_V12_UNCHANGED**。原1cd/Registryv12保持，全部完整候选保留；H1/其它专家不动，总质量目标未完成。相对W11严格联合信用增加：True，normal物理终止增加：False。单seed/五姿态筛查不建立多seed毕业或matched native因果；诊断量变化不自动晋升。

原74请求与6normal分列：normal首episode物理终止0/6不是normal接受率；请求组物理终止18/74。原stable50 public100Hz=0.5s=25控制，request300=3s，不拼reset。

## 唯一行为参数与固定边界

相对W11 STD0.05/no-heightgate配置，本轮仅将主优化器LR日程的initial/min/max共同×0.01：1e-3/1e-5/1e-2→1e-5/1e-7/1e-4；这是一个日程尺度因子，不冒称只改initial一个数值。STD0.05、encoder LR0.001、原desiredKL/entropy/5epochs×4/clip/两Adam算法与PPO核心源码保持。实际constructed linear/tight/yaw weights分别1.0/0.2/0.5，heightgate marker为false；26 recipes/原8s超时/reward/commands/action scale/2c-bae/物理fullD0D7与所有门限不改。不继承坏cc41，不以小KL或更新次数作技能接受。

原1cd actor8+critic8 MLP warm；encoder随机fresh、新latent列0、STD0.05/新缩放LR/两Adam/private generator/计数fresh，零继承，不续cc41/246ac/bf824/205。source_iter43090仅来源，实际1cd14715029B一次physical/hash/CPUdecode；原优化器/DR/history/旧迭代不应用。N20000/sole fresh reset/raw35×5，不声称PhysX位级resume。

Native 1200控制/9600physics/2400feedback/24,000,000真实转移；未优化pending0控制/0转移。完整候选146,247,985B/SHA `55afa784423b5af3d3e3300932628d4d213756c3d2b6c4edaaba2e66b1aaabd7`。inner+outer actual wait、成本结清/释放/errors=[]；GO至outer约1202.868s是metadata解释，不改账。

首1次更新均值KL22.888443/actualLR1e-7，第25次更新内20minibatch均值KL **0.0050813306**、actualLR **2.562890625e-6**，desiredKL保持0.005。finite gradients/groups separated真；只作实测优化器诊断，不用KL替代独立原74信用或把起初高KL/最终低KL宣称为已证明根因。

## 原位pre-reset被动统计，不是联合技能接受率

低组样本11,996,400，均高0.242848m，≥.23样本比例0.980829；已结束低episode29,991，峰值均高0.253470m，峰值≥.23比例1.000000。训练信用4/29991分列，不当独立分数。

| 原条件 | 通过样本数 | 比例 |
|---|---:|---:|
| height_ok | 11,766,418 | 0.980829 |
| upright_ok | 11,801,917 | 0.983788 |
| speed_ok | 2,826,581 | 0.235619 |
| angular_ok | 9,173,059 | 0.764651 |
| wheels_ok | 11,701,347 | 0.975405 |
| chassis_ok | 11,995,570 | 0.999931 |
| joint_good | 2,437,872 | 0.203217 |

七项复用原update已有height/gravity/root_speed/angular/contact，不增加getter/physics/sensor/RNG，typed float64[7]累计，不参与reward/credit。joint_good含原request条件；单项样本通过或高度峰值不等于连续0.5秒联合成立。本次与W11均有被动计量，仍非逐样本配对native因果证据。

## 同五姿名义31体MuJoCo末态均值

| 指标 | 本候选55afa784 | W11 STD0.05/原LR（已发布） | 冻结1cd（本次实跑） |
|---|---:|---:|---:|
| 高度 m | 0.241784 | 0.210951 | 0.241437 |
| 倾斜 deg | 0.538 | 14.608 | 0.638 |
| 根速度 m/s | 0.032465 | 2.264332 | 0.038073 |
| 起终点平面位移 m | 0.596205 | 12.554245 | 0.639393 |
| 曾连续满足0.5s的工程联合信用 | 5/5 | 0/5 | 0/5 |
| 满足过信用且8秒末态仍稳定 | 0/5 | 0/5 | 0/5 |

**5/5指8秒内曾连续0.5秒满足全部原低趴联合条件，不等于8秒终点持续稳定**：五条末态速度都略高于0.03m/s，候选`credited_and_stable_at_end=0/5`；原74仍0/74。因此保留55afa作独立scope确认，不替换Registryv12/1cd，也不把这五姿当E3全技能或多seed/fullDR通过。

本轮受控接续器等待真实训练outer wait1793834291.269021、成本结清/释放后才stage原N80（445完整nonPT），原评测父创建回执epoch1793834307.0811164，相隔约15.812s；eval仍重验privateEX+finiteEX/CownerNone/reserve/实际资源，随后真实common barrier/actual wait/qualified全部完成，没有把stage当GO或跨owner递锁。native/eval/CPUexport/同五姿及publication由唯一job pwsh-bd58147566b04531 completed0/output collected，未自动重试。不是仅read-only observer，也不读模型/raw/C本体；原父继续掌管预算和SDK生命周期。[实际接续状态](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_LRSCHEDULE001_W12_HANDOFF_STATUS.json>)。

双方五条均400控制/8秒、finite完整，同31机器人body/30坐标/原限位、50策略/100PD/.0025物理、PD60,2/wheel.6/scales.5,10、400N-k2000-d3，无外力/yaw/动画。clean raw35/frame-major5，不是native fullDR/硬件/视频整腿同端验收。严格工程条件：h≥.23、gz<−.984807753、v<.03、omega<.2、两wheel>1N/chassis<1N连续.5s。母版抬身能力与strict0/5分开陈述；实际末态分项见完整决定，不把0联合信用解读为全无能力。

## 保存、IO与证据

原唯一canonical/charge_values/authority2EX/privateGPU_EX/trainSH-evalEX/reserve86412.86069250107/3900-3600-300/1800preGO保持，无外国signal/清锁/改账/扩预算/退款。新完整来源每实际用途一次whole CPU read/hash/decode；原N80不投影20k DR/history、不装训练overlay、不优化。CPUexport仅下载338,873B/14pi/82505派生，非完整resume；没有为状态/Git开原PT或旧raw。

- [训练完整终态](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/reports/FDN_N20000_W12_LRSCHEDULE001_20261105_065807/CLOSED_RESULT.json>) / [实际原门控GO](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/reports/FDN_N20000_W12_LRSCHEDULE001_20261105_065807/FIRST_ACTUAL_ADMISSION.json>)。
- [原74 recipe及实际父资格](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDNLR001_FROZEN_ORIGINAL_SCOPE_RESULT.json>) / [同五姿十条完整物理案例](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_LR001_MUJOCO31_LOWRise_RESULT.json>)。
- [一次CPU派生收据](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDNLR001_PI_ONLY_EXPORT_STARTED_ONCE.json>) / [完整质量决定](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_LRSCHEDULE001_CLOSED_QUALITY_DECISION_V1.json>)。

不按更新数或单项高度自动长跑/晋升。所有新成功失败/源码/本报告在下一有意义feature-only唯一annotated trial合并记录，main只读，不为Git重跑物理或消费旧once。质量goal保持active。


## Archive boundary
Actual fresh1cd N20000/T48 finite25 main LR schedule scale0.01 relative to qualified W11 STD0.05 no-heightgate baseline: initial/min/max together 1e-5/1e-7/1e-4. Encoder LR0.001, STD0.05, exact PPO core, all original rewards/commands/timeout8/physics/fullDR/acceptance unchanged. Dynamic real counters/scores/decision, no preset success/failure. Original1cd actor8+critic8 MLP-only source once, fresh encoder/latent-cols0/Adam/private generator/counters; bad checkpoints not resumed. Preserve original owner exact budget/locks/actual GO-through-SDK-close-wait-account-release. Controlled new-purpose local bridge waits actual training qualification/inner+outer wait/cost/release before immediate original N80 stage/dispatch; original eval rechecks all gates, no cross-owner lock handoff, signals, copied ledger, automatic retries or changed physics. Native and eval actual evidence/CPU pi export/ten nominal finite cases and all preserved failures/text are included; bridge itself uses no model/raw/C IO. Source-only tools and KL diagnostic are not skill evidence. Registryv12/1cd unchanged; positive evidence if any retained for confirmation, not automatic multi-seed/hardware graduation. Original record validation/redaction/hashes and exact staged set retained; only2 short git-add scopes. Model/raw/JSONL/media/geometry skip before stat/read/hash; feature-only atomic push and main read-only, no physical or old-once replay for Git.
