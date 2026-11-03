# SPR 开源启发：优先改变模式与执行器分工，不抄增益

**资格：指定ZIP中央目录复核 + 已审文本SHA复核 + 实际源码静态调用链；不是固件运行/机械验证。PH8 pending，270mm未毕业，h002/default-off与旧分数保持原样。**

## 1. 来源与本轮实际动作
- 本次指定ZIP为192257143B；当前外层21项的size/CRC/压缩方式/属性等与旧审计逐项一致；chassis容器122201554B、CRC `24706a7e`。见[当前中央目录](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/OPEN_SOURCE_INSIGHT_V1/SPR/CENTRAL_CURRENT.json>)。
- 只新读外层1450B说明并核CRC/SHA；另复用旧审计27个已提取底盘文本，共28文件/218234B，逐文件核旧readable SHA，保留原member SHA/CRC/编码链。每文件≤1MiB，总量≤12MiB。见[选中来源manifest](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/OPEN_SOURCE_INSIGHT_V1/SPR/SELECTED_SOURCE_MANIFEST.json>)。
- 这是“当前容器中央元数据→旧嵌套索引→旧成员producer SHA→本轮引用副本SHA”的可审计关联；没有重读/解压122MB容器或重算大ZIP SHA，CRC关联不冒充本轮嵌套payload密码学复验。
- 用read读取真正函数，用grep定位引用；未运行ZIP脚本/构建/README命令，未启动PHY/模型/训练/旧QA/Git/新agent，未改旧源码。对照R62数字来自父已读诊断与消息，未另开raw/H5。

