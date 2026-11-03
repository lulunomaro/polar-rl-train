# R63实际关闭：push-only名义气弹簧FF单变量未提升严格通过率

## 权威位置和环境

[准备/零步接续](<CONTINUATION_R63_PREEXEC.md>)保留所有新source路径、符号、单位、alias/finally、失败harness及workflow历史；[R62](<CONTINUATION_R62.md>)/[两ZIP](<CONTINUATION_OPEN_SOURCE_V1.md>)保存旧事实。cwd F:/RMPOLAR-RL，任务ROOT为本目录。Python C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe -B，BLAS/OMP/MKL1，最多4物理CPU，禁止干扰RL/GPU/SSH/PPO/canonical/专家index；仅复用C abf2088f-af10-479a-9108-202785031447、model e4e6c8f2-f08d-4df1-9150-945c804e8c2a。Office/ACL无控制代码技能；危险全访问且approvaldisabled，不escalate。无Mnemon写。最近Goal实际rev14/round8/max12，active/armed，不重建/complete/blocked；当前直接人类“继续”已落实到真实新物理。

## 新来源与审批实际完成

只timed_push静态FF加名义正G；原spring/damping物理、PD/32限/roll/yaw/wheel/final40、Position、observer、air/capture公式、模型/.5ms/10ms/完整D0–D7/boxcar→D1→D3/inversePD→D4→随机PD→signedDC与原评分保持。默认开关False，未替换旧保底profile。不叠AIR002。static endpoint混合非G(q(t))、更非纯gravity/硬件辨识。

- sealed数学27FK/168checks0；正G到FFold+G，dataSHA1b47bb7d75205c907f9116cb658adbb2922e82decee2c9b19c2fab8d86db762e。
- 新controller8d59143b961e1ff93e284cd81be8070508d580509985aa41e3d26db7ab4e8765；entryb7a8c4b76192a57d0e4e63ce9b4c0ad9a1cfde78451a21dea855b16d6aaf82c3；binding7f0135b063a8c4d6f459972d8ce40172d038322efbf744c62e8df949c93df4a4。
- 500×3新synthetic9129/0、Geometry84，0新NominalFK/SDK模型；entry26/0实际Ctor2但fakePlant/DR，0loop/packet/actuator/model。原harnessSyntaxError及一空格修正两版都保存，未重跑unit/数学。[最终C报告](<SPRING_PUSH_RELEASE_V1/REPORT.md>)父read27行。
- [Nominal protocol](<R63_SPRING_PUSH_ADMISSION_V1/PROTOCOL.json>)SHA246c79f6952621be05688a8665bef5120f57e3913d44e45df82cc703d756434e，[74-source index](<R63_SPRING_PUSH_ADMISSION_V1/SOURCE_PREEXEC.json>)SHA75de49079a6f2c9ea3ba65ade0be5c13410007b6c0ceeadddeadf9d9f68294e5。
- model独立[名义review](<R63_SPRING_PUSH_ADMISSION_V1/PRE_EXEC_REVIEW.md>)/[JSON](<R63_SPRING_PUSH_ADMISSION_V1/PRE_EXEC_REVIEW.json>)SHA70f2716b23c07794ba66e9568ba056cc892e858340b23c1dfc052980b4b8b9cf，paired[review](<R63_SPRING_PUSH_ADMISSION_V1/PAIRED_PRE_EXEC_REVIEW.md>)/[JSON](<R63_SPRING_PUSH_ADMISSION_V1/PAIRED_PRE_EXEC_REVIEW.json>)SHA0168b3bf49fd7f262588383cbf93c52cab498699b3347a79d85d0abcbb8ce5eb；父已read四份。74中48缓存exact记录/26本次小SHA，不冒全body复读或动态资格。
- 父分别签[名义approval](<R63_SPRING_PUSH_ADMISSION_V1/PARENT_LAUNCH_APPROVAL.json>)、[paired approval](<R63_SPRING_PUSH_ADMISSION_V1/PAIRED_PARENT_APPROVAL.json>)；实际result/config/manifest/core/entry/data关联在V5与每paired wave间验证。新paired scriptSHA62caba3bc31e68de984e5fc8f90fad26ea93631ce924d7c5a023ff6ff19581fc。

## 六个新物理结果已全部收集

