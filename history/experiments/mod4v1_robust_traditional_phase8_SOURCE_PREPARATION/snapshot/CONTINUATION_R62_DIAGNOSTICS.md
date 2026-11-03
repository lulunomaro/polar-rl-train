# R62诊断后接续：保留1/4，新增几何诊断已零步验证

## 目标、工作区和冻结项

当前goal仍goal-4d4bef80-e614-432d-a8cd-8f385ef2dd7d，最近实读rev9/round6/max12 active/armed。旧scope、PH7真实归档、R62审批和全部6例实物理成绩见[CONTINUATION_R62](<CONTINUATION_R62.md>)，来源链/启动器修复见[V2执行前接续](<CONTINUATION_R62_V2_PREEXEC.md>)。这些case不重跑或换seed，原local名义2/2、固定TRAIN1/4 vs旧同seed2/4；H5仍40/64，不是270mm可靠跳阶。Stage1V1/旧holdouts保持byte。

cwd F:/RMPOLAR-RL；Python314 -B/BLASOMP MKL1/最多4PHYCPU；无GPU/SSH/PPO/canonical/专家index/新agents/Mnemon写。Office/ACL catalog无robotics匹配，已有filesystem/CLI。read-before-edit/glob/grep。dangerfullaccess/approvaldisabled，无escalation。原模型/闭链/所有contacts/原100Hzmean→D1→D3/PD/D4/gain/signedDC不改。

PH7 223577994e0f750e0ae062ce9ffee204273c90a2已真实归档且回执已read，不重复record/push。全部AIRref002/R62/本诊断/以下新模块PH8pending，新归档须新cutoff。原用户跳台阶问题已答，最新14:53 final也已如实给R62退化，无待答人类问题，继续原goal。

## 4610小结果诊断：已read全报告及receipt

[R62_FINAL_SCOPE_REGRESSION_V1报告](<R62_FINAL_SCOPE_REGRESSION_V1/REPORT.md>)22行SHA011cd8a390e5cde7132fba3661f55bcc500f67a7e9d1c9d5655b6ec4925e249c；[receipt](<R62_FINAL_SCOPE_REGRESSION_V1/RECEIPT.json>) b34c1b07ce64cb58239e21f5f415b3a8f5913ece82a98fb39e55211016c962c3。

- firstbarback同1.837022444717014m，旧sphere minX1.8663830929796186/new1.828106759617952，margin+29.360648→−8.915685mm。
- root POST x2.264746806334247→2.2268677453554955，少37.879061mm；bound minX少38.276333mm，descriptive offset仅差.397272mm。主要保存数值差是停车位置，不是已证明因果或姿态故障；cache7.9995 vsrootPOST8.0错时.5ms。
- 新pitch .00961646/roll .0015065rad、guide/hard0，原local仅conservative final allcollision behind新增FAIL。实际shape minX/argminGeom未存，未知；球AABB false不证明实际撞bar/mesh overlap，也不证明实际已过而只是false-negative。
- 父发现表头“main/local”易误解，已append并read[FIELD_NOTE](<R62_FINAL_SCOPE_REGRESSION_V1/FIELD_NOTE.md>)：第一项为scene-specific flatflag，RM恒False，不是common-main失败；common-main两案通过。原报告/receipt/分数byte未改。

## C agent的实际响应诊断：已正式seal，父已read全58行报告

仍只复用C abf2088f-af10-479a-9108-202785031447。[R62_AIRREF_RESPONSE_CAUSAL_V1报告](<R62_AIRREF_RESPONSE_CAUSAL_V1/REPORT.md>) SHA8f2427a8f21027c8e2bedf6700c0da12152bd6e4f016a141d32afd477ef9cea4、FACTS26947B SHA3369fa9ec4a624caab76ada43a562c2d78b05ad446916ceaef20b490e5d31cbf，[receipt](<R62_AIRREF_RESPONSE_CAUSAL_V1/RECEIPT.json>) SHA826ccdd1d19e66b97425edf216de98fa77a620df5826ea68518a08331e240f23；父read完整报告和receipt主要字段（单行长JSON尾部read截断，不谎称全部source数组逐字read）。26小source未变、58producer匹配。5允许raw各一次：旧/新4606、4610四控制trace×800+仅新4606physics16000=19200行，0raw重hash/PHY/旧QA。不得重开数据为归档。

- 25 flight tick/case，4606首flight2.01/capture2.26，4610=2.16/2.41。预锁target_q4/encoder_q4/encoder_qd4按140/3重建flight PD及wheel式，外clip40，对全部记录actual requested误差0（原门1e-9）；h/target公式误差0。
- 同一recorded packet的去h代数反事实（不是旧trajectory）：new4606 100腿axis-ticks=22全遮蔽/2部分/76传递，new4610=16全/0部分/84传递。只能支持局部request clip遮蔽，不能推整体动态因果/actualDC或硬件饱和。
- 4606 t2.01..2.04四tick四腿全遮蔽，requested leg分歧2.05、theta/rate分歧2.07；4610全遮蔽t2.16..2.17、leg分歧2.18、theta/rate/wheel2.19。不是D4时延单独辨识。
- 4606全部25 raw hGoal<−.10、capture anchor−.10；4610首h+.005006083、anchor−.0122668985，goal未碰两端。尚不选择第三h范围/gain。
- firsthard new4606为chassis_front→rm_bar_011 TOP，PRE2.3335，point[1.835758630,.137575306,.059094460]，normal[0,0,1]，Fn35379.105N；次tick2.3340为4814.556N。theta−.820941578/roll−.0581640，capture后73.5ms，weight .28175，observer隔离至2.50。
- 2.3235时theta已−.800208且totalForce0，impact不是全部先行pitch来源。D.ctrl同stage wheel[-.798005,-.787674]，对照request@2.33两轮−5.77591相差3.5ms；前者是旧PD/D4/gain/DC末端模拟命令，不是独立电机反馈或clipmask；其它三例同stageactual仍unknown，fullDR2kq不递推。
- firstflight前201/216个100Hz公共snapshot、22字段，9174字段位比较0差异；不是全2k证明。以上需待正式receipt再最终封存引用。

