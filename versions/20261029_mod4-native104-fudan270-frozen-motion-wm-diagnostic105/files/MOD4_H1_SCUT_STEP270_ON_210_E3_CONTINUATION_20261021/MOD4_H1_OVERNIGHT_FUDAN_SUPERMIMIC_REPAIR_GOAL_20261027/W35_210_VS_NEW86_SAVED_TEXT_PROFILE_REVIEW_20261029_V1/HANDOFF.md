# FROZEN — W35 210完整窗与NEW86部分窗保存文本审查

本目录是一次有界LOCAL text-only审查，无新评测/PPO/模型加载/WM训练/远程连接/预算写入。仅读取两个明确允许的JSON文本，没有跟随其中路径。所有新文件待root普通Git补档，未创建trial/tag；冻结后idle，不自动执行后续任务。

运行源码：`review_saved_W35_210_and_NEW86_text_once_v1.py`，stdlib Python314 `-B`，实际返回0。34项保存文本一致性检查全部通过。完整结果和全部42 profile覆盖见 `W35_SAVED_TEXT_COMPARISON_COMPLETE_ACTUAL.json` 与 `W35_SAVED_TEXT_COMPARISON_COMPLETE_REVIEW.md`。输入路径/字节SHA在 `INPUT_SAVED_TEXT_BYTES_SHA_AND_SCOPE_ACTUAL.json`。仅输入JSON文本被计算SHA；没有读取/哈希其指向的模型、NPZ、USD、runtime源码或large artifacts。

允许输入：

- `L/W35_210_OWN_STORAGE_PROFILE_READONLY_READERS_SOURCE_V1/reports/W35_210_OWN_STORAGE_FINAL_TERMINAL_FULLTEXT_RETURNED_ACTUAL.json`
- `N104/reports/NEW86_W35_ACTUAL906_PARTIAL_FROZEN_COVERAGE_AND_NEW210_GPU_NATIVE24_ACTUAL.json`

L是本目录的parent；N104是L的parent下`MOD4_H1_FUDAN270_SHARED4090_RESOURCE_V104_20261029`。不读取该86汇总指向的旧full terminal/raw/模型。

核心结果：

|范围|86原汇总|210新完整窗|
|---|---:|---:|
|全窗controls/秒|906 / 18.12|1200 / 24.00|
|steady controls/秒|806 / 16.12|1100 / 22.00|
|全窗moving人口control加权误差|0.30613922337682037|0.3061771853449584|
|steady moving人口control加权误差|0.3047957003979565|0.3052546559708023|
|完整有符号cycle事件（不等于unique env）|444+428=872|steady 720+694=1414|
|非timeout base_contact事件|4|4|

210全窗moving exposure=991848/24000000（4.1327%）；steady=861209/22000000（3.914586%）。全人口forward/yaw/height MAE不代表moving或每profile表现。210全窗forward/yaw/height MAE分别0.032051432402804496 / 0.040254291923095785 / 0.0051491437702983；steady分别0.030037434453314 / 0.03938274357129227 / 0.0050394587684422735。

210 full1200/1100steady请求完成；原actualwait0/allownout/privateEX释放/integrity[]保存。86原906 partial/wall-time-limited状态不改。两次同源frozen mean/actor/critic/STD/norm/17Adam648360证据保持；不同观察时长及未配对轨迹不能推出硬件差异、模型改进或成功率。

210 terminated mask事件4，truncated mask事件28352。原time_out原因9947、rough_route_boundary原因18411，二者均timeout；原因合计28358，比truncated mask多6个重叠原因发生数。不能相加为unique reset，不能把rough_route_boundary重分类为非timeout技能失败。终止原因完整phase分拆与原阈值保留在报告。

五种实际G3都有gentle/standing，retained signed straight/world-yaw只在plane出现；不是所有family的moving验收。plane straight最长连续3.539997339/2.939997911秒，moving6.519994736/6.319994926秒；这是每profile保存最大值，不能代表每个环境或22秒持续完成。cycle事件不是unique环境，未保存每profile MAE/unique env分母/逐环境全signed完成/完整legacy毕业阈值，不推导缺失值。原audit恢复累计histogram不当本窗口新曝光；报告使用实际每control profile人口并逐项核对2×42 fresh histogram。

结论：执行/完整性通过，技能毕业仍PENDING，不继承原毕业标签、不提升模型来源；selected32元数据和人口指标不构成完整typed WM transition数据集。最小缺口已逐项列于报告，不要求为本审查重读模型、NPZ或重跑仿真补统计。

原本地查找/输出错误独立保留在 `ORIGINAL_LOCAL_TEXT_LOOKUP_AND_OUTPUT_ERRORS_PRESERVED.json`，不重跑原失败查询。源码/执行/AST与冻结范围由 `SOURCE_AST_AND_ACTUAL_EXECUTION_RECEIPT.json`、`FROZEN_TEXT_ONLY_REVIEW_INDEX_ACTUAL.json` 绑定。parent root负责ordinary补档并核验remote；本目录不声称已入Git。
