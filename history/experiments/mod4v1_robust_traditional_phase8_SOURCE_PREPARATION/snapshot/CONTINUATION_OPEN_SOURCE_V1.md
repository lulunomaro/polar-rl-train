# 接续：两份开源材料启发已读，R62旧成绩不变

## 当前直接任务、目标与环境

用户直接指定 C:/Users/lulu/Downloads/SPR Balanced-infantry (1).zip 与 Qi-Q26-Leg_Robot.zip，要求“看看开源有无启发思路”。父和原两agent已实际读控制源与Qi的M/PDF，合并[启发报告](<OPEN_SOURCE_INSIGHT_V1/REPORT.md>)已正式present。父metadata-only finalize一次完成：10小文件、82个本地链接/0missing、0newPHY，主报告SHA84832c0d509edb27632c76604e260f06f08e42b053e7d6a8cd71015cba9dea36，[总receipt](<OPEN_SOURCE_INSIGHT_V1/RECEIPT.json>)已写。

随后用户问“你需要matlab来帮助你工作吗？”已18:52回答：有帮助非必需，Python NumPy/SciPy/MuJoCo可继续；复现Qi符号/离散化/LESO最需Symbolic Math Toolbox+Control System Toolbox，Simulink/MPC Toolbox暂不必。未确认已有MATLAB、未安装、未运行M。未来复现须审过后用独立新副本/输出目录，不写只读源码或旧gain。

新自动goal实读idgoal-4d4bef80-e614-432d-a8cd-8f385ef2dd7d revision10/round7/max12 active/armed，不recreate/resume/complete/blocked。cwdF:/RMPOLAR-RL；GUI63971无关。Python314 -B/BLASOMP MKL1/最多4PHYCPU，无GPU/SSH/PPO/canonical/专家index/新agents/Mnemon写。dangerfullaccess/approvaldisabled，不escalate。旧H1/H2/H4/H5/Stage1/model/gates保持；PH7真实223577994e0f750e0ae062ce9ffee204273c90a2已归档，不重复record/push。所有本轮新源/报告PH8pending。

18:28恢复时两物理agent inactive、OPEN_SOURCE目录无输出；父send_message唤醒同ID后实际开始，不把15:50..18:28两小时通知间隔算PHY或审读计算时长。仅复用C abf2088f-af10-479a-9108-202785031447与model e4e6c8f2-f08d-4df1-9150-945c804e8c2a，其余Mnemon idle children不动。

## 开源审读实际完成内容

父[inspect_archives](<OPEN_SOURCE_INSIGHT_V1/inspect_archives.py>)只列两个指定ZIP中央目录，[manifest](<OPEN_SOURCE_INSIGHT_V1/ARCHIVES_CENTRAL_DIRECTORY.json>)留entry/size/CRC，不hash大ZIP、不执行ZIP程序。SPR192257143B，21entries/15files：chassis.zip122201554B、gimbal、matlab及Futile包。Qi1514976B，仅M4711B与PDF1690184B。

### SPR：正式sealed，父已read56行报告

[报告](<OPEN_SOURCE_INSIGHT_V1/SPR/REPORT.md>) SHA01bee20bf9cfe197c2788df8e0379857f8b9077dd3bd5346ee029b6d9be17b82，37条source链接；[selected manifest](<OPEN_SOURCE_INSIGHT_V1/SPR/SELECTED_SOURCE_MANIFEST.json>) cb492ba9731227c5b4b6b86437e28b4950c3f988f7ac67e217c2cd6a40117253，[receipt](<OPEN_SOURCE_INSIGHT_V1/SPR/RECEIPT.json>) ef400638a68832f4e558e863dc015c40673c8185422a03fdbf080f2fe7468642。

