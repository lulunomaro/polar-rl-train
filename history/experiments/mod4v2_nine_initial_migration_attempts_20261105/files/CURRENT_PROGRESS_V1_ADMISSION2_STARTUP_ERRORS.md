# MOD4v2九专家迁移 — Admission2实际启动、尚无PPO

- 用户授权所有9正式旧专家（本轮含H1新分支）迁移至MOD4v2-HW300N60；host86排除。正式源由MODEL_SELECTION/SOURCE_NINE_PLAN锁定，E3=1cd母版/H1=71db，非未晋升Fudan8e；v1母版与Registry不改。
- 工作root `F:/RMPOLAR-RL/mod4v2_expert_normalization_20261105`。每角色原PPO/N20000/24steps，首窗口最多20实际更新；双GPU4090两slot队列，不是9个20k同时挤一张卡。不混normalizer、不从零训练；目标完整learner继承，源旧D0/DR/task/history/queue/RNG全部CPU历史保留而不应用，新V2 sole fresh reset建立物理和科目状态。
- 第一独立purpose root `MOD4V2_NINE_FULL_LEARNER_MIGRATION_20261105_203701_1793882221738932800`：controller1672459/owner1672466。导入原three_slot_common即缺`SCHEDULE_PUBLIC.json`退出，实际outer rc1/wait/reaped，OWNER_STARTED/GO/所有native/learner/final均null。0SDK/0源PT/0PPO，源错误与首次owner源码完整保留。不是0分或训练成功。
- 原common的SCHEDULE仅工作CAPS/GPUS元数据，不是ledger；新Admission2补此依赖，并补GO.max_parent_seconds供原charge_values原样记账。新root `MOD4V2_NINE_FULL_LEARNER_MIGRATION_ADMISSION2_20261105_204602_1793882762331398200` stage295shared nonPT，9完整runtime/lib/assets/staticNPZ不裁剪，原source-index不重写、old run不热改。
- Admission2实际dispatch epoch1793883418.722/controller1672920。原owner通过原双authorityEX/private两GPU_EX/finiteSH/canonical无owner+预算/新GPU资源检查后开始GO；不是仅空闲快照。单canonical和charge_values实际GO→load→save→SDKclose→childwait记账，reserve86412.86069250107、3900/3600/300与1800preGO均不变；没有退款/扩预算/清外国锁或signal。
- 唯一observer job `pwsh-9869bd3f14bc43c9` 正在读取本run白名单JSON，不读权重/raw/canonical。末次snapshot1793883454.607：E0/C878/W35/E2/E3已GO后在旧AppLauncher路径环境缺键失败，parent实际rc1/wait/semantic=false；PT前、native0未完成、无learner或实际PPO。E1后续3角色由于同family启动失败被原owner阻止未改源重放。H1独立启动尚在观察，未写native/learner/final，不能当成功。
- 实际错误：E0/E2/E3的`MOD4V1_<role>_JOB_ROOT`，E1的`MOD4V1_E1_ACTUAL_JOB_ROOT`/KIT_STORAGE_ROOT，W35的`MOD4_NEW208_JOB_ROOT`。worker child只在独立`worker_mod4v2_expert_migration_v2.py`补源launcher所需新私有路径；A2已部署worker_v1/manifest保持原样，不热改跑中source。必须待所有自己的actual wait/close/account/release后新purpose，不能把失败覆盖成pass。
- 当前没有真实PPO更新，没有新V2专家毕业、没有新Registry。H1最终状态/所有实际close后以observer CLOSED为准；新原scope80评测worker仅在准备，不与跑中的训练抢finiteEX。
- owner原生成器的两次纯本地anchor/换行失败和修复源全部保留；实际owner的gpu/account/environment函数原样，ROLES已显式9含H1，source stage不是native proof。后续新SDK原错误继续保留，不加新CPU/封印/逐位农场。
- 本阶段尚待meaningful feature-only annotated Git；旧最新user-review commit e8e159472cae4543282cc9789aa9592dee2bef9f。主分支只读，模型/PT/旧raw不为Git或状态开读。
