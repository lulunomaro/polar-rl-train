V2/V3静态转换候选已冻结，V1及所有旧目录未改。

根可直接使用最终镜像表：OWN_STEP_REFERENCE_TABLES_V3_SIDEWALL_REPAIRED_CANDIDATE_NOT_ADMITTED.json。SHA 9069e57e627549404597be10a65891b77e10b111e3557b8a036984d90134a7db。含 ages0..300、control_dt_s=.01、packed73/mask73、phase、own joint_names30及metadata.phase_contract；rootXY与velocity槽包含独立own前进goal。basename带SIDEWALL_REPAIRED，但本次实际changed=false：数值轨迹没有变，只更正metadata标签。numpy future10接口沿用冻结V1 own_step_reference_tables_v1.py；实际接Torch/MDP与age300后的hold/boundary规则由根声明。

V1拒绝全部保留。V2首次touch在原下降age144->145的0.342354插值，不把非neutral姿态瞬间改为q0；最先轮底[.27000000022,.32259748067]m，明确单轮先到，未假装双轮同时接触。source-air直到age144的Z/R/q/Vz/omega/qd逐字保持；独立own XY前进goal按V1参数改变，真实command仍.8/request100..179/source时钟不改。

age145..165共21帧，用原OwnUsdKinematics.solve(max_iterations40及原容差)逐帧解motor/passive闭链。接触阶段20controls逐渐使wheelcenter高度趋向.27+r，rootR回identity、rootZ回spawn+.27=.607742301121。没有在flight整体加.27m，也没有直接对30joint线性插值当闭链解。全帧IK STATIC_KINEMATIC_FIT；closure最大.0001683545768m，接触后wheelbottom最低.27000000022m，无平台穿透。末端center高度偏差[.000686169,.000043425]m；受mask关节max.00462826rad，是原1mm wheel-center IK容差下near-standing，不声称字面q30全零。未观测wheelspin保留并被mask排除。

初touch的max q跳变.0220555rad，小于原source相邻两帧.0644229；接触段max q步长.0293806rad。这只是静态连续性尺度，不是motor速度/力矩合格。自己的forward goal平均1.02521m/s、峰1.37969m/s与真实.8command差异完全保留；到达前目标峰ax10.208m/s²，驱动可行pending。

按根补充要求，已用生成表重算全段前缘/后缘侧壁窗口，未重IK：双轮首次前缘cross age130，straddling130..140；左最低bottom.299855894m、右.316101469m，分别高于平台29.8559/46.1015mm，violating ages均[]。故没有实施delayed-approach修改。sidewall_forward_repair_v3.py保留严格检查和必要时的XY修复代码；其修复分支此次未执行，不冒充已测试。

已保存一项真实报告命名错误及更正：初V2 metadata.entry_masked_motor_q_abs_max实际取了全部30q，包含unobserved wheelspin1.19601；真实受mask entrymax.3192155、endmax.00462826。原源码存为contact_splice_own_IK_v2_before_metadata_review.py，原表/CPU报告未覆盖；当前module只改metadata表达式，AST其余完全相同，未重IK。最终表采用正确字段。完整source/报告SHA见索引。

严格限制：这是候选own几何参考，不是actor动作、接触证据或技能毕业。实际电机/冲量/功率、全body非穿透、single->dual真实接触、物理接触后校正与原callback成功标准均pending。source contact从未当own接触，原物理/动作/年龄/command/成功条件未改。无PT/raw/NPZ/USD/mesh资产读取，无actor/WM/physics/GPU/SSH/Git/账本操作。归档由根负责。
