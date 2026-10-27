X/VX修正候选已冻结。最终文件 MOD4_OWN_BALLISTIC_HORIZONTAL_REFERENCE_V1_NOT_ADMITTED.json，731029bytes，SHA 85a8c56924118ae6d90b7bf8165652c1a46ac5a6cff0fdde5f27789618ce8456。完整表保留root标准schema及ages0..300、packed73、mask73、joint_names与metadata；只有第0列X和第7列VX改变，旧q/Z/R/dq/Vz/omega、全部IK、mask、成功标准、动作和物理command都未改。

source接触任一false、两轮false以及own FK双轮bottom>.005的首年龄均为122；取最早标记作为保守flight122..145。它们是source/几何标记，绝非own真实takeoff证据。flight各行VX字面相同.9000000000000001m/s，AX严格0；X匀速递增，未在半空停车。

pre100从X0起，以0.2s小ramp达到v=.1385m/s后缓慢接近，全部pre-request计划平面速度<=.18、低于原ready阈值.2，最后20controls覆盖80callbacks=.2s。没有改ground_ready或was_ready，未宣称实际ready满足；其接触/姿态等其它条件待真实运行。100..122在地面计划以a3.46136m/s²加速至.9；X_air=.238885，首次touch145的X=.445885。保留公共request100..179与真实vx command.8，此轨迹只是new own goal，不施加动作或外力。

touch后0.4s以-2.25m/s²计划刹车，到age185停在X=.625885，随后至300保持X且VX0；原pose endpoint也保持。既存接触阶段q/rootZ/R不变，未重IK。

缓存FK的整段侧壁/平台检查通过：双轮前缘首次cross129，左straddle129..142最低bottom.27477856（净空4.7786mm），右129..141最低.29353505（净空23.5351mm），violating ages均[]。首次touch后完整footprint都在平台.35..1.15内，末段最大frontX=.68919251，wheelbottom最低仍.27000000022。最小pretop水平余量约60µm，只是精确参考几何结果，不能称实际安全余量或跟踪容差。

搜索仅使用既存reference/contact JSON和一次NumPy FK，缓存bounds后对vflight.8..1.25、vpre0.. .18小网格做线性位置约束。没有旧static261 rerun、IK、USD/mesh资产、raw/NPZ/PT、actor/physics/GPU/SSH/Git/账本操作。本轮没有失败；原非恒速表和旧拒绝完整保留在旧目录，source SHA均已索引。

待验证的是实际地面加速/驱动/力矩/功率、系统CoM/动量和真实接触/恢复，以及全body碰撞；参考满足root-X恒速不等于多体系统动力学已合格。root应以新referenceSHA重pin，不使用旧半空变速X曲线，并保留原physical callback技能标准。普通归档由root负责。