- 当前ZIP外层21元数据全与旧SPR index一致，chassisCRC24706a7e；复用27旧selected文本+本次外readme，共28/218234B，旧readable/member SHA/CRC编码链留存。未重读122MB嵌套payload、不冒本次密码学全ZIP复核。
- 真active链RTOS→chassis任务→getF/jump→standing/VMC→setTp→send_task；LQR_K前if(0)不是实际参数分支。readme明确底盘妙板02、云台C板；3508轮+DM_J8009关节，不等MOD4全达妙/双板BSP。
- 跳跃按实际腿长事件推进，非全timer；0.25参考偏置用世界腿倾角(theta=(legphi0−pi/2)−bodypitch)，不抄数值。准入theta条件仍comment，无H0/轮速准入证书。
- JumpFlyFlag从伸腿起点可能仍接地即true，气弹簧软件补偿清零沿F→leg_force→关节输出真实可达；机械弹簧保留。符号、左右交叉引用、几何J须重建。
- KNN离地分支确清wheel current、改腿theta/thetadot Tp；661/662每轮先清Fn_flag，JumpFlag&&otherFlag不独立保证air。目标signedDC跨no_load后0可能不合法，不能直接保证真实零τ。
- Fn是控制F/Tp加惯性模型非实测，KNN训练作者自述不佳，220计数为特定条件累计，落地Fn条件注释，无连续触地/无跳变capture或通用timeout资格。默认UNKNOWN/cap不提升。
- 功率分平衡/移动/转向优先级可借，实际预算差值/分母/Right_Leg字段错误不照抄，无完整signed速度/实际施加antiwindup。Racc=1e12、未见air拒轮测量/完整杆臂同步，不能拿它倒退替现有V4。
- activeMPC.c仅31行init；Futile/LinearMPC/Tiny是作者尝试说明，不等提供主链约束求解。没有270/完整RM/hardware新资格。

### Qi：父已read M157行、PDF文字全部749行/17页，正文51行已读

[源码](<OPEN_SOURCE_INSIGHT_V1/QI_Q26/source/Qi-Q26-Leg_Robot/LQR_calc.m>)、[原PDF](<OPEN_SOURCE_INSIGHT_V1/QI_Q26/source/Qi-Q26-Leg_Robot/山东理工大学轮足机器人腿长建模及LESO观测器开源.pdf>)、[文字](<OPEN_SOURCE_INSIGHT_V1/QI_Q26/PDF_TEXT.txt>)、[Qi报告](<OPEN_SOURCE_INSIGHT_V1/QI_Q26/REPORT.md>)。正式MANIFEST/receipt已18:59完成并通知：REPORT51行/8907B SHA699ba49ec3650f40c4582ceb4ce1765f9e9f303d4dd460c0d26240559d801748；MANIFEST3412B SHA190fad9d50b617aaea72f955d39946fcb25d3c0b360161e0f79412cb2275f28a，receipt COMPLETE。唯一privatepreview已条件清理。关闭时发现逻辑LF文本25546B与实际Windows CRLF26295B的SHA差异，一次LF规范化诊断吻合，两种SHA同时披露，原text/旧metadata未改；这是管理metadata事件不是source或机器人失败。

- PDF因>1MiB父明确单次例外<=3MiB，文本<=2MiB(实际25546B)；只用现有PyMuPDF文字。Office/office-render均已load，child报告称用安装Office PDFium按skill看p4/8/14，父只读text不冒自己已看图。privatepreview应清理，只留文字/metadata。
- PDF model x=[roll,rolldot,H,Hdot], u=[FNleft,FNright]，合支撑/差支撑→VMC，与LQR摆角/轮τ并行，避免独立legPID与rollPID冲突。适用支撑域，非全3D空中momentum控制。
- N15×10ms=.15s腿MPC与LQR+LESO1ms分层。无C++QP/main/tasks或4生成函数，Linux<1ms只是作者陈述不作本板WCET。
- M .1:.01:.35腿长离线6state/2input dlqr，Ae=[G H;0 I2],Be=[H;0],Ce=[I6 0]，8维LESO匹配慢变input扰动，矩阵分别三次拟合。不能拷K/极点或将requestτ当真实effective input；延迟/噪声/饱和/mandatorybrake/correlated estimated state必须处理，先ground shadow。
- PDF26kg/.16m半距与本机不同；FN绝对值/平衡mg2与再加重力FF存在表述歧义，需先厘清deltaF，防doubleG；ZOH展示是一阶近似。FN20..150/Δ30N不是目标约束，air不应有正FN下界。polyfit不保全域Schur，有界扰动导数不保证任意变化误差归零。
- PDF明确跳跃有瞬时供电不足掉电、比赛转跨阶；200mm100%是目标而非独立试验可靠率，图表/1ms/3m/s性能只作作者自述。无H0/air/landingFSM实现。

