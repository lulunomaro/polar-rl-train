# 接续 R38 — 高频shadow采集已完成，原Goal仍active

上游[CONT_R36](<CONTINUATION_R36.md>)→[CONT_R34](<CONTINUATION_R34.md>)保留全部模型/DR/技能/旧失败/冻结边界。当前cwd F:/RMPOLAR-RL，root本目录；Python3.14 `-B`，BLAS/OMP/MKL1，≤4 CPU physics workers。无GPU/SSH/PPO/canonical/原expertindex操作。最新get_goal仍id`goal-4d4bef80-e614-432d-a8cd-8f385ef2dd7d`、revision7、roundsStarted3/max12、active/armed，没改complete/blocked。当前catalog Office/ACL无机器人匹配，使用文件/Python/现有CLI。

## PH3 已真实commit并atomic ownrefs push

[正式receipt](<../repo-lqr-robust/history/experiments/mod4v1_robust_traditional_phase4_PENDING/ARCHIVE_PHASE3_RECEIPT.json>)已由父read核对：

- commit `fa6838807f4d69d2b8ac52300d74ad40f365d2ed`，parent`02b5ff84...`；branch`mod4v1-lqr-mpc-robust`。
- 新annotated tag`trial-20261102-mod4v1-robust-traditional-phase3`，object`163d331cc4dade7bee2e870c7f2da852edec44ab`；remote ownbranch/tag/peeled全部核验同commit，PH1/2 tags保持。
- 原helper SHA b2fd15...未改，仅in-memory argv/narrow-add，不用其--push；显式OWNrefs atomic，无force/main/expert/reset/checkout。
- 2148 expected paths全A/noD/no foreign，stage后/commit前两次blob SHA全核；SOURCE_PREP2143+cover4+record1。[record](<../repo-lqr-robust/history/experiments/20261102-mod4v1-robust-traditional-phase3.json>)、[cover](<../repo-lqr-robust/history/experiments/mod4v1_robust_traditional_phase3/>)。
- cutoff仍R34；3229source entries/2119newtext15.17MB+441PH1/2ref+669rawmetadata(665known/4unknown)，270physical/4R25software/22batch保持。
- main仅pre-record/pre-push/post窗口均`013ee164...`，不说整个capture期全球不变。
- SOURCE_PREP历史“Git waiting”文本不改，新cover说明后续实际commit。push后正式receipt本身写新PH4_PENDING sibling，**不在PH3 commit内，后续PH4需纳入**，避免无限receipt trial。
- 不再record phase3。R35/R36/ASQP/FRONT/新supervisor/IO blocked/FSM/RAW2K等全部PH4pending。

## HOST_ACTIVE_QP_IO_V1 仅blocked证据包，不是可用IO

C child已收尾[README](<SPR_AUDIT/HOST_ACTIVE_QP_IO_V1/README.md>)/[VALIDATION](<SPR_AUDIT/HOST_ACTIVE_QP_IO_V1/VALIDATION.json>)/[INDEX](<SPR_AUDIT/HOST_ACTIVE_QP_IO_V1/INDEX.json>)，77files/54links，INDEX`25eb0a099f8b08849324920a2224da3fe2cfc6753b31ff66a7d86a4772af0b0e`。状态**BLOCKED_NOT_SEALED、TRAIN_integration_allowed=false**，检查此字段，不能因INDEX存在就接入。

- prod/harness exe link0但Created→Deleted，actor UNKNOWN；精确路径/时间窗Defender1116/1117和Application1000/1001无事件命中。后来strtof小probe也缺失，其他小probe存在；**不认定AV、不认定sandbox denial**。
- 已停止同源反复编译/重命名探针、未改防护/排除项。后续外部保留条件/具体归因改善才恢复该组件，不绕删除。
- clock QPC254向量/2514checks0；SDK-only29154checks0主要输入f32bit/合成decoder/独立owned fixture pipe cleanup，不冒solver验证。
- 93×2=186帧全部UNSENT，**0 prod请求**；真正C逐帧/parserfault/stdioearlyabort均NOT RUN。旧626文件/ASQP core/header SHA保持。
- 草稿[SDK](<SPR_AUDIT/HOST_ACTIVE_QP_IO_V1/active_qp_stdio.py>)`ActiveQPLocal.solve(H,f,lo,hi,warm=None,max_pivots=64,tolerance=.002,budget_us=0)`返回JSON valid/status/z/kkt_upper/stats/roundtrip_wall_ns，匹配父callback。**不接R37，不运行draft。**
- sealed ASQP数值核18/18+75stress、531内部earlyabort及旧C3/HOST-P25仍有效；局部IO阻碍不等于整个Goal blocked。

