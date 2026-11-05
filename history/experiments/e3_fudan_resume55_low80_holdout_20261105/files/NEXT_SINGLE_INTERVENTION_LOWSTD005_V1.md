# 下一有限试验：以W8为对照，仅将初始策略探索STD由0.5降至0.05

## 已有实测，不作因果归因

- [W9实测结果](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_HEIGHTGATE_CLOSED25_QUALITY_RESULTS_V1.md>)：N20000/T48真实25轮收口，原N80为0/74，名义31体5姿态联合判据0/5；母版保持。
- 对当前[MuJoCo结果元数据](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_HEIGHTGATE_MUJOCO31_LOWRise_RESULT.json>)只读分解5条末态：候选高度与机体速度各失败5/5，倾斜、角速度、双轮接触、机身接触各失败0/5；母版仅机体速度失败5/5。末态分解不是整段失败根因。
- W9训练29991个低趴episode中29922曾达到高度0.23m，却联合credit为0；单看峰值高度将掩盖停稳问题。
- 母版名义末态速度0.038073m/s略高于严格0.03m/s门限；候选约1.012090m/s。原门限和分母保持。

## 单项可检验假设

以已经真实完成的W8 fresh1cd/no-heightgate/STD0.5为行为对照，本试验唯一新增行为参数是 `core.PPOConfig(initial_std=0.05)`。不继承246ac/bf824及205轮坏支路，不把失败heightgate当默认基线；奖励恢复W8原函数/权重，明确不是继续叠加reward改动。

原六维Gaussian均STD0.5，动作scale保持leg0.5、wheel10，对应策略采样目标扰动STD分别0.25rad与5rad/s。STD0.05时分别0.025rad与0.5rad/s。此为策略采样尺度解析量，非机体速度实测，也不证明高STD导致既往失败。保留learnable log_std、entropy0.01、KL、PPO clip、两Adam和原自适应LR数学；只改变新分支初始STD配置，后续STD仍由原算法学习。

## 固定边界与测量

- 原1cd actor8+critic8 MLP warm；encoder随机新建、latent新增列0、STD/LR/两Adam/private generator/计数fresh。N20000/T48，cap25；不从旧RSL iter43090或205累计轮数拼接。
- 保留原low8s独立timeout、26 recipes、原姿态/commands/height reward与负项、2c/bae资产、原PD/400N气弹簧、fullD0D7。降低策略Gaussian探索不关闭或缩窄域随机化、动作延迟/effort/sensor噪声。
- 原W9高度峰值/采样统计仅被动保留；另被动累计低趴height/upright/speed/angular/wheels/chassis/joint_good七项样本数，复用原update已有量，不参与reward/credit，不增加getter/RNG/physics/sensor。原grader与工程联合条件不变。
- 原父唯一canonical/charge_values/authority2EX/privateGPU_EX/finite trainSH-evalEX/reserve86412.86069250107及3900/3600/300窗口/1800preGO保持。每实际窗口完整保存、SDK关闭、inner+outer actual wait、结清释放。
- 完成后独立原N80/160/seed20260928/74firstepisode+6normal与同31体5合法姿态各8秒MuJoCo。原N80不安装训练timeout或reward overlay。训练更新、峰值、CPU/source检查不作技能通过。
- 仍无联合质量改善则保持Registryv12/1cd；H1及其它专家不动，候选完整保留。阶段记录全部成功失败，feature-only唯一annotated trial，main只读；状态/Git不开模型或旧raw。

## 当前状态

仅下一假设与源码准备，尚未新准入/GO或训练。活动goal round3/14，质量目标未完成。此前已核验feature b8be2526473b439b9b6c529a3ce35da7a320395a。