Nominal job pwsh-95627d116d084811，paired pwsh-63651898fe904cc4 均COLLECTED exit0。最大PHY并发名义1/paired2，六案全complete/每案800controls16000steps，合4800/96000，0softwareERROR/0unstarted；不是6个独立鲁棒样本。Nominal先flat原门pass且绑定后才RM；两名义原门均pass，guide/hard0、end4.63s，flat/mainmesh峰值.19168605m、RM.19210015m，RM firstflight2.361s/两个scope证书True。

固定旧TRAIN4602/4605/4606/4610（事后按旧R60结果选择机制队列，非holdout），source在两wave前后锁定，无内批改动/种子替换：

|seed|local原门|旧R60同seed|guide/hard ticks|轮mesh空中峰值m|end stable s|其他失败|
|---|---|---|---|---:|---:|---|
|4602|PASS|PASS|0/0|.2748247680|4.87|无|
|4605|FAIL|FAIL|2/0|.2045356891|4.51|guide不能舍入|
|4606|FAIL|FAIL|0/2|.2441071228|3.89|max worldY .4877216>.3|
|4610|FAIL|PASS|3/0|.2179424968|4.56|guide新增，原通过回退|

四案main-rear firstflight都有、full-final/never-next证书都True，但这些不抵消guide/hard/偏航失败。**严格通过1/4，相同四old baseline2/4；无净鲁棒提升、4610退化，不提升为保底默认。** 一例轮mesh空中27.48cm不是270mm台阶验证（实际场景首bar只有6cm），更不是全机净跨/全RM/硬件证明。

[统计程序](<record_r63_spring_facts_v1.py>)只一次读小results/config/old小baseline，原门逐项重算与result一致，DR receipts字面相同；[facts JSON](<reports/R63_SPRING_PUSH_FACTS.json>)/[18行MD](<reports/R63_SPRING_PUSH_FACTS.md>)已写且父已read。大raw只引用producer SHA/size，统计0新PHY/旧QA/asset hash。H1/H2/H4/H5/Stage1未变。

## 尚在独立进行的任务

1. C机械功审计已实际SEALED并停止，父read[39行REPORT](<R63_SPRING_MECHANICAL_WORK_V1/REPORT.md>)及[receipt](<R63_SPRING_MECHANICAL_WORK_V1/RECEIPT.json>)关键字段：[SUMMARY](<R63_SPRING_MECHANICAL_WORK_V1/SUMMARY.json>)SHA bd873bf72a9905a865143e32014daf892163dc4d10d4a5eef9c21b8927082368，report526b1aa1e62f366240a6c54c0274a0fb1086691a018ba3485154a73e19bfd057、receiptb119ae70c86c74bd187fa005f498c28f352f26bf40600a98cf7cdd88186dad6c。仅旧r58_tall0_position_flat与新r63_spring_release_nominal_flat，4raw各1open/33600rows，10小源SHA保持，0重hash/其他raw/新FK/PHY/旧QA/新hypothesis。两案actual phase均195approach/15push/25flight/565capture（push[1.95,2.10)含300*.5ms=.15s，不按cfg .14硬裁）。195个100Hz prepush/13公共域8190标量maxdiff/bitdiff0，非2k证明。samePRE τ*dq左端积分包括末格7.9995→8.0，clockmax1.714e-12s；push腿净2.695748→1.490828J（正16.744320→16.898606、负-14.048572→-15.407778），flight腿25.474726→30.004897、轮11.447669→15.248652；capture腿-19.790081→-21.833659、轮27.092745→24.171531；whole腿7.747727→9.029399、轮74.196835→75.267450J。mainmesh峰.181228926→.191686051，首landing PRE2.4115→2.4090；正机械峰544.96→603.33W在flight。不能简化为push额外净功导致更高；后续状态/限幅重分配作用，actual gas/全能量账/电气损耗未辨识，不是母线或独立motorfeedback，两旧grade不变。
2. PH8_SOURCE_PREPARATION（截止R62+insight+sealed spring math，排除activeR63）model已完成1797entries/344newtext2.24MB/1016priorGitrefs/437rawmeta435known2unknown。父read handoff/consistency/资格、缺口全部类别与表示边界主要段；父新[小数值核对](<PH8_PARENT_NUMERIC_CHECK.json>)独立6snapshot+4priorGit小result PASS6/4800/96000、nom2/2 selected1/4 vsold2/4，明确2unique saved-text版本缺口(FSM ERROR_REPORT和synthetic prechangefixture)、2冲突exe unknown。没有重建缺失fixture或hash大raw。
3. PH8实际已完成并远端核验，父read正式[postcommit receipt](<../repo-lqr-robust/history/experiments/mod4v1_robust_traditional_phase9_PENDING/ARCHIVE_PHASE8_RECEIPT.json>)149行：commit/remotepeeled662204600bf79ace36815db569a5d02f3b327981，parent223577994e0f750e0ae062ce9ffee204273c90a2，tag trial-20261103-mod4v1-robust-traditional-phase8/objectddcfcf6e1afc48490493529377d1263c8fe4ef08。373全A=363SOURCE+9cover+1record，两staged和committed-tree逐blobSHA/recordmap门通过。最初新adapter literal_eval遇旧BASE符号在main/helper/Git之前失败，原trace/source10ecb5...两文件保留；只修新adapter明确常量，之后原helper rec.main确一次，不重record。只atomic非force ownbranch+新tag、旧PH1–7 refs不变；main0e9c71a06d802723185fa54b2410915d931e6925只相邻push窗口相同，不冒全程无并发。原helperb2fd15...及source封存/3父copySHA不变。仅关闭R62+既定数学/insight，active R63全部排除；此正式receipt自身明确PHASE9_PENDING_POSTCOMMIT_NOT_IN_PHASE8_TREE，旧pending5/6/7/8不stage/delete。不得再次record/push本PH8。

