# Good holdout lifecycle V5 — 精确 case-FINAL 体积契约 SOURCE

## SOURCE_READY_NOT_NATIVE：PREP12 与 D7 最终绑定分列

父已转交冻结的 D7 / component V3 双 FINAL。首轮十二项 NEW fake/temp/memory/AST 测试仍是 **PREP时12/12、0.722秒、D7 pins尚未收到**；没有为最终封存重跑同十二项。[独立最终绑定检查](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_lifecycle_routes_v5/FINAL_PIN_BINDING_CHECK.json>) 只查真实 SOURCE 身份与已测代码保留，不算第二套测试或 native证据。合约只把预留的 runtime/index/stager/单runtime overlay 四处 pin metadata 从 None 填为真实值；13个完整函数及仅归一化这四值后的全module AST 与PREP相同。最终 SOURCE seal为13成员，测试数量仍为12。没有实际执行、approval或新GO。

Catalog 为 Office/Windows ACL，无 RL 专用匹配；使用 FS 与允许的 Python314 `-B` stdlib。所有修改只在本 NEW V5。旧 V1–V4、D2–D6 与 component 原封件不改。没有 SSH、实际 reports/原 whole FINAL、模型/PT/raw、Torch/SDK/GPU、canonical C、锁、signal、Git、controller、watch、collect、原 task 模块或 main 执行。

## 唯一独立 reader 生产差异

[完整 reader](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_lifecycle_routes_v5/good_holdout_remote_reader.py>) 只在既有 `maximum(name)` 开头增加精确分支：

```python
if name in ('cases/CURB_PROTECTED878/FINAL.json', 'cases/SLOPE135/FINAL.json'):
    return C.CASE_FINAL_MAX
```

[合约](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_lifecycle_routes_v5/good_holdout_contract.py>) 新增 `CASE_FINAL_MAX = 2097152`。现有 `MetadataReader.read` 与 `_complete` 原已共用 `maximum`；它们及所有其他 reader 完整函数/类的 AST 和 function source 保持 V4。`BIG` 仍只是 terminal-only/sole whole cache 分类，而非上限 selector。

