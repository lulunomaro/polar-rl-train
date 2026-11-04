# V22 — lowSTD005 Admission2有限25真实质量结果

- goal-c490e4cc-b28b-440e-bde6-30ee956813f0 rev3 active/armed/round3/14，质量未完成；H1/其它专家/Registryv12/1cd不变。[实测报告](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_LOWSTD005_ADMISSION2_CLOSED_QUALITY_RESULTS_V1.md>) / [完整决定](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_LOWSTD005_ADMISSION2_CLOSED_QUALITY_DECISION_V1.json>)。
- W11 Admission2 root /home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_E3_FUDAN_N20000_LOWTIMEOUT8_FRESH1CD25_LOWSTD005_W11_ADMISSION2_20261105_045304_1793825584020001500，GO1793826908.3855948；实际25PPO/两Adam各500/24,000,000已优化转移，base0/无旧计数拼接；1200native controls/physics9600/feedback2400/pending0，完整146247985B/cc41bd5b8787a00be9a5d42fb7c52f8959344c9b58cedf9c24229211b4e55244，inner+outer wait/cost/release/error[]全闭环。
- 原N80 EvalAdmission2/V6_LOWSTD005真实父及collector全qualified；原0/74，normal物理0/6。名义MuJoCo十条completefinite，新候选0/5与母版0/5；候选h/v/XY 0.210951/2.264332/12.554245，母版0.241437/0.038073/0.639393；非硬件/fullDR/video验收。
- 实际init STD0.05、tracking无heightgate；passive七项保留原阈值/联合good，不当独立信用。完整候选保留，决策KEEP_REGISTRY_V12_E3_1CD_NO_LOWSTD005_PROMOTION，goal_completeFalse；原source/current坏候选不为状态/Git开启，旧once不重放。训练068、W10 read-only release44、原N80 Eval1 c8（真实0启动超时）、其后release34、实际EvalAdmission2 1aa、先前准入Git f73均completed0/output collected，当前无本任务native/eval/observer剩余。实际EvalAdmission2 root FDNLOWSTD005_FROZEN_ADMISSION2_ORIGINAL_N80_20261105_061148_1793830308595166900/controller1638807/parent1638814，未读取/虚构worker PID。旧Eval1 root/false scope/outerwait全部保留，新qualified评分不是给旧失败改标签。
- 下一[主LR日程统一×.01假设](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/NEXT_SINGLE_INTERVENTION_MAINLR_SCALE001_HYPOTHESIS_V1.md>)已补记实际原0/74，只是待选文字：保持本轮STD.05/no-heightgate/fresh1cd与core不改，主initial/min/max同时按同一因子缩放（1e-3/1e-5/1e-2→1e-5/1e-7/1e-4），encoderLR.001不改。由实测KL首7约11.6395、末次2.6331且main已到1e-5引出，不作根因证明。尚未任何新worker/source/admission/GPU执行；下一goal round只选一项有限验证，不续坏cc41、不改门限/分母/physics/DR、不按25更新盲长跑。
- 上一准入阶段已核验feature14d2f3cca33913933f16d8baa6188d6d02567399/tag trial-20261105-e3-fudan-lowstd005-original-admission，616源，main只读c43b88f8d2f054dde60ffe546855a5817bef8651。其后真实GO/首positive/完整收口/N80/export/MuJoCo/本报告待新意义quality归档；原记录全校验+2短pathspec/fullstagedset，模型/raw/JSONL/geometry先跳再stat/read/hash，不为Git重跑物理、不造无限验证链。


# E3 初始策略STD0.05 / N20000有限25：真实质量结果

## 结论

**实际25次PPO/两Adam各500次/24,000,000已优化转移，完整收口。原N80执行资格通过，首episode恢复信用0/74。**

**KEEP_REGISTRY_V12_E3_1CD_NO_LOWSTD005_PROMOTION**。原1cd/Registryv12保持，全部完整候选保留；H1/其它专家不动，总质量目标未完成。相对W8严格联合信用增加：False，normal物理终止增加：False。单seed/五姿态筛查不建立多seed毕业或matched native因果；诊断量变化不自动晋升。

