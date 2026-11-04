# Good-expert holdout V7 — immutable SOURCE package

本封件仅承接 NEW [case-FINAL contract V3](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_case_final_contract_v3/README.md>)，用于父 agent 后续独立 review/CPU/preflight/stage/dispatch。交付态 `enabled=False`、`source_native_enabled=False`、`staged=False`、`dispatched=False`；真实 native binding 为 `UNKNOWN`，不发现场 GO。

## 1. 只改变必需入口

[NEW V7 完整入口](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v7/stage_good_expert_holdout_v7.py>)：53571 bytes / SHA256 `06e82474aa80ec1280cc38aee8a199556ec2ff054189db02394f7f608f30b8f5`。

相对 [D6 完整入口](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v6/stage_good_expert_holdout_v6.py>)，仅 active `INDEX_PIN`、文档/V7 revision、两个 typed receipt kind 及其 revision 值改变。两个函数 `preflight_summary` / `stage` 仅标签更新，其余29完整函数的 Source/AST 一致；逆向完整 bytes 等于 D6。详见 [whitelist 证明](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v7/WHITELIST_DIFF.json>)。

- active index 为 [NEW V3 index](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_case_final_contract_v3/GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V3.json>)：21907 bytes / `aa22260f2198ad37d6bb265c85d870203536a5dec19c6e554a556244cc5cddda`。
- active runtime 为 [NEW 完整 runtime](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_case_final_contract_v3/good_expert_holdout_runtime_v1.py>)：56467 bytes / `29d29e96899575b0e1e1a805d210a04aba7cb0e50376959ff91779c13927b911`。
- runtime 仅增加 `CASE_FINAL_MAX=2097152` 与三个原 case-FINAL 调用的显式 keyword，包括 grade 的直接 `_base._metadata`。其余27完整函数、2完整类不变，全文逆向等于 D6。
- 20 个实际 overlay 仅 runtime 一 row 更新。其余19 whole rows 和 guard 原 bytes 保留；原格式 V1、历史 teacher revision2 保留，新增明确 case-final revision3，不借旧 kind 冒充新版本。

## 2. 原合同不变

完整 `prepare` / full9dict teacher deepcopy / producer validation / source cache / copy-stream-fsync / source mappings / full metadata / original27+3 / assets / vendor / original parent9679 / canonical7a092 alias / AppV6→dc4 Base 依赖全部不变。原 dependency 闭包和 canonical alias 保留，没有循环，也没有 AST 剪碎的运行模块。

原 native `app.close()` 参数及顺序、intent fsync + atomic replace、完整 raw SHA/length、p.wait/privateGPU_EX+finiteEX、C-readonly、emptyGPU23500、RAM96、disk25、1800wait、ready900、2400deadline、完整 staticbanks + deps 维持原 AST。源码保留不等于执行：本任务未创建实际 GPU/C/lock/process/session 或真实 native App。

canonical `_metadata` 默认262144、其他 task-plan / error / receipt / intent 上限、group 8MiB 均不变；CFF packet 16MiB 不由本组件扩大。完整 physical query / before-after DR / source-cache / 未知字段保留，不以投影字段、canonical hash、紧凑重编码替代 raw identity。

仅 CURB_PROTECTED878 / SLOPE135；其余六角色 deferred，H1 不构造。两独立 holdout seed20260929 / 20260930 各自独立 purpose；N80、每角色750 control、原 ascending/descending/standing 条件、physical D0–D7、one-reset/doneflag、原 STD/whole-pi/Norm/freeze/RNG 均不变。两角色源是 actual0-update fullcapture 中 embedded 原 teacher mean，source container 身份与 mother teacher 身份分开；不把 fresh WM / optimizer0 称作训练。

## 3. 十二项 NEW stdlib / own-temp 测试

[完整测试源码](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v7/test_good_holdout_v7_source.py>) 与 [TEST_REPORT](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v7/TEST_REPORT.json>)：12/12 PASS，3.797s，Python3.12.14 `-B`。不是旧8/12/36套件或旧报告的重跑。

| # | NEW覆盖 |
|---|---|
| 1 | D6两旧 seal 成员/根与145旧 mirror row 声明；27敏感历史行只继承 pin、不打开 |
| 2 | runtime 三处同2MiB有限上限；reverse全文、27完整函数、2完整类 |
| 3 | V3仅一 overlay；其他19 whole rows、guard 和20 Source闭包 |
| 4 | V7两 typed 标签及 INDEX_PIN；reverse全文、29完整函数 |
| 5 | 完整 canonical reader：2MiB−1 / 精确2MiB / +1 / 截断 / 非dict / 默认262144 / 未知字段 |
| 6 | 两 seed 完整20 module metadata；真实 AppV6→Base import；cross-seed/历史seed负门 |
| 7 | 完整 strict9 teacher guard、source identity、seed负门 |
| 8 | 完整 close：env/App各一次、未知字段保留、raw len/SHA、fsync→atomic intent→原close |
| 9 | missing/wrong/canonicalized intent 仍失败，raw identity 不被canonical替代 |
| 10 | oversize / durable worker error 仍close一次且无成功intent |
| 11 | 完整 synthetic group grade；第三处直接Base reader；完整未知字段数据相等负门 |
| 12 | 未改原 collector 的独立 outer RC0/RC1 / false source-grade 门；非 NEW CFF packet 验证 |

