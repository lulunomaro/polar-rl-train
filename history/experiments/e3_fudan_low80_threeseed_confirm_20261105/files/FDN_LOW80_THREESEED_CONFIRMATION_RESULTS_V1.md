# 冻结55afa：三seed原生fullDR低姿确认结果

**实际资格通过；首episode连续.5秒联合信用 21/240（8.75%），曾获信用且8秒末帧全部条件满足 7/240（2.92%）。**

这没有证实稳健起身：原E3评分仍沿用0/74，本轮不改分母/门限、不自动晋升，Registryv12/1cd/H1/其它专家不变。

| Seed | 首episode连续25控制信用 | 曾获信用且末帧good | 首episode物理终止 |
|---|---:|---:|---:|
| 20260929 | 8/80 | 3/80 | 0/80 |
| 20260930 | 8/80 | 2/80 | 0/80 |
| 20261001 | 5/80 | 2/80 | 0/80 |

## 五个原合法姿态（跨三seed，分母各48）

| Pose | 连续信用 | 曾获信用且末帧good |
|---|---:|---:|
| 0 | 3/48 | 0/48 |
| 1 | 5/48 | 1/48 |
| 2 | 3/48 | 1/48 |
| 3 | 7/48 | 3/48 |
| 4 | 3/48 | 2/48 |

## 终点标签边界与失败反馈

旧producer字段 `credited_and_stable_at_end=7` 的实际公式是『此前曾获连续25控制信用 AND 第一episode仍存活 AND 第400控制单帧joint_good』；**它不是最后.5秒连续满足的计数**。末帧streak未序列化，严格末段连续25信用记null，不伪造为7或0。原JSON、实际物理、资格及门限不变；原自动报告标签备份保留，单列[读者语义澄清](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDNLOW80_CONFIRM_ADMISSION2_ENDPOINT_READER_CLARIFICATION_V1.json>)。

首episode物理终止 0/240。仅在第400控制仍属第一episode且无物理终止的样本统计端点失败分量：`{"height_ok": 0, "upright_ok": 0, "speed_ok": 124, "angular_ok": 12, "wheels_ok": 0, "chassis_ok": 0, "joint_good": 129}`；分量可重叠。末态根速均值 0.034450m/s、中位 0.030714m/s；最长good streak的跨env中位 15.0控制。它们是本轮观测，不是奖励/优化器/DR单项的因果根诊断。

## 实际协议、保留与边界

三独立process，各constructor cfg.seed=20260929/20260930/20261001；N80=五pose各16，400控制8秒，sole explicit fresh reset，原50/100/.0025/TGS32,4/400N-k2000-d3/2c-bae/fullD0D7/闭链.01m与mimic.01保留。第一episode在原pre-reset hook冻结，物理失败不删除/reset不拼接。传感噪声/lag仍原链，无额外观测采样。全部callbacks3200与feedback800/actor400，权重前后不变、无优化器更新。

候选only，本批母版native参考没有运行，paired差值null；不能拿同seed或旧名义5/5声称native因果改善。名义MuJoCo此前5/5曾达标而终点0/5，与本轮fullDR三seed分列，不迁移分母。保留完整55afa，不证明整腿同端视频/硬件/原74专家毕业。

第一批原1800资源等待自然过期，全case/null、无admission/SDK/模型，分数null；实际inner+outer wait/原双EX释放后，独立只读summary watcher真实观察ownerNone，才新Admission2。新原父再做全部fresh资源与reserve检查，实际common barrier/三worker/close/child+outer wait/释放全qualified；不清外国锁、不signal、不改账/复制预算/退款/延长父或重放旧once。每case整份N20000 checkpoint一次physical/hash/CPU decode/whole未知根CPU保留，只14pi上线；组实际三次，不谎称全组一次。

[完整分析](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_LOW80_THREESEED_CONFIRMATION_ANALYSIS_V1.json>) / [实际资格与scope](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDNLOW80_CONFIRM_ADMISSION2_SCOPE_RESULT.json>) / [原闭环metadata](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDNLOW80_CONFIRM_ADMISSION2_CLOSED_RESULT.json>)。本轮所有源码/失败/澄清/报告待一次有意义feature-only annotated trial与远端核验；main只读，模型/raw/旧物理不为Git重跑。goal保持active。
