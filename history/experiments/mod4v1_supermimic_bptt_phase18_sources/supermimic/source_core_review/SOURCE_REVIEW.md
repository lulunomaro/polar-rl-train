# SuperMimic vendor / bridge / frozen actor 源码审计

## 结论

1. 既有 vendor 的 policy_update 是通过**学习到的状态 WM**时间展开的真实 policy BPTT，不是可微 PhysX，也不是 PPO。H 个 imagined transitions 最后合并一次 actor loss，通常只有一次 pi optimizer step，H 不乘入真实更新计数。
2. 原 vendor 没有 reward head。旧 LQR/H1 analytic reward 不等于八条原 skill 的任务奖励；此分支已提供独立扩展，监督实际原环境 r/done，并展开 next-context。
3. 原 full checkpoint 能恢复模型/critic/三个 optimizers 与主要计数，但缺 replay/RNG/observation history/环境fullstate等，不等于可持续 exact rollout resume。
4. 新核心与接口已交付；本机只有 stdlib/AST/计数协议测试，Torch module spec 缺失，所以**runtime gradient 与真实 skill 验收尚未执行**。无训练开始、GPU占用或技能达到率声明。

## 源码证据与准确插入点

以下副本均来自本地 Python 源码，SHA/字节与原路径在[验证报告](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_core_review/VALIDATION.json>)中；原文件未修改。

