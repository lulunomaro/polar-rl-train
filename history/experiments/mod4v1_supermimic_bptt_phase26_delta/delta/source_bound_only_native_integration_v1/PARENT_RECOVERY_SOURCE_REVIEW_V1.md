# 独立恢复源审计 V1

**结论：SOURCE_READY；17/17 PIN、5项固定锚点及8项现有 build manifest 全匹配。现有 handoff/quickstart 已完成。未发现已确认硬 bug；source-ready 与 stage/native/qualification 是分开的状态。**

## 1. 本次范围与证据强度
- 技能 catalog 仅 Office/ACL，无本任务匹配；使用 read/glob/grep 与 stdlib-only CLI。只做源码/小 metadata 读取、SHA/AST 检查；未执行项目模块、旧22tests、stager、native、Torch/SDK/GPU/SSH；PT/raw/model stat/open、锁/账本/Git、旧文件修改均为0。只新增本报告和配套 JSON。
- 独立静态检查：17源码全部 AST/PIN PASS；index/stager/runtime 三套别名集合相等；17个 provenance basename 唯一；原14索引的11依赖条目原样保留；共22个 Python AST及6个新JSON解析 PASS。
- [TEST_RESULTS_BOUND_ONLY_NATIVE_FINAL_V1.json](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_native_integration_v1/TEST_RESULTS_BOUND_ONLY_NATIVE_FINAL_V1.json>)：现有22 tests /0 failures /0 errors/PASS，10.689525900001172s；含历史 full-real-stdlib-import/fake/AST 声明。本次没有重跑。[TEST_RESULTS_BOUND_ONLY_NATIVE_STDLIB_V1.json](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_native_integration_v1/TEST_RESULTS_BOUND_ONLY_NATIVE_STDLIB_V1.json>)保留初次1 ERROR；[CPU_SOURCE_TEST_HISTORY_V1.json](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_native_integration_v1/CPU_SOURCE_TEST_HISTORY_V1.json>)解释为 NEW fixture 的 source_audit 查找改成 source_guard_mechanism 后最终PASS。receipt未对完整源码/test清单做密码学绑定，不等同本次动态重测。
- [BUILD_BOUND_ONLY_NATIVE_SOURCE_V1.json](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_native_integration_v1/BUILD_BOUND_ONLY_NATIVE_SOURCE_V1.json>) 8项均匹配；[BOUND_ONLY_NATIVE_SOURCE_HANDOFF_V1.md](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_native_integration_v1/BOUND_ONLY_NATIVE_SOURCE_HANDOFF_V1.md>)、[BOUND_ONLY_NATIVE_FIELDS_CONTRACT_V1.json](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_native_integration_v1/BOUND_ONLY_NATIVE_FIELDS_CONTRACT_V1.json>)均已完成。前子中断不等于源码已坏，也不自动代表封件已完成。

