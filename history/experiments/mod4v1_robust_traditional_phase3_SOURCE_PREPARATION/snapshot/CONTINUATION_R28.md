# 接续R28：Phase2真实归档、当前C封存、启停换向与材质敏感性

先读[上段R26接续](<CONTINUATION_R26.md>)，再以本补充覆盖其pending旧状态。Goal仍`goal-4d4bef80-e614-432d-a8cd-8f385ef2dd7d`revision4/active/armed/max12；勿新建/提前complete/blocked。实际cwd F:/RMPOLAR-RL；技能Office/ACL不匹配；无GPU/SSH/PPO/其它会话改动，最多4物理CPU。不要为归档重读大raw/大资产，producerSHA直接索引。

## R26已闭合，不再跑同ID

[完整批次](<batches/r26_transitions26/BATCH_RESULT.json>)26个rc0、全完成；之前R23/R24 prep0Step与R25四个postprocessing失败见上段，原样保留，不补造遗失trajectory，不统计成robot失败。

- P25 +2m/s→刹停：newTRAIN204..211综合5/8。全部都完成刹停，停稳约2.71–2.86s；204/205/210在短drive窗持续实际速度2秒未达(.15容差)，205 vRMS.150066不可舍入通过。注意原批次gate给normal drive连续2s，不能后改成只看brake通过。
- P25 −2m/s→刹停：TRAIN201..208 **8/8**，另nominal过。约2.68–2.90s停稳；仍不是新独立holdout。
- 固定H2控制 +4π9s→停3s→−4π9s→停4s，全8DR完整，正负yaw各连续约7.06–7.10s维持，**综合0/8**；nominal过。主要停车后v残余/xy漂移，部分第一stop.5s保持没达；202endpoint1.5035m。不能用双向yaw稳就说启停换向过关。

## R27新控制TRAIN，仍不毕业

新[spin_stop_capture_v1](<spin_stop_capture_v1.py>)继承冻结H2，低command/低refw/低估计w10ticks后，用P25 normal捕获**估计**forward gauge参考并200ms凸组合输出；未改rootPose/物理state。新[runner](<run_spin_stop_v1.py>)可在measuredgyro_z和refw都<2时恢复V4 accelgain1.5，高spin仍0；纯传感器，没有truephase/姿态输入。旧冻结H1/H2源没变。

[R27](<batches/r27_spin_stop27/BATCH_RESULT.json>)同R26 schedule/grader，3variant×nom+201..208：accel_only0/8，capture_only0/8，both **2/8**(203/204)；所有nominal过、全27rc0完整。both改善停车尾v与漂移，但201第一stop保持.48s<.5，202endpoint.942m/余速，205xy.300399m>.3不能四舍五入；206/207/208虽phase多数好，original wholecase yaw RMS等仍fail。2/8不是高鲁棒与独立成绩，不对H2旧结果重新归类。

## 重要新材质层级审计（旧数据不改）

[USD+实际pair0step审计](<MODEL_AUDIT/GUIDE_EFFECTIVE_MATERIAL_V1/RESULT.json>)：USDguide材质static/dynamic约.02，无authored combineMode；主MJCguide geom.02与step.9但priority均0，因此实际contact.friction5 **[.9,.9,.003,.0001,.0001]**。RMSCUTboxground1.0同priority也有max-mixing解释。原D0只提升main tirepriority，所以不受地面覆盖，而guide未有对应提升。

详见[追加澄清](<reports/GUIDE_EFFECTIVE_MATERIAL_ERRATUM.md>)：authoredgeomμ≠effectivepairμ≠实时PhysX场景combine≠硬件标定，不凭未测的PhysX规则认定唯一修正；旧guide相关跳阶/起伏结果应在**原有效高μ规则**下读，不能冒effective.02资格。

新显式[guide-priority材质分支](<physics_bridge_guide_mu_v1.py>)只作为替代语义敏感性：guide提高priority、tireDR再提高其上，0stepQA实际pairμ.02；优先级还影响其他接触参数选择，不冒只改一个标量的完全等价。[静态QA](<MODEL_AUDIT/GUIDE_PRIORITY_VARIANT_V1/STATIC_QA.json>)。

[R28](<batches/r28_guide_material8/BATCH_RESULT.json>)两固定control×nominal/101/201/203共8，全部完整但低μ分支：
- 原pushδ.34/.11：nominalend2s过，三个DR都未达(0/3)，仍Guide/少量hardcontact。
- 延伸δ.65/.13：nominal过，DR只有101过(1/3)；201立面guide first且airclearNone，203end1.02s。
选取的TRAIN小敏感性样本不是成功率资格，不能挑更易分支报鲁棒完成。旧source/结果/Phase2不回写。可进一步测试RMGRID同材料分支/找6cm实际blocker，但保持标签/最坏case，不删导轮、不弱接触刚度刷分。

## 当前C port已实际封存（下一CLI在做）

