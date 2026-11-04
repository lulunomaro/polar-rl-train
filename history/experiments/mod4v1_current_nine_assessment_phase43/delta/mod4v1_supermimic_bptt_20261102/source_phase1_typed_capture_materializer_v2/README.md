# Typed capture 材料器 SOURCE publication 2：仅修历史 B2 绑定

**Source publication 2 ≠ Producer wire 2。** 本包仍严格绑定原 typed Producer V1 的15个发布成员、finite34、Task/Plan/Producer ABI V1与原receipt协议。阶段源码的 `SOURCE_DERIVATION_VERSION=1`、原lineage、root prefix、completion及原调度／资源／close语义保留；仅新增 `MATERIALIZER_SOURCE_PUBLICATION=2` 与历史binding V2。

本交付解决一处已核实的 SOURCE identity selector 错位，不包含 compact-wire 修复，不声称大包问题已解决、不声称真实 Linux 预检或 native 已通过。父会后续 Producer 最小传播另立版本；这里不猜新 pins，不改 final13 collector，不安排旧 indent2 native。

## 1. 唯一确认的错位

[V1完整阶段模块:279](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_capture_materializer_v1/stage_phase1_typed_capture_v1.py#L279>) 原来以 `DEPENDENCY_SEALS['sensor']` 验历史 B2 diagnosis handoff。冻结 V4 的 sensor 是 B2，而 typed V1 的 active sensor 正确升级为 B4；原历史函数整体保留后造成错误相等条件。

本次已读完整V1阶段、support、旧V4历史函数／manifest、typed index与历史 SOURCE handoff，审查所有 selector 及 post188 固定假设。完整结论、16组后续条件与396 actual realSource／272 SourceProof 独立核验，见 [SOURCE审计说明](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_materializer_history_binding_audit_v1/AUDIT.md>) 和 [审计数据](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_materializer_history_binding_audit_v1/SOURCE_AUDIT.json>)。只确认这一处同类错位，未将其解释为所有其它实际条件已通过。

父会失败与后续 CPU wire-volume 信息均为 PARENT_REPORTED；本子会没有打开 actualreport、没有复跑已消费 `_SOURCE_INPUT`，也未进行 wire-volume 或 typed SDK 试验。

## 2. 两个独立已发布 reference

| 用途 | 固定 raw publication | 完整 source proof |
|---|---|---|
| 历史 diagnosis B2 | [原B2 seal](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v2/SOURCE_SEAL.json>)，2909 bytes，`be538a07c8ccfb785023422ace6985e1fde0bd5b885266124e430527c1ec558a` | 原 typed index 的 `original_B2_reference_seal`；13个实际member identities；历史 handoff3991 bytes／`238ef8f8ecd99383f91d3d474cbae3a409a16f9ec56e8e49f2c56e5b9b523c99`；原声明 root:null保留 |
| active sensor B4 | [B4 seal](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v4/SOURCE_SEAL.json>)，3824 bytes，`81fe69c8c2f2ffde98b2a5e4b03d6921207d60156dcb180ab0097aa7397813b3` | 原 active dependency selector及21成员严验，整段源代码不变 |

[双reference SourceProof](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_capture_materializer_v2/SOURCE_REFERENCES.json>) 独立记录13＋21实际源码字节／SHA，而不是只复述 claim。

## 3. 精确修改与安装语义

[完整V2阶段模块](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_capture_materializer_v2/stage_phase1_typed_capture_v2.py>) 从完整冻结 typed V1 以唯一局部hunk派生，不用AST片段生成runtime、不做全局replace。

- 14个原top-level函数全部保全，**13个完整 function source及AST逐字一致**。唯一修改 `verify_B2_source_closure(source_root, index)`：原222–289→新224–297；原function source SHA `c4ac37f7c1f8699e835fd5c0766f1a426824d464b5ce8f0f56ba10e056451acd`→新 `973c9e46c38a99e10e9cba6f70cc8d3c5ba799befa892a2c27cfdc64dc7fcb04`。
- 新hunk重新执行独立literal B2 raw seal SHA／13成员 `verify_package`，再用原bounded metadata读取raw；把真实member identities交给新纯memory [历史selector](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_capture_materializer_v2/historical_b2_binding_v2.py>)。这段实际 SOURCE closure 未由本子会调用。
- selector先用独立固定2909／be538硬pin锚定published raw，**之后**才解码其13个expected members；实际observed、任意index/handoff claim、active sensor均不生成expected。再要求index、handoff与实际完整13一致；缺失／重复／漂移／错误类型均报错。helper不读active selector，不接受True充当proof，不修复null，也不fallback。
- 只向原SOURCE closure receipt增加 `historical_B2_reference_binding`。原SOURCE receipt family及Producer wire V1不升级；不添加runtime审批／parent-review gate。
- 17个原shared helpers整文件字节同；原 typed support及396 mirror整文件字节同。全部其它原函数、try/finally、模型／raw／operational-before-stat、完整复制与原资源行为不变。

查看 [完整函数diff](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_capture_materializer_v2/FUNCTION_SOURCE_DIFF.txt>)、[整个模块diff](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_capture_materializer_v2/MODULE_SOURCE_DIFF.txt>)、[逐函数source/AST证据](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_capture_materializer_v2/FUNCTION_SOURCE_DIFF.json>)；[source index](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_capture_materializer_v2/SOURCE_INDEX.json>) 保存九个本包Python pins和精确API/line/sourceSHA。

## 4. 本次六个新定向测试

[测试源码](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_capture_materializer_v2/test_history_binding_v2.py>) 和 [实际收据](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_capture_materializer_v2/SOURCE_TEST_RECEIPT_attempt1.json>)：**6/6 PASS，0 failure／error，0.16345110000111163秒，audit[]**。

1. 完整14函数／13同源、17helpers、原active B4 block、原prefix及Producer seal/ABI/finite34 pins不变；可逆精确模块hunk。
2. 真正published B2 raw＋index＋handoff＋实际13的memory正例；active B4保持独立。
3. 把active B4放进historical index／handoff／raw的负例。
4. 伪造raw同时替换全部claim仍失败，claim不生成expected。
5. 缺少／多出／重复／改变实际13或index/handoff member、bool proof／float size等负例。
6. 缺reference、错status／origin、relative claim、byte-count float、root:null→False、缺成员等负例。

仅AST、纯memory selector与只读published source fixture；**材料器import、loader、原B2 builder、wholeprepare、wholemetadata、entry、SDK、Torch均0**。旧9未跑，6例不再重复执行。原407已发布text inputs＋旧V1全部29个文件＝436 pinned text，before/after全部同；logical SHA256 `f1378a97c84ae87846b6f248ebbf9d3153b360c265613549200d3248072a9042`。这不是全真实baseline、vendor7、actor35 equality或native call counts证明。

审计阶段两次自有命令问题（执行前长shell源校验拦截、自有C1 relative-key解析断言后修正）保留于外部两份审计文件；本次六例首次运行全过。测试前source inspection发现B4 seal是dict rows，已把仅自有reference记录器按原package格式规范化；生产源码未因此变更。

## 5. 原完整材料化协议不变

- 原完整V8 `worker_sources`、pinned assets、八棵runtime树、全部静态NPY/NPZ、native vendor7，不以finite34或Python closure替代。
- 32 overlay＋2独立baseline-authoritative bootstrap；34个installed aliases全核对。原origin/input path/logical digest、动态旧source冲突retention与actual stream SHA／fsync／observed保留；不硬编码冲突数。
- 显式R395＋T1共396输入；原R332全部保留。T只固定653-byte capacity source，不扫描T树、无原F盘fallback。两份外部.patch只按既有精确triple作SOURCE proof，不执行patch。
- 原physical／DR／H1／mothers／acceptance、AppV6→Base、完整core、GPU／fd／deadline／GO／调度／成本／lease／原env/App close不变。
- 原新root prefix、原completion filename与“metadata→全copy/hash/fsync→observed→GROUP_PLAN→actual-root metadata/ROOT==HERE→completion”次序不变。失败消费root，旧失败SOURCE_INPUT不复播。

## 6. 未来CLI：仅供父会按新用途最小传播

下述不是本子会执行记录；Source publication2并未改变任何CLI参数、control bounds、roots约束或原runtime资源条件。`M2` 为独立NEW V2包目录；R/T为实际显式Source mirrors，原group/native roots是原协议输入，不由本子会访问。

```bash
"$PYTHON" -B "$M2/verify_source_seal_v2.py"
"$PYTHON" -B "$M2/stage_phase1_typed_capture_v2.py" \
  --original-group-root "$ORIGINAL_GROUP_ROOT" \
  --source-root "$R_MIRROR_ROOT" --t-source-root "$T_MIRROR_ROOT" \
  --native-root "$ADMISSION2_ROOT" \
  --new-root "$B/tasks/$NEW_GROUP_ID" --group-id "$NEW_GROUP_ID" \
  --gpu-uuid "$GPU_UUID" --controls 64 --preflight-only
# controls 仅64或128；mode只能preflight-only或stage二选一。
# 由父会选新未消费root；原MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_前缀不变。
# 可加_TYPED_V2_后缀，不复用V1失败的_SOURCE_INPUT。
```

[只读seal verifier](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_capture_materializer_v2/verify_source_seal_v2.py>) 仅本包hash／AST／JSON／index/test pins，不import阶段入口；[SOURCE封印](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_typed_capture_materializer_v2/SOURCE_SEAL.json>) 覆盖最终全部18 members。

父会已在m01892全文review完整函数diff／模块diff／helper／references／逐函数JSON／六例receipt，允许只补NEW V2 index／本文／只读verifier／seal metadata。此为SOURCE审查记录，不是新runtime gate。

**最终边界：** actual loader／B2 builder／prepare／preflight／metadata／stage／parent、actualreport、PT／raw／C／lock／Git、SDK／Torch／训练均0；`materialized:false / native_enabled:false / exact:false / Gate1:UNKNOWN / stage2_GO:false`。真实SDK binding、bitwise actor35 equality、call counts与阶段1验收仍属父会后续独立证据。