原74请求与6normal分列：normal首episode物理终止0/6不是normal接受率；请求组物理终止31/74。原stable50 public100Hz=0.5s=25控制，request300=3s，不拼reset。

## 唯一行为参数与固定边界

相对已经真实运行的W8无heightgate/STD0.5 baseline，仅将新policy Gaussian初始STD降为0.05。恢复W8原tracking函数/权重，不把失败heightgate继续叠加。实际constructed linear/tight/yaw weights分别1.0/0.2/0.5，所有heightgate marker为false。原低8s/400timeout、26 recipes、commands/height/negative奖励、动作scale、PPO核心与entropy/KL/两Adam自适应LR、2c/bae物理/fullD0D7保持。降低policy探索不是关闭D0D7噪声或延迟。

原1cd actor8+critic8 MLP warm；encoder随机fresh、新latent列0、STD/LR/两Adam/private generator/计数fresh，零继承，不续246ac/bf824/205。source_iter43090仅来源，实际1cd14715029B一次physical/hash/CPUdecode；原优化器/DR/history/旧迭代不应用。N20000/sole fresh reset/raw35×5，不声称PhysX位级resume。

Native 1200控制/9600physics/2400feedback/24,000,000真实转移；未优化pending0控制/0转移。完整候选146,247,985B/SHA `cc41bd5b8787a00be9a5d42fb7c52f8959344c9b58cedf9c24229211b4e55244`。inner+outer actual wait、成本结清/释放/errors=[]；GO至outer约1224.565s是metadata解释，不改账。

## 原位pre-reset被动统计，不是联合技能接受率

低组样本11,996,400，均高0.247655m，≥.23样本比例0.959400；已结束低episode29,991，峰值均高0.256177m，峰值≥.23比例1.000000。训练信用0/29991分列，不当独立分数。

| 原条件 | 通过样本数 | 比例 |
|---|---:|---:|
| height_ok | 11,509,341 | 0.959400 |
| upright_ok | 11,544,863 | 0.962361 |
| speed_ok | 300,922 | 0.025084 |
| angular_ok | 1,813,223 | 0.151147 |
| wheels_ok | 10,895,566 | 0.908236 |
| chassis_ok | 11,996,387 | 0.999999 |
| joint_good | 140,668 | 0.011726 |

七项复用原update已有height/gravity/root_speed/angular/contact，不增加getter/physics/sensor/RNG，typed float64[7]累计，不参与reward/credit。joint_good含原request条件；单项样本通过或高度峰值不等于连续0.5秒联合成立。旧W8缺同一被动计量，不能凭此建立配对因果。

## 同五姿名义31体MuJoCo末态均值

| 指标 | 本候选cc41bd5b | W8 STD0.5/no-gate（已发布） | 冻结1cd（本次实跑） |
|---|---:|---:|---:|
| 高度 m | 0.210951 | 0.198817 | 0.241437 |
| 倾斜 deg | 14.608 | 10.886 | 0.638 |
| 根速度 m/s | 2.264332 | 0.684080 | 0.038073 |
| 起终点平面位移 m | 12.554245 | 5.325706 | 0.639393 |
| 工程联合信用 | 0/5 | 0/5 | 0/5 |

双方五条均400控制/8秒、finite完整，同31机器人body/30坐标/原限位、50策略/100PD/.0025物理、PD60,2/wheel.6/scales.5,10、400N-k2000-d3，无外力/yaw/动画。clean raw35/frame-major5，不是native fullDR/硬件/视频整腿同端验收。严格工程条件：h≥.23、gz<−.984807753、v<.03、omega<.2、两wheel>1N/chassis<1N连续.5s。母版抬身能力与strict0/5分开陈述；实际末态分项见完整决定，不把0联合信用解读为全无能力。