[portable_control_v3_current README](<SPR_AUDIT/portable_control_v3_current/README.md>)父已读前120行；SHAaec1f23a44a6b6422275c003b6d90d6d5a2a39312517458028dcb78f76235dc3，INDEX51cfc25a956539557144208900ab238a3573c63ded0dd3fde4be6ded06c37a09。

- 当前V4 quaternion/lever+pivot/vector gate/Joseph/heading/age view +真实P25K/leg120-4/yawPI.8-.5/.052rateFF/.08accelFF/shaper/envelope +strictsingleenqueue gate；不是R00C1更名。
- 最终**6509unit断言0失败**，3200packet9场景C status全OK/预定budget0超限。Py64重放R04_202/R11_k20_201 logged14 max差0，C vs原distance5.33e−6m/yaw1.15e−5rad/vx6.58e−6m/s/整链τ2.00777e−4Nm。
- 当前三源×M4/M7新6objects成功、C++externC通过。只-c，无BSP链接/BIN/ARM运行/HIL/flash/FPSCR/WCET。14冻结源/221旧source快照无变。
- 只1+2(P25)，**H2 feedbackτ20未移植**，仅同包FK/gyrovy诊断，不是世界速度独立测量。100Hz聚合epoch≠瞬时通道同步≠硬件2kCAN。
- 声明输入domain/有效/时序/mean/age/alias/重复一致；显式arming；坏metadata不能继续old estimate出正常τ。细节见README。

复用child`abf2088f-af10-479a-9108-202785031447`现在新HOST_CLOSED_LOOP_IO_V1 ACTIVE：本机resident typed stdio +wireseq/payloadcount+Python64封装，MinGW32exe不ctypes，回**P25 preDC mathτ**与**cycle finalDCguardedτ**明确区分。父plant还有inversePD/D4/current-loop逐步DC夹；下一新physics要记录所选τ域/双层限幅，不偷换语义。无CAN/BSP/板卡deadline，child不做physics。C3及此均postR16 PH3pending。

## Phase2已真实commit+atomic push，勿再record

父已读[回执](<ARCHIVE_PHASE2_RECEIPT.json>)：
- own branch`mod4v1-lqr-mpc-robust` commit`02b5ff84b905a4e40f207a44b0491aeff2f79b7e`。
- annotated tag`trial-20261102-mod4v1-robust-traditional-phase2` object`4ac41c1403a3daefa52acedbf659ee89120b6046`，remotepeeled同commit。
- Phase1tagobject1064f48.../peeled93e081...不变；只own branch+newtag --atomic，无force/main/expert目标，2621expectedstaged全A/noD/foreign，每blobSHA匹配；originalrecordhelper未改。
- 紧邻push mainpre/post31132dbf2207e96e64c5eddbf16f27dfecbb5a17；早期412d→3113并发变化单列，不声称整个归档期间main不动，更不回滚。原专家branch/HEAD/index非写目标。
- 截至R16严守；3489源条目=2602新text13.18MB+410Phase1同byte引用+477rawmetadata(447producerSHA/30unknown)，282externalmetadata。446物理result含30旧Phase1，R15软件33独立且prefix实际109920steps不当jump能力率。478future/active为PH3pending。
- Git记录history/experiments/20261102-mod4v1-robust-traditional-phase2.json。回执本身postcommit归下一PH3，不receipt递归。

复用child`e4e6c8f2-f08d-4df1-9150-945c804e8c2a`已转新DYNAMIC_COM_MOTION_V1 ACTIVE：public31bodyFK/MCI移动COM全项proper_COM=properOrigin+α×r+ω×(ω×r)+2ω×rDot+rDDot；sensorq/qd/qdd/ωα及噪声/置信，wheelCOM偏心需wheelangle则显式绑定或降conf，不假balancedwheel。0Step static/synthetic、不改CONTACT/FSM、不用DRtruth。CONTACT静态32tests/nom70N不是动态接触可靠概率，cap.55仍低于FSM默认.8。

## 当前jobs/接续

**父所有相关job均finished/collected，无running父物理作业。** R26`pwsh-66c19964e8dd45f5`、R27`pwsh-52e1d9bc69204b80`、materialaudit`pwsh-5bc0e211b25f4004`、R28`pwsh-478e0d61e03e41ad`已收。各软件fail均已读，不存在待查nonzero。

下一优先：拿residentC adapter进行NEWstand/forward/brake物理闭环而非只向量；拿dynamicCOM做flight/guide支持shadow验证；整理R26/R27报告并继续停转捕获，不改H1/H2/门槛；用named contact找实际6cm障碍阻挡，考虑sensor-realizable ToF/impact/腿控制，不从worldGT伪造障碍输入。范围明确：SCUTtiny_step仅一family实际几何，fullCADarena文件workspace未找到；2cm只有nominal通过，4/6cm失败仍在；270定时profile不能冒contactFSM毕业。

可为PH3再做snapshot/archive，必须新trial id、不复recordPhase1/2、不触碰活跃expert树/索引、不把尚在写CLI/COM纳为sealed、不为归档hash重读raw。Goal保持active，仍有实质任务可做，别complete/blocked。
