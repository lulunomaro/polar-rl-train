# 同一完整 A1 cache 的 original embedded-teacher mean reference — SOURCE V1

## 1. 交付与边界

本件仅新增源码、stdlib 假对象测试和未来父端 CPU/Torch fixture；没有 native/reference 实测，没有改 405 当前依赖闭包修复、旧 microbatch、accepted 循环、控制/DR/physics、原阈值或旧封件。catalog 的 Office/ACL 与本任务不匹配，实际使用 read/glob/grep、FS 与 stdlib CLI。

- [adapter](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_frozen_embedded_teacher_reference_v1/embedded_teacher_reference_v1.py#L72-L186>)：直接使用公开 `mean.pi.teacher`，不是另造母模型或把失败候选换回旧 actor。
- [API](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_frozen_embedded_teacher_reference_v1/API_CONTRACT_EMBEDDED_TEACHER_REFERENCE_V1.json>)：构造、caller、producer 证据、semantic gate、CPU 依赖。
- [42项最终 stdlib 回执](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_frozen_embedded_teacher_reference_v1/CPU_TEST_RESULTS_HARDENED_V1.json>)、[测试源码](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_frozen_embedded_teacher_reference_v1/test_embedded_teacher_reference_stdlib_v1.py>)：0 failure、0 error、约0.03s；Torch 未导入，SDK/native/GPU/实际 PT 操作0。
- [未来真实软件 CPU fixture](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_frozen_embedded_teacher_reference_v1/remote_cpu_embedded_teacher_synthetic_v1.py>)：本地未执行，真实 Torch 数学结果仍 null。

parent 提供的本次旧 V1 native 上下文是 E3/W35 完成160/1600 controls和冻结校验，但 AppV6 少依赖导致 close ERROR，故不是 qualified execution；这不是新 reference 结果，也不在本件修其依赖。该窗口的 E3 credit0 / W35 pooled26/86不能充作增益证据或母本替换依据。

## 2. 来源事实与冻结证据层级

1. [405 附录A:96–104](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_a1_frozen_eval_integration_v2/SOURCE_A1_FROZEN_EVAL_INTEGRATION_V2.md#L96-L104>)明确允许从同一 full cache 的 strict-loaded `mean.pi.teacher` 取参考，同时要求 actual producer weights+buffers 冻结证据、RSL source PIN、独立 fresh env 与实际 paired 证据。设计路线不是已有母本结果。
2. [原 wrapper:70–82](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_native_v6_runtime_compat/_SOURCE_INPUT/sealed_source/native_supermimic_bridge.py#L70-L82>) 的 base 是 `teacher(TensorDict(policy=history[-1, offset:offset+35]), stochastic_output=False)`。raw35分支offset0，候选是 `clamp(base+.05*delta, -6,6)`。参考是 **`clamp(base,-6,6)`**，不从已clip候选动作减delta，也不执行 residual。
3. [full cache 校验:119–153](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_eval_a1_raw35_v1/frozen_a1_raw35_v1.py#L119-L153>)保留四模型/优化器/环境扩展整根、N1024 source context；[one read/hash/decode:157–193](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_eval_a1_raw35_v1/frozen_a1_raw35_v1.py#L157-L193>)不切replay/history。参考仍从完整A1产生的mean取得teacher，并不抽一个teacher-only checkpoint再读。
4. [build mean:195–221](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_eval_a1_raw35_v1/frozen_a1_raw35_v1.py#L195-L221>)先构造原wrapper，再exact-key/shape/dtype/finite/full-value strict load整份pi，避免构造时清零已训练残差；[原冻结守卫:224–246](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_eval_a1_raw35_v1/frozen_a1_raw35_v1.py#L224-L246>)覆盖整个pi的parameters+named buffers和整份CPU根。本adapter在每次动作前后继续调用这些守卫，constructor/receipt另比完整teacher state_dict全键/shape/dtype/value，norm/std绝不挑选丢弃。非persistent live buffers仍由原named-buffer守卫覆盖。
5. [历史V4 producer:71–84](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_resume_runtime_v2/worker_supermimic_bptt_pre_reset_candidate_v4.py#L71-L84>)不是只写一个bool：`actor_snapshot={key:value.detach().clone() for key,value in actor.state_dict().items()}`；`assert_teacher_actor_unchanged`检查整键集、全部`torch.equal`以及requires_grad=False，每次complete save前执行。该actor同对象传入`TeacherResidualPolicy`；[FINAL前:99](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_resume_runtime_v2/worker_supermimic_bptt_pre_reset_candidate_v4.py#L99>)再次执行。原full teacher的state_dict包含persistent weights+buffers。这是**已读历史源码机制**，不是当前实际staged worker的身份回执。
6. [本adapter的producer evidence:52–69](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_frozen_embedded_teacher_reference_v1/embedded_teacher_reference_v1.py#L52-L69>)要求父将实际producer role/key/run、完整A1 SHA、实际staged worker bytes/SHA与上述真实guard语义绑定，再传显式证据。缺件则`producer_teacher_weights_buffers_guard_verified=null`，qualification gate结束；不从历史V4或FINAL的`teacher_unchanged=True`自动补True。该参数是父的已核实证据接口，不是此adapter独立证明历史执行。

actual RSL class+source必须同时匹配原mean绑定和重新inspect到的实际teacher类源码：`rsl_rl.models.mlp_model.MLPModel`、10334B、SHA256 `6219ebb3ed4df036dae7ff1c30d0fbb169eaaa659e44a659dd757a292124476b`。来源是[405所选CPU source:34–48](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_a1_frozen_eval_integration_v2/a1_frozen_eval_runtime_v2.py#L34-L48>)；此source选择不是native测量。

## 3. 推理API与双来源hash

```python
# mean由原cache.build_mean_policy(device,num_envs=80)严格构造一次，尚未调用act。
reference = EmbeddedTeacherMeanReference(
    mean, tensor_dict_cls=TensorDict, producer_final=actual_attested_A1_FINAL,
    expected_rsl_source=approved_RSL_source,
    producer_freeze_evidence=parent_verified_actual_staged_producer_guard)
caller = EmbeddedTeacherReferenceCaller(
    reference, boundary=OriginalEpisodeBoundary(torch, reference.device))
action = caller(original_TensorDict, stochastic_output=False)
# 原 env.step(action) 一次；其后恰好一次：
caller.observe_transition(original_terminated, original_truncated)
```

输入直接是原 noisy/delayed policy35；没有重算观测、真值gravity替换、去噪、DR/critic/UID输入、history切片或RNG恢复。teacher本来是当前观测的MLP，不需要历史；参考不编造历史或以全零xi恢复。仍保持[原 first/previous true term|trunc boundary:284–305](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_a1_frozen_eval_integration_v2/a1_frozen_eval_runtime_v2.py#L284-L305>)：首步all fresh，每步后只吃真实term、trunc的OR，缺一次真实step即结束，不能凭上下文推mask。

receipt严格区分：

- `source_A1_SHA/source_A1_bytes/source_cache`：实际own完整A1 checkpoint的字节来源；cache读/hash/decode各1。
- `original_bootstrap_teacher.source_SHA/source_bytes/source_path`：原bootstrap teacher PT的producer provenance，**不是重新打开该PT后得到的独立对比**；mother opens=0。
- `full_teacher_state_manifest`：实际live teacher与缓存`pi['teacher.*']`的全state键、shape、dtype、parameter/buffer种类；constructor和receipt全值比较。
- source producer训练counts若外层保留，应明确标为`source_producer_counts`，而reference本轮`optimizer_updates=0`。不切片或重置旧counts冒作reference训练。
- `policy_variant=ORIGINAL_EMBEDDED_TEACHER_MEAN_FROM_FULL_A1_V1`、`purpose=FROZEN_ORIGINAL_EMBEDDED_TEACHER_REFERENCE_N80_V1`，不是`A1_RAW35_FRESH/RESUME`候选行为。

同一cache指本reference实例直接共享其尚未消费的mean/cache。跨两个独立worker进程各自own-A1 single-read cache是两个各一次的读，不能合计成只读一次；母PT仍0次。旧helper每cache仅build一个fresh mean，本件没有解锁或复制该约束，也不把一个已执行candidate的mean中途换成reference。

## 4. 本地测试、未来真实CPU fixture与unknown

最终42项stdlib假对象测试覆盖：直接raw35身份/clip、candidate/residual不执行、全teacher keys/shape/value缺口、norm/std/root/对象篡改、原guard继续调用、输入/动作NaN、首步mask/真实tertrunc/漏step、producer/bootstrap/RSL来源缺口、candidate variant、bool控制数和terminal来源混用等。

首轮39项有1个**假Tensor.clamp夹NaN错误**：Python min/max把NaN吞成边界，导致`test_bad_action_nan`没抛ValueError；修正仅新fake的NaN传播后39全PASS。之后加terminal actual RSL PIN/producer证据/bool boundary三项并硬化新semantic函数，42全PASS。首轮失败回执、39通过回执和最终42通过回执均保留于本目录；无旧源改动。

未来父端真实CPU命令（当前未执行）：

```bash
# PYTHONPATH中保留原已封helper/core/bridge/vendor和实际Torch/RSL/TensorDict。
python -B remote_cpu_embedded_teacher_synthetic_v1.py \
  --new-output NEW_UNUSED_OWN_SYNTHETIC_CPU_ROOT
```

fixture复用[旧真实软件fixture构造方式:13–46](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_eval_a1_raw35_v1/remote_cpu_synthetic_check_v1.py#L13-L46>)，但只写、读自己本次新造full root；不读取旧PT。4×N80步比较原RSL software teacher mean与本reference，candidate residual刻意非零用于排除误走candidate；检查全局CPU RNG不变、own cache one read/hash/decode、mother0，真实persistent buffer与std的负向变更必被检测。任何真实source/norm/std不符即保留失败，不猜类、不切换actor。即使CPU通过，也只是software数学/冻结证明，不是native技能/收益证明。

## 5. 下一NEW reference native入口的最小差异清单（本件不落地worker）

| 层 | 下一新版本必须改的最小项 | 必须原样保留 |
|---|---|---|
| plan/parent | NEW group purpose与每member的reference policy_variant；仍显式E3/W35选择和其余deferred；stage新adapter精确bytes/SHA；由当前已修复版本继承**完整实际依赖闭包** | 不改405当前14映射重跑；不复用旧缺resume contracts的V1；原privateGPU-EX/globalfinite-EX/admission/deadline/actualwait/account/close |
| checkpoint adapter `.actor` | 原strict full-cache→fresh mean后，构造本reference和caller；不创建第二MLP，不走`mean.act`；actual attested FINAL/producer guard/RSL PIN显式传入 | own full A1 read/hash/decode一次、整根CPU/源counts原样、old mother PT opens0 |
| checkpoint adapter `.check_actor` / holder | 明确允许当前caller或其`reference.pi`（即public teacher），不是候选whole wrapper；守卫仍检查底层完整`reference.mean.pi`与cache | 整根和全部candidate teacher+residual的原snapshot/assert frozen守卫；不可删guard以方便接口 |
| checkpoint adapter `.receipt` | **必须新写**policy_family/reference variant/purpose，暴露独立A1 SHA与bootstrap teacher SHA、reference receipt/parent producer evidence；原core的`.receipt`访问`caller.mean.source_bindings`且硬写candidate family，不可原样继承造成假标 | source-cache outer `source_SHA`仍是own A1 hash，原producer身份与counts保留且标来源；实际执行RSLsource另列 |
| worker/task validator | 首action前强制reference purpose，raw35当前输入；每control后原真实term/trunc进同一boundary；保存new reference receipt/actor family，失败走原关闭，不candidate fallback | E3原160/W35原1600 controls、原N80/seed/physics/DR/noisy-delay35、原observer/grader/接受阈值 |
| waited semantic/FINAL | 调本`validate_reference_semantics`作为**policy分量**；再独立做原actual p.wait/RC/error/完整FINAL/env/App close等所有原门。禁止把policy gate返回值当qualified native | 原App依赖与关闭行为；error/缺件/null关闭fail-closed；不提前释放锁或做账 |
| row分组/比较 | 每case外部FINAL必须绑定新policy_variant/purpose；W35 rows仍按原standing Boolean/UID/complete谓词消费，本源不改obs/UID/阈值 | 旧consumer不替你证明policy reference身份；同A1 hash不区分candidate/reference，需外层case/variant/group/semantic先绑定，再调用原single-pass grader |

这里交付的是可调用的**policy adapter + API + CPU fixture**，不是已经实现/执行的native parent。下一入口至少需要加入该adapter的新source映射，并为有变化的runtime/parent/worker建立新版本PIN和完整dependency index；精确映射总数应来自那一版实际闭包，不能从旧“14”硬推数量。保留本次405的独立工作与其封件不变。

## 6. 怎样才可以谈效果

candidate和teacher-reference各用独立fresh N80 env与相同计划pose/reset版本、seed、physics/DR/noisy-delay35/原技能时钟。相同seed不证明不同策略造成reset后仍有相同DR流或UID；需保存实际初态、source/pose/cache/protocol、accepted UID/standing分组、完整原分母和实际wait/close证据。E3仍按原74 rescue recipe、normal6隔离；W35 moving/standing原分组不混；E0/S50原binary缺口仍null。

`validate_reference_semantics`只给policy分量true，`qualified_reference_execution`、`actual_paired_protocol_UID_match`、`independent_original_mother_PT_equivalence`、`relative_improvement`、`skill_pass_rate`仍显式null。CPU误差0、冻结合法、pose修正、低MAE或无跌倒都不自动等价原技能提升。本轮所有实际reference/grading/paired结果保持unknown。
