# PH3 SOURCE_PREPARATION — 书面批准的through-R34 source snapshot only

授权：父2026-11-02接续消息，截止R34结束；依据原CONTINUATION_R34及上游。仅在本独立目录生成snapshot/manifest/排除与缺失表/一致性收据。**不stage/commit/tag/push，不调用recordhelper；原Phase1/2只引用，不改sourceRoot/旧expert树/index/main。** 无physics/GPU/新agent/真实IO。

## 入档规则

1. 闭合round命名空间：batches/configs/results/errors/snapshots/source_snapshots/reports内R17–R34实际源/小result/失败日志及raw metadata。所有原状态保持；prep/API/postprocess失败不偷算成机器人能力0/N，已消费但未存trajectory的缺口不重建。
2. 父明确sealed模块：SPR_AUDIT/portable_control_v3_current、HOST_CLOSED_LOOP_IO_V1、portable_spin_h2_v1；DYNAMIC_COM_MOTION_V1、SENSOR_CAPTURE_CLOOP_V1、COM_SENSOR_CAPTURE_AUDIT_V1、INTEGRATED_COM_WINDOW_V1。
3. R17–R34的完成证据闭包：H4 protocol/frozen source、已完成RM/TALLbank/material/diagnostic目录，只通过continuation已完成部分、执行SOURCE_MANIFEST/INDEX/PROTOCOL的具名路径与SHA扩展；根文件建立explicit allowlist，不用mtime全树纳入。
4. 根CONTINUATION_R34及上游≤R34、ARCHIVE_PHASE2_RECEIPT明确纳入。CONT_R34后段R35等仅为handoff上下文，不代表R35 source/experiment入档；遍历闭包时截断PH4pending段。
5. PH1/2同byte文字通过既有Git归档path+SHA引用，不重record；历史sourceSHA若不等于当前文件，只找已保存同SHA版本或列missing，不覆盖/重造过去版本。
6. raw/JSONL/NPZ/binary/USD/ZIP/大资产只path/size/已有producerSHA metadata；unknown保持unknown，不为此重新hash/读大raw。文字报告不因其底层raw大而省略。

## 无条件排除

ACTIVE_BOX_QP_V3/ASQP_V3、FRONT_RANGE_PROPOSAL_V1、所有heading*及TRAIN_HEADING引用、R35及后命名空间、streamed_trace_rows_v1、临时/活跃路径、凭据/SSH脚本和runtime cache。它们不因被oldREADME提到就扩入。文件名之外的continuation叙事完整保留但标注context-only。

此准备目录不代表Git已提交。后续独立新phase3trial/原helper/ownrefs的操作需另行明确；当前只封source snapshot和字节一致性。Goal保持active，H4速度64/64不等于车道/全Goal/board资格，积分COM仍UNKNOWN/hardwareunbound。
