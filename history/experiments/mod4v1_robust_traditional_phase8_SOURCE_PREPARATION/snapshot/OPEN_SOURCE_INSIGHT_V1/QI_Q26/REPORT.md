# Qi-Q26：可借鉴的是支撑域建模、时域规划与扰动观测，不是第三组空中h增益

**只读源码/文档评审；PH8pending。** 指定ZIP仅含[M脚本](<source/Qi-Q26-Leg_Robot/LQR_calc.m>)与[17页PDF](<source/Qi-Q26-Leg_Robot/山东理工大学轮足机器人腿长建模及LESO观测器开源.pdf>)。无C/H/main/task、QP实现或生成的控制函数；因此“实际部署调用链”在本包内未闭合。PDF作者称Orange Pi C++主控＋MCU C/CAN部署，属作者工程陈述，不是本次已核实实机代码/测试。

## 1. 实际可追踪的代码链与证据等级
- M顶层：腿长网格→三条非线性动力学方程solve→零姿态Jacobian→c2d(1ms)→dlqr→8维LESO对偶place→各矩阵元素三次拟合→生成4个MATLAB函数；这是**离线设计脚本**，不是控制任务。[M:7–50](<source/Qi-Q26-Leg_Robot/LQR_calc.m#L7-L50>)、[M:53–141](<source/Qi-Q26-Leg_Robot/LQR_calc.m#L53-L141>)。
- 输出名字lqr_k_calc/leso_A_calc/leso_B_calc/leso_L_calc对应函数未打包；无证据确认谁调用、是否实际用该权重/极点或同一矩阵。未运行solve/dlqr/place/polyfit/MATLAB。
- PDF p4图1（已视觉核对）给出作者架构：关节/轮/gyro→五连杆解算＋KF速度→腿长/摆角/俯仰/速度→腿支撑力MPC与LQR+LESO摆动力矩/轮τ→VMC→电机。它是架构图，不补成缺失main调用链。[p4文字](<PDF_TEXT.txt#L110-L151>)。
- PDF p6/p12/p16性能与实机曲线只作作者报告：200mm/100%是设计指标，不能当重复试验成功率；跳跃仅给定时间腿长参考。无可检查起跳角动量调度、H0估计、air/contact FSM、完整landing状态机或电气限幅源码。[p6](<PDF_TEXT.txt#L157-L192>)、[p12](<PDF_TEXT.txt#L534-L564>)、[p16](<PDF_TEXT.txt#L713-L744>)。

## 2. 五个真实可迁移思路（每项先补绑定，以下验证均未执行）

### A. 用BODY高度/roll的支撑和差，替代相互打架的独立腿长与roll PID
- **来源：**作者明确指出独立腿长/roll PID冲突；取x=[roll,rolldot,H,Hdot]，u=[FNl,FNr]；垂直支撑和控制H，左右差控制roll；MPC支撑与摆角τ经VMC统一映射。[p1](<PDF_TEXT.txt#L4-L28>)、[p8](<PDF_TEXT.txt#L198-L274>)、[p10–11](<PDF_TEXT.txt#L516-L532>)；p8公式已视觉核对。
- **迁移：**MOD4应先表达期望BODY运动/支撑扳手，再用闭链Jᵀ与gas/passive/电机约束分配，而不是把PD腿参考变化直接当作世界竖向支撑保证。起跳前须同时审计接触域内的pitch冲量/动量和轮τ余量。
- **不照搬/缺项：**该模型只简化高度＋roll，不是我们的pitch-centroidal/3D空中模型；其M=26、I=.64、半距.16与MOD4不同。缺实际GRF/VMC源、足接触可信度、力矩/摩擦/弹簧映射。
- **最小后续验证：**另行批准后仅在public pose静态核坐标、Jᵀ虚功及FN→jointτ可行域；明确contact-unknown输出，不先跑新物理或改目标高度。

### B. 按“秒”覆盖事件的预测窗，并在QP中显式约束支撑及变化率
- **来源：**N15×Ts=.01→.15s；N15×.001仅.015s，作者因此选100Hz腿MPC＋1kHz平衡。FN范围20…150N、|ΔFN|≤30N/step。[p8–9](<PDF_TEXT.txt#L275-L340>)、[p10–11](<PDF_TEXT.txt#L340-L532>)。
- **迁移：**把起跳/空中/着陆的预计接触时域、数据年龄和动作余量纳入同一规划时间轴；同时约束GRF、jointτ、signed轮速-扭矩、总供电/制动能力，而非仅延长定时air或再放大h补偿。
- **不照搬/缺项：**其正支撑下界是支撑域假设，空中不能保留20N；没有摩擦锥、失接触、跨no-load强制制动或电池约束实现。Ts/预测窗/Δforce必须按本机重新绑定；作者1–3ms/<1ms不是本板WCET。
- **最小后续验证：**先书面列stand/push/air/landing的允许力域与事件窗口，离线用新公开矩阵/既有预算审计可行性；不借用其150N/30N数值，也不声称原MPC已支持这些新增约束。

### C. LESO只观测“匹配到输入的慢变扰动”，并使用实际施加的广义输入与正确时序
- **来源：**M确有Ae=[G H;0 I2]、Be=[H;0]、Ce=[I6 0]、place求8×6增益；PDF将两维d作为输入等效扰动，补偿LQRτ。[M:53–90](<source/Qi-Q26-Leg_Robot/LQR_calc.m#L53-L90>)、[p14–15](<PDF_TEXT.txt#L652-L712>)；p14增广/观测方程已视觉核对。
- **迁移：**可提新离线shadow研究摩擦/负载残差，但必须先绑定T/Tp与本机六电机输出侧广义τ、实际signedDC后输入、样本/滤波时刻；让饱和残差、未知接触和电机跟踪误差各自可见，设观测器域/限幅/抗windup。
- **不照搬/缺项：**假定6个原状态全部可测、d下一步近恒；我们的速度本身来自KF且有boxcar/D1/D3。不能把requestτ作为真实已施加τ，再把饱和/mandatory brake误认外扰并继续加力；LESO不是contact detector、H0或guide动量观测器。
- **最小后续验证：**先做信号域/符号/采样年龄与实际输入receipt的静态映射审查；另批准新合成有界扰动、延迟/饱和测试后才谈估计精度，勿用DR真参数抵消或旧H5选择极点。

### D. 模型随形状变化，并验证“拟合后的整体闭环”而非只存一组K
- **来源：**L0=.10:.01:.35逐点求K/Ae/Be/L，再对每元素三次拟合并导出。[M:7–22](<source/Qi-Q26-Leg_Robot/LQR_calc.m#L7-L22>)、[M:94–141](<source/Qi-Q26-Leg_Robot/LQR_calc.m#L94-L141>)。
- **迁移：**完整MOD4可研究h/δ等形状依赖的惯量、输入映射、接触域与控制矩阵；已算Ac/Adelta随pose变，仅是增量Y-row null，不能用一条常比例在未知H0下宣称reactionless。
- **不照搬/缺项：**M是6state/2input单腿近似，状态顺序[theta,dtheta,x,dx,phi,dphi]，非MOD4 state14；M参数bodyM25/Rwheel.06、Ts1ms，均非当前14.294kg fullmodel/100Hz。单腿长不完整描述双自由度闭链、气弹簧、wheel/guide自旋。
- **最小后续验证：**另批准后先查拟合残差、可观性/稳定性与插值域/端点，不能由各点dlqr成功推断三次拟合全域稳定，也不直接复制任何Q/R/K/极点或跑该M。

### E. 把起跳接触冲量/电气与着陆工作域当作前提，而非靠air小h追补
- **来源：**作者自述跳跃因关节瞬时供电不足掉电，比赛改用接触阶后规划腿长/摆角跨越；p12只展示定时腿长参考；并非证明空中pitch控制解决跳270。[p6](<PDF_TEXT.txt#L157-L192>)、[p12](<PDF_TEXT.txt#L534-L564>)。
- **迁移：**我们R62的起跳H0、whole-body接触域与轮速剩余动量/制动包络仍缺；优先提出起跳前角动量/GRF及landing可行域账本、失败保持与域切换，不再据这包材料选择第三h gain。
- **不照搬/缺项：**未提供动力电池/电流/电压/制动吸能/driver时延、空中初始动量或可核实landing/contact源码。PDF指标/比赛成绩不是独立基准，更非本机270mm、fullDR、整RM或板级资格。
- **最小后续验证：**只提案：先补电机/供电/制动/反射转子及guide相位速度边界，定义起跳和着陆域与独立真值判据；任何新动态实验须父另审方法/预算，当前不实施。

## 3. 照抄前须处理的源码/文档歧义
- p8 u写FN绝对值、平衡FN=Mg/2；p10又说MPC支撑再加重力前馈。先区分δF与absolute-F/仿射平衡项，防重复补g；p9虽称ZOH，展示Ad≈I+AT/Bd≈TsB，是一阶近似，不冒exactZOH。[p8–11](<PDF_TEXT.txt#L198-L532>)。
- M以abs(eig(Ae))*.4、下限.2、最后两个=.985构造极点；eig返回顺序不保证最后2就是d模态；并未执行/验证该排序。PDF“扰动导数有界→误差趋零”的笼统陈述并非任意时变扰动保证。[M:73–88](<source/Qi-Q26-Leg_Robot/LQR_calc.m#L73-L88>)、[p13–14](<PDF_TEXT.txt#L567-L650>)。
- 声称200mm目标100%、MVP/比赛与3m/s对照仅保留作者陈述；没有raw数据或runtime来复核样本/电气/接触门槛。[p16](<PDF_TEXT.txt#L713-L744>)。

## 4. 提取/阅读与交付边界
仅指定Qi ZIP中央目录；未hash整个ZIP。M4711B/CRC73175bf6，PDF1690184B/CRCc370a59a；PDF单次≤3MiB例外已父批准，文本25,546B<2MiB，常规文本4711B<12MiB/单1MiB；路径/symlink/解压比≤100检查，CRC读取验证与选中字节SHA见[manifest](<MANIFEST.json>)。
已用read读取M与全部17页文字；office/office-render路由后仅用现成PyMuPDF取text、安装的Office PDFium renderer看p4/8/14，无OCR猜公式。预览私有、阅读后清理；未执行ZIP脚本/MATLAB/宏/embedded命令，未安装或改变环境。一次控制台gbk打印异常已记[读者事件](<READER_EVENTS.json>)，不作PDF/机器人失败。
0模型/FK/物理/训练/旧QA/DR/H5/旧raw/Git/newagent；不动既有source/score。结论是5个可检验迁移方向，不是部署承诺或新实验批准。
