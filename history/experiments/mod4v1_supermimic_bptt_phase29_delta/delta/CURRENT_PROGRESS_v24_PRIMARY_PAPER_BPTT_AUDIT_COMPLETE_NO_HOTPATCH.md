# v24：用户新请求——原论文与实际BPTT逐项审计完成，未热改/未启动新训练

2026-11-03 15:09 +08:00。直接human 14:43：详细找SuperMimic论文，判断我们的BPTT训练方式是否有问题。Goal `goal-1c14ef7d-c888-4287-83bf-c008d54545fb` 最近revision13/activearmed/round8/max48，质量优先总目标仍未完成，不complete/blocked。所有H1/母本/Registryv12、原physics/fullDR/speed/acceptance/Csinglewriter/reserve/locks/3900-3600-300/1800未变；现在无自有GPU训练/评测/资源observer或hostjob在跑。前序真实CPU replay诊断/来源/字节与不变性见[v23](<CURRENT_PROGRESS_v23_ACTUAL_REPLAY_CPU_CLOSED_GOOD_HOLDOUT_SOURCE_READY.md>)，原技能及Phase28实际核验见[v22](<CURRENT_PROGRESS_v22_PHASE28_VERIFIED_BOUND_NOT_PROMOTED_THREE_SOURCE_TASKS_ACTIVE.md>)。

## 用户问题的实质结论

**有明显需要纠正的适配问题；不是“没有真正BPTT”。** 真实actor→WM跨time/state/action梯度、soft survival shift、γ^H critic bootstrap、imagined-only fixed λ-target、γ.99λ.95、actor Adamβ(.9,.95)、norm1后elementwise.1、无EMA critic均与论文主链相符。当前legacy不能据VJP非零认证为论文忠实实现，更不能据更新次数认证学会。

最强已确认差异：
1. 论文clean observation+WM外fresh sensor noise；我们将已noisy/delayed raw35放进动态xi、一阶delta监督、actor add_noise identity并自回归xi。
2. stateWM虽k8，但每步teacher-force真xi；aux heads在真s/s1上单步监督，而policy用predstate+predxi闭环H16。paper Eq1 learned heads应在autoregressive window中监督；learned reward/done本身论文允许，不是错误点。
3. 本地invariant_features丢x/y/yaw，实际layout没显式terrain geometry/tile/heightmap；flat-ground对称性不自动迁移到Curb/Slope/W35。接口事实高置信，但Markov混叠/同输入异target尚未构造，不能称已证失败因果。
4. teacher+.05*unbounded residual是我们自定义架构，scale不是hard .05界。实测E3 residual RMS两分量6.96/11.49与动作饱和支持优先审查漂移；零更新bound也未改善原技能，不能宣布tanh已修复。
5. E2 body/world command随heading演化而imaginationheld，W35 BODY正常held与其自然resample边界须分开；term|trunc重置概率的bootstrap语义须按原task核验，paper未给Isaac timeout细则。
6. 当前WM512×3/4×512、actor512×H16、replay128/env、critic2×2，paper2048×3/10×2048、4096×H32、1000/env、5×4。是显著缩配，不足单独定罪；H16+critic有paper正向ablation，H越长不单调更好。critic结构256/128、cosine lr_decay_iters250000是匹配；planned iterations100000不是decay常数。

下一步先修闭环语义/clean100Hz原noise-delay队列/多步heads分布和模型地形可识别性，再评估critic/rollout length与单因素小段训练，不盲加H32/奖励或继续badlegacy凑3000。所有方法调整目前只是报告方案；没有新native训练或热改，E3签名upright候选仍disabled/κnull，good专家仍保留。

## Primary与实际源证据

[综合报告](<SUPERMIMIC_PAPER_VS_OUR_BPTT_AUDIT_V1.md>) 已保存并present，含Eq1–3、正确机制、P0/P1问题、配置表、实际posthoc对照和修正顺序。母本原技能相对/因果/multiseed仍null。

