# E3复旦方法：4096窗64轮闭环，按用户要求切换20000

## 当前唯一任务
- 用户2026-11-04 19:13:50明确“4096环境太少，一般20000环境”。Goal `goal-c490e4cc-b28b-440e-bde6-30ee956813f0` revision **3** active/armed，max14；只推进E3起身质量，H1/其它专家/Registryv12/1cd母版不变。4096不是后续训练规模。
- 4096 Admission3已通过原 `STOP_AFTER_SAVE.json` 在完整保存边界退出；没有发信号或热改运行源。
- 本文件时点：**20000版本源码接入中，尚未stage/dispatch，也尚无20000新增学习**。只有一个源码子agent，没有自己的native GPU训练进程或活动collector。

## 4096真实闭环及迁移源
[原闭环证据](reports/FDN_W3_20261104_185442/CLOSED_RESULT.json) 与 [20000迁移源资格摘要](FDN_W3_4096_CLOSED_FOR_N20000_SOURCE.json)。
- 真实PPO **64**，policy Adam **1280**，encoder Adam **1280**，已优化transitions **12582912**。
- 实际原生controls **3110**、physics **24880**、feedback **6220**。其中64×48=3072 controls已参与优化；余 **38 controls / 155648 transitions** 为完整保存的未优化pending，不冒作第65轮。
- final/fullsave/原父qualifier均true，inner+outer actual wait完成，原成本结清与leases释放，errors=[]。原GO至原父接收terminal派生 **1363.4290580749512 expert-seconds**，没有另写账、退款或加预算。
- 保存202962459 B，SHA `47937b27407d6994b08f206c386d54eba220fe637a1082a32d9e7d127e5bbe4d`：
```text
/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_E3_FUDAN_SEQ_PPO_LOWRise_W3_MAPPING_ADMISSION_20261104_185407_1793789647408789000/roles/E3/production/fudan_seq_full_u000064_c00003110_s0003.pt
```
- 训练描述中低趴credit仍0，不称起身通过；独立原74+6评测尚未运行。

## 20000接法：不丢learner，也不投影旧环境
- N20000/T48、5epochs×4minibatches，其余原模型、DR、PD、400/k2000/d3、课程和clip6保持。
- 原 [PPO核心](source_fudan_seq_ppo_v1/fudan_seq_ppo.py#L439-L473) 完全不改。`load_state_dict(source['learner'])` 已有一次CPU无alias完整恢复证据；其config不含N，完整恢复网络/STD/LR/两Adam/64累计计数和learner私有generator，不重跑旧fixture。
- 新环境构造、原sole fresh reset、DR/history/queues全部20000 fresh。4096环境状态和38步pending只在CPU源整根保留，stream cut，不切片、不重复、不给新env套旧队列，不称整环境或PhysX位级resume。新环境seed和旧learner config/seed分别处理。
- 源整文件在新实际训练用途只物理读/hash/CPU decode一次，缓存全部CPU root含unknown字段，Mapping/OrderedDict/Tensor/NumPy强guard；不重开1cd祖先。
- 累计learner从64/1280/1280/12582912起；`window_counters`=累计减`learner_continuation.base_counters`。实际新增每update 960000 transitions、两Adam各20；禁止20000乘旧64。新窗final要求新增update/两Adam>0。

## 当前接入文件及下一步
- [原资源父20000新版本](source_original_owner_v3_20k/fudan_original_owner_v1.py)、[新增窗close资格](source_original_owner_v3_20k/fudan_worker_close_contract_v1.py)、[nonPT stager](stage_fudan_nonpt_v3_20k.py) 已生成。[源码结果](FDN_N20000_OWNER_STAGE_SOURCE_RESULT.json)：原gpu/account/environment和1800准入等待段字节完全相同，未运行SDK/模型/原生。首次本地生成因缩进敏感字符串anchor失败、未写source文件；已只修生成器，保留空目录后生成成功，不涉及物理重跑。
- [待执行新purpose组装/stage](prepare_stage_fudan_n20000_w4_once.py)、[待执行dispatch](dispatch_fudan_n20000_w4_original_owner_once.py)、[待执行唯一collector](collect_fudan_n20000_w4_window_once.py)。均未消费，最终worker交付后先窄审再执行。
- 子agent `3b92c2b6-8850-4ad3-857f-77fc0e518590` 正实现 `source_fudan_native_worker_v3_20k`，入口basename沿用 `worker_fudan_sequence_ppo_native_v1.py`，新增 `retained_learner_source_v1.py`。只源码+一次AST，无真实PT/SSH/SDK/GPU/新CPU fixture/Git。不要重复分派或重跑4096。
- 先前N80新增父qualifier已定稿为 [stdlib文件](source_fudan_frozen_parent_v1/fudan_eval_parent_wait_contract_v1.py)，386行/24469B/SHA ad2957c7bec72bba6c60a4dbcd4848d1a3db96b56b3d521fd321ca0893b13bda，仅AST、未执行。N80源仍未stage，旧4k provenance还需以后最小适配，当前别为它延迟20000。

## 原约束与Git
原canonical唯一writer/charge_values、authority双EX/private GPU EX/finite训练SH与评测EX、reserve86412.86069250107、3900/3600/300窗口/1800preGO全部保留。没有自己的活动GPU collector；旧 `pwsh-d1904ce6e51c48fb`已完成且输出已收取。
最新已远端核验feature commit `9e11cc7039bbc4a027f022193d09e02dad825dd3`，annotated trial `trial-20261104-e3-fudan-sequence-lowrise-native-w1-fix-w2-admission`。其后W2 timeout、原资源release、W3真实64轮闭环、N80源和用户20000切换/新源码待下一有意义阶段合并归档。main只读，不为Git打开模型/旧raw，不重复已消费archive/once任务。
