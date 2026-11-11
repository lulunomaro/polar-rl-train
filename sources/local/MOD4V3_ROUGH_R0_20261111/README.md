# MOD4 R0 shallow terrain: authorized first 40-minute round

2026-11-11 用户授权按 R0 推进。父为 square1_030m / iter22618 / SHA d5e176401c20dd1b88a74003f7d4993aadc9a9cda301f042953de08fb6108851。

保留完整 DR、名义819/DR3277、35/78/6接口、2.5/10/20ms、TGS32/4与−1.0e²奖励。新增浅地形与最低等级出生、交叉20%平地分配、reset边界能力课程。完整PT每5分钟保存；本轮40分钟，不自动开R1。

R0去掉中级台阶，地形4等级覆盖difficulty[0,.35]，70列让出生分散；随机起伏显式按难度调幅，因为IsaacLab原函数忽略difficulty。地形边界按timeout单列。

当前为实现/探针阶段，真实启动与结果随证据更新。


## 本轮已完成

实际2405.700s、4096env、8个5min检查点，9份不同字节全PPO PT已保存，final是040m字节别名。训练numerical0、closure7093/55519episode事件（2mm单envreset）。

保留20m候选（iter22785、SHA64affb5794f5518f2b84611ab7d3904aef95b7e1ea660e1efd87820102cc14d6），5m备用；原Flat父与Step6/7冻结不替换。level0父119/120、训练权重120/120，level3父与所有检查点120/120，浅地形已可用但无明确新增越障收益；同批Flat父44/60、20m40/60。后期35/40m虽名义MuJoCo60/60，PhysX fullDR欠速扩大，因此不默认续final。

最终表格与reset限制见[FINAL_REPORT](FINAL_REPORT.md)；完整PT见weights，逐份SHA和课程状态见[evidence/MODEL_ARCHIVE_INDEX.json](evidence/MODEL_ARCHIVE_INDEX.json)。候选完整配方[CANDIDATE_RECIPE](CANDIDATE_RECIPE.json)，备用[ALTERNATE_RECIPE](ALTERNATE_RECIPE.json)。R0本轮结束，R1未启动。
