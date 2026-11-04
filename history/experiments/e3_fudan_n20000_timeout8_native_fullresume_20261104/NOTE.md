# E3 N20000：完整learner续接与低趴8秒timeout已实际训练，独立评测入口已就绪

## 任务与保留决定

仅推进E3起身质量，Fudan五帧速度encoder＋PPO、N20000/T48。目标仍未达成。H1、其它专家、Registry v12与选定1cd母版不变。上一窗8af4候选已真实闭环，但原N80恢复信用0/74，名义MuJoCo两组严格信用均0/5且行为不同；继续沿用 [上一窗质量决定](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_N20000_CLOSED69_QUALITY_DECISION_V1.json>)，不晋升8af4。

本窗唯一训练干预是recipe>=13的低趴episode在400个已完成policy控制步（8秒）触发time_out；原fall/normal、奖励、PPO、动作、物理及fullDR不变。不是整环境或PhysX位级resume。

## 已发生的实际进展

原父实际GO：2026-11-04 23:13:09 +08:00，epoch1793805189.6210587。owner1621824、outer controller1621817、worker1621886。原canonical单写者、authority两EX、private GPU0 EX、finite SH与FD3/4/5/6均在准入时落实。前面的Err11是GO前历史记录，不是当前等待。

完整N20000源8af4（1,204,250,903字节）本次实际物理读/hash/CPU decode各一次，完整模型/critic/STD/LR/两Adam/private generator续接成功；本次母版读0、N4096祖先读0。源的历史64+69 lineage与48个未优化pending控制保留于CPU元数据/完整缓存，未应用到新环境。新N20000环境DR、返回的带噪raw35×5 history与全局环境RNG从sole fresh reset生成。

[不可覆写的首次真实训练点](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_N20000_W6_TIMEOUT8_FIRST_REAL_TRAINING_EVIDENCE.json>)冻结在本窗5个新增PPO、两Adam各100步、4,800,000已优化转移，累计138 PPO/两Adam各2760/83,622,912转移。其后唯一observer已报告本窗10 PPO、两Adam各200、9,600,000转移，累计143/2860/88,422,912。均不是技能通过或新窗完整保存声明。

实际env.cfg.episode_length_s回读20.0；低趴专用TermCfg回读time_out=True、episode_length_buf、dt=.02、400控制步、8.0秒。原全局20秒不改；只低趴子集增加独立timeout。未把训练任务Term安装进原N80评测。

## 运行与收口

唯一observer job：`pwsh-009dc725e30b4144`。不要重复启动collector、训练父或worker。

```text
remote root: /home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_E3_FUDAN_N20000_LOWTIMEOUT8_CONTINUE133_W6_20261104_231058_1793805058620541900
local output: F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/reports/FDN_N20000_W6_TIMEOUT8_20261104_231152
save deadline: 2026-11-05 00:13:09 +08:00
nominal max end: 2026-11-05 00:18:09 +08:00
```

以上是原窗口边界，不是完成时间预测。先由原父完成fullsave、SDK close、inner＋outer actual wait、成本结清与释放，读取实际CLOSED_RESULT，再开启候选评测。当前窗仍在运行，尚无本窗独立技能分数。

## 下一候选评测源码（已准备，未stage/dispatch/执行）

- [冻结原N80 stage](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/stage_fudan_timeout8_frozen_original_once.py>)：强CLOSED metadata frontdoor，new root version3/base133/source8af4/overlay386107；完整原runtime/lib/assets/staticbanks，原N80/160/seed20260928/74首episode恢复＋6normal不变。
- [原父dispatch](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/dispatch_fudan_timeout8_frozen_original_once.py>)与[唯一collector](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/collect_fudan_timeout8_frozen_original_once.py>)：新FDNTIMEOUT8_FROZEN命名空间；原资源门槛、actual wait、close/FINAL.skill/TERMINAL_ROWS/FINAL.rows资格不变。
- [CPU pi-only export](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/export_fudan_timeout8_pi_for_mujoco_once.py>)：与新stage使用相同闭环frontdoor；selected新候选独立功能purpose一次完整CPU读/hash/decode，只导出14个actor/encoder张量、82505标量的小artifact，不是训练resume文件。
- [名义31体MuJoCo五姿态对照](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/evaluate_fudan_timeout8_pi_mujoco31_lowrise_once.py>)：与上一窗相同五合法低趴姿态、8秒、50Hz policy/100Hz PD/.0025 physics、同工程joint predicate；不能替代原native/fullDR/硬件或视频整腿同端验收。

新冻结mean来源SHA fb4890c49cb79afc0aeedfc37cc8a489b72e4531aa0036a3055fef525ecd2bcd；safe 0f11940344868e17681a39ce9e5861f15125950f9ab3fafc035f3af896386c34；父qualifier 6269b12055aead81da3f47dae4769eab5eaebd19eb12061a4262155a22f5908b。只改3个来源metadata模块，其余7个模块字节保持；14张量数学/history/clip6、原N80循环/物理DR/close原样。旧CPU合成证明不重跑，没有新Torch fixture或额外审计农场。

## 原约束及Git边界

原canonical唯一账本、charge_values实际GO到保存/close/waits结清、原锁、reserve86412.86069250107、3900/3600/300窗及1800 preGO不变。不碰foreign进程/锁，不复制预算/退款/扩窗。源码sealed不热改；旧stage/dispatch/record/physics once不重放。模型/raw不为状态、Git或标签重新stat/read/hash。

最近已远端核验的质量归档commit：21763dd0c4ca97cb009913c1075caa6ca09160e6；tag trial-20261104-e3-fudan-n20000-closed69-quality-keep-mother。本窗完整源续接、timeout8原生正更新、首次5点及评测source准备将合并为下一有意义阶段归档，当前本交接正文生成时仍pending。之后的原生窗收口、评测和质量决定需继续按实际阶段补档；不制造逐健康checkpoint标签或无限验证回执链。


## Archive boundary
Actual new W6 N20000 full learner continuation from complete 8af4 source, model/critic/STD/LR/both Adam/private generator restored, sole physical read/hash/CPU decode once. Current source ancestor reads zero. Five positive native PPO updates and actual 20-second global episode configuration with separate low-only 400-control time_out are frozen evidence, not final-window or skill acceptance. No production promotion: Registryv12/1cd, H1 and other experts unchanged. New ten-source original N80 evaluator and CPU pi-only/MuJoCo follow-ups are source-ready but unexecuted. Preserve all text source/failure/report history. Later final save/actual waits/account/release and original quality assessment remain pending. Original physics/fullDR/PPO/resources/budget/closure semantics unchanged. This record is consumed; never replay for synchronization.