## 父supervisor v2：58/0、0physics

新[supervisor_v2](<C_ACTIVE_MPC_SUPERVISOR_V1/supervisor_v2.py>)在所有valid-C基线路径做最终wall poll，accepted计数与warm延迟到最终通过后提交。解在mux后/return前过期→恢复独立C3 GUARDED，warm/accepted不提交。时间字段改`supervisor_final_poll_elapsed_ns`，不冒后续日志/驱动提交完整WCET。

[attempt003](<C_ACTIVE_MPC_SUPERVISOR_V1/attempts/003/RESULT.json>)58checks/0，0物理，core SHA`309af7b2822fceb78632d4b680823035fce077d4e83811d83322bb9c40812297`；v1与001保持。新[attempt002错误](<C_ACTIVE_MPC_SUPERVISOR_V1/attempts/002/ERROR.txt>)在第34断言：旧测试想generic QP reason，v2最终clock返回更具体caller_clock_fault_at_return，原run没打印实际log值未重建。003仅更新新测试预期，v2源码不再变。整个supervisor仍UNSEALED/无生产C IO/不准TRAIN。

## RAW2K_SHADOW_V1 新信息shadow分支已真正封存

入口[README](<RAW2K_SHADOW_V1/README.md>)、[INDEX](<RAW2K_SHADOW_V1/INDEX.json>)、[SENSOR_ONLY_MANIFEST](<RAW2K_SHADOW_V1/SENSOR_ONLY_MANIFEST.json>)，INDEX SHA`b1ad181cb939a1f40e39b46c6b83bed2d81316f85a73e330ee617ba6cad9c09c`，39smallfile links/12rawmetadata。

目的：落实原[最小2k提案](<INTEGRATED_COM_WINDOW_V1/MINIMUM_2K_CAPTURE_PROPOSAL.md>)，保留R(t)/proper窗口内信息供后续COM恒等式研究，**不是提升旧H4成绩或改变在线控制观测**。

### Producer与噪声/时序

- [publisher](<RAW2K_SHADOW_V1/publisher.py>)producer-private内部保存clean raw，利用原100Hz已经抽出的D1/D2 offset构造每窗所有2k样本共同offset。clean/offset/DR/root/contact等不进入public projection，字段严格allowlist，changed duplicate锁存。
- 同窗差分抵消共同offset，这是额外信息、相关噪声新branch，**非IID2k，不÷sqrt20，不冒旧benchmark等价或实机**。
- 原authoritative mean直接保留；raw重算mean仅roundoff相等，不修改末条伪造bit-identical。
- D3按原返回packet的source epoch选择完整源窗口；先存current源，再选old源；boot instant count1/aperture0重复时原payload SHA/seq不变，不重抽/新旧混拼。
- 每条raw q/qd/wheel-rate在mj_step前复制，随后读同pre-step dynamics stage的gyro/proper。稳态20样本×500us，末条source epoch−500us，各raw通道同时间。
- 原`endpoint_joint_pos4`仍epoch端点，mean qd/gyro仍窗口均值；不能拼成同步端点。COM窗口用raw中已存在的同时间端点。
- 拼连续2k路径时先按source去重，instant boot单列/舍弃；boot与首个full window可能覆盖同物理时间但不同噪声构造，不当独立重复采样。
- 无末尾flush，最后collector窗口尚未发表；发表sample数≠physics总数。

### 派生physics与控制边界

[raw2k bridge](<physics_bridge_raw2k_v1.py>)只插两条只读hook；[AST收据](<RAW2K_SHADOW_V1/BRIDGE_PRECHECK.json>)证明移除hook后apply_torque_request的AST与原v3完全相同，源SHA固定；[grade桥](<physics_bridge_raw2k_grade_v1.py>)仍v4 current freejoint grading。原model/接触/closedchain/PD/D4/gain/signedDC都没改。

[新runner](<run_raw2k_shadow_case_v1.py>)控制器仍只读原100Hz packet，P25+heading2/r.0625/传感器V4；2k只另写sensor_shadow文件。publisher完整性故障会中止新采集case，不宣称全部故障路径或wall开销bit-equivalent。没有C worker依赖，没有root assist。

### 验证与新物理R38

