# 最新handoff：Startup V3A/B实际失败闭合，目标C6首ARM对象已生成

最新已接续到[支撑几何与C8预执行handoff](<CONTINUATION_SUPPORT_GEOMETRY_AND_TARGET_V8_PREEXEC.md>)；本文件保留V3A/B与C6闭合事实。旧[StartupV2/新V3handoff](<CONTINUATION_STARTUP_V2_CLOSED_AND_V3_NEXT.md>)保留所有精确旧源与预执行协议，[本轮进度](<reports/STARTUP_DEPLOY_PROGRESS_20261104_V2.md>)是用户可读主报告。用户23:27进度问题已答，不当新问题重复答。

## 固定约束
cwdF:/RMPOLAR-RL，任务R=本目录。Python C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe -B，BLAS/OMP/MKL1，最多4外层PHYCPU；无GPU/SSH/PPO/训练canonical/其他RL工程index/新agent/Mnemon写。危险全访问、approvaldisabled，不请求escalation；Office/ACL不匹配robotics，用文件/CLI。只复用model e4e6c8f2-f08d-4df1-9150-945c804e8c2a、C abf2088f-af10-479a-9108-202785031447，其余Mnemon idle子代理忽略。
最后actualget Goal17/round9/max12 active/armed，idgoal-4d4bef80-e614-432d-a8cd-8f385ef2dd7d，不新建/resume/complete/blocked。摊卧自主起立＋真实旧工程接入是用户当前两主优先级。动量/R64仍暂停未执行。旧H1/H2/H4/H5/Stage1/原模型/增益/评分冻结。所有本阶段新工作PH10pending；PH9真实7b7d2633.../tagphase9已结束，不重record/push。完整原Goal尚未完成。

## Startup V3 proof与物理
- core [143行](<STARTUP_STAND_V3/controller.py>) SHA0a29053da9270932037889130ad514345571d222bb9d3e34c3a6ef335a9fc3b2；entryV5 dc542b53ebe0c549aa0308886e635b1176ac0718ddc2bc6f5938aeb1d43b0275；prooff8a26a9dd6fe80612ddc3231a1ba7a12ef96f9b84099545ab03ab0ca2af2d0f6。一次新368enabled/40totaldisabled/12typed/2787checks、nestedbase403/GC360另列，0PHY/旧QA；非站起。父实际read core143、entry105、REPORT12、receipt91、AST56、proof头，未重跑。
- A/B均同自然落稳front初态pitch.3836868/Z.2371387，原MuJoCo/20substeps/100HzSensor/driver与private2k支持末3s等门。A腿120/4tracking、轮阻尼；B只在VERIFY qerr<=.08/qd<=.40后latch pose-only原Kwheel，3Nm/12rad/s软反馈；两者wheel-rotation proxy>.50m INHIBIT，原ready另收紧wheelquiet<=2，不改privategate。
- A [admission40](<STARTUP_STAND_V3/front_A_admission001/PROTOCOL.json>)＋独立reviewdd23...父read19＋approval真实；jobpwsh-abbe47cf2de241b1已COLLECTEDexit0。实际[result](<results/startup_front065_tracking_v3a_nominal1/result.json>)601controls/12020PHY/27.412s，6s timeout/noBALANCE/originalgateFalse/softwareFalse。rootXY.10204844m，height+.03695452m，finalZ.27409323/pitch.60957105，guide12000/hard0。
- A分析原script首次KeyError gainRoot['q']在trace.open前0row；原脚本和错误保留。父read真实gainJSON前85行确认['gain']['q']，derive_v2只改这一访问，之后actual新A trace一次601row/physics0/大rawhash0。[A saved RESULT](<STARTUP_STAND_V3/front_A_saved_analysis001/RESULT.json>)：VERIFY referr末.070909rad而V2~.77；369实际sensor eligible(first2.31s)，非接触许可。原A result SHA8db5c3a3fffeeaee4fbaf98386ffed48016c423037d876ef117d4a4cd0682476；savedAnalysis9a14de07652f4ee98d0bb006d4b635763b4acc77a23a665c4ff89783012bc0b3。
- B [derive](<derive_startup_v3b_admission.py>)和[prepare55](<prepare_startup_tracking_front_v3b.py>)仅新ID/flags+实际A失败/eligibility条件，D=front_B_admission001/44源含A四小证据。新cfg6af394f4.../protocol7bf19eb3.../index3d22331f...；[launcher29](<launch_startup_tracking_front_v3b.py>) SHA45f452262c8ad576d392733d83aed76908d259ab009e0e09598bacb0498b589e；独立review22 SHA26b12dcbcb4ac275c4d5d0a7e86ab21c89fc31da4fe9e87372d58ca6ad334d88父actualread(长数组截尾披露)，approval写后才执行。reviewSHA是父记录，launcher未声称自身消费它。Bprep首行profileA继承注释未改，实际config/protocol/selector是B。
- B jobpwsh-906bd0c406824499已COLLECTEDexit0。[result](<results/startup_front065_tracking_v3b_nominal1/result.json>)298ctrl/5960PHY/16.479s，command2.97s因proxy>.50m INHIBIT/noBALANCE/originalgateFalse/softwareFalse；rootPOST2.98。maxTrueXY.36250709m、height+.03579377、finalZ.27293247/pitch.60144215，bodyVx.6687m/s，guide5407/hard0。不是实际XY>.5或已证打滑。父read小result1–135，尚未亲读Braw。
- 两个parent物理jobs均已collect，无parent runningPHY。Model已获新单独任务：只此B control一次<=298行，physics0/旧Araw0/大hash0/模型FK0，保存<=12关键事件/最小数值后报告，再只read现有TALL gain_delta20小q和旧WorldLeg源码给<=30行V4方法proposal。禁止新gain/参数选择、proof/FK/MuJoCo/新PHY/旧terrain失败变起立证据。当前B诊断/方案未收到，勿重复它的raw工作。