所有运行模块均完整载入，未以 AST 片段或 stub 代替 runtime/AppV6/Base/guard。完整 metadata 使用 OWN F: temp 中20个文本模块、精确原 producer worker/bridge Source、合成 TASK/manifest/完整9字段 teacher。fixture 只将 SOURCEPATH 映射到从未创建或 stat/open 的 OWN `FAKE_complete.pt`，固定 byte/SHA/mother identity/strict predicates 保留。

原 AppV6 helper 明示允许 TEST-only private `_APP_PIN` 指向 OWN FakeApp Source；该测试执行完整 pin/MRO/close-line/source-byte/binding receipt 检查。原 AppV6 与 Base 未 stub。FakeApp.close 返回；只删除 OWN returned marker 以覆盖 fast-intent 分支，不声明 native binding 或原 close 非返回成立。

首次 OWN fixture 曾出现 `KeyError: 'group_id'`，随后出现 `exact selected E1 row required`。仅调整 NEW wrapper：真实 `select_requested_roles` 得到精确原 row，再调用完整原 `make_task`；未猜字段、未改生产谓词。最终12项全通过。WindowsApps Python alias 初次无输出退出1后，改用 runtime 提供的 bundled Python3.12.14；未安装依赖。

实际 reports/FINAL opens、模型/raw/budget/lock IO、native imports、process/network/lock operations、原入口调用、NEW目录/OWN temp/report 之外写入六 counters 全0。完整 metadata 的 Source-only 验证不等于实际 preflight；真实 prepare/preflight/stage/dispatch 未调用。

## 4. 两 seal 与实际 logical mirror

- 本目录8成员 + [V7 SOURCE seal](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v7/SOURCE_SEAL.json>)。
- V3组件4成员 + [独立组件 seal](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_case_final_contract_v3/SOURCE_SEAL.json>)。
- [SOURCE_INDEX](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v7/SOURCE_INDEX.json>) 记录上述两组件与 active20 mapping；[SOURCE_MIRROR_INPUTS](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v7/SOURCE_MIRROR_INPUTS.json>) 实际164个去重 logical dependency rows。
- 164 = 原145 + 新增19：旧D6 bundle9、已闭合 SOURCE audit2、原CFF测试 Source依赖3、新V3组件4+seal1；新V7本目录9文件不重复列入 dependency mirror。
- 原145 whole row 原样保留；其中118 eligible SOURCE 文本重新核对 SHA，27条 reports/discovery 历史路径及 pin 仅 metadata 继承，未 stat/open。新增19均 SOURCE。本任务绝不声称已现场重新打开/hash 全164个输入；该边界写入两份 metadata。
- logical164 / active flat20 / 原 native asset/vendor/static tree 三者不同；不以 logical mirror 冒充 native 包含性。父 agent 沿既有完整 materializer 自行处理实际包装，不从文件存在猜 active 链。

[固定 SOURCE derivation/seal helper](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v7/build_source_v7.py>) 仅允许两 NEW SOURCE 目录，实际 report/discovery/FINAL/model 路径在 stat/open 前即排除。其 `--derive` / `--seal` 是固定文本派生和封件，不是 prepare/stage；`--verify` 只读。seal 后不再运行重写 report 的测试，不再修改成员或重 seal。

封件为当前 Windows 来源字节和 provenance；外部 mirror 应验证既有 seal bytes，勿在不同根重新派生、路径标准化、改 metadata 或重 seal 来匹配。真正 flat20 import 仍按原 alias/basename/pin 协议工作。

## 5. 交接与结论边界

父 agent 接收两 seal/pins/实际mirror计数后，再交接 CFF 的 NEW exact case selector / 完整 packet16MiB 边界测试。这里不猜 CFF 的新输入、返回或封件，也不修改旧CFF Source。

历史750故障、root/worker error、无intent、falsegrade、outerRC1保留原失败；本次没有打开历史实际 reports/FINAL，也不回填 intent、旧报告或原封件。没有新质量实测、没有新的 native binding、没有 Stage2GO。多seed仍只按各方向/standing条件独立统计，不混成整个技能90，也不新增 E0/S50 谓词。下一步仅由父 agent 自行决定真实 review/CPU/preflight/stage/dispatch。
