# v25：Phase29远端核验；原论文方法审计完成，下一步先改闭环不盲训

2026-11-03 15:14 +08:00。用户14:43新请求“详细找找supermimic的论文，看看我们的bptt训练方式是不是有问题”已完成原始论文/附录/作者项目页与真实qualified A1源逐项审计，综合[报告](<SUPERMIMIC_PAPER_VS_OUR_BPTT_AUDIT_V1.md>)和[原PDF](<research/supermimic_arxiv_v1_20261103/paper.pdf>)已present。具体source/实际CPU/接续见[v24](<CURRENT_PROGRESS_v24_PRIMARY_PAPER_BPTT_AUDIT_COMPLETE_NO_HOTPATCH.md>)、[v23](<CURRENT_PROGRESS_v23_ACTUAL_REPLAY_CPU_CLOSED_GOOD_HOLDOUT_SOURCE_READY.md>)。本轮所有hostjob/三source子任务均completed且收取，无自己的GPU/资源observer/hostbackground工作；没有热改/安装新训练源、没有新native训练。

## 稳定结论与主目标

Goal `goal-1c14ef7d-c888-4287-83bf-c008d54545fb` 最近revision13/activearmed/round8/max48，**总目标原技能80/90+鲁棒性/保持仍未达**，不complete/blocked。用户训练量只手段；母本/Registryv12/H1、原物理2c/bae/400-k2000-d3/50-100Hz/.0025/TGS32,4/.01闭链/.01mimic/D0D7、原速度/验收/C唯一writer/authorityEX/privateEX/trainSH-evalEX/reserve86412.86069250107/3900-3600-300/1800全保持，不清外国锁/发signal/扩预算/造账本/退款。

原文arXiv2610.28480v1确定，作者项目与主页互证，本次未找到作者公开training Code link。本地vendor/民间Reproduced不当官方。**BPTT真实主链、survival/bootstrap/λ-target、actor β(.9,.95)、gradnorm1后value.1、critic无EMA大体对齐；并非“没BPTT”。** 明确优先缺口是paper noise-free obs+external fresh sensor noise与我们的noisy/delayed dynamic xi不同；state k8 true xi teacher forcing+aux true-state-pair一步监督，不等于actor H16预测state/context多步闭环；平地invariant features丢xy/yaw在terrain任务有Markov风险；teacher+.05无界residual实际可大漂移；E2随headingcommand演化与held目标不同。learned reward/done论文允许、DR/noisy POMDP训练原文已有、critic H16有正向ablation，都不能误判。terrain alias/因果/真实Jacobian准确性仍待证。

critic结构256/128与paper相同，训练次数2×2 vs5×4；WM512×3/4×512windows vs2048×3/10×2048、actor512×16 vs4096×32、replay128/env vs1000/env是缩配，非直接根因。schedule实际继承lr_decay_iters250000，planned100000不重定该常数（父草稿曾混淆，已经在归档前纠正）；warmup/原norm/actionbounds/head最终analytic选择等未披露，unknown保留。

当前原技能teacher/unbounded/bound：E3全0/74、normal6term0/6,6/6,0/6；W35moving19/63,10/69,14/60、standing26/26,16/17,13/22。三个独立自然cohort单seed、relative/causal null，仍KEEP_REGISTRY_V12_SCOPED_BEST_NO_CANDIDATE_PROMOTION。真实posthoc WM诊断两角色各own PT1bytes/SHA/decode/完整CPUroot与RNG不变：E3FULLH16qMAE.167317/obsSensor.066328，W35.083898/.056114，均沿记录action非counterfactual/heldout；E3residualRMS6.96/11.49只是漂移实测，不宣布根因。E3reward候选κnull/disabled，boundpostprocess没收益，不默认新训练。

## Git Phase29实际已完成

```text
feature mod4v1-experts-fulldr-rm70
HEAD 8700b912c08f8e1b5d45bbfc152a2524cc7ff755
trial trial-20261103-mod4v1-supermimic-primary-paper-bptt-audit-replay-consistency-phase29
annotated object 780bff9ea6ca2f073253a301e84e37c88ed011d4
remote branch/tag/peeled exact verified, clean
6657 entries /6110 priorSHArefs /92 new texts
main仅读 dbb054d10d0728a70f93b9611a08572f3e941d6d （独立推进；不push/reset）
archive job pwsh-94ebbb3a7acd4e29 /push pwsh-f75502c5b87c49ee 均RC0/收取
```

[archive29](<archive_phase29_paper_bptt_audit_replay_delta.py>)只执行一次，基于之前exact-short-dir adapter/known18..28文本SHA引用；真实CPU双诊断守恒+一次decode/原qualified保母门明确。不为Git重跑/读模型或raw；PDF/gzip/tar/source_archive只metadata，无binary内容捕获。primary TeX/receipt、两个独立论文/源码审计、实际CPU smoke/import/pins/原角色诊断、compactfacts/格式修正、reward分层、好专家holdout SOURCE与此时刻materializer源码均已point-in-time归档。

v24归档前所写“待Phase29”现为历史；此v25、新materializer封件收尾/后续补件或新native用途待Phase30追加。未为后续归档重放任何once旧purpose。

## 后续可用SOURCE与下一步边界

`source_good_expert_holdout_subset_v1`封件root032c431b…20overlay/原deps，原C878/S1350-update owncapture embeddedteacher独立seed20260929/30保持评测方案。实际主入口走E1，不套formal；750controls/原27up27down26stand/Predicate保持，当前实际holdout仍未materialize/stage/测量。不要将source21tests当新技能证据。

`d66482f4-bbf6-4ad6-a2b4-231a32e6bf8a` NEW `source_stage_good_expert_holdout_v1`已完成inactive：CLI38828B/fc9dd74437258d408e0223359b45814909b5a9a2f80df450dfdea1f546290a2f；index4039/ddc7d82e…；guide11611/4860ba79…；seal root94330bb54b9dda0a7081d139f1cd0bd156f5e62c387273871f5b7cfebdea2e79；18/18stdlib/fake/原helpers AST通过。完整安全metadata闭包realimport，不stub；nativeTorch/SDK/parent仅PIN+AST保留不import。未调用prepare/stage()/CLI--stage或真实inputs预flight；真实原asset/vendor7/runtime/banks完整性仍待futurepreflight。原18helpers函数AST相同，7处白名单路由。固定STAGE_COMPLETE_GOOD_EXPERT_HOLDOUT_V1.json，未来materialized=true但source_native_enabled/staged/dispatched仍false、无Popen，不伪称native准入；下一parent review/enable需要明确新purpose，不绕原hardgate。父尚未全文review这个新stager，不直接执行。late seal可能在Phase29capture后，下一append按实际SHA对照补。

下一技术优先：按paper拆static DR / dynamic queues+phase / clean100Hzsensor及noise；核对terrain可识别性和E2指令参考；对齐k8 learned-head预测域；再给critic/合法rollout/noise新测试与独立原技能闭环。不得只把H16换H32/把batch放大/叠加reward、anchor、tanh多因素后宣称修好。候选训练仍1–2角色有限段、完整保存/原close-wait-结算释放后复测，坏方案不为凑3000续跑。好专家先完成独立保持资格是可并行的未扰动路线。总Goal继续active。