## C实际编译
- V3A/V4原各main.c真实fail依赖漏选，原物理和源码记录均保。精确补原器件头1350860B CRC9a578ca0/SHAa0e7...；V5纯metadata仅发现一个原编码漏选cmsis_os.h53065B CRC61803e9e，31可能根/162C literalinclude已有路径；首null-member脚本失败和单处修复都保留。父actualreadV3A39/V4 36/V5 32。
- [V6 REPORT42](<MOD4_DEPLOYMENT_TARGET_COMPILE_V6/REPORT_V6.md>)父actualread。Header原ZIP确切一次payload53065B，SHA51420495a86c8aea829f63a156c475c225bf9c51429e0bb210eb35db0b1fd1ba；UTF8sig/GB18030失败、cp1252strict兼容而非唯一原charset；compiler raw，可读副本分离。163 argv逆变换全部true，仅新-I/输出，旧device-I保留。
- V6真实main.c armcc u6.750诊断variant exit0，object7804B SHA8f39c7f715a84fd46df710a19ec69309677b0014c542f555285527247b1a1f51；fromelf1 exit0。FILE ELF32LE/ET_REL/EM_ARM/CPU13v7EM/profile77M/Thumb2/FP6/HardFP_use1/VFPargs1/denorm2。
- 原reader只取FILE，不含18/26而gateUNKNOWN，立即停：C1/ASM0/compiler成功1/ABI认可0/161C+1ASM未启动/native2=armcc1+fromelf1/0link。随后saved-only实际读fromelf尾发现SECTION函数4/5/6明确wchar2/enum策略1，intrinsic1/2/3另align/optim。不是整体缺tag或已证不兼容。原reader/gate/argv/result/ledger不改、不重编main/不probe。REPORT73b30122.../facts8f77660c.../receipt7adbba80...均封存，无子任务runningjob。
- C已收到新STATIC_V7_SCOPE：仅现有7804B object＋保存fromelf＋旧reader，读ARM官方Addenda32/AAELF32关于FILE/SECTION/(有则SYMBOL)覆盖和省略语义，写新独立scope-aware解析，不改旧；<=4新纯解析fixture，0ARM/compile/probe/fromelf重复/link/旧QA/PHY/Git。报告逐section有效18/26/来源，不能把缺tag直接猜成编译器默认；只有后续父明确scope才准许剩余161C+1ASM继续。两worker当前running已实际list确认，别因C旧closing通知重复派发同一V7工作。

## 下一步
1. 收model一次B诊断与未执行V4方案；勿再读A/B raw补账，source新策略需父先审明确预算后单独新ID物理。
2. 收C V7静态层级属性证据，父read后决定仅继续未启动TUs；无全target/link/HIL/电机绑定/flash资格。
3. [PH10截止draft](<ARCHIVE_PHASE10_STARTUP_V3B_TARGET_V6_CUTOFF_DRAFT.json>)已写但未执行Git。待上述B诊断落盘后父finalcutoff，可封存startup至B与target至V6(排除activeV7/V4+)，再原helper一次/narrowallowlist/ownbranch+newtag，不触expertindex/main/旧tags。大raw/assets/ZIP/lib用producer元数据，未知不编，postreceipt放phase11_PENDING。
4. 目标仍active，摊卧恢复尚未通过；无背躺/侧卧/新DR技能率。原4π持续自转与停换向/270跳阶/MCUWCET/实机都独立待验。
