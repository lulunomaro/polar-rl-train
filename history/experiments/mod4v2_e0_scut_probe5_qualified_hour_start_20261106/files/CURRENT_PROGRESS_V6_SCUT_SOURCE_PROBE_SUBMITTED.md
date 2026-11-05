# E0：已闭合旧配方26更新，SCUT原配方接线短探针已独立提交

Goal664 rev5 active/armed；用户要求按华南虎真实训练过程逐专家，不编奖励/权重，当前仅E0串行/GPU0/host72，不运行其他8、不访问86。上游SCUT origin scutrobotlab/wheeled-legged_RL、本地观察HEAD b8ff79f3df855faf9dc92f4a282bd80c42649466；不声称工作树全部等HEAD。实际任务链是Robotics-Wheelbipe-V14-Flat-v0→V14Env/FlatEnvCfg→V14FlatPPO继承链，不是文件第一个25V3类、Play或Rough。完整依据见[唯一源对齐报告](<F:/RMPOLAR-RL/mod4v2_expert_normalization_20261105/SCUT_ORIGINAL_TRAINING_ALIGNMENT_V1.md>)及[用户原配方政策](<F:/RMPOLAR-RL/mod4v2_expert_normalization_20261105/SCUT_ORIGINAL_RECIPE_POLICY_V1.json>)。

## 真实既往结果，未晋升

旧无限follower原PhysX mimic有explicit有限限位要求错误，20更新候选0fdc原评测80/80 mimic终止8000次；保留故障/候选。新独立D6 V3保持8无限轴/31体MCI/277mesh/300N140–200mm/CAD端及原逻辑健康门，仅四后端excluded orientation D6/三线性自由；canonical平面neutral1:1等价不是任意3D/winding。N16无PT/PPO60control诊断真实close/wait/EX释放qualified、mimicmax.001381/四named native全<.01，cached backing unknown非0；后hour另做了N20000 native-before-PT传动/gas/limits/closure/1zero8physics2feedback。

旧hour root MOD4V2_E0_HOUR_WINDOW_FULL_LEARNER_MIGRATION_20261106_023350_1793903630723043100确实26新增原PPO/17Adam各+520/12480000优化transitions；因实际env term0/value_loss2等与V14Flat-v0不同，以原STOP_SAVE完整更新边界保存退出，未热改reward或扩时/退款。full f326418aea63a9a73b06fb887de88426b856c904048aa5fcea3d4c3c994b487b/104430359B/实际iter32029/17个Adam槽step642120/LR1e-5。真实SDKclose/inner+outerwait/charge_values结清/lease释放qualified。有效loop(扣save)1004.355s、rollout calls994.332s、update calls5.422s、startup379.715s、save1.824s：不称跑满一小时。原N80/1000/seed20260928 fullDR闭合executionqualified但42/80 unique物理终止、80bad_orientation事件、38timeout/mimic0；速度MAE1.479729/.042732/2.337838，maxclosure.00158513/mimic.00154408/rawaction2025.72/clipped6。技能不合格，缺失完整binary/profile grader仍null，正式6cd/旧Registry保留，见[E0_D6_STOP26_QUALITY](<F:/RMPOLAR-RL/mod4v2_expert_normalization_20261105/E0_D6_STOP26_QUALITY_V1.md>)。非配对因果改善，不因mimic0称毕业。

## 当前源码接线与严格小探针，不是小时训练

reward v1 ed3293a9...保持；新v2 d9c876183aebfb39085e336d35b717c4574b2fda4e88ee73aa5f1db93722e685单独核原SDKbase.step a963...及真正MOD4wrapper b7dede.../MRO+func identity+唯一super顺序，不要求合法wrapper等于base源码，不绕过step。原37有序项/26非零/11零项、(raw*.02)*weight→finite处理→原numeric-env归零→37slot原序sum、无only_positive保持。接触history3×.005 >3N，done当前contact>1N/40deg20steps/numeric500/200/100彼此不混。command v1 3f4c9343...为真实Uniform subclass，5–15s/standing.1/heading.5/gain5/vx±2.7/yaw±2π/真实iteration特殊模式；保原double-standing draw与reset flag；debugFalse时obs>120 gate计数保持0。只机械缺gimbal映射/原闭链resetbank/MOD4 actor35/critic38与参考35/78不同是明确适配，不能称原观察数值完全相同。既有源存在并不等于adapter运行通过。

