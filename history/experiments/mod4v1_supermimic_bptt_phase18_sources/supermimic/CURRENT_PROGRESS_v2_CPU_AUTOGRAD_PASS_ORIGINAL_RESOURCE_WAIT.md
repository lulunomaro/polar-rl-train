# Round6：CPU真实autograd软件检查通过；原authority仍等锁；native BPTT尚为0

2026-11-02 18:45更新，goal-1c14ef7d-c888-4287-83bf-c008d54545fb revision8/round6 active armed/max48（后续控制面revision用get_goal）。目标未达，H1冻结，八条非H1每条>=3000真实policy BPTT + 自身原技能最终>=90%不变。完整源/协议见 CURRENT_PROGRESS_v1_SOURCES_STAGED_ORIGINAL_RESOURCE_WAIT.md。

## 当前实证，而非旧叙述

- `reports/REPAIRED_OWNER_ACTUAL_STATE_ROUND6_ONCE.json` 实际remote epoch1793616298.139（18:44:58），精确原parent **1475630 creation1793614676.22** 仍sleeping、cmdline指向既有SuperMimic root；OWNER_CURRENT/EXIT/ERROR均无，八条GO全部无。原1800秒preGO wait Errno11，partial locks0/PT_SDK_GO_Cwrites=False。**所有native专家BPTT仍0**；没有把未发布计数当已训练。
- 实际原canonical active仍 `Linux_LQR_MPC_DEPTH_STUDENT389_1793612814735279864` parent1474033，remaining351927.3099360466；GPU0free24203MiB/util0，GPU1free19653MiB/util14/compute1474057使用4542MiB。原项目kernel锁模式完整保存在同报告，未信号/清锁/改账/抢GPU0。
- 旧host观察器在GUI重启后消失：18:44:55检查local Python processes无collect_actual_supermimic脚本；旧pointer最后18:30:50。仅在确认无进程之后恢复新唯一observer **pwsh-0628d778d2fa4b85**，还是原 `collect_actual_supermimic_run_metadata_once.py`，新时间戳目录/当前pointer、未复制worker/父控。观察器36000秒cap，20秒published metadata轮询，原模型/raw/SDK/C操作0；收相关job_output，别重复启动。
- 既有ownparent1800preGO期限约18:47:58；若确切超时0GO则保留其ERROR/EXIT，不重跑原已消费stager/同root OWNER_STARTED。接续应新unused root和原有限父控，在原锁真实释放后或原boundedwait中准入，不提高原gate/预算/权限。

## CPU软件检查真实通过，严格不计入专家训练

已唯一执行 `run_cpu_software_contract_check_once.py`，job **pwsh-971753d1767d49a1** RC0/输出已收。结果 `reports/SYNTHETIC_CPU_SOFTWARE_AUTOGRAD_V1.json`，remote CUDA_VISIBLE_DEVICES=''，真实Torch CPU、FakeEnv/FakeTeacher，无SDK/源checkpoint/GPU/C/GO。

- pi attempts3，actual pi optimizer3，verified BPTT3，unverified0；WM20/aux20/critic3。
- H3合成 temporal future→a0梯度norm0.017899727448821068；future→s1→a0 WM-path norm0.0038903355598449707；finite=True，paramgrad0.036314308643341064，参数probe变化0.0033210923429578543。
- 合成teacher state未变、CUDA未initialize；**actual native expert BPTT_updates=0**。这验证了软件真实autograd链可运行，不验证真实MOD4学习能力、H16资源、完整保存恢复、任何专家80/90通过率。
- 不热patch已封版 `source_core_review/ctx_reward_learner.py` SHA2603308f1adfe65f576eaf2aa3e0275d8465f110e6edd6e3db38304bf3e72039。

## 测量与归档并行

源专项agent **d9af2e50-3e24-4eb6-8177-72271f9d0ac2** 正在全新 `source_measurement_review_v1` 只读审计E2/W35 root getter、参考/phase、UID/episode cohort并准备只读observer+CPU纯合成test。无remote/SDK/GPU/PT/raw/canonical/locks/GO/Git，不改原接受阈值、moving/standing不混；父代理负责实际native冻结验证。E0/S50 binary accepted谓词仍缺，rate=null，不造proxy。

本阶段所有新SuperMimic源/两个封版审计/缺SCHEDULE失败+preGO修复/资源等待/DR确认/CPU检查/host恢复与本交接，**phase18归档仍pending**。repo feature当前HEAD de21f20380296541e5fd508e87edb27ff0a2483b、clean；18:45只读remote main=1044a69fef42ace2dee82f2dcb229538dc029a9b independently advancing。按repo-lqr的record_experiment+唯一annotated trial+exact-short-dir adapter归档，feature/tag push且远端branch/tag/peeled/currentmain核验；主分支只读。不要为Git再开模型/raw或重复物理任务。

## DR原问题结论沿用

全body质量/惯量一共同per-env density factor[.9,1.1]，腿/连杆包括；不是每杆独立质量随机。COM目前仅chassis xyz±5mm，腿/连杆COM未独立随机；MOD4v1新名义COM不等于随机化覆盖。用户只是确认提问，无擅自DR扩域、无hotpatch既有训练。
