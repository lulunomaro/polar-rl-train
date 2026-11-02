# V2 Admission2：四caller SOURCE builder

**状态：42/42 stdlib/AST/假元数据测试通过；仅源码，R根目录4caller尚未由本子代理生成或执行。** 本session技能目录仅Office/ACL，不匹配此任务；实际使用FS/stdlib CLI。原V2超时、旧caller与所有accepted/actor/资源门源保留。

## 父代理使用

先运行builder；加`--emit`只在R生成4个全新源码与独立SOURCE回执，既不上传也不运行它们：

```powershell
python -S -B F:\RMPOLAR-RL\mod4v1_supermimic_bptt_20261102\source_frozen_v2_admission2_callers_v1\build_frozen_v2_admission2_callers_v1.py --project-root F:\RMPOLAR-RL\mod4v1_supermimic_bptt_20261102 --emit
```

随后由父代理依次运行R中的新caller；前两步只准备源，后两步为独立原门准入与本组观察，**本子代理没有运行这些步骤**：

```text
upload_preflight_frozen_e3_w35_microbatch_v2_admission2_once.py
stage_frozen_e3_w35_microbatch_v2_admission2_after_preflight_once.py
dispatch_frozen_e3_w35_microbatch_v2_admission2_original_parent_once.py
collect_frozen_e3_w35_microbatch_v2_admission2_metadata_once.py
```

全部本地marker/report/pointer使用`FROZEN_E3_W35_BATCH_V2_ADMISSION2_*`；观察目录使用`ACTUAL_FROZEN_E3_W35_BATCH_V2_ADMISSION2_*`。远端新root前缀`MOD4V1_A1_FROZEN_E3_W35_BATCH_V2_ADMISSION2_`，上传目录为新root追加`_SOURCE_INPUT`。`codeVersion=V2_ADMISSION2`仅外层元数据，原actor/source/parent ABI仍V1，V2 stager/index不改。

## 精确闭件与release门

- [原V2闭件](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/ACTUAL_FROZEN_E3_W35_BATCH_V2_20261103_012611/CLOSED_RESULT.json#L997-L1056>)：要求top admission/children/barrier/start/terminal/final全null、E3/W35两行NOT_ADMITTED且ready/eval/progress/final/error全null；actual wait=true、child_waits=[]、两EX释放=true、C写入/SDK_PT打开=0，保留原1800秒Timeout和no_samepurpose_automatic_retry。精确exit epoch `1793642078.162321`，完整闭件SHA `8fdf76f57d7f3cb73417504d9c5a0123632656af2c9a5e8cf16bfb6d076df3f6`。
- **源码准备无需release为真；dispatch在任何新marker/SSH前强制读独立release回执**：`reports/FROZEN_V2_RESOURCES_RELEASED_AFTER_ZERO_GO_TIMEOUT_V1.json`。需要同old_root/old_closed_epoch/old_closed_metadata_SHA，resource_release_observed严格true、actual.original_frozen_resources_observed_clear严格true、actual.original_relevant_leases_clear严格true、observer未超时、actual.epoch有限且**严格大于**旧exit epoch、只读计数0。缺件或负值在连接前结束，不消耗dispatch marker。
- release仅历史观察快照，**不代表未来资源所有权**。原parent继续按原private EX/global finite EX/canonical只读/硬件/1800秒有限等待等完整门重新决定准入；本代码不触碰外部owner或切换GPU。原GPU_UUID保持`GPU-16828f91-2b45-b646-8dc0-9481138e2842`。
- root/group/input_root/argv精确绑定同一新root；原native来源、14依赖、原组来源与GPU固定。stage从首次读取即使用`STAGE_COMPLETE_MICROBATCH_V2.json`；标准报告同时保存完整stager字节/SHA和实际stage_complete字节/SHA。dispatch直接读取本组`...ADMISSION2_ACTUAL_SOURCE_STAGE_V1.json`，没有旧erratum依赖。

## 固定源PIN与验证

|源|bytes|SHA256|
|---|---:|---|
|[V2 stager](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_a1_microbatch_eval_v2/stage_a1_microbatch_eval_v2.py>)|32953|9c788fc5435dcbe2af25d13390c2fb008be77c23fbe83104b170d8091cb72952|
|[V2 14项index](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/payload_frozen_microbatch_v2/MICROBATCH_STAGE_INDEX_V2.json>)|4886|69688e86528e400f188de3f147614cde5c66f86985adaceed805af800819dc50|
|[原V1 parent](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_frozen_eval_microbatch_parent_v1/single_gpu_e3_w35_a1_frozen_parent_v1.py>)|8991|9a943e730f66bfb1a68af35ddfa8118d6da605dc83f442e3c0b51c9c7ad8da7b|

9个明确小源码/JSON输入快照，14项原源PIN逐字节复核；白名单逆变换恢复4旧模板完整字节和AST。远端dispatch主体去除唯一外层request metadata追加后完整源码相等，Popen和原parent ABI原样。42项最终测试覆盖闭件null/空列表差异、bool类型、strict post-close时钟、source/hash、缺release、分组路径/argv错绑、GPU/native不可切换、V2首读与自身标准stage报告、only-new写入和observer actualwait语义。

历史保留：首次dry render因CRLF锚点失败，改新builder锚点不改模板；首次37测试5个isolated fixture错误为未注入原header已导入的json，修测试namespace后38/38；增加argv/ASCII门后42/42。旧失败回执保留，最终以[42项回执](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_frozen_v2_admission2_callers_v1/CPU_TEST_RESULTS_HARDENED_V1.json>)为准。没有测试/读取实际release回执，真实Admission2准入/skill结果保持null；无SSH/SDK/GPU/PT/raw/C/锁/Git/parent/caller执行。