原论文：SuperMimic: Scaling Humanoid Whole-Body Control with One Differentiable World Model，Qiayuan Liao等7人，arXiv2610.28480v1，2026-10-20，CoRL2026 Oral由作者/项目/arXiv交叉核实。https://arxiv.org/abs/2610.28480 / https://supermimic.github.io/ / https://qiayuanl.github.io/ 。本次checked primary没有公开training Code link；本地vendor和网上Reproduced/mjlab不是已证官方源码。

[原PDF](<research/supermimic_arxiv_v1_20261103/paper.pdf>)3524904B/fe213017…；[下载收据](<research/supermimic_arxiv_v1_20261103/PRIMARY_DOWNLOAD_RECEIPT_V1.json>)原src gzip2901561B/256a2533…；只作不可信参考数据，不执行TeX/下载代码。HTML404、PDF web_fetch unsupported均保留，改由真实原arxiv/src TeX读取正文/附录而非编造网页结果。Office general路由已加载；最终直接TeX/MD审计，没有生成Office文件/渲染。

- `71a4786a-f3b1-4b53-92f6-2619481d5156` primary research已完成/inactive：[PRIMARY_LITERATURE_REPORT](<source_supermimic_primary_literature_v1/PRIMARY_LITERATURE_REPORT.md>)及[17claims/17unknowns机器摘要](<source_supermimic_primary_literature_v1/PRIMARY_EVIDENCE_SUMMARY.json>)，原source完整核对、引用0missing。未读本地PT/raw或判实际根因。
- `85057b7f-d097-48e2-abca-9aeecba5b70e` local source审计完成/inactive：[MD](<source_supermimic_paper_code_audit_v1/PAPER_CODE_SOURCE_AUDIT_V1.md>)32323B/5b638478…、JSON35512B/0815f885…、AST65499B/4a80b817…；11源SHA复核、66source anchors存在。core2603→resume8116所有训练函数AST相同，只有load分拆且去torch.load后body相同。raw35 actor正确覆盖base，不能误报privileged泄漏；未打开模型、无Torch/SSH/native/Git。
- 原训练源仍worker7c4298/core2603(resume8116)/bridge821/raw35bb75；whole-copy20fd CPU修复尚未安装native。论文没有公开完整state decomposition、normalization recipes/action squash bounds/warmup/各head最终analytic选型，报告保留unknown，不以民间复现填空。paper train本来有物理DR和观测noise，noDR/noobsnoise只benchmark，不能错误说原法不支持DR。
- 本轮只重读已出版actualCPU metadata作比较，没有再次打开原模型/replay。此前sourceRuntime import-only/synthetic/actual两角色CPU jobs全部结束且已收，没有遗漏hostjob。

## 唯一仍进行的SOURCE任务

`d66482f4-bbf6-4ad6-a2b4-231a32e6bf8a` → NEW `source_stage_good_expert_holdout_v1` materializer源码。已报18/18stdlib/fake/白名单通过；全metadata闭包真实import，不stub；parent/native bridge/Torch只PIN+AST保留不import；完整role/static/vendor树未来preflight验证。未执行真实inputs preflight、prepare/stage函数或Popen；received SOURCE seal后父再独立review，不触发native。用户paper优先已转达，当前不扩enable框架、不动V1seal。原C878/S135两seed holdout SOURCE20overlay seal032c…依旧稳定；不冒称已materialized/新seed已测。

Phase28已remoteverified ba10b847…/annotated0ddb5ccb…。本轮actual CPU consistency/source/kwargs/import/pins/E3reward+分层/goodholdoutsource/primarypaper与codeaudit/此handoff待Phase29追加；archival只保存文本/producer引用，不为Git重跑physics/CPU/模型/raw。后续修复要NEW branch/sourceindex/完整保存恢复/原实际close-wait-结算-release，原primary质量仍逐专家80/90、多seed原predicate完整分母。
