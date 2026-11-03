# Phase1 原SDK被动接口：最小 SOURCE 集成 V1

## 结论 / 当前边界

- NEW purpose：`NEW_PASSIVE_INTERFACE_PROBE_NO_TRAIN`。默认只请求 E3，64 controls、N80；另可显式请求 `[E3,W35]` 或128 controls。它是接口验证窗口，绝非原 E3 160 / W35 1600 controls 的技能质量分母；synthetic0 tape 的0%或RC0都不表示技能通过。
- 本封件只提供 **已初始化原env/bridge的adapter + SOURCE只读preflight + NEW FINAL证据谓词 + stdlib fake/AST测试**；没有native worker、scheduler、materializer、dispatcher，也没有CPU SDK、resource gate、stage、dispatch、PT、GPU执行。
- 原parent/资源owner整段保留；先读原SOURCE并列出10处可审计差异，父review/另授权后才制作NEW-purpose nativeworker和close/guard衔接。本轮不是自动适配旧guard。
- sensor只使用已知稳定 `install_passive_capture` / `BoundedRecorder` API，通过显式参数注入，不import浮动native依赖。sensor SHA未随本封件冻结，等待父代理给出封件后创建新lineage。actuation observer尚未交付：**DEFERRED_UNSEALED，不猜API**。
- partition冻结root：`0feb70e552a915ca698b87cdc7a4e3b22ee614e86ce55c2b9677a6f0e9c30bdf`；原32 stdlib tests PASS仅SOURCE，Gate1仍 `UNKNOWN`，exact=false，阶段2未放行。

## 关键审计发现

