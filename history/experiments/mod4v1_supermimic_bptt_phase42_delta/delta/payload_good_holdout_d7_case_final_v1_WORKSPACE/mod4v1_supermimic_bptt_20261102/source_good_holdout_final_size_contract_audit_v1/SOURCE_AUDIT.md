# Good-expert holdout：FINAL 体积与完整身份 SOURCE 审计 V1

**结论：这是“完整 E1 FINAL 输出形状与通用小 metadata reader 上限”之间的契约缺口。** 当前三个 native case-FINAL 读取点和独立 CFF reader 都落在 **262144 B**；源码没有单独的、有意设定的 case-FINAL 上限。建议后续 NEW SOURCE 使用有限且专用的 **`CASE_FINAL_MAX = 2097152`（2 MiB）**，只作用于这三个读取点和两个精确 CFF case-FINAL 名称。**本次只审计：没有生成后继 runtime、修补原件、重跑原流程或补写 intent。**

## 1. 证据层次与边界

- **CHILD SOURCE：**读本地完整源码、用 stdlib AST 定位调用/字段、计算下列十个源码 pins。没有 import 任务模块，没有执行实际 metadata/prepare/stage/parent/worker 函数。
- **PARENT_REPORTED：**父消息 m02955 的一次功能性 byte/schema 诊断与先前闭合失败摘要。下表数值来自父报告；child 未打开任何实际报告或原 case FINAL，未独立复测它们的 bytes/SHA。
- Catalog 只有 Office/ACL 技能，与本 RL/SOURCE 审计无匹配；使用 FS read/glob/grep、批准的 Python314 `-B` stdlib。新目录首次 glob 的 `os error 2` 是尚未创建，不是 ACL 故障。
- 仅新增本文与[结构化审计和十个源码 pins](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_final_size_contract_audit_v1/SOURCE_AUDIT.json>)。无 SSH、SDK/Torch、PT/raw/banks、GPU、C-budget、锁、Git；旧源码/seal 不变。SOURCE 审计不构成新质量实测。

## 2. SOURCE：全部相关 FINAL 读取边界

