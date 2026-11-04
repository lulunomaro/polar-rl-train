# 本轮E3续训已结束：新候选保留、不采用

用户要求继续E3；新Goal `goal-5e9cd92c-d0a3-40d1-92e9-33913df2683d` revision1。旧八专家SuperMimic重构和已完成九专家评测Goal均未恢复。

## 实际结果
- 原PPO/fullDR/N20k有效完成20更新/400 optimizer.step/9.6M transitions；原回报、物理、命令、DR和接受阈值未改。
- 输入67ee/iter43110/Adam866460，输出a3cef1489614a018492bbe3078e752e3384604371ddaf7a3fa0062d728923fec/iter43130/Adam866860/14,721,171 bytes。所有完整状态及未知字段保留，全部实际关闭、内外wait、原计费结清/释放。
- 原E3 N80/160 controls/3.2s/seed20260928评测执行合格，恢复credit仍0/74，normal物理终止0/6；不是全场景自救能力结论。
- 同一后收平放本地MuJoCo13s诊断执行成功。新候选8s世界位移(-6.04365,-6.41036)m、倾角14.5885°、线速度1.87985m/s；旧选中1cd同期X位移-.856538m、倾角.619625°、速度.04211m/s。新候选13s倾角22.6303°，明显差于旧版1.85183°。
- 结论：KEEP_SELECTED_1CD_NO_A3CE_PROMOTION。原演示、H1、Registryv12和所有母版未改；保留所有候选，不自动再加窗。输入67ee未做同样本地对照，所以相对1cd的差异不全部归因本轮20步。

## 真实失败同样保留
1. W1在初始完整保存前旧母版专用元数据断言处停止；producer更新计数null，代码位置表明尚未进入PPO。已结清408.09455943107605 expert-seconds，无退款。W2仅用唯一当前run_id保存命名空间，旧元数据不覆盖，实际成功窗1164.2446715831757 expert-seconds。
2. 冻结评测源读者第一次在本地AST树顶层找不到嵌套try中的code赋值，StopIteration；发生于stage marker/SSH/root/SDK之前。新stage_e3_frozen_after_close_v2_once.py只用ast.walk定位，原完整材料化代码不变；新root评测实际成功。

## 全部一次性任务均消费、全部job均collected
- W1 stage1b191、dispatch1a6b6、collectorcb595；W2 stage21f758、dispatch9df192、collector76d0：均已收取，旧root不得重放。
- 新候选MuJoCo0c9da成功且已收取；native stage第一次d88af本地失败、新stage6e059成功、dispatchcfa394、collectora3fa734均已收取。没有相关native训练/评测进程或observer继续运行。
- 旧MuJoCo回放窗口仍属于用户已有可视化，不属于本轮训练，不因归档关闭。

[最终报告](<mod4v1_e3_continue_v2_20261104/E3_CONTINUATION_RESULTS.md>)、[紧凑结果](<mod4v1_e3_continue_v2_20261104/E3_CONTINUATION_RESULTS.json>)保存主要结论与完整证据索引。

本交接生成于一次合并归档之前。下一步仅运行本目录record_e3_continuation_once.py一次，核验feature/tag/peeled/main只读后收取工具结果，完成新Goal。归档失败只续已有objects，不重跑record或任何训练/评测，不开新审计/训练分支。最终Git身份以随后工具输出为准，避免为验证回执无限生成新文件。
