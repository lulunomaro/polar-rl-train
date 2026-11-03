# V2 短追加｜base view 与 active A1 RAW35 分层

**仅追加澄清，V1 四件及其原 SHA 完全保留；无模型读取/执行/诊断。**

- **Base 事实：** [bridge:51–63](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_runtime/native_supermimic_bridge.py#L51-L63>) 的 `OriginalTaskMdp.obs` 确实拼接 `invariant_features(state), previous_action, context`；这只是 base 实现，不等于当前 A1 actor 的最终观测。
- **Active 覆盖层：** 父任务已确认当前 qualified A1 绑定 worker SHA `7c42986077de62278e33a49f560f22602c9ba4d4e69b058f5f5f8f0893c099c7`。本地同 SHA 的 [sealed worker:66–84](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_a1_native_v5/_SOURCE_INPUT/sealed_source/worker_supermimic_bptt_app_close_candidate_v5.py#L66-L84>) 在 `actor_view==RAW35_ACTOR_VIEW` 分支把 `bridge.mdp` 替换为 `Raw35ActorMDP(bridge.mdp,transition_projector=None)`，并断言 `obs_dim==35`、`actor_context_offset==0`。
- **实际 actor 入口：** [wrapper:164–200](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_a1_native_v5/_SOURCE_INPUT/sealed_source/command_tracking_torch_candidate_v1.py#L164-L200>) 的 `obs(...)` 严格返回 `context[..., :35]`（即 xi[:35]），忽略物理 state/previous_action 参数；`add_noise` 为 identity，保留原 noisy/delayed raw35，`goal` 用 xi[:3]。因此不据 base.obs 单处推断当前 qualified A1 actor 仍使用 privileged base view。旧 A0 privileged 路线属于历史，和当前 active A1 分开记录；privileged WM/critic 仍可用。
- **未来 reward-only baseline：** 以当前 A1 **RAW35 legacy** 路线为基线，保留 wrapper、`transition_projector=None`、actor offset0 及原动作/噪声/验收。只增 V1 所列训练奖励；既不回退 A0/base actor view，也不夹带 actor 接口或 projector 修复这一第二因子。原 plant reward/三路分账及 WM/质量闭环门槛不变。
- **κ 权限/状态澄清：** `κ<=1/3 reward/s` 只是本 review 提出的 **DISABLED 数学标定封套**，不是用户批准值、历史 authority 或已选择实验超参。`enabled:false`、`kappa_NEW:null` 保持；尚未实现或启动候选。

[28/28 stdlib 测试收据](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_e3_signed_upright_reward_review_v1/TEST_RESULTS_V1.json>)保持原件；首轮 quaternion 尺度归一化 1ulp 严格相等 fixture fail 及修正摘要仍保存在 [V1 manifest](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_e3_signed_upright_reward_review_v1/SOURCE_REFS_MANIFEST_V1.json>)。本追加是 source 分层，不增加测试、native executor 或 WM 诊断；精确源/保留件/追加件 bytes/SHA 见 [V2 refs](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_e3_signed_upright_reward_review_v1/A1_BASE_VIEW_LAYERING_REFS_V2.json>)。