| 对象 | 有限 bytes 上限 |
|---|---:|
| 精确 C878 / S135 两个原 case FINAL | 2097152 |
| 其他 cases/*，包括 task/READY/error/preclose | 262144 |
| GROUP_PLAN | 262144 |
| 原 group/terminal metadata | 8388608 |
| 完整 JSON packet / 传输 stdout 原上限 | 16777216 |

不存在任意 FINAL 后缀或 `cases/*` 泛化扩大。角色/路径大小写、反斜杠、嵌套、partial、尾斜杠等变体不获 case 专用 cap，且原 allowlist 继续单独生效。

[controller](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_lifecycle_routes_v5/good_holdout_parent_actual_wait_controller_v1.py>) 5170 / `4cb6994a9afa0b399598f9af012529c9cd06bf6a8ad2e91c7d34f1c8496399c0` 与 [collector](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_lifecycle_routes_v5/collect_good_holdout_result.py>) 15045 / `988f4fcce7f58fe33c105e86e2f1028c9b37ded7696bba00250d02b0359d3eab` 保持 V4 全字节。合约仅预备 Stage7/strict7 label、新 case cap 与必要新身份；其他完整函数 AST 不变。

## 有限 raw 身份和失败语义

- 2 MiB/+1 检查在 open/read_count/decode 前进行；首次 stat 超界仍是 ERROR、read_count0、bytes/SHA unknown，不伪造“一次完整读取”。
- 有效原 JSON 全文 hash、len、未知字段、route/DR/metrics/cache 和 null 保留。相同 decoded object 的不同 wire 编码仍是不同 raw 身份。
- read 保留原 `json.loads` 结果，未加通用 dict 强制（TERMINAL_ROWS 本来为 list）。非 dict case FINAL 由既有 case gate 阻止；不修复、不强转。
- 四个 whole FINAL/terminal cache 各自读取/hash一次，不以 group 嵌入对象代替原 case bytes；changed-stat during/after read、disappearance 保持错误，不重新读取救 grade。
- 原 SOURCE False/runtime True、COMPLETE V1 文件名、非 PREFIX root、raw-plan 三身份、full20、原 teacher/cache/physics/acceptance、资源1800/900/2400及close/intent/grade/ERROR/childwait＋doubleEX＋outer actualwait 全部保留。
- 没有补 intent、重 grade、重评旧 root。原 D6 actual close/GradeFalse/outerRC1 不升级；未知 counts 保持 null，stage2 GO=False。

## 完整 export 是独立硬门，含现有 print LF

各 case <=2MiB、group/terminal各<=8MiB **不保证**重复保留的整个 packet <=16MiB。本 NEW 测试构造全部四文件均各自合界、但整包超16MiB的完整 fixture；原 export/transport 明确失败，不投影或删未知字段。

完整 `remote_main` 保持原 `json.dumps(..., allow_nan=False)`、UTF8 byte 长度门及 `print(raw)`，所以 stdout另含 LF。完整 `remote_packet` 对包括 LF 的 stdout 执行原16MiB门：

- JSON serialized 16MiB−1，外加 LF：wire恰16MiB，通过 fake transport。
- JSON serialized恰16MiB，外加 LF：wire16MiB+1，明确失败，decode不发生。

这里不悄悄更改 printer、newline 或 EXPORT cap；生产端 JSON 门与 transport 整体 wire 门是两层现有事实。fake client 只返回 BytesIO、记录命令字符串；没有执行任何 command、SSH或 remote main。测试 source-lock 完整 producer/transport 函数，没有将 AST 片段裁成替代 runtime。

## 十二项 NEW targeted SOURCE 测试

[完整 NEW 测试](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_lifecycle_routes_v5/test_v5_case_final_size_source.py>) 首轮十二项全通过，0.722秒；fail/error/skip/exclusion及四类 audit 全0。未复制或重跑旧40/11/8/7及任何 upstream/native套件。

1. controller/collector whole bytes、reader全部完整函数/类 source/AST 最小 delta、contract完整函数 delta、pending pins 先于 I/O。
2. 精确双 selector 与全部 small/group/变体边界，原 allowlist 独立。
3. 两 case 原 dict 2MiB−1 / 2MiB，完整 hash/cache/一次 decode。
4. 2MiB+1 及不扩的 GROUP_PLAN/task/READY/error cap，stat即挡、无 open/decode。
5. truncated/invalid UTF8/invalid JSON、非 dict 原 case gate与合法 terminal list。
6. `_complete` 同 cap、strict counts/types/status/hash/no-projection 阴阳性。
7. 等值不同 raw 编码的完整 len/SHA 区分。
8. 全四 cache、未知字段、terminal/group/role 全对象等同性与原 case 独立 identity。
9. stat在读取期间/读取后变更及文件消失的原错误路径。
10. 完整 packet wire16MiB与+1、现有 print LF、全字段不投影。
11. 每文件各自合界但全packet超界，transport明确失败，不丢字段。
12. fake GradeFalse/WorkerERROR/outerRC1 即使 innerwait/两EX真也保持失败，unknown counts null。

仅导入本 NEW own full C/reader/collector 定义；未加载任务 runtime/guard/App/Base。非dict早门使用 `None` 表示原闭包不可用，没有 App/Base stub，也没有据此声称完整闭包通过。测试仅在本目录专属临时子目录创建/读取/删除合成文件，清理前校验解析后的目标；Fake transport没有运行 captured command。

## SOURCE 审计引用与父报告分层

已按全文校验获准的 [SOURCE 审计](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_final_size_contract_audit_v1/SOURCE_AUDIT.md>) 13401 / `68487e3690a6f99106416e83236cb522bedd065df9a4c92b9629628503d1848e` 及 [结构化 SOURCE 审计](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_final_size_contract_audit_v1/SOURCE_AUDIT.json>) 16755 / `b648a00aa3f1c2d090b63b58f257825f5be5353c454e841452b11c692b9b800b`。

802787/509289原 case bytes、750/6000/1500/750、innerwait RC0/双EX释放、close622 generic262144错误、GradeFalse/outerRC1 均仅 PARENT_REPORTED 历史，非本子复测。原 audit报告中的42/31/26 SOURCE AST 和十个 SOURCE pins 是上游审计证据，不冒称本子重做结构审计或实际一次读/hash/decode。

首次十二项结果保存到 [PREP 回执](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_lifecycle_routes_v5/PREP_SOURCE_TEST_REPORT.json>) 和 [PREP 日志](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_lifecycle_routes_v5/PREP_SOURCE_TEST_LOG.txt>)。这是首轮工具输出的转录，original_stream_bytes_captured=False；没有为落盘重跑。D7_final_pins_received=False保留为当时事实，不改写为最终pins已参与测试。final另核四份已测源码整字节和contract13完整函数，后者采用与PREP Path.read_text一致的universal-newline文本表示；完整module AST只归一化四处pin值，SHA仍为`fc0e5af29caaa37d6078c81f2719d7af37451cfc067c77a07b5b083bd870cfb6`。这不是以AST或重编码代替生产raw身份。

## D7 / component 最终实际身份与诚实库存

- [D7 seal](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v7/SOURCE_SEAL.json>)：1699 / `88da829b7f9b6d4076e8cae14c367463b79285755b3f79a91e911fdad277142e`，8成员根`1b2624e17e69046c7c8c5d7cbb6d8ec01dbbe97021dccfccbcd5fa4553003787`。
- [component V3 seal](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_case_final_contract_v3/SOURCE_SEAL.json>)：1090 / `3b7356b5a9ca44b0b7e86e5bd73fd424919aa8dccf3a5ce43ea1d7bd1b99a658`，4成员根`e524d81448cf8e007ddcb79ce1cbc28a96431194882af0d62a70e549583df535`。
- [active V3 index](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_case_final_contract_v3/GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V3.json>)：21907 / `aa22260f2198ad37d6bb265c85d870203536a5dec19c6e554a556244cc5cddda`；格式仍V1、teacher revision2原样保留、另列case revision3。
- [active runtime](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_case_final_contract_v3/good_expert_holdout_runtime_v1.py>)：56467 / `29d29e96899575b0e1e1a805d210a04aba7cb0e50376959ff91779c13927b911`。仅一个overlay row变，其余19 whole rows包括9635/a839 guard全同D6。
- Source-only完整逆向比较：runtime仅CASE_FINAL_MAX2097152和三个显式case-reader关键字，逆向全文等于D6，27完整函数+2完整类保持；D7 stager29完整函数保持，另外两个函数仅typed7标签。没有导入或执行这些模块。

[SOURCE 库存](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_lifecycle_routes_v5/SOURCE_PINS.json>) 将D7逻辑164分为**137当前eligible SOURCE全文SHA/Python AST**与**27继承声明（9 reports＋18 discovery）**。后27在is_symlink/stat/open之前即排除；其中wire、ROOT2及15 capture本轮只核固定声明，不重读/重解码。旧145 whole rows完整保留；新增19 = D6 bundle9 + SOURCE审计2 + 原CFF源码3 + component4与seal1。Source验证集合互有重叠，不冒充不相交总账或全部164现场重hash。

D7 [SOURCE_INDEX](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v7/SOURCE_INDEX.json>) 内source_mirror段保留的是D6历史145/37206/e7be引用；当前164/49135/c895 [mirror](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v7/SOURCE_MIRROR_INPUTS.json>) 单独由D7真实seal及本包stager pins绑定。没有篡改旧段去冒充新manifest，也没有把旧kind当新身份。logical164加D7 own9不是flat20，更不是native完整static/vendor/banks包含性。

原good14、D2–D6、teacher component5、先前lifecycle V1–V4完整seal/成员均额外核对；其记录可能仍陈述旧轮136＋9，保持历史，不冒充本轮137＋27。相关SOURCE JSON中的模型/报告地址只是数据，不跟随访问。父独立producer身份及D7上游12测试均不跨schema借为本包测试或native证据。

最终SOURCE绑定作者过程保留三次检查纠正：审计MD pin抄录漏`962`导致完整声明门失败；仅标签逆向检查误写大写变量名导致精确函数比较失败；首轮PREP baseline为Path.read_text的LF而checker最初用raw CRLF，AST已相等但完整函数字符串摘要不等。仅修正NEW SOURCE verifier/checker，未改生产reader/controller/collector/已测12源码、未改PREP回执、未放宽原生产门。12项测试本身没有失败或重跑。

## 只读复核与边界

```powershell
& 'C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe' -B source_pins.py
& 'C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe' -B seal_source.py
```

上述在本目录只复核现有SOURCE库存、PREP保留、独立final检查及13成员整封，不运行测试/任务或重写报告。封存后不再修改成员。实际Native/Gate1仍UNKNOWN，actual quality=null，exact/interface/stage2 GO=False；交付状态SOURCE_READY_NOT_NATIVE。没有approval/GO/ledger，D6实际750故障、缺intent、falsegrade、outerRC1全部保持失败历史。typed phase1 collector是另一个目录/独立封件，没有串改。
