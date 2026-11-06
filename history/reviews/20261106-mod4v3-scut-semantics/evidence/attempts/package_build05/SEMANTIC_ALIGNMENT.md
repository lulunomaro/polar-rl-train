# MOD4v3 与华南虎 V14_2 语义对应

参考来自固定 Git revision 的华南虎 USD、关节顺序、观测和奖励代码。该参考仓库无 MJCF。
下表的“对应”是机构功能与坐标定义对应，MOD4 的尺寸、惯量、硬件限位不会替换为华南虎参数。

| 华南虎关节/闭链轴 | 原 MOD4v2 | v3 接口 | 状态 |
|---|---|---|---|
| gimbal_yaw_joint | — | 明确不存在，读取报错 | absent_on_MOD4 |
| gimbal_pitch_joint | — | 明确不存在，读取报错 | absent_on_MOD4 |
| left_bottom1_guide_joint | — | 明确不存在，读取报错 | absent_on_MOD4 |
| left_bottom2_guide_joint | guide_roller_00 | direct_native_coordinate | homologous_pivot |
| left_bottom3_guide_joint | guide_roller_01 | direct_native_coordinate | homologous_pivot |
| left_bottom4_guide_joint | — | 明确不存在，读取报错 | absent_on_MOD4 |
| left_front1_guide_joint | — | 明确不存在，读取报错 | absent_on_MOD4 |
| left_front1_joint | left_crank | direct_native_coordinate | homologous_pivot |
| left_front2_joint | left_coupler_pin | direct_native_coordinate | homologous_pivot |
| left_front3_joint | left_proximal_closure | derived_scalar_from_native_hinges | homologous_pivot_different_tree_cut |
| left_front4_joint | left_distal_pin | direct_native_coordinate | homologous_pivot |
| left_front_guide_joint | guide_roller_04 | direct_native_coordinate | homologous_pivot |
| left_rear1_joint | left_hip | direct_native_coordinate | homologous_pivot |
| left_rear2_joint | left_knee | direct_native_coordinate | homologous_pivot |
| left_rear2_guide_joint | — | 明确不存在，读取报错 | absent_on_MOD4 |
| left_wheel_joint | left_wheel_spin | direct_native_coordinate | homologous_pivot |
| left_spring1_joint | left_gas_pin | direct_native_coordinate | homologous_pivot |
| left_spring2_joint | left_gas_slide | direct_native_coordinate | homologous_pivot |
| left_rear_guide_joint | guide_roller_05 | direct_native_coordinate | homologous_pivot |
| right_bottom1_guide_joint | — | 明确不存在，读取报错 | absent_on_MOD4 |
| right_bottom2_guide_joint | guide_roller_02 | direct_native_coordinate | homologous_pivot |
| right_bottom3_guide_joint | guide_roller_03 | direct_native_coordinate | homologous_pivot |
| right_bottom4_guide_joint | — | 明确不存在，读取报错 | absent_on_MOD4 |
| right_front1_guide_joint | — | 明确不存在，读取报错 | absent_on_MOD4 |
| right_front1_joint | right_crank | direct_native_coordinate | homologous_pivot |
| right_front2_joint | right_coupler_pin | direct_native_coordinate | homologous_pivot |
| right_front3_joint | right_proximal_closure | derived_scalar_from_native_hinges | homologous_pivot_different_tree_cut |
| right_front4_joint | right_distal_pin | direct_native_coordinate | homologous_pivot |
| right_front_guide_joint | guide_roller_06 | direct_native_coordinate | homologous_pivot |
| right_rear1_joint | right_hip | direct_native_coordinate | homologous_pivot |
| right_rear2_joint | right_knee | direct_native_coordinate | homologous_pivot |
| right_rear2_guide_joint | — | 明确不存在，读取报错 | absent_on_MOD4 |
| right_wheel_joint | right_wheel_spin | direct_native_coordinate | homologous_pivot |
| right_spring1_joint | right_gas_pin | direct_native_coordinate | homologous_pivot |
| right_spring2_joint | right_gas_slide | direct_native_coordinate | homologous_pivot |
| right_rear_guide_joint | guide_roller_07 | direct_native_coordinate | homologous_pivot |
| left_f3r1_joint | left_rocker_pin | native_hinge_instead_of_reference_spherical_cut | homologous_pivot_different_tree_cut |
| left_f4r2_joint | left_distal_closure | native_spherical_loop_closure | homologous_pivot |
| left_s2r2_joint | left_gas_closure | native_spherical_loop_closure | homologous_pivot |
| right_f3r1_joint | right_rocker_pin | native_hinge_instead_of_reference_spherical_cut | homologous_pivot_different_tree_cut |
| right_f4r2_joint | right_distal_closure | native_spherical_loop_closure | homologous_pivot |
| right_s2r2_joint | right_gas_closure | native_spherical_loop_closure | homologous_pivot |