1. [原frozen正式worker](../source_bound_only_native_integration_v1/worker_formal_bound_only_v1.py#L53-L108)仅直接env+actor运行，**没有NativeTaskBridge**。把sensor tap塞进该worker会在原bridge binding检查处失败；不可伪造bridge来过检查。
2. [原A1训练worker](../source_native_v6_runtime_compat/_SOURCE_INPUT/sealed_source/worker_supermimic_bptt_app_close_candidate_v5.py#L15-L119)虽有完整bridge，但main硬training task/GO、4FD、N512/1024/2048、target>=3000和learner。只复用其原setup→首次reset→命令绑定→bridge构造路径，不调用其main或learner。
3. [原NativeTaskBridge](../source_native_v6_runtime_compat/_SOURCE_INPUT/sealed_source/native_supermimic_bridge.py#L84-L161)构造不reset，`initial_obs`可避免init_state重新compute。teacher仅state_dict/export路径使用；synthetic0无需teacher权重，未来可以 `teacher=None`，同时禁止state_dict/export/trainer路径；本轮未实际构造nativebridge。
4. [原parent](../source_bound_only_native_integration_v1/single_gpu_e3_w35_bound_only_parent_v1.py#L11-L84)的kind、固定双成员检查和旧quality gate均不适用NEW capture，原生运行不能靠改controls就通过。
5. [原runtime](../source_bound_only_native_integration_v1/bound_only_native_runtime_v1.py#L110-L205)仍强制原8角色catalog、E3/W35两成员、旧controls、cache/producer/ref identity、2个继承资源FD；这些旧条件不自动承认NEWpurpose。

## 最小数据流（本轮只实现粗体adapter）

```text
qualified original owner + complete parent acquisition/readiness/wait/finally
  -> NEW-purpose explicit task validator (future source diff, not emitted runnable)
  -> original source/module setup + complete static banks/runtime/vendor7
  -> original build_env(N80) -> exactly original first reset (once)
  -> original command/pose ordering retained; take reset-returned original obs
  -> original NativeTaskBridge(same env, ..., teacher=None, initial_obs=original_obs)
  -> bridge.init_state() (original bridge behavior; no observer recompute)
  -> ADAPTER install_after_first_reset(same env, same bridge, stable sensor API)
  -> external original bounded driver: synthetic zeros6 -> bridge.step once/control
     OriginalEpisodeBoundary.for_action / after_original_step retained
     ADAPTER observe_actor35(original returned policy buffer, same buffer)
  -> ADAPTER close -> original bridge.close -> original env.close -> full AppV6->Base
  -> actual worker Popen.wait -> NEW capture FINAL semantics
  -> original finally waits ALL own children then privateGPU EX+finite EX release
  -> outer controller actual parent Popen.wait -> new-purpose closed result
```

reset返回obs若与E3原pose发布顺序存在差异，先源审计并由父review；不可为tap增reset。原frozenworker的既有initial compute与训练worker initial_obs路线不是可混搭的等价物。当前adapter不负责构造env/bridge/teacher，不调用任何step/reset/compute/SDK getter，也不创建RNG。

## 明确的10处最小函数/调用点差异（尚未移植到旧文件）

| # | 原函数 / 范围 | NEW-purpose最小差异 | 必须原样保留 |
|---|---|---|---|
| 1 | `select_requested_roles(plan)`，原runtime110–142 | 显式kind/purpose；请求仅`[E3]`或`[E3,W35]`，完整原catalog仍保留 | 原role source、runtime/static银行及worker_files全集，不裁AST子集 |
| 2 | `make_task(role, plan, deadline, fds)`，原runtime193–204 | NEW capture task/FINAL labels、64/128、synthetic0及PT0声明 | 原deadline、GPU_UUID、来源/physics/DR/cmd/phase/speed/acceptance、资源FD继承 |
| 3 | `validate_group_task(task, role, group_root, case, contracts=None, *, environment=None, fd_check=None, now=None)`，156–190 | 独立NEWpurpose校验，禁止旧qualQualityTrue转义；模型cache条件只在显式synthetic0 PT0路径取消，不伪造A1cache | canonical/owner权限、2 inherited resourceFD、完整原契约/来源检查 |
| 4 | 原parent `main()`，11–78 | kind + `len(children)==len(requested) in (1,2)`配合精确成员校验；newsemantic调用；其余资源块保持 | 17–38全部资源准入；39–58 Popen/barrier；63–78 actualwait+释放完整闭包 |
| 5 | NEWworker `main()`（由原setup/原loop窄移植，不调用旧main） | N80、原首次reset返回obs、teacher=None/zero6tape、bridge init一次、每control一次step、OriginalEpisodeBoundary和原buffer传入adapter | 原物理/DR/命令/pose顺序，term/trunc分离；无母本reopen，无训练保存 |
| 6 | 本封件 `install_after_first_reset(env, bridge, feedback_module, role_api, bridge_pin, request, *, sensor_api, snapshot=None)` | 只注入稳定sensor API，验证sameenv/已firstreset，原buffer记录+restore | sensor实际binding/MRO/code SHA/原一次调用及returnidentity检查；无新plant/RNG调用 |
| 7 | `close_original_eval_resources(env, app, case, task, *, env_already_closed=False)`，原runtime365–419 | NEW FINAL/integration与tap-before-bridge恢复顺序，原App实际binding检查仍调用完整helper | env.close一次、完整AppV6->Base、fsync intent、app.close一次，绝非stub |
| 8 | NEW `validate_capture_preclose_final(final, task)`，替换原eval close runtime408的旧quality precondition（计划，不在本轮导出） | 独立NEW capture kind/steps/count/PT0/restore证据；原AppV6 training `_validate_final_for_intent(final, task, job)`保持原样，不调用它冒充capture validator | 完整AppV6与Base来源/实现不裁剪，原App close实际Python/MRO pin、envclose+intent hash/atomic/fsync完整性 |
| 9 | `evaluate_waited_eval_case(case, returncode, role_entry, group_id)`，原runtime470起 -> 独立capture谓词 | 要求实际step/tick/100Hz唯一key计数、原buffer、terminalpre-reset/partialreset/clock、wait/close/release，不看skill百分比 | 真实worker Popen.wait必须先发生，RC0单独无效 |
| 10 | `batch_result(plan, terminal, group_start, *, epoch)`，原runtime311起及末尾closedgrade调用点 | 输出NEW capture scope与每成员UNKNOWN/covered/inconclusive，不借旧qualitypass；等待外层parentwait后再闭包 | 完整parent退出/EX释放证据及来源；无训练账本写入 |

第8项区分了原eval专用close precondition与原AppV6 training predicate；后者形参已按原源码230行核实，SOURCE preflight记录其精确AST签名，仅证明旧training语义不适用capture。此处只表达待review差异，不输出可执行patch。新worker/parent/controller/sourcehardpin的NEWpurpose白名单和外层关闭grade也必须显式新lineage，旧newkind/sourcehardpin guards照常阻止新件。本轮没有建立任何绕行入口。

## SOURCE adapter接口 / 能证明什么

- `install_after_first_reset(...)`：caller先得到原env/bridge，稳定sensor API做完整actualbinding/source/MRO/code检查；本adapter只确认sameenv和已初始化状态，严格请求契约。
- `session.observe_actor35(actor35, original_policy_buffer=..., control_index=...)`：`actor35 is original_policy_buffer`且宽35，保留原对象返回，克隆bounded witness而非生成clean35；不是untapped/tapped bitwise结论。
- `session.report()`：只给SOURCE集成receipt，native_enabled=false，exact=false，Gate1 UNKNOWN；actuation deferred。`session.close()`仅恢复tap；caller随后执行原bridge/env/App关闭，adapter不替代resourceowner。
- `validate_waited_capture_evidence(...)`：NEW证据schema谓词，显式需要真实counts、terminal/partialreset coverage、actor bitwise对照、完整close/wait/EX释放。fake schema通过也不构成现场验证；当前action deferred使 `capture_interface_passed=False` 恒成立。
- 64/128窗口未自然出现terminal/partial reset时应报inconclusive；不通过新增reset/强制死亡来造覆盖，也不擅自增加controls。

## 只读preflight相对旧preflight的差异

- 旧stage/preflight服务17完整映射、原160/1600质量及资源parent准入；本preflight仅核对NEW SOURCE request + 原17来源全bytes/SHA + parent关键块AST + partition seal身份 + sensor稳定函数签名。
- 不执行stage.prepare、不import原runtime/worker/SDK、不查看模型PT或canonical账本、无远程/锁/进程/GPU命令；不会产生NEWpurpose准入。
- 原17映射含完整canonical A1 core独立alias37927/7a092…、formal h1ea4、poseCacheV4、AppV6 27769/3d2d…、Base22337/dc4…、nativebridge13125/8211…；其余runtime/static banks/7vendor应由原stage完整inventory保持。原stage `VENDOR_PIN=(7,ddf9d6e1744c050fd5298805d125a611673ff22ade52c5177fb02c488ff8f0c0)`；本轮只读其源码，不复制/运行vendor或静态资源。
- owner/canonical/私GPU_EX/finiteEX、3900–3600–300/1800、reserve86412.86069250107不变。未来单E3任务只减少requested成员，不减少完整source/runtime/static/vendor集合。

## 明确 blockers / 父review后顺序

1. **B sensor seal待父review**：本件只基于稳定API，不锁浮动SHA；冻结后新lineagepin实际完整sensor source/API/test receipt。
2. **action observer未交付**：raw action/18 queue、各阶段实际参数/caches没有API；不猜，不宣称全Gate1。
3. **NEWworker缺省尚未生成**：原frozenworker没bridge，原trainingmain不适用；需review上述窄移植和E3pose/initial_obs顺序。
4. **NEW close/gate/guards尚未接通**：完整AppV6->Base代码已找到；新kind/FINAL/fastcloseintent和NEW parent/controller/sourcehardpin需显式review，旧件不自动放行。
5. **真实资源/SDK证据为0**：没有原SDK实际binding、same-instance实时tap、100Hz clean16/noise/delay、真实terminal/partialreset/clock、untapped/tapped actor35 bitwise、实际close/wait/EXrelease证据。SOURCE测试不能替代这些。
6. 父review后另授权 **NEWpurpose真正CPU/原资源gate验证**，先验证以上最小路径再决定真实native接口窗口。训练阶段2保持未放行。