## 下一步与仍开放的总目标

C机械功与PH8正式postreceipt均已父实际read，以上更新为当前事实；所有相关父jobs已收集，无额外PHY在跑。model的[4610 guide回退17行报告](<R63_GUIDE_REGRESSION_V1/REPORT.md>)/[23行receipt](<R63_GUIDE_REGRESSION_V1/RECEIPT.json>)也已父read：只new4610 trace+physics各1open/16800rows、旧R60只smallresult；0模型/FK/PHY/QA/真q重建/rawhash。新firstlanding2.495 right_tire→GROUND7421.33N、pitch-13.5417°/roll2.80255°/PREz.303081395；之后guide_wheel_07→rm_bar_011 TOP三连续tick2.5135/.5140/.5145(PREz.27036→.26906、pitch-13.06→-12.78°)，guideFn7674.26/1252.54/473.486N，hard0。mainrear-firstflight2.456比mainlanding早39ms、再18.5ms才guide刮bar顶，main轮跨出不等整机净跨。实际capture2.41/首正weight2.42，brake2.50，observer恢复2.66晚于guide，非初guide前因；不能据单案归因capture/brake/FF唯一原因。三tick均captureWeight.5、observerdisabled，actual landing_position_ref4在[EVENTS](<R63_GUIDE_REGRESSION_V1/EVENTS.json>)，2k真q仍unknown。新失败/旧pass不改。reportSHA8241d7f99e234335bbecde2bf72200d4d4aff1675a4ec8b84568e4c87e91e2e5、eventSHA41ae16a6c28c17c772dff19ae400d094d2c47cb547118de5fde0ae40e6845ba0。

C现在只受托新的takeoff动量telemetry**方法只读**：核本机mj_angmomMat/subtreeVel API、实际PRE/cache/qvelPOST混用风险、whole robot subtree/COM和external contact wrench定义、armature/遗漏项；0模型/forward/PHY/raw/第三gain。尚未收到方法结果，不把它当新controller/已跑诊断。当前没有R64代码/新physics/新holdout，后续不要凭这里的设想当已实现。单独弹簧释放仍留guide/硬撞/横漂，下一策略应从统一腿力/姿态优先及起跳状态与饱和约束着手，而非把FF/h继续无约束叠加。

Goal仍active：完整9m/更多terrain、270真实跳阶及落台、自旋停启换向、实际driver功率/actual-held+unique-send、两板BSP/ARM执行/WCET/HIL均未毕业。所有R63与postcut报告后续PH9pending(旧metadata暂写postPH7 pending只是历史标签，不冒已入PH8)。源文件先读后改，冻结失败/旧once不重跑，缺SHA仍unknown。
