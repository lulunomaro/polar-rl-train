# AIR_REACTIONLESS_FEASIBILITY_V1 — 只读结构可行性，不是新控制器

**结论：公共31body刚体模型足以构造条件centroidal-momentum系数；尚不足以认证实际reactionless路径、选gain/h第三range或扩大旧资格。当前仅文字/公式审查，0模型实例/FK/新query/integrator/PHY。**

## 已有材料与实际缺口
- [公共常量](<../CONTACT_PROXY_NOMINAL_V1/PUBLIC_NOMINAL_CONSTANTS.json>)确有31body质量、COM、完整6惯量、body树/姿态、30joint轴/锚点、gas-slide/mimic/armature等；不是缺body inertia。fullinertia为body坐标表达的COM惯量，转到B后再加轨道项，勿重复平行轴。
- [nominal FK/J代码](<../CONTACT_PROXY_NOMINAL_V1/nominal_model.py#L72-L116>)可导出COM、R、Jcom/Jrot及闭链被动Djoint；[moving-COM代码](<../DYNAMIC_COM_MOTION_V1/com_motion.py#L91-L116>)有whole-COM与显式wheel相位修正，但均未为本提案执行。
- 旧四encoder映射把wheel_spin=0，未映射guide hinge用0，且terms显式删wheel转动负载；故**不能原封复用terms当全系统角动量**。八guide是独立hinge；其自旋速率和两wheel速率不能填0。若已验证某轴严格轴对称可去掉其相位依赖，不会去掉自旋动量。
- 闭链rocker/coupler/shin/gas/drive-mimic的nominal姿态率应由同一连续分支Djoint映射；gas内杆质量平动也进Jcom。实际soft-constraint偏差、分支/极限/奇异附近映射误差仍需界，不把理想闭链当实际完整passive状态。
- joint armature是反射广义惯量标量；其物理rotor轴/gear/body归属、是否已包含于drive-body惯量不足以单由该标量恢复。既不盲加进centroidal H，也不声称省掉后与原plant完全等价；需独立模型差异/绑定。

## 统一COM与坐标：H不是root点的简单Iyy·omega
- B取regular chassis frame，I_i^B=R_i I_i,COM R_i^T；r_G=Σm_i r_i/M，rho_i=r_i−r_G，J_G=Σm_i Jv_i/M。
- 令z含q4及显式wheel/guide独立相位，所有J均对z；Jw_i给relative BODY角速度，Jv_i给COM在B中的相对速度。
```text
I_locked = Σ [ I_i^B + m_i ((rho_i·rho_i)I − rho_i rho_i^T) ]
A        = Σ [ I_i^B Jw_i + m_i [rho_i]× (Jv_i − J_G) ]
H_G^B    = I_locked omega_B + A zdot
```
- 此式同时含link自转与COM轨道动量；整体平移从centroidal式消去，无需root world XYZ。不要把torso自身Iyy替代I_locked。
- symmetric形变q4=[h,h+delta,h,h+delta]，故B_c=[1,1,1,1]^T、B_delta=[0,1,0,1]^T；A_c=A_q B_c，A_delta=A_q B_delta。广义力是B^T tau；双hip实际力矩通道不是common-h的等价形变速度。
- pitch标量只是3D式的Y行：还含I_yx omega_x、I_yz omega_z、wheel/guide项；大roll/yaw或非对称运动不应硬归成1D。
- freeflight仅在外力矩近零时满足dH_G^B/dt+omega×H_G^B=0，即惯性系H恒定，非任意BODY H_y恒定。均匀重力关于whole COM不产生净力矩，勿额外加g补偿；接触/guide支承、气动等外力矩存在则失效。

## 可研究的轨迹结构，不作稳定gain或许可
- 平面近似下可写H_y=I_lock,yy*omega_y+A_c*hdot+A_delta*deltadot+wheel/guide项；这是可计算的nominal机械连接，不是已测参数。
- A_c*hdot+A_delta*deltadot=0只给**leg-induced增量动量零方向**，需检查两系数rank/条件数和机械可达；它不是绝对body无转动。未知初始H0、I(q)变化、wheel/guide动量都会保留omega漂移，闭合形变还可能积累姿态几何相位。
- 若目标是保持指定omega，应使用I(q)omega+A(q)zdot与完整H估计/区间相容，而非令H0=0。gyro/qd/wheel与时间/零点/轴/相位缺绑及guide spin未知时，只能做条件路径族或有界不确定，不硬填零。
- 可先研究common-h与delta协同形变、零端点形变速率及连续capture连接；气弹簧/摩擦/PD/D4/四象限速度与力矩限制决定能否跟踪，动量学本身不认证可实现性。这里未实现控制、选h范围/新gain或接入接触FSM。
- [已保存AIR表](<../AIR_PITCH_AUTHORITY_V1/REPORT.md#L17-L38>)是三pose×零速+1Nm-pair瞬时qacc；含原重力/气弹簧/armature/soft equalities，原混合单位加速度残差仍存在。它可作局部符号线索，不能反解centroidal速度系数、稳定gain、持续wheel权威或旧benchmarks失效。
- [保存RESPONSES](<../AIR_PITCH_AUTHORITY_V1/RESPONSES.json>)与frame修订保留；BODY惯性i-frame≠XBODY regular frame，不能再将未变换Y分量作gyro/chassis pitch。

## 建议另行批准的最小0-integrator验证预算（尚未执行）
1. 只用旧AIR已经预定的crouch/pushend-delta+.2/landing-delta0三public pose，不扫第三h范围、不读DR/旧raw/H5/失败事件拟合。先锁新脚本/假设/输入版本与计数。
2. ≤27次纯NumPy FK：每pose base+四active坐标central差分共9；显式独立wheel/guide列用已声明轴解析构造，phase0仅为synthetic fixture，不冒实际未知相位。
3. ≤54次代数body-sum：每pose zero+17basis（3base omega、4active rate、2wheel、8guide）；比对sum与I/A列、零速、线性叠加、I_locked对称/正定/单位及常坐标旋转一致性，报告SI残差/舍入尺度而非新增机器人验收门槛。
4. 未锁物理rotor/armature、未知H0/guide spin或phase模型时停止在reduced-model结论。此预算0SDK/modelboot/mj_forward/RNE/integrator/PHY，不重跑旧QA；如需独立引擎对照，须另获新方法/预算，不复用已有12次当通过。

## 收据与边界
仅read文件/现有表、写此提案与小receipt；未import项目/NumPy实例/运行FK/模型/query/物理，未读DR样值/真值/旧raw/H5/mesh，未改旧source/分数/范围，0Git/newagent。Office/ACL catalog无本数学提案匹配，选read/files。初始误查AIR README不存在，已改读实际REPORT/RESPONSES，未造源。PH8pending；整体Goal仍active。