## 2. 先确认真正的source-active链
- [main:128–132](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/OPEN_SOURCE_INSIGHT_V1/SPR/source/chassis/Core/Src/main.c#L128-L132>)建RTOS并开调度；[freertos:120–127](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/OPEN_SOURCE_INSIGHT_V1/SPR/source/chassis/Core/Src/freertos.c#L120-L127>)实际创建chassis/INS/send线程。
- [模式:66–70](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/OPEN_SOURCE_INSIGHT_V1/SPR/source/chassis/application/chassis_behaviour.c#L66-L70>)把mode9变成JumpFlag；[主循环:110–117](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/OPEN_SOURCE_INSIGHT_V1/SPR/source/chassis/Task/chassis_task.c#L110-L117>)按模式→反馈→设定→控制执行；[控制:329–359](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/OPEN_SOURCE_INSIGHT_V1/SPR/source/chassis/Task/chassis_task.c#L329-L359>)先get_F与LQR_K，再在STANDING调用主平衡/VMC路径。
- LQR为腿长调度，真实取[else分支:142–219](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/OPEN_SOURCE_INSIGHT_V1/SPR/source/chassis/algorithm/LQR_K.c#L142-L219>)，不是前面的`if(0)`系数。以下“active”均指源码可达，未据此声称某个固件已经实机运行。

## 3. 五条最有价值的真实机制与迁移判定

### A. 蓄力/伸展/收腿按几何事件推进：把起跳准入放到腾空之前
- **实际机制：**[jump:827–859](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/OPEN_SOURCE_INSIGHT_V1/SPR/source/chassis/Task/chassis_task.c#L827-L859>)先缩腿，双腿L≤0.16再伸展，双腿L≥0.30再收腿；不同阶段改腿长PID与JumpF。阶段名与动作不是一一同义，不能把`JumpFlyFlag`当接触传感器。
- 在伸展/收腿阶段另有[轮LQR参考偏置:631–650](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/OPEN_SOURCE_INSIGHT_V1/SPR/source/chassis/Task/chassis_task.c#L631-L650>)；但其theta是[腿绝对倾角:246–254](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/OPEN_SOURCE_INSIGHT_V1/SPR/source/chassis/Task/chassis_task.c#L246-L254>) `(leg_phi0−π/2)−body_pitch`，不是我们的body pitch，0.25偏置不作移植参数。
- **可迁移结构/需重做：**起跳阶段与几何状态绑定，比只延长air h更靠前；SPR的theta准入条件在842/852行仍为注释，未找到起跳角动量/轮速头房准入。R62在首flight已pitch−0.1124、rate−3.1087，因此重点是离地前的合法状态/冲量预算，而非声称SPR已解决该问题。
- **最小建议（未执行）：**先做独立0step状态表审查：双腿不对称、伸展未到、过大pitch-rate、轮速接近no_load时，各阶段应等待/退出何处；不拿SPR长度、角度、计数或增益替换现值。

### B. VMC与机械储能解耦：软件别在起跳时抵消自己要释放的弹簧
- **实际机制与输出闭环证据：**[get_F:898–915](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/OPEN_SOURCE_INSIGHT_V1/SPR/source/chassis/Task/chassis_task.c#L898-L915>)确实调用jump_set；[956–973](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/OPEN_SOURCE_INSIGHT_V1/SPR/source/chassis/Task/chassis_task.c#L956-L973>)计算气弹簧软件补偿，JumpFlyFlag时清零该补偿，然后进入两腿虚拟F。
- F与LQR虚拟Tp进入[leg_force调用/关节符号:737–745](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/OPEN_SOURCE_INSIGHT_V1/SPR/source/chassis/Task/chassis_task.c#L737-L745>)；[变换实现:103–111](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/OPEN_SOURCE_INSIGHT_V1/SPR/source/chassis/algorithm/leg_force.c#L103-L111>)输出两关节扭矩；[send:70–75](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/OPEN_SOURCE_INSIGHT_V1/SPR/source/chassis/Task/send_task.c#L70-L75>)确实引用set_Tp发送，不是未调用的gas_ff函数。
- **迁移边界：**Flag在L≤0.16、开始伸展时就置1，可能仍接地；清的是软件抵消项，不是关闭机械气弹簧，也不是零支撑力。左右Gas变量在F式交叉引用；生成VMC含[0.21/0.25几何与除法:54–104](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/OPEN_SOURCE_INSIGHT_V1/SPR/source/chassis/algorithm/leg_force.c#L54-L104>)，机械、支路、符号、限幅均需重建。
- **最小建议（未执行）：**用目标公开几何单独核虚功 `tau·qdot = F·Ldot + Tp·phidot`、弹簧势能/已有FF是否被重复抵消、最终关节限幅后还剩多少作用；不是由本轮源码给新gain。R62 h在22/100轴tick完全遮蔽，换成VMC也仍须做约束分配，绝非天然免饱和。

### C. 空中不用同一套轮平衡律：腿姿态与轮动量是两个分配通道
- **实际机制：**[air分支:666–731](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/OPEN_SOURCE_INSIGHT_V1/SPR/source/chassis/Task/chassis_task.c#L666-L731>)调用KNN，命中后将wheel.set_current置0，取消左右协调Tp，改为腿theta/theta-dot项的虚拟Tp；不是继续把地面全状态轮LQR原样用于空中。
- **关键限定：**[661–662](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/OPEN_SOURCE_INSIGHT_V1/SPR/source/chassis/Task/chassis_task.c#L661-L662>)先清两侧Fn_flag，因此691/712的`JumpFlyFlag&&otherFlag`在这段顺序内并非独立离地保证；真正入口依赖KNN，不可凭Flag名字承诺coast一定发生。
- **可借分工，零命令不适用：**R62两轮25个flight请求全−5.7759且后来跨no_load；提前限制轮角动量消耗比再扩h更切中结构。但目标DM3519的signed-DC box在负向超速时强制正制动，0也可能不在可行域；SPR的3508零current不可直接复制。空中腿动作只重分配系统内部角动量，不会凭空消去总角动量。
- **最小建议（未执行）：**先审“接触许可unknown/air/ground × 正反转 × box含0/不含0”的小状态表，逐通道说明合法轮策略和腿策略；对每个模式都保留最终driver域可行性，不把清轮请求等同零实际力矩。

### D. 支撑估计、预测flight、落地capture必须分清：源码是线索，不是新许可
- [支持力:537–564](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/OPEN_SOURCE_INSIGHT_V1/SPR/source/chassis/Task/chassis_task.c#L537-L564>)确有F/Tp与惯性项模型；但这些F/Tp在主控制中形成，并非这里读取力传感器/逆算实测关节扭矩。Fn与实际KNN gate是两条不同路径；FnMax=−20见[宏:56](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/OPEN_SOURCE_INSIGHT_V1/SPR/source/chassis/Task/chassis_task.h#L56>)，负阈值源注释也承认气弹簧建模偏差。
- [KNN:11–15、57–85](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/OPEN_SOURCE_INSIGHT_V1/SPR/source/chassis/algorithm/KNN.c#L57-L85>)是真标准化/邻居投票；调用端10维顺序以实际668–679行为准，不按示例注释猜。训练表本轮未提取/运行，作者在666–667行明确抱怨只在特定抱持姿态好用；投票比例不是经本机校准的接触概率。
- [软落地:862–894](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/OPEN_SOURCE_INSIGHT_V1/SPR/source/chassis/Task/chassis_task.c#L862-L894>)仍是腿长条件下累计220次调用才RETURN，Fn触地条件在876行注释；没有连续触地/通用timeout证明，也未找到与V3 h-anchor/eq0无跳变连续性等价的capture实现。
- **需重做/最小建议（未执行）：**把意图/预测/可信接触证据/落地允许混合度分字段；单腿触地、导向轮/硬件触碰、短暂反弹与unknown分别做0step迁移测试，并检验接管前后实际ref与输出连续性。R62首hard前已−0.6758rad capture、hard时−0.82094rad，不能把撞击当全部先前转动的原因；不由此提高FSM/contact cue cap。

### E. 平衡优先的功率分层值得借鉴，但不等于轮速头房或完整antiwindup
- [功率:1072–1143](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/OPEN_SOURCE_INSIGHT_V1/SPR/source/chassis/Task/chassis_task.c#L1072-L1143>)实际把平衡、移动、转向分解，并按电流×RPM/电流平方预测轮功率，试图先保留平衡。主STANDING在659行真实调用它，不是文档设想。
- **只取优先级，不取实现：**[1145–1165](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/OPEN_SOURCE_INSIGHT_V1/SPR/source/chassis/Task/chassis_task.c#L1145-L1165>)余量是预测总功率−平衡功率，不是可用预算−平衡功率；`MovePower+TurnPower`未防0；右侧误写Right_Leg.Tp而非Wheel_Right.Tp，可能连腿/分类特征都污染。仅两轮模型、绝对值形式，也不构成六轴/再生/母线边界证明。
- [轮限幅:652–656](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/OPEN_SOURCE_INSIGHT_V1/SPR/source/chassis/Task/chassis_task.c#L652-L656>)是固定Maxout；[PID:77–90](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/OPEN_SOURCE_INSIGHT_V1/SPR/source/chassis/algorithm/PID.c#L77-L90>)只有积分分离/积分与输出夹紧。已读active链未找到signed torque-speed/no_load box、轮动量预算或actual-applied回馈统一antiwindup；功率不超限也会失去同向制动力矩头房。
- **最小建议（未执行）：**先用不含0的制动box与平衡reserve不可行等小反例审查分配合同；将电源预算、转速包络、最终施加量/积分状态协调分开证明。现有未绑定电机/电池校准仍未绑定，不用SPR拟合系数填空。

## 4. 找到了什么，哪些不应当成答案
- **融合确有实现而非仅头文件：**[BMI088→QEKF/重力扣除/轴变换:77–125](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/OPEN_SOURCE_INSIGHT_V1/SPR/source/chassis/Task/INS_task.c#L77-L125>)，并有[实际残差分支:499–554](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/OPEN_SOURCE_INSIGHT_V1/SPR/source/chassis/Task/INS_task.c#L499-L554>)；不是只凭“没用卡方”的注释判断。
- 轮腿运动学速度有[实际解算:527–534](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/OPEN_SOURCE_INSIGHT_V1/SPR/source/chassis/Task/chassis_task.c#L527-L534>)，但速度KF [Racc=1e12:32–43](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/OPEN_SOURCE_INSIGHT_V1/SPR/source/chassis/Task/chassis_task.c#L32-L43>)极弱使用IMU加速度；[258–273](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/OPEN_SOURCE_INSIGHT_V1/SPR/source/chassis/Task/chassis_task.c#L258-L273>)只特判ZERO_FORCE，未见这里按air拒绝轮测量。已读融合路径也未见完整杆臂/多epoch同步契约，不应倒退替换现有V4。
- **机构差异：**SPR轮为3508电流协议/0.065m轮、四个DM_J8009关节；[反馈域:32–69](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/OPEN_SOURCE_INSIGHT_V1/SPR/source/chassis/application/CAN_receive.c#L32-L69>)、[轮宏:47–55](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/OPEN_SOURCE_INSIGHT_V1/SPR/source/chassis/Task/chassis_task.h#L47-L55>)、[关节协议范围:8–21](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/OPEN_SOURCE_INSIGHT_V1/SPR/source/chassis/application/CAN_receive.h#L8-L21>)不能当目标DM3519/DM8009P的惯量、减速、扭矩/电流与速度认证；协议范围也不是额定/峰值能力证书。
- **unused/comment/作者经验分级：**[底盘MPC全文:1–31](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/OPEN_SOURCE_INSIGHT_V1/SPR/source/chassis/algorithm/MPC.c#L1-L31>)只有A/B与矩阵init，所读主链未见调用/求解；[外层说明:3–9](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/OPEN_SOURCE_INSIGHT_V1/SPR/source/SPR%20Balanced-infantry/readme.txt#L3-L9>)把Futile列为尝试，TinyMPC未实现，作者称用过LinearMPC不等这份active底盘已有MPC约束链。本轮不读其大包、不把名字当实现。

## 5. 建议优先级与结论
**优先“起跳前状态/动量与驱动预算”以及“air/landing的腿轮分工和模式仲裁”两项独立设计审查，而非第三组h/gain搜索。** 先做上述新0step合同验证；如父随后安排TRAIN消融，每次只变一条结构、保持旧baseline与安全边界，不由这份源码推进动态资格。
SPR没有交付“270稳定、轮速包络健壮、接触可信、再生功率可行”的本轮证据。R62 nominal2/2、selected DR1/4对旧2/4照旧；源码启发与已封物理成绩分开保存。