| 证据 | 已确认的事实 |
|---|---|
| [learner:273–300](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_core_review/evidence/learner.py#L273-L300>) | pi→WM.step→next obs→shifted history→next goal；原 context 固定，reward/soft_term 不收context。这里需要 next-xi 更新、ctx-aware goal 与学习 reward/terminal。 |
| [learner:311–365](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_core_review/evidence/learner.py#L311-L365>) | collect 实际环境 transition/r 入 replay；WM 监督仅 state error，没有 reward fitting。新 collect/aux_update 在这个边界接入。 |
| [learner:386–457](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_core_review/evidence/learner.py#L386-L457>) | H 次 unroll，不 detach imagined state；冻结 WM/critic 权重而非输入梯度；survival、discount与reward形成loss；finite grad_norm 才实际 opt_pi.step。 |
| [learner:462–528](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_core_review/evidence/learner.py#L462-L528>) | critic 用 detached imagined targets，lambda return；其多次 optimizer step 不计 actor BPTT。 |
| [learner:537–582](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_core_review/evidence/learner.py#L537-L582>) | 原 save/load 的实际字段。full含critic和三个optimizer，inference numbered快照不含它们；load 不验证cfg一致，也无 replay/RNG restore。 |
| [learner:621–668](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_core_review/evidence/learner.py#L621-L668>) | iteration 里先采样，再 wm_batches 次WM更新，再至多一次policy_update；wm_only_iters 阶段没有policy更新；采样 fractional accumulator 是局部变量。 |
| [replay:8–24](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_core_review/evidence/replay.py#L8-L24>) | r 已存，但原replay只有done，没有xi1/term/trunc。 |
| [replay:61–102](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_core_review/evidence/replay.py#L61-L102>) | sample_windows 不返回r；mask包含terminal当步、排除之后；sample_starts 用 ep_step 和 replay age 边界补齐history。 |
| [networks:87–163](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_core_review/evidence/networks.py#L87-L163>) | WM输出12+2J个局部state increments；没有reward、done、context预测头。 |
| [networks:194–222](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_core_review/evidence/networks.py#L194-L222>) | stateless goal encoder: z=tanh(enc(goal_norm(goal)))；decoder吃z和normalized history。没有RNN hidden-state；hist最后帧最新。 |
| [networks:73–84](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_core_review/evidence/networks.py#L73-L84>) | 此版为bf16 autocast，不是GradScaler。因此skip点是有限梯度判断，仍应以实际optimizer hook为真值。 |
| [geometry:151–183](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_core_review/evidence/geometry.py#L151-L183>) | packed state为13+2J且quaternion wxyz；invariant_features同为13+2J维。 |
| [frozen_e0:118–124](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_core_review/evidence/frozen_e0.py#L118-L124>) | E0 frozen权重保留obs输入导数，正确；不要在teacher.forward加detach/no_grad。 |
| [frozen_e0:149–209](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_core_review/evidence/frozen_e0.py#L149-L209>) | 旧wrapper从history末尾35维取E0输入、residual走vendor normalizers；该tail假设不是generic契约，新wrapper改为显式offset。 |
| [train_supermimic:58–78](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_core_review/evidence/train_supermimic.py#L58-L78>) | 原policy_updates为method返回次数；finite-gradient被跳过也会加1，不能用作>=3000成功step凭据。 |
| [isaac_bridge:49–68](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_core_review/evidence/isaac_bridge.py#L49-L68>) | 旧bridge有terminal physical capture，随后用LQR MDP重算reward，丢弃env reward；还含270mm特定cross/success逻辑。只可借terminal设计，不复用奖励/技能逻辑。 |
| [step_env:16–26](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_core_review/evidence/step_env.py#L16-L26>) | 旧环境把原reward替换为alive，并改270mm障碍、reset/commands；不是当前八原任务工厂。 |
| [lqr_reference_mdp:8–46](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_core_review/evidence/lqr_reference_mdp.py#L8-L46>) | 旧J30/A6/D40/obs108/reference73及固定轨迹reward、obs35解析都带任务假设，不作为当前generic目标。 |

## actor35 / action / history / latent

旧E0 source的raw35依次是cmd3、height1、angvel3、gravity3、legq4、wheelpos零槽2、legqd4、wheelqd2、lastaction6、mode7。对应固定SI scales与真实delay/noise；维度相同不保证所有专家context语义同源。父把原环境实际obs35放xi[:35]，优于手工从清洁q/qd重建旧35输入。

- vendor Policy.forward 签名为 `(obs_hist, goal)`；history `[B,hist,obs_dim]` newest last，goal `[B,K*goal_frame_dim]`。
- `Policy.enc/dec/obs_norm/goal_norm/hist` 是wrapper必须转发的接口。最后输出层是 `dec[-1] nn.Linear`，可以精确zero使新分支从teacher开始。
- 冻结参数本身不切断输入梯度；新 pi optimizer 必须仅含student的requires_grad参数；原PPO optimizer不恢复到新residual。
- 如果MDP.obs为 `cat(invariant_features(state),a_prev,xi)`，J30时teacher offset=73+6=79，不是旧tail35假设。D动态由父冻结并记录。
- goal latent为每次forward重算的tanh向量，不是需要逐步保存的recurrent latent；checkpoint恢复enc/dec/RunningNorm与cfg即可复原其结构，实际history仍需保存。

## 新核心的最小差分

[ContextRewardLearner](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_core_review/ctx_reward_learner.py>)以subclass覆盖collect/policy_update/valid-start/checkpoint/load/train，保持vendor的WorldModel、state多步WM loss、geometry、Policy/Critic结构。

1. replay增加xi1/xi1_valid/term/trunc/split_known/stream_cut；同一真实transition的state/reward/done不改源。
2. aux从真实 `(s,s1,a,a_prev,xi,f)` 学r、done、delta-xi；done无terminal actorobs时strict mask context监督。
3. 每个imag step更新state和xi，并用新xi构造obs/history/goal；WM/aux/critic冻结参数保输入梯度。
4. BPTT成功hook + future->a0 + future->s1->a0 WM VJP +非零参数变化；各counter独立保存。
5. full checkpoint保存replay/RNG/obs_hist/auxopt/counters/schedule/environmentpayload；parent无exactfullstate时明确reset-resume并封stream边界。

详细的field形状、父MDP方法、wrapper与保存接口见[接入契约](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_core_review/ADAPTER_INTERFACE.md>)。

## 原 full save 仍缺什么

| 项 | 旧 vendor | 新核心 / 父尚需负责 |
|---|---|---|
| WM/pi及其RunningNorm | 有 | 原样保留；pi包含teacher时也随state_dict保存 |
| critic及其RunningNorm/三optimizer | full时有 | full时保留，新增aux/opt_aux |
| replay/data/ptr/size | 无 | 新核心完整保存 |
| Python/NumPy/CPU/CUDA RNG | 无 | 新核心保存全局；父保存独立generator/private RNG |
| obs_hist | 无 | 新核心保存；reset-resume时有意清空 |
| exact physical/env/bridge/queues/commands | 无 | 父export/import hooks，须包括真实缓存/计时/DR/phase/episode与传感器历史 |
| 累计成功BPTT步 | 无 | 新核心counts与receipt，checkpoint为持久真值 |
| fractional collection / pending controls | 无 | 新核心保存collect_fraction与pending_iteration |
| 原asset/expert/reward/context source身份 | 不充分 | 父加入run/asset/teacher/task fingerprints，不能仅用形状判断 |

本地H1全状态checkpoint源码副本为**0字节**，已保留空文件及hash，不据此推断任何完整环境恢复能力。

## 当前50Hz MOD4v1约束

当前[Registry_v12](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/EXPERT_NORMALIZATION_REGISTRY_v12.json#L13-L36>)给出actor35/critic38/action6、physics=.0025、policy50Hz、feedback100Hz、TGS32/4；资产hash为2c421a8e…，contract为bae3203a…。旧H1脚本有policy100Hz（decimation4），旧mod4源码注释也可保留100Hz字样，不能覆盖当前绑定。新核心显式dt=.02；H16=0.32s、hist10=0.2s，不沿用100Hz下的时间含义。

8条目标不包含H1：E0、W35、E2、E3、E1_SLOPE135_5deg2m、E1_CURB_PROTECTED878、E1_CURB_INDEPENDENT113、E1_SLOPE_INDEPENDENT50。资产、原task/reward/DR/fsm保留；N1024/2048须标fresh constructor，不称20k原fullstate复原，也不挪用旧N80cap。

## 父 runtime preflight 的必要检查（本次未执行）

1. pack shape/state关节顺序、root quaternion用当前projected_gravity校验；不要无证据照抄旧xyzw重排。
2. 逐transition确认s1为pre-reset；done下xi1_valid=False，next stateinfo为reset后独立起点；WM masks包含terminal当步、不跨reset。
3. raw35 real replay与原actorobs逐值一致、无双重噪声/RunningNorm污染；imag35来自明确模型context而非旧H1/LQR清洁近似。
4. teacher权重hash不变；WM/aux/critic权重在pi阶段不变；student有非零变化。检查权重而非残留.grad（WM训练前留下的.grad不代表pi阶段更新）。
5. reward/terminal/context/state holdout误差、rare done校准、多步漂移与survival；head预测误差不是skill成功率。
6. 单步真实policy_update receipt同时具备future action梯度与WM VJP，所有loss/grad/参数有限，逐次hook真计数。
7. 自有新full checkpoint roundtrip校验model/optimizer/normalizers/replay/RNG/counter；无父exact环境fullstate时只声明reset-resume。
8. 每条累计>=3000 verified policy optimizer步骤后，仍按原skill独立真实评测80中间/90最终；WM-only步数、imagination步数、BC和PPO历史不抵扣。
