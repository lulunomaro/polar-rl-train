# 四个E1子worker：单GPU并行N80 fresh-fullDR技能screen（SOURCE_ONLY）

**尚未实际执行；没有SDK/GPU/PT/预算/GO操作。** 父进程负责9成员总调度、单GPU原privateEX+globalfiniteEX、actualwait/RC0与全9结果。这里仅4个E1子worker。

## 稳定接口
`python -B WORKER --task <case/task.json> --group-root <groupRoot>`

| role | worker | N80窗口 | 解释 |
|---|---|---|---|
|CURB_PROTECTED878|[worker_curb878_n80.py](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V1/worker_curb878_n80.py>)|750control /6000physical /1500feedback|ORIGINAL_N80_MANUAL_ROUTE_ENDPOINT_CONTACT_SCOPE|
|CURB_INDEPENDENT113|[worker_curb113_n80.py](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V1/worker_curb113_n80.py>)|750control /6000physical /1500feedback|ORIGINAL_N80_MANUAL_ROUTE_ENDPOINT_CONTACT_SCOPE|
|SLOPE135|[worker_slope135_n80.py](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V1/worker_slope135_n80.py>)|750control /6000physical /1500feedback|ORIGINAL_N80_MANUAL_ROUTE_ENDPOINT_CONTACT_SCOPE|
|SLOPE_INDEPENDENT50|[worker_slope50_n80.py](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V1/worker_slope50_n80.py>)|1000control /8000physical /2000feedback|DEFAULT_TRAINING_AXIS_DESCRIPTIVE_SCREEN_NO_ORIGINAL_ACCEPTED_COHORT|

## 目的分域与原条件
- 每个case保留完整typed PT的一次bytes/SHA/decode缓存，全部unknownroot/nested/20k savedDR历史不改不投影；live原A0 actor+learnedSTD strict载入，critic/17Adam/LR/iter前后cache identity，不冒liveoptimizer/full20kDR恢复。旧whole20k nativePASS分立。
- N80全D0–D7由各自原构造器、privatefresh seeds和ONE本次explicitreset生成，2c/bae新constructor nominal保护；D0白名单mass/inertia/material/motorgain，D1-D2噪声bias，D3 100Hz反馈lag，D4独立leg4/wheel2物理lag，D5 k2000，D6原gasdamping，D7 COM/PD不删。API/component-memory审计不是backend独立资格。
- 前三原factory40x40/80独立tile、40+40镜像、27up27down26stand、seed20260928；15s=750×.02、6000×.0025、1500反馈。Curb端点±.275，Slope135端点±1.2，两轮before/after同episode/firstordinary前且meanload>1N；stand不强cross，不增加总体率。
- Slope50只用自身train_independent_owned_axis_v1.build_env AST+原freshbinder、自然commands/RNG20s，描述自己的trainingaxis/fullramp目标family，不借135的80cohort/27+27成绩。
- 原Curb源码明记RSLwrapper额外reset；新A0无reset数据bridge规避第二reset，以此明确是新的N80freshDR cohort，不称旧assignments配对。

## 并行屏障与退出
四子worker不抢privateGPU/finite锁、不检查空卡、不执行nvidia查询。验证父已held且passfd有效（只fstat），CUDA_VISIBLE_DEVICES与groupUUID匹配，cuda:0。每case唯一Kit/warp缓存与-B。
scene/actor/freshDR准备好写WORKER_SCENE_READY.json，此时0physics/actorforward；等GROUP_EVAL_START.json最长900s，wait无step/actor/RNG。任何WORKER_ERROR由父取消整个自己group scope，不单case重试。FINAL/PRE_CLOSE先写，原Appclose可能exit，actualparentwaitRC0才为最终退出证据。

## 本地验证
4来源整cache/unknownroot不可变/禁止20khistory暴露/组fd与GPU/abort与900s/零callbarrier/双轮端点跨reset禁止拼接等60项纯stdlib合成MOCK通过；不是Torch/SDK或物理PASS。3个原80factory前缀的授权替换逆变换AST完全一致；S50只抽自身build_env AST、不执行entrymain/第二App/restore helper。
模型metadata和完整源码依赖详见机器索引，父fresh实际资源/源SDK准入后才可统一一次group执行。

## 主要文件
- [ROLE_CONTRACTS.json](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V1/ROLE_CONTRACTS.json>)
- [FOUR_E1_WORKER_PARENT_INTERFACE_SOURCE_V1.json](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V1/FOUR_E1_WORKER_PARENT_INTERFACE_SOURCE_V1.json>)
- [FULL_FRESH_N80_D0_D7_SOURCE_DEPENDENCY_GRAPH_V1.json](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V1/FULL_FRESH_N80_D0_D7_SOURCE_DEPENDENCY_GRAPH_V1.json>)
- [FOUR_E1_ORIGINAL_FACTORY_AST_DIFF_PROOF_V1.json](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V1/FOUR_E1_ORIGINAL_FACTORY_AST_DIFF_PROOF_V1.json>)
- [FOUR_E1_SOURCE_ONLY_MOCK_PROOF_V1.json](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V1/FOUR_E1_SOURCE_ONLY_MOCK_PROOF_V1.json>)
- [emit_four_e1_descriptors_sourceonly.py](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V1/emit_four_e1_descriptors_sourceonly.py>)