## 先前未启动与本次真实评测分列

W10训练准入曾按原1800s门控超时，0GO/worker/SDK/PT；随后实际释放后新W11才产生本报告25轮。原N80 Eval1也曾在原private/finiteEX门控等待1800s后退出，child_waits为空、所有case/FINAL为空、父与outer已实际wait和释放，原scope `execution_qualified=False` 保留，其恢复分数为null而不是0/74。真实只读ownerNone之后的新EvalAdmission2才完成原N80控制与V6_LOWSTD005父资格/collector全部检查；本报告0/74来自这次实际执行。未修改旧false、延长旧parent、重放物理或改原锁/账本。

首7和末次update的均值KL分别约11.6395、2.6331，对照desired_kl=.005且实际mainLR到1e-5，是优化诊断，不直接证明漂移根因。下一主LR日程整体×.01仍仅待选假设，不继续本坏分支长跑，不在本轮叠加新参数。

## 保存、IO与证据

原唯一canonical/charge_values/authority2EX/privateGPU_EX/trainSH-evalEX/reserve86412.86069250107/3900-3600-300/1800preGO保持，无外国signal/清锁/改账/扩预算/退款。新完整来源每实际用途一次whole CPU read/hash/decode；原N80不投影20k DR/history、不装训练overlay、不优化。CPUexport仅下载338,873B/14pi/82505派生，非完整resume；没有为状态/Git开原PT或旧raw。

- [训练完整终态](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/reports/FDN_N20000_W11_LOWSTD005_ADMISSION2_20261105_051151/CLOSED_RESULT.json>) / [实际原门控GO](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/reports/FDN_N20000_W11_LOWSTD005_ADMISSION2_20261105_051151/FIRST_ACTUAL_ADMISSION.json>)。
- [原74 recipe及实际父资格](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDNLOWSTD005_FROZEN_ADMISSION2_ORIGINAL_SCOPE_RESULT.json>) / [同五姿十条完整物理案例](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_LOWSTD005_MUJOCO31_LOWRise_RESULT.json>)。
- [一次CPU派生收据](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDNLOWSTD005_PI_ONLY_EXPORT_STARTED_ONCE.json>) / [完整质量决定](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_LOWSTD005_ADMISSION2_CLOSED_QUALITY_DECISION_V1.json>)。

不按更新数或单项高度自动长跑/晋升。所有新成功失败/源码/本报告在下一有意义feature-only唯一annotated trial合并记录，main只读，不为Git重跑物理或消费旧once。质量goal保持active。


## Archive boundary
Actual finite N20000/T48 lowSTD005 fresh1cd branch, dynamic observed counters and scores in report, no preset success/failure. Single initial policy Gaussian STD0.5-to0.05 relative to W8 no-heightgate baseline; original reward, entropy/KL/core, physics/fullDR/commands/action-scale/acceptance unchanged. Passive seven pre-reset criterion samples reuse original values, not a new grader. Original1cd actor8+critic8 MLP-only source once, fresh encoder/latent-cols0/STD/LR/Adam/private generator/counters; bad branches not resumed. Preserve W10 actual original1800 zero-GO timeout/allFDNnull, readonly owner-release observation and genuinely new W11 admission; original owner fresh gates and unique canonical charging/waits/leases unchanged. Capture real GO and immutable first7 positive evidence, full complete checkpoint and actual independent N80 V6_LOWSTD005 qualification, one wholeCPU pi export and10 nominal complete finite cases. Preserve local generator indentation failures/corrections, optional reader static command not started by tool, and original unmodified failed sources; no fake CPU/native success. Registryv12/1cd remain; positive results if any retained only for scoped confirmation, not automatic multi-seed/hardware promotion. All success/failure/source/current text included; original recorder validation/redaction/hashes and exact staged set remain, only2 short git-add scopes. Models/raw/JSONL/media/geometry skipped before stat/read/hash; no old once or physical rerun for Git; feature-only atomic annotated push and main read-only.