## 2. 关键源码与守卫
- [bound_only_native_helper_v1.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_native_integration_v1/bound_only_native_helper_v1.py#L95>)：原构造器先zero、再strict load整个pi；fresh cache只build一次。保持 `clamp(teacher + .05*tanh(delta), -6, 6)`；训练/BPTT/四优化器均0。界限为相对CLIPPED teacher的逐分量0.05，不是L2界、不是相对旧candidate。
- [bound_only_native_runtime_v1.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_native_integration_v1/bound_only_native_runtime_v1.py#L446>) → [bound_only_native_route_v1.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_native_integration_v1/bound_only_native_route_v1.py#L9>) → [a1_frozen_eval_runtime_v2.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_a1_frozen_eval_integration_v2/a1_frozen_eval_runtime_v2.py>)；canonical独立保留37927B/7a092364cf63e9621481dc0a5554b56a22e4412cf89870c3db9a124864074b2e，无循环。原act/真实35噪声延迟/history10/真实T|Tr、whole ROOT identity/version/CPU/schema/scalar守卫继续继承；不恢复live WM/critic/optim/replay/RNG。
- [stage_bound_only_native_v1.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_native_integration_v1/stage_bound_only_native_v1.py#L358>)：完整AppV6/contracts_v3闭包；metadata validate 对model/budget的stat/lstat/open拦截及词法resolve临时守卫有finally恢复。未来admitted cache仍保留原physical own-path containment、一开/一hash/一CPUdecode；本次0模型访问。
- [producer_bound_probe_guard_v1.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_native_integration_v1/producer_bound_probe_guard_v1.py#L51>)及[worker_supermimic_bptt_app_close_candidate_v5.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_native_v6_runtime_compat/_SOURCE_INPUT/sealed_source/worker_supermimic_bptt_app_close_candidate_v5.py#L70>)：实际producer17704B/7c42986077de62278e33a49f560f22602c9ba4d4e69b058f5f5f8f0893c099c7，bridge13125B/8211964c2ce3dd78fdb9fee6603ee4a4dcfbca6fa9d7df44f20d3ddb7aaead29；全actor.state_dict参数+buffers快照，save/FINAL前torch.equal，eval/requires_grad False。未来从安装TASK/manifest/实际源码重推，不是新GPU trace。
- `collect_action_statistics=False` 默认不变；显式 `--collect-action-statistics` 才打开same-forward scalar stats，可能影响walltime，不新增forward/观测/RNG。helper/route中的 `native_enabled=True` 是选定能力，不是当前actual enabled。

## 3. 真实 stager CLI（仅抄录，未执行）
```sh
python -S -B SOURCE_REVIEW/stage_bound_only_native_v1.py \
  --original-group-root ORIGINAL_GROUP \
  --original-group-plan ORIGINAL_GROUP/GROUP_PLAN.json \
  --source-dir SOURCE_FLAT \
  --source-index SOURCE_FLAT/BOUND_ONLY_NATIVE_STAGE_INDEX_V1.json \
  --native-root CLOSED_A1_ADMISSION2_ROOT \
  --new-root UNUSED_NEW_BOUND_GROUP \
  --group-id NEW_BOUND_GROUP_ID --gpu-uuid GPU_UUID \
  --preflight-only
```
- 参数定义见[stage_bound_only_native_v1.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_native_integration_v1/stage_bound_only_native_v1.py#L509>)。`--original-group-plan` 同义名 `--original-plan/--plan`，省略则用 ORIGINAL_GROUP/GROUP_PLAN.json；`--preflight-only` 与 `--stage` 必选其一。统计flag可省略，默认False。
- SOURCE_FLAT须放17个provenance basename，而不是installed alias：AppV6→v5 alias，new formal→worker_sources/parent/worker_five_original_n80.py。新root必须未用、无重叠；失败root消耗，不同root重试，不清理覆盖。
- 原native gate须有原Admission2身份、八角色（无H1）、GO/terminal和PARENT_WAITED_ACTUAL一致、allwait/cost-settled/leases释放/noerrors、选中E3/W35成功producer FINAL及counter/source provenance；checkpoint path/bytes/SHA只当metadata。
- 成功receipt准确名 `STAGE_COMPLETE_BOUND_ONLY_NATIVE_V1.json`，kind=`SOURCE_BOUND_ONLY_NATIVE_STAGE_COMPLETE_NOT_DISPATCH_V1`；`staged=True, actual_native_enabled=False, parent_launches=0, model_stat_hash_open_decode=0, C_lock_SDK_GPU_GO_operations=0, resource_admission=None, actual_frozen_evaluation=None`。失败为 `STAGE_ERROR_BOUND_ONLY_NATIVE_V1.json`。

## 4. 父入口、实际wait与资格边界
- [single_gpu_e3_w35_bound_only_parent_v1.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_native_integration_v1/single_gpu_e3_w35_bound_only_parent_v1.py#L79>)：`bound_probe_parent_entry()`先原main/finally，后写 `BOUND_PROBE_GROUP_CLOSED_SOURCE_GRADE_V1.json`；source-grade失败exit1。原privateGPU EX+finiteEX、只读C predicates/原预算、own-identity cleanup、实际wait后release都保留。
- [bound_only_native_runtime_v1.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_native_integration_v1/bound_only_native_runtime_v1.py#L549>)要求：ACTUAL_GROUP_ADMISSION的same group、original_private_GPU_EX_held/ original_global_finite_EX_held=True、canonical_writes=0、canonical_owner_at_read=None；PARENT_EXIT_SCOPE all_own_children_waited及两EX released=True、errors=[]、canonical_writes=0；exact E3/W35 child_waits/terminal，actual_waited=True、typed returncode=0、PID一致。
- aggregate FINAL须requested complete+ready-before-start+原八角色；每case FINAL与terminal data相等；实际p.wait后重算semantic，要求原errors缺席、own family/whole cache frozen/一开一hash一decode/mother0/真实TTr计数/zero updates、env.close及原App returned或绑定实际FINAL SHA的fast-close intent。intent自身不冒充外层wait。
- source grade明确 `external_executing_parent_actual_wait_required=True`, `external_parent_wait_proof_created_here=False`, `qualified_bound_probe_execution=None`。外层执行父仍须亲自对本parent PID实际wait并记录typed rc0、actual_waited、own group identity与closed source grade。V1不生成自身外层wait证明。

## 5. 不变条件与readiness落点
- E3/W35独立ZERO_UPDATE用途；N80、E3 160/W35 1600、seed20260928、fresh fullDR、physics .0025/control .02/100Hz、8 callbacks+2 feedback、TGS32/4、closure .01m/mimic .01rad、gas400/stiffness2000/damping3、接受阈值/原预算锁均不变。原八角色catalog保留，六角色deferred，H1冻结排除。
- 仅按用户既有metadata记录：mother teacher E3 0/74、W35 moving19/63 stand26/26；旧candidate 0/74、moving10/69 stand16/17，normal6 physical-term6/6。保持mother；截断效果不叫训练收益。独立cohort/单seed不产生matched UID/DR trace或收益证明。
- 当前 `source_native_capable=True; actual_staged=False; actual_native_enabled=False; qualified_bound_probe_execution=None`。optional CPU fixture只含未来synthetic N80/4 controls/独立公式/真实TTr/RNG/root等检查，不在17映射、本次未运行；不是native/skill证据。
- 本轮没有已确认硬bug或hotpatch建议；后续若发现硬bug，给精确行并另起NEW版本，旧/封件V1维持不动。

## 6. 实际 bytes / SHA256 inventory（17源码 + index + stager + optional CPU = 20）

| # | 来源文件 | staged alias / 类别 | bytes | SHA256 |
|---:|---|---|---:|---|
| 1 | [e1_parallel_worker_a1_frozen_candidate_v2.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_a1_frozen_eval_integration_v2/e1_parallel_worker_a1_frozen_candidate_v2.py>) | `worker_sources/e1/e1_parallel_worker_safe.py` | 16164 | `0e85c472e4e3fe60a434e7b7c9844fc81356a5f66cce7013f4c105a44ac05ba8` |
| 2 | [e1_fresh_bridge_a1_frozen_candidate_v2.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_a1_frozen_eval_integration_v2/e1_fresh_bridge_a1_frozen_candidate_v2.py>) | `worker_sources/e1/e1_fresh_runtime_bridge.py` | 3451 | `be442b02a606be9bd17a3ae996e52978057a778d8e593df64fc8c5b0ea9dde8b` |
| 3 | [a1_frozen_eval_runtime_v2.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_a1_frozen_eval_integration_v2/a1_frozen_eval_runtime_v2.py>) | `a1_frozen_eval_runtime_v2.py` | 37927 | `7a092364cf63e9621481dc0a5554b56a22e4412cf89870c3db9a124864074b2e` |
| 4 | [frozen_a1_raw35_v1.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_eval_a1_raw35_v1/frozen_a1_raw35_v1.py>) | `frozen_a1_raw35_v1.py` | 19226 | `1ea4bcfa1081d63d0da2136fedf8c9fafa508d7bb2155095352da496327e4a21` |
| 5 | [pose_cache_runtime_adapter_v4.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_native_v6_runtime_compat/pose_cache_runtime_adapter_v4.py>) | `pose_cache_runtime_adapter_v3.py` | 18161 | `7357827a72a03f6300ce3f7c6da3ad2a05a551480a1aad04a91dbaac4a497e2f` |
| 6 | [app_close_semantics_v6.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_app_close_runtime_compat_v6/app_close_semantics_v6.py>) | `app_close_semantics_v5.py` | 27769 | `3d2d75196fb98fdb45c80a79b5b8bb69873e7c0c2c0b0f6f6610eb11a8c63c39` |
| 7 | [native_supermimic_bridge.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_native_v6_runtime_compat/_SOURCE_INPUT/sealed_source/native_supermimic_bridge.py>) | `native_supermimic_bridge.py` | 13125 | `8211964c2ce3dd78fdb9fee6603ee4a4dcfbca6fa9d7df44f20d3ddb7aaead29` |
| 8 | [networks.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_core_review/evidence/networks.py>) | `supermimic_vendor_v2/networks.py` | 8609 | `c7829e6a1bb9166d724a931858b76424439f371669dfb4bb534b9e76c5c74706` |
| 9 | [geometry.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_core_review/evidence/geometry.py>) | `supermimic_vendor_v2/geometry.py` | 6960 | `89ac3b9470fd6f041fd418365283355a07ad96c4bf38740cf3c5d2d98acb7787` |
| 10 | [contract.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_core_review/evidence/contract.py>) | `supermimic_vendor_v2/contract.py` | 2517 | `d756f2a102a81b2f16295dad66f46e9783b42a3f67e7416360fcf136c2ff06ce` |
| 11 | [single_gpu_e3_w35_bound_only_parent_v1.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_native_integration_v1/single_gpu_e3_w35_bound_only_parent_v1.py>) | `single_gpu_e3_w35_bound_only_parent_v1.py` | 9348 | `63eaa4b04ee085a1efbbbc72a4d0756036faa7928af01e19713e6871925d0e80` |
| 12 | [bound_only_native_runtime_v1.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_native_integration_v1/bound_only_native_runtime_v1.py>) | `bound_only_native_runtime_v1.py` | 40234 | `e6b64b0757c97f02a9df936fe6d8edfd9e99914fb3d372c9021eb301d700d30f` |
| 13 | [worker_formal_bound_only_v1.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_native_integration_v1/worker_formal_bound_only_v1.py>) | `worker_sources/parent/worker_five_original_n80.py` | 15267 | `d558cb899115f0082a0671a265cd9ea179e3cc91608d8b412a39b73abf1c2642` |
| 14 | [resume_runtime_contracts_v3.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_resume_runtime_v2/resume_runtime_contracts_v3.py>) | `resume_runtime_contracts_v3.py` | 22337 | `dc4bc67193457a4fb72b125d23fa482cd3d686363bd1a93eb07268f4e4e26cb7` |
| 15 | [bound_only_native_helper_v1.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_native_integration_v1/bound_only_native_helper_v1.py>) | `bound_only_native_helper_v1.py` | 19233 | `3375168c0d11fe349c8428cb81bb343a90d1520feb90c1e034f829f98ef4a0c9` |
| 16 | [producer_bound_probe_guard_v1.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_native_integration_v1/producer_bound_probe_guard_v1.py>) | `producer_bound_probe_guard_v1.py` | 9754 | `a840746e22eab3a55781069521b77ba92f67427baae1001b117d732453c76f1e` |
| 17 | [bound_only_native_route_v1.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_native_integration_v1/bound_only_native_route_v1.py>) | `bound_only_native_route_v1.py` | 3378 | `0f241475909a7c84e325416f2f6530f7ad912526ff41d7779f5ac0bcb2c87458` |
| 18 | [BOUND_ONLY_NATIVE_STAGE_INDEX_V1.json](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_native_integration_v1/BOUND_ONLY_NATIVE_STAGE_INDEX_V1.json>) | `SOURCE_INDEX` | 6085 | `d0519c7a351513a61f4c0c5c055b74bc7df41ac0300ce964207dd9508254f19a` |
| 19 | [stage_bound_only_native_v1.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_native_integration_v1/stage_bound_only_native_v1.py>) | `STAGER_NOT_EXECUTED` | 34960 | `74f52b47c54e742f2a60a8459b7fa013dd52793b2adc970d02149474eb21eb40` |
| 20 | [remote_cpu_bound_only_native_synthetic_v1.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_native_integration_v1/remote_cpu_bound_only_native_synthetic_v1.py>) | `OPTIONAL_CPU_FIXTURE_NOT_EXECUTED` | 10731 | `a22d8b471f2cab46addc1592875b557e5c4f225a76dd386efe9f8f2086c9dff0` |

配套JSON另含9项support/evidence实际hash、完整CLI/gate字段、receipt原文与静态检查计数。现有文件hash在报告创建后再核对不变。