新worker **worker_e0_scut_v14_probe_v1.py** 85507B/SHA0fae091905c790602e7543ff352738099187a722159dc88fbbcaca8d3f910cdc（child AST在同值三alias之前，最终完整源又由父stage AST解析）；单E0/N20000/T24/mode **SCUT_V14_NATIVE_AND_ONE_PPO_PROBE_NOT_HOUR/max_additional_updates=1**。stage297 shared非PT+完整472runtime/lib/staticNPZ；两个adapter与worker同目录并列入sharedmanifest。原source6cdac1e4b84df407d41a38444b87eaa91309ed898af05fe95a6c80f6ac3fd693/14035411B/iter32004/Adam641600/LR.0002562890625000001保持，绝不替换成坏0fdc/f326。

代码接线：hardware.apply→cmd.configure→reward.configure→env ctor返回cmd.bind+真实source_iteration32004→原sole freshreset→reward.bind(v2)→同一原native zero，无额外reset/obs.compute/noise/RNG。删除原legacy RM_SPIN_STAGE/RM_GYRO_CURRICULUM禁yaw断言环境标记；不是热改原运行时文件。PPO系数按注册Flat value4/gamma.99/lam.95/clip.2/entropy.005/5×4/desiredKL.01/maxgrad1，原A0网络/norm/learnedSTD/17Adam/mutableLR严格源载入不重置；参考defaultLR1e-4和实际继承LR分开记。

实际运行若native+fullcache/load严格一致且fullsave callback安装后，先发布U000完整初始checkpoint/独立SCUT_INITIAL_CHECKPOINT_ACCEPTANCE，actor/critic/norm/STD/Adam17/LR/iter逐项同源+own roundtrip/source1IO，之后才恰24PPOcontrols/1alg.update/20Adam并完整U001；cmd/reward原状态/history3/cfg/源SHA加入新checkpoint。FINAL/initial/recipe/实际192physics48feedback增量+envclose/V6 intent+真实p.wait+无ERROR才父semanticqualified；短探针不当hour/skill。此处均为实现契约，直到actual receipt出现才称运行成立。

新parent只收窄更新数到1、mode/initial acceptance门，原gpu/account/environment/main资源/计费/wait/cleanup AST保持：原global两EX/GPU0privateEX/finiteSH，reserve86412.86069250107/3900-save3600-headroom300/preGO1800，无C复制、foreign signal、清锁抢占、退款/扩账。父probe prep第一版静态插入使用两空格而原owner body一空格，失败在任何文件发布/SSH之前；v2按真实AST col_offset修复，仅后续一次发布，旧错误源保留。未发现本地JSON中任何UnboundLocalError运行receipt；不以无可核验旧叙述替代actual smoke证据。

## 当前实际状态（2026-11-06 +08:00）

root **/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V2_E0_SCUT_PROBE_FULL_LEARNER_MIGRATION_20261106_043618_1793910978054991000**。stage actualverify_sources rc0/PT0/SDK-GPU-GO-C-lock0。dispatch1793911128.5434763/controller1693216，唯一observer **pwsh-1368f7d56a9e4020**，首次1793911131.8238463 **GOtrue/nativeBeforePTfalse/learnerfalse/update null/noError/noactualwait**。尚未看到U000/oneupdate/close资格，小时窗未启动，其他8未调度。只用此独占observer继续，不重复once/源权重。

最近verified Git9c2dcd2e3a06ffc03105fed9329d758700b2938e后本串行原生/20失败/D6诊断/26旧配方闭合评测/SCUT源证据与本probe源码提交待meaningful feature-only archive。main只读；原record_experiment全validation/redact/hash/uniqueannotatedtag/真实remote核验；模型/raw/USDmesh先跳再stat/read/hash，不重放物理/旧once或造无限验证链。goal未完成，Registry不晋升。