## 新私有几何kernel：已真实执行、已seal，不是新机器人实验

[PRIVATE_COLLISION_SUPPORT_V1](<PRIVATE_COLLISION_SUPPORT_V1/README.md>) status VALIDATED_PRIVATE_GEOMETRY_KERNEL_NOT_RUNTIME_INTEGRATED，[INDEX](<PRIVATE_COLLISION_SUPPORT_V1/INDEX.json>) SHA219f013b4f9abeb7f85fc5a3d3fa5bd66d002422d0dd9a8d185487d2c9806b4f，9小文件。新[PLAN](<PRIVATE_COLLISION_SUPPORT_V1/PLAN.json>)在执行前锁定，[support](<PRIVATE_COLLISION_SUPPORT_V1/support.py>)和新[validate_once](<PRIVATE_COLLISION_SUPPORT_V1/validate_once.py>)一次815检查0失败，max oracle4.440892098500626e-16m（原预算2e-12）。

- 1次原XML编译、5次显式mj_forward，6integrator入口计数0、episode0。几何姿态不是闭链平衡/动态轨迹。nbody32/ngeom312/nmesh279、34collision=8box+16capsule+2mesh+8cylinder；sphere/ellipsoid有新synthetic支撑点验证。6小source before/after同，XML0e9ca...不变。
- 缓存compiled mesh_vert，geom_xmat/xpos只变换一次；解析primitive方向支撑，不重复mesh_pos/quaternion。输出raw/minmax+1e-8 padding、argmin/argmax names/IDs、pergeom及旧sphere界。与Tire helper新5姿态逐方向相同，全部在旧球界内；data byte/time不变。
- 只private grading，不contact shell/actualoverlap/支承/稳定/形式interval。未接runner或2k writer、未测runtime开销，future必须对齐force PREstage、保留原sphere字段/分数。未追填R62真实shape净空；没有R63代码/PHY。
- 一个误查MINIHOP_AUDIT_V2/contact_grade.py不存在，glob已确认实际contact_grade_v2.py，未绕路径/ACL补救或读旧raw。
- 父job pwsh-88df3f70b1dc4f0c已COLLECT completed0；metadata seal foreground exit0，无QA重跑。当前父无running相关job。

## 动量结构提案及下一任务

父已read[AIR_REACTIONLESS_FEASIBILITY_V1 REPORT](<AIR_REACTIONLESS_FEASIBILITY_V1/REPORT.md>)40行，SHA d7c1a6575423af89f5a56f01c17dbc8c431ae8150aed2501e78b1d22cb3ac2fa，receiptff98d40f...。仅文字/源，0FK/model/query；公共31body有full惯量，旧fk/terms默认wheel/guide spin0并删wheel rotational load，不能当全H。全COM H=I_locked*omega+A*zdot，common列ones4、delta[0,1,0,1]；leg增量抵消不是实际reactionless/landing稳定，未知H0、wheel/8guide、armature物理rotor归属、softpassive和接触仍缺。

父已给同model agent e4e6c8f2-f08d-4df1-9150-945c804e8c2a新一次批准 AIR_CENTROIDAL_COEFFICIENT_V1（尚未报告执行结果）：
- 三既有public poses(crouch/endδ+.2/landδ0)、epsilon1e-5rad、最多27 NumPy FK，source/预算/数值门执行前锁；内部FK调用也需计，API不适用先停不扩大。
- 执行前明确代数sum预算由提案54改60，用3pose×(zero+17basis+固定mixed+常旋转mixed)=60，增加独立3D混合/协变case，并非失败后放预算。固定mixed和Q见父message。
- 每pose I_locked/Aq/Awheel/Aguide/Ac/Adelta和条件ratio输出，不选轨迹/gain/h第三range；phase0仅syntheticfixture，rotor未盲加，原Source不改。SI1e-8abs+1e-10rel代数自洽门预锁，不是实际物理误差界。
- 0MuJoCo boot/forward/RNE/integrator/PHY/旧raw/DR/H5/mesh/Git/newagent，0旧QA重跑；做好后等父，无自动物理。任务当前pending，不填未来数值。

C正式因果报告已收，父随后给同C一个新只读 R62_DRIVER_HEADROOM_SAVED_V1：仅saved EXTRACTED/FACTS七PRE小窗及必要driver小源，若明确同stage signed6速度domain，则重建原signedDC wheel box/no-load比例、first/nexthard τ相对界；1e-9Nm仅公式一致门。父“下一tick正τ可能是no-load超速mandatory-brake”仍待证，不能从τ反解ω/缺数据补值，不再raw扫描；输出<=45行。不是raw-PD/内部clipmask或硬件测力证据，缺域则UNKNOWN停。这个任务pending，无新PHY/旧QA/参数。

下一步收C saved-headroom和model新零步系数；不因名义/几何815检查/系数自洽虚增鲁棒资格。全goal未complete，当前无父running相关job，PHY仍0新增。