父曾用技能明示node/CLI调用--help，返回Unknown option --help exit1。父job pwsh-94820168f848412b已COLLECT，**不是render失败**；未装renderer/改环境/重试图像。Qi一次stdout GBK异常在READER_EVENTS保存，提取已持久化因此未重提取。

## 本轮可执行启发（尚未实现）

优先：起跳前状态/角动量和执行器预算 → 实际腿事件与timeout → VMC径向F/角向Tp及姿态优先分配 → 气弹簧软件FF分解 → 空中腿轮分工/landing模式仲裁。不是只把轮PD删掉或把h限幅再加大；单独coast可能失纠偏，且mandatorybrake物理保持。新研究需单改动名义flat→bar、再TRAIN配对；不可为过关削contacts/气弹簧物理或改原score。

本文用户任务只看启发，未新跑PHY/旧QA/训练/新controller。未来LQR调度/LESO或H/Roll MPC另做地面shadow，重建本机模型/测量域/实际输入与deadline；不是直接在未绑定硬件上用作者矩阵。

## R62两项新零步诊断实际关闭（更新旧接续pending）

[AIR_CENTROIDAL_COEFFICIENT_V1报告](<AIR_CENTROIDAL_COEFFICIENT_V1/REPORT.md>)父已read15行+METHOD30行+receipt主要字段，27NumPyFK(0recursive)/60body sum，0SDK/forward/RNE/step。Iyy/Ac_y/Ad_y/ratio：crouch .272437640747/.080077535237/.032326891166/−.40369488235；pushend .331253334464/.149398709074/.068981165189/−.46172530952；landingδ0 .310768782773/.126125922692/.057668937423/−.45723302706。SPD/zero/17basis/mixed/坐标协变自洽全pass，最大残差约5.57e−16，不是独立plant验证/真实reactionless路径。未知H0/自旋/phase/armature归属/softpassive/外力仍缺。REPORT SHA6e2aa42e...，receipt49ee97fe...。不自动选择第三h或gain。

[R62_DRIVER_HEADROOM_SAVED_V1报告](<R62_DRIVER_HEADROOM_SAVED_V1/REPORT.md>)父已read21行，actual signed6 PREdq与bounded d.ctrl域核对。N55.3557/S28.18532894736838/P5.775909774436091；box lo=max(−P,S(−1−v/N)),hi=min(P,S(1−v/N))，vguard±N(1+P/S)。2.3335 L/R w−53.689959/−53.808716、lo−.848141/−.787674、applied−.798005/−.787674；2.3340 w−56.779767/−56.220410、lo+.725089/+.440282、applied+.725089/+.466640。次tick两box均mandatory正制动、guard未激活。4scalaralgebra差4.44e−15<1e−9，重投影残差0。仅saved JSON/小源无raw reopen/driver执行/新PHY，不推唯一clipstage/硬件测力或碰撞因果。REPORT3e7b15e.../receipt61381a65...，只读PH8pending。

[私有compiled方向support](<PRIVATE_COLLISION_SUPPORT_V1/README.md>)已815/0、1compile/5staticforward/0integrator，仍未接runner，不重判4610。细节[上轮诊断接续](<CONTINUATION_R62_DIAGNOSTICS.md>)。当前父无running相关job；Goal未complete。Qi最后metadata已父完整read89行MANIFEST/32行receipt，82本地链接检查0missing，合并报告已present。源启发问题已完成，保持goal active；后续若推进新相位/VMC控制，应先锁设计/预算与独立case，不扩大旧资格或重跑旧trial。