| 真实位置 | 读取用途与当前边界 |
|---|---|
| [canonical core:65–74](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_a1_frozen_eval_integration_v2/a1_frozen_eval_runtime_v2.py#L65-L74>) | `_metadata(path, maximum=262144)` 先读 `maximum+1`，先检查长度，再 JSON decode 与 dict 检查。报错逐字为 `JSON metadata exceeds bounded source contract`。这是通用默认值。 |
| [NEW runtime:622](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_teacher_schema_v2/good_expert_holdout_runtime_v1.py#L616-L632>) | `close_original_eval_resources` 在原 App.close 前读完整 case FINAL；未传 maximum，继承 262144。 |
| [NEW runtime:709](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_teacher_schema_v2/good_expert_holdout_runtime_v1.py#L700-L714>) | `evaluate_waited_eval_case` 读完整 case FINAL；同样 262144。 |
| [NEW runtime:821](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_teacher_schema_v2/good_expert_holdout_runtime_v1.py#L813-L824>) | `grade_closed_reference_group` **直接**用 `_base._metadata` 读 case FINAL，再核对整个 terminal row；仍是 262144。仅替换 `_metadata` 别名会漏掉此点。 |
| [NEW runtime:779–790](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_teacher_schema_v2/good_expert_holdout_runtime_v1.py#L776-L790>) | 自有 group metadata reader 是有限 **8 MiB**；group FINAL/TERMINAL 等的边界不是原 case 原始字节证明。 |
| [原 native parent:59](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/single_gpu_good_expert_holdout_parent_v1.py#L52-L61>) | 等待后 `read_bytes()` 解码整个 case，嵌入 terminal/group；该处无有限长度检查。这解释 group 中仍有完整对象，不等于 bounded close/intent 成功。 |
| [AppV6:201–205、343、436](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_app_close_runtime_compat_v6/app_close_semantics_v6.py#L201-L205>) | 通用 `_read_object` 是无界 `read_bytes()`；其通用 close/evaluate 有 FINAL 读取。**本 E1 的 active close 并不使用该 reader**，而是借其核验原 App 绑定后，在自己的 runtime:622 读 FINAL。 |
| [CFF reader:17、32–35、54–91](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_lifecycle_routes_v4/good_holdout_remote_reader.py#L17-L91>) | `BIG` 表示 terminal-only/once-cache，不表示大文件上限。`maximum(name)` 对全部 `cases/*` 返回 `PLAN_MAX`，包含两个 FINAL，故仍是 262144。 |
| [CFF reader:164–168](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_lifecycle_routes_v4/good_holdout_remote_reader.py#L164-L168>) | `_complete` 再使用同一错误分类上限，修 read 但漏此验证也会继续失败。 |
| [CFF exporter:394–402](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_lifecycle_routes_v4/good_holdout_remote_reader.py#L394-L402>) / [collector:156–170](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_lifecycle_routes_v4/collect_good_holdout_result.py#L156-L170>) | 整包保留 Group、TERMINAL、两个 case 与 validation；传输另受 **16 MiB** 限制，无投影兜底。 |

canonical core 的原 close/semantic 定义也继承同一小默认值；NEW E1 runtime 覆盖了自己的 active 路线。task/plan/producer 等普通 metadata reader 并非本次建议扩大对象。现有 group 的 8 MiB 是 **group** 先例，不冒称已有一个专用 8 MiB case-FINAL 规则。

**CFF 计数含义：**stat 长度检查在 open/read_count 设置之前。首次 stat 即超界时，error、`read_count=0`、bytes/SHA unknown 是一致的失败证据，不是完整读取一次。group 嵌入的 case 对象也不是该原 case 的 raw identity；[完整 case 必须等于 terminal row.data](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_lifecycle_routes_v4/good_holdout_remote_reader.py#L329-L332>)。

## 3. SOURCE：为何完整 FINAL 大，而非 checkpoint 被复制成 JSON

[原 worker:32–87、120–135](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/e1_good_expert_holdout_worker_v1.py#L32-L87>) 的 AST 静态合并结果是 **42 个顶层字段**。原 FINAL 完整保留 `route_scope`、metrics、fresh DR before/after、source_cache；raw 仅是路径、bytes/SHA、shape 元数据。writer 使用原 indent2、flush/fsync、atomic replace，没有 FINAL producer 字节上限。

- [C878 factory:75–96](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/e1_good_expert_holdout_factories_v1.py#L75-L96>)：完整 80×35 ground/normals，加 actual world ray origins、expected ground、world-mesh receipts 等，共 **31 个 route_scope key**。这些是原物理 query 证据，不是可删除的状态冗余。
- [S135 factory:266–277](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/e1_good_expert_holdout_factories_v1.py#L266-L277>)：完整 80×35 ground/normals 等，共 **26 key**。
- [fresh DR bridge:21–43](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/e1_good_expert_holdout_bridge_v1.py#L21-L43>)：完整 live parameter、sensor manager、chassis PD、spring/gas、action/feedback 等 recipes 与 seed/reset/D0D7 audit。before/after 原样入 FINAL。
- [runtime cache receipt:661–695](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_teacher_schema_v2/good_expert_holdout_runtime_v1.py#L661-L695>)：保留完整 teacher 身份、producer evidence、reference state **manifest/receipt**；嵌套元数据的重复不是第二次 PT decode，也不是把全 checkpoint tensor root 写进 JSON。parentwait、matched UID、effect/cache improvement、skill 等 unknown/null 或 unresolved 字段维持原状，不代填为成功值。

## 4. PARENT_REPORTED：真实体积与闭合失败分开列示

下表只转录父 m02955；本 child 的 SOURCE AST 只独立核对 **42/31/26 字段结构**，没有复测原 case 字节。

| 父报项目 | CURB_PROTECTED878 | SLOPE135 |
|---|---:|---:|
| 原 case FINAL bytes | **802787** | **509289** |
| compact JSON bytes | **396677** | **270439** |
| route_scope compact bytes | 306127 | 184875 |
| route_scope standalone indent2 bytes | 571047 | 321277 |
| metrics compact bytes | 26155 | 21183 |
| before DR / after DR 父报 field bytes | 21642 / 23147 | 21642 / 23267 |
| source_cache 父报 field bytes | 14008 | 13895 |

原 bytes 的父报 SHA：

```text
CURB_PROTECTED878 20e07a25e41b00849e271a009d9e9859ee24751ff2571bd37c52b4a50d885ea7
SLOPE135          4249ebaff07dd8a0d8b2ab45df806d96172b2c4960f7288789c48fe6bea766cc
```

父诊断 RC0，各原 case 一次物理 read/hash/decode，indent2 重编码长度恰等原长；原数据、生产 cap 和结果全未改。**即使 compact，两者仍大于 262144，所以去 indent 也不足以修复。** subtree 的 standalone 编码不是原文件内可相加的字节切片；DR/cache 子值编码方式不进一步推定。

父报两者均 750 controls / 6000 physics / 1500 feedback / 750 actor、optimizer0、env_close_returned=True、worker 早期 passed_execution=True。它们不覆盖后续 close/grade：历史缺 intent/close error、sourceGrade=False、独立 outer wait RC1 全部保留。不是新合格 seed，不合并成全技能 90%，不声明 improvement/noninferiority。

## 5. 原 App.close 与完整 raw 身份仍是硬条件

[active close:580–636](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_teacher_schema_v2/good_expert_holdout_runtime_v1.py#L580-L636>) 的顺序是原 env.close → 核验原 App Python source/绑定 → 完整 case FINAL → 原 raw len/SHA 的持久 fast-close intent → **原 app.close 零参数一次**。622 的 size error 被记为 durable primary error，仍继续调用原 app.close；fast App 退出 RC0 并不会补出 intent。

[waited semantic:700–769](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_teacher_schema_v2/good_expert_holdout_runtime_v1.py#L700-L769>) 与 [CFF collector:34–90](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_lifecycle_routes_v4/collect_good_holdout_result.py#L34-L90>) 仍要求原 source grade、无 durable error、两个 inner wait/both EX、独立 outer actual wait。新上限或缓存 group 对象不改变历史失败定性；不事后补写 pre-close intent。

native close/postwait/grade 是不同用途的完整 metadata 读取；CFF 的 onecache 与父诊断的一次 read 也各属独立用途。它们不是“所有阶段共用一次 FINAL 物理读取”的承诺。PT 的原 onebytes/hash/decode、mother0、whole-cache/freeze 约束保持不动。

## 6. 最小后续方案——仅建议，尚未实施

1. 后续 NEW runtime 声明专用有限 `CASE_FINAL_MAX = 2*1024*1024`，**只**给 622、709、821 三个原 FINAL 读取点显式使用；保留 canonical core 默认 262144，不 monkeypatch 通用 reader。
2. 后续独立 CFF 使用同名有限约束，selector 仅精确匹配：
   - `cases/CURB_PROTECTED878/FINAL.json`
   - `cases/SLOPE135/FINAL.json`
   read 与 `_complete` 共用该 selector。不要扩大任意 `cases/*`、READY、error、task 或 GROUP_PLAN。
3. PLAN 262144、GROUP 8 MiB、EXPORT 16 MiB 不变。完整 route/DR/metrics/cache/unknown fields 不删、不投影、不用重新编码后的对象冒充原 raw SHA。parent 的无界 embedding 也不替代 case 完整身份。
4. **整包边界仍单独验证：**两 case 各 2 MiB 与 group 8 MiB 本身不保证重复保留 group/terminal/cases 的完整 packet 落在 16 MiB。后续必须 fake 整包边界；超 export cap 仍明确失败，不丢字段救传输。
5. READY 等其他 case 文件保持原上限。SOURCE 可见 READY 含完整 before-DR/cache，提示独立潜在体积风险；没有实际 READY 超界证据，不把它预判成已发生失败。
6. producer 分片不是此轮最小方案：需 NEW 明确格式、完整内容寻址、所有 shard 身份与 intent/grade/export 同步协议；当前格式下的短摘要不等价于完整原 FINAL。
7. 真正实施前同步 NEW runtime/完整20 index、materializer active index binding、独立 CFF pins/seals；不动 canonical7a092、AppV6/Base、原接受/physics/reset/done/D0D7/缓存/teacher/资源/wait/close。之后才考虑有独立明确 purpose 的新 root，不重评旧 root。

**后续至少八类 fake 阳阴性门槛（本审计未运行候选实现）：**三个 native 点+两个精确 selector 一致；2 MiB 临界及 +1/truncated/non-dict；原 raw len/SHA 和等值不同 wire；未知字段与完整终端等同性；intent fsync/顺序与一次原 close；缺 intent/错误/outerwait 失败保持；完整 16 MiB packet 边界；完整 SOURCE 身份/闭包/seal 后才新 root。原独立 seed20260929/30、N80/750、六角色 deferred/H1 冻结及 conditional direction/standing 统计均不变，stage2 GO=False。

## 7. 只读核验与十个 SOURCE pins

本次 AST 断言通过：generic default=262144、FINAL=42 fields、route_scope=31/26 keys；十个完整源码均 AST parse，任务函数执行数 0。精确 bytes/SHA 和三份原 seal 观察值见[结构化审计](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_final_size_contract_audit_v1/SOURCE_AUDIT.json>)。

十个 pins 覆盖：NEW runtime、canonical core、E1 worker/bridge/factories、原 native parent、CFF reader/contract/collector、AppV6。核验是读取源码与旧 seal，不是重放旧测试或实际 preflight。报告只保留 SOURCE 建议与 PARENT_REPORTED 事实的分层，未新增 native 通过声明。