| 华南虎刚体 | 原 MOD4v2 | v3 刚体 | 状态 |
|---|---|---|---|
| base_link | chassis | base_link | homologous_role_different_dimensions |
| gimbal_yaw_link | — | — | absent_on_MOD4 |
| gimbal_pitch_link | — | — | absent_on_MOD4 |
| left_bottom1_guide_link | — | — | absent_on_MOD4 |
| left_bottom2_guide_link | guide_roller_00 | left_bottom2_guide_link | homologous_role_different_dimensions |
| left_bottom3_guide_link | guide_roller_01 | left_bottom3_guide_link | homologous_role_different_dimensions |
| left_bottom4_guide_link | — | — | absent_on_MOD4 |
| left_front1_guide_link | — | — | absent_on_MOD4 |
| left_front1_link | left_input | left_front1_link | homologous_role_different_dimensions |
| left_front2_link | left_coupler | left_front2_link | homologous_role_different_dimensions |
| left_front3_link | left_rocker | left_front3_link | homologous_role_different_dimensions |
| left_front4_link | left_distal | left_front4_link | homologous_role_different_dimensions |
| left_front_guide_link | guide_roller_04 | left_front_guide_link | homologous_role_different_dimensions |
| left_rear1_link | left_thigh | left_rear1_link | homologous_role_different_dimensions |
| left_rear2_link | left_shin | left_rear2_link | homologous_role_different_dimensions |
| left_rear2_guide_link | — | — | absent_on_MOD4 |
| left_wheel_link | left_wheel | left_wheel_link | homologous_role_different_dimensions |
| left_spring1_link | left_gas_inner | left_spring1_link | homologous_role_different_dimensions |
| left_spring2_link | left_gas_barrel | left_spring2_link | homologous_role_different_dimensions |
| left_rear_guide_link | guide_roller_05 | left_rear_guide_link | homologous_role_different_dimensions |
| right_bottom1_guide_link | — | — | absent_on_MOD4 |
| right_bottom2_guide_link | guide_roller_02 | right_bottom2_guide_link | homologous_role_different_dimensions |
| right_bottom3_guide_link | guide_roller_03 | right_bottom3_guide_link | homologous_role_different_dimensions |
| right_bottom4_guide_link | — | — | absent_on_MOD4 |
| right_front1_guide_link | — | — | absent_on_MOD4 |
| right_front1_link | right_input | right_front1_link | homologous_role_different_dimensions |
| right_front2_link | right_coupler | right_front2_link | homologous_role_different_dimensions |
| right_front3_link | right_rocker | right_front3_link | homologous_role_different_dimensions |
| right_front4_link | right_distal | right_front4_link | homologous_role_different_dimensions |
| right_front_guide_link | guide_roller_06 | right_front_guide_link | homologous_role_different_dimensions |
| right_rear1_link | right_thigh | right_rear1_link | homologous_role_different_dimensions |
| right_rear2_link | right_shin | right_rear2_link | homologous_role_different_dimensions |
| right_rear2_guide_link | — | — | absent_on_MOD4 |
| right_wheel_link | right_wheel | right_wheel_link | homologous_role_different_dimensions |
| right_spring1_link | right_gas_inner | right_spring1_link | homologous_role_different_dimensions |
| right_spring2_link | right_gas_barrel | right_spring2_link | homologous_role_different_dimensions |
| right_rear_guide_link | guide_roller_07 | right_rear_guide_link | homologous_role_different_dimensions |

## 零位与正方向

所有 hinge 均采用实体 +Y 转轴。通过对应销轴连线推导 anatomical reference frame；
v3 MJCF 使用 ref 偏移，USD 使用连杆局部帧，实体 mesh/collider/惯量反向变换抵消，原世界几何保持。
原闭链树切口保留。front3 为 front1+front2 连杆到 rocker 的相对标量：
`q_front3 = q_rear1 + q_f3r1 - q_front1 - q_front2`。位置、速度、加速度与力矩分别正确转换。
rear2 是原 knee/shin，确有对应。此前“没有 rear2”判断错误，原错误记录不改写。

## 几何量和执行时序

华南虎腿长：base-to-wheel 向量的 heading XZ 投影范数。腿角 atan2(-x,-z)。
MOD4 L0：真实 hip-to-wheel 三维范数；theta 为 atan2(x,-z)。两套量独立命名。
终止奖励读取本步最终 terminated 后再 reset；timeout 的价值自举读取 terminal observation。
非零权重项未计算必须报错。历史动作和力矩在本步计分完成后推进。

## 适用边界

37 个参考刚体、42 个参考关节/闭链轴均逐项说明；MOD4 少两个云台刚体和八个导轮刚体。
不存在项不生成假质量/假接触或零奖励。MOD4 的四个传动 follower 保留为额外显式坐标。
此包不声称原华南虎 checkpoint 可直接复用，也不声称 PPO/SuperMimic 已收敛。
