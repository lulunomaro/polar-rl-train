# R62 V2当前接续：流程两处静态反例已另版修，仍0新物理

完整旧scope/PH7真实归档/AIR002资格见[前接续](<CONTINUATION_R62_PREEXEC.md>)。原goal最近实读revision9/round6/max12 active/armed；不要重建/resume/complete/blocked。只复用原两agents/<=4PHY CPU/无GPU、SSH、PPO、canonical、专家index、Mnemon写；Python314 -B与3线程变量1不变。所有旧scores/sealed/model保持，整个新候选与R62均PH8pending。

## PH7确已关闭

commit223577994e0f750e0ae062ce9ffee204273c90a2、annotated tag trial-20261103-mod4v1-robust-traditional-phase7/object14ec4a088bd7959ef8811feded2c51e77c70f35d，447allA，remoteown/tag/peeled验证。父read[127行postreceipt](<../repo-lqr-robust/history/experiments/mod4v1_robust_traditional_phase8_PENDING/ARCHIVE_PHASE7_RECEIPT.json>)，不重复record/push，也不假称新候选已纳PH7。

## 原V1不是当前launch许可，历史全部保留

model agent对[AIR002 core/entry](<MINIHOP_AIR_PITCH_REF_V1/REPORT.md>)/79源/nominalprotocol/V3所做[原静态PASS review](<R62_AIRREF_ADMISSION_V1/PRE_EXEC_REVIEW.json>)SHA4aabe1f...与MD1a895d...事实保留，但另C-agent[窄审V1 false](<R62_AIRREF_PAIRED_LAUNCH_REVIEW.md>)/[JSON](<R62_AIRREF_PAIRED_LAUNCH_REVIEW.json>)提出实际源码反例：

1. legacy fresh_train_batch_v1.py:29–45在rc0+ERROR或缺result时不以softwarefail停后续波；badJSON还会抛出而缺batch保存。未声称这些坏分支已在当前nominal发生。
2. paired_v1仅查nominalgate+结果SHA，不把actualnominal config和enabled candidate绑定lockedPROTOCOL，且key会删airflag；文件名/计划正确不代actualcfg证明。

父确认并[HOLD](<R62_AIRREF_ADMISSION_V1/PARENT_REVIEW_HOLD.json>)，从未写V1approval/从未launch。model一度先备份原byte后改readyfalse，收到父明确指令后恢复原报告精确bytes，将更正append保存，见[历史收据](<R62_AIRREF_ADMISSION_V1/REVIEW_HISTORY_PRESERVATION_RECEIPT.json>)。不要删原PASS、FALSE或HOLD，也不据原readytrue开旧V3；model原审覆盖nonzero rc但漏rc0 artifact路径已承认，核心审查事实复用。

## 新软件版本（旧源码/物理阈值不动）

- [fresh_train_batch_v2](<fresh_train_batch_v2.py>)SHA30915257ecd9b1e832b23861e5c46f9348976b39bf4f7feecb73cdd6d52328d6：非零rc、ERROR存在、缺result、坏JSON、基本schema/错case等标software_failure，保存row/原artifact解析错误/actual未知不猜步数，停止未来wave；合法robotfail result继续计划。真实subprocess CLI/CPU线程/保存prefix旧path不改。V1与既有scores不动。
- [nominal launcher V4](<launch_manual_profile_train_v4.py>)SHA2c2e0022447152b01a7a91ef2c2aece133739993cd18698b643e6104b6b4e9ce：V3 guarded nestedentry/源锁/review/父approval都保留，改用helper2，并在flat software abort时写全部RM deferred decision后raise。不是放松flatgate。
- [纯metadata binding](<r62_nominal_evidence_v1.py>)SHA89965a3aaa2146f32fd662320f66137a99f741abda25b03b6e055440e49c4ea7：actualflat/RM config逐dict==锁定enabledPROTOCOL、airflag isTrue；actual result/manifest.kind和manifest启用标志、core/entry SHA对锁；原flat/local gate+mainfirstflight仍必需。
- [paired launcher V2](<launch_r62_airref_paired_train_v2.py>)SHA5727c24f624773a5298a25bc371a413c4f78c6a55b9e3801fd24050843366ec7：用helper2/D2sourceindex，父绑定两actualresult与两SOURCE_MANIFEST SHA，再上述validator。原4旧TRAIN4602/05/06/10、2workers/原controlparams/gates保持，不是holdout。V1只读未跑。
- [生成delta](<prepare_r62_launch_delta_v2.py>)仅生成新source AST，不改旧source，0项目/模型/PHY。

父一次[新16fixture](<PARENT_R62_DELTA_PREFLIGHT_V1/RESULT.json>)/[preexec](<PARENT_R62_DELTA_PREFLIGHT_V1/SOURCE_PREEXEC.json>)/[脚本](<preflight_r62_launch_delta_v2.py>)PASS：8个artifact停波/robotfail继续分支，7个nominalcfg/manifest绑定分支、1个actual V4 top-level mock软件abort→全RM递延。全部mock，无子进程/候选/controller/model/PHY/600/FK重跑；fixture私有树的result中的controls1/steps20是明确synthetic，不得当实际试验入case计数。

## 真正当前plan目录V2

[prepare_r62_admission_v2](<prepare_r62_admission_v2.py>)实际只元数据执行一次，生成[R62_AIRREF_ADMISSION_V2/PROTOCOL](<R62_AIRREF_ADMISSION_V2/PROTOCOL.json>)/[source90](<R62_AIRREF_ADMISSION_V2/SOURCE_PREEXEC.json>)/[RESULT](<R62_AIRREF_ADMISSION_V2/RESULT.json>)/[correction](<R62_AIRREF_ADMISSION_V2/CORRECTION_FROM_V1.json>)。继承已审79源+新流程和证据；不重跑81源审查/600/FK/entry/模型。两个名义caseID沿用从未消费的r62_airref002_nominal_flat/rm，原R58cfg只新enable/ID/cohort、全部push/air/obs/landing/DR/driver/oldgate不变。

当前还没有新nominal PHY、不填通过率。model agent正在V2 delta-only审查待D2/PRE_EXEC_REVIEW.json/.md；C agent正在paired_v2 delta-only审查待R62_AIRREF_PAIRED_LAUNCH_REVIEW_V2.json/.md。两个ready只支持条件准入，父仍须read并另写绑定当前protocol/sourceindex/review/launcher的approval。

实际下一命令在这些齐全后才可用：

```powershell
& 'C:\Users\lulu\AppData\Local\Programs\Python\Python314\python.exe' -B '.\launch_manual_profile_train_v4.py' --plan-dir 'R62_AIRREF_ADMISSION_V2' --expected-status PASS_R62_V2_METADATA_ONLY_SOFTWARE_DELTA_TESTED --preparer prepare_r62_admission_v2.py --runner 'MINIHOP_AIR_PITCH_REF_V1/attempt002/run_manual_air_pitch_ref_v1.py' --batch-prefix r62_airref002_nominal_v2 --review 'R62_AIRREF_ADMISSION_V2/PRE_EXEC_REVIEW.json' --parent-approval 'R62_AIRREF_ADMISSION_V2/PARENT_LAUNCH_APPROVAL.json'
```

父在本note时仍无approval/job。名义flat严格过才RM；RM原local+mainfirstflight再加独立pairreview/父approval及actualcfg/manifest绑定才可4TRAIN。若失败保持/递延，不放窗口、舍入guide tick、换seed或重跑baseline。270mm/全地形/可靠停启换向/Power实际driver/unique-send/BSP/HIL/WCET仍未毕业。Goal active。