- [mock unit](<RAW2K_SHADOW_V1/attempts/001/RESULT.json>)61/0，0physics；fixture末尾fault_latched=true是故意changed-duplicate注入的预期，不是实际采集故障。
- [真实模型boot准入](<RAW2K_SHADOW_V1/admission001/RESULT.json>)mj_step禁用，0步；schema/mean/finite原控制命令通过。
- [R38 protocol](<batches/r38_raw2k_shadow6/PROTOCOL.json>)先冻结，再新6case：nomstand2s、nomforward6s、TRAIN4211..4214各forward6s。[结果](<batches/r38_raw2k_shadow6/BATCH_RESULT.json>)**6/6完整/原短时筛选过**，3200controls/64000physics，非新技能holdout。
- 4211/4212 D3=0；4213/4214 D3=10ms含重复boot；D0–D7全部保持，未选seed调参。
- [独立QA](<RAW2K_SHADOW_V1/capture_qa001/RESULT.json>)**48020checks/0**，0新物理；3200frame全部schema/source/queue/packet mean核验。authoritative mean逐array等原控制trace字段，raw重算mean最大误差`2.1316282072803006e-14`。
- 63848发表raw samples(含2重复boot)，按source去重63846；不当独立试次数。各raw大文件只引用原producerSHA；QA读raw是实际consumer合同验证而非为归档重hash。
- 没有独立2k世界COM/外力truth采集；R38只能做离散sensor-functional/模型预算比较，**不可叫连续时间trueCOM误差已测得**。未来动态spin/jump如需grade应单独新实验并隔离真值。
- confidence cap/FSM阈值均未改，hardware_binding/actuation_used=false，无新增可信cue。

## 两个agent当前任务，继续复用

C child `abf2088f-af10-479a-9108-202785031447`：blockedIO已收尾，现在[portable_fsm_detector_v1](<SPR_AUDIT/portable_fsm_detector_v1/>)新C port，源是根[FSM_DETECTOR_V1](<FSM_DETECTOR_V1/README.md>)。父已接受本轮**binary64相对秒/数值**保真API(不是旧header ABI)，optional/unknown显式bit、69reasonID/双word+顺序表，默认动作unbound/disabled与cap阈值不动；C3 f32提升不增加传感器精度。softdouble helpers未来BSP链接/计时再绑，M4/M7只-c，不叫SP算术/ARM运行/WCET，不为旧physics/RL加FP64门槛。

最新20:09进展：746旧source快照，63方法构造61 contexts/1042steps用于**新C合同**；first C replay46087checks0/maxnumeric0，native1652/0，CPP externC通过，所有新host产物存在，未触blocked IO。但typed NULL-context路径output wheel contact memset0而应unknown−1，agent正在保存first源/exe/log后做一次实际修订/typed补测再ARM，**尚未收到最终seal**。不要把首轮成功夸成所有guard已完。

Model child `e4e6c8f2-f08d-4df1-9150-945c804e8c2a`：PH3已完，正在新ROUGH_POSTURE_CAUSAL_V1，从R22六个4/6cm旧TRAIN trace+TALL_ROUGH_BANK/R30小contact摘要做0新physics因果分析，确认实际姿态高度/跟踪/扭矩限/接触与终止顺序。不借100Hz trace补造2k identity，不碰heldout/新controller。

已排队给它**完成rough后**的新RAW2K_COM_WINDOW_V1：只消费SENSOR_ONLY_MANIFEST的6sensor_shadow路径与public nominal model，不读同目录trace/result/DR/GT；先synthetic SO3/bin/端点测试再6case shadow。比较2k离散functional与旧100Hz mean/constant-bin近似差，非true连续COM误差；保留时间年龄、相关offset/bounds、wheelphase未知、cap.50/冻结threshold.60，trustedcue不提升/不接actuation。0新physics/旧once/GPU/Git/新agent。结束rough先回报，再做此项。

## Jobs/后续

父本段两个bg均已collect exit0：R38`pwsh-cca6c79bd66b4c3d`、QA`pwsh-6392795e3fb4469e`；其余prep/unit/v2/precheck/seal全foreground结束。无父physics/job running，两个child继续，不另开agent、不碰Mnemon idle children。

接下来依据rough因果证据再选主动腿/小跳策略，不重复盲降速/删contact；C FSM最终seal只数学语义，不冒可靠contact闭环。MPC R37仍停在productionIO准入前。270mm、停转/换向、4–6cm鲁棒技能、完整board/HIL/功率验证仍未毕业。所有R35+新成果/失败/报告包括本handoff与PH3 postcommitreceipt均明确**PH4pending**，下一稳定cutoff再新唯一phase4按原Git策略，不重record PH3、不为归档重跑physics。
