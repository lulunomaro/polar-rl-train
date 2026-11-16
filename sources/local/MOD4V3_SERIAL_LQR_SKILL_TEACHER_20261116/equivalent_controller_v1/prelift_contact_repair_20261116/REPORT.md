# MOD4v3 200mm前段接触与参考修复：单例候选，动作质量未验收

记录时间：2026-11-16 19:22 +08:00。仅标准起点200mm，学生优化器/PPO更新0；未扩三/五起点矩阵，默认c874不变。

## 当前结论

前段姿态与触发位置明显改善，但整体动作目标未完成、教师未合格。清理版step200_prelift_candidate_clean_center_v2与较早6.64°候选的qpos、完整trace和动作逐帧相同；登台评分通过不等于动作质量通过。

| 指标 | 源端独立复现 | MOD4原始基线 | MOD4前段候选 |
|---|---:|---:|---:|
| 实际入阶速度，m/s | 0.530 | 0.518 | 0.518 |
| 碰阶至lift前俯仰峰值，° | 1.248 | 7.054 | 2.824 |
| 首个lift记录时间，s | 4.407 | 4.320 | 4.400 |
| 首个lift记录基座X，m | 1.32838 | 1.28738 | 1.32589 |
| 首个lift记录俯仰，° | +0.836 | +6.422 | -1.378 |
| lift执行前最后一帧速度，m/s | 0.516 | 0.509 | 0.392 |
| 首个lift记录速度，m/s | 0.516 | 0.332 | 0.276 |
| 首个lift记录基座Z，m | 0.38118 | 0.38224 | 0.37915 |
| 爬台window俯仰峰值，° | 14.452 | 16.658 | 6.644 |
| lift至capture基座前移，mm | +83.56 | -7.97 | -9.28 |
| window最小前向速度，m/s | -0.004 | -0.186 | -0.208 |
| 连续登台稳定，s | 5.126 | 5.260 | 4.460 |

X/Z为基座原点，控制门控使用全系统COM相对触阶平面的距离。源端采样1ms、MOD4采样20ms，首个lift记录均为执行后记录，因此另列执行前速度。视频按真实时间1x、首次接触对齐；不是严格等速成功配对。源端是独立复现，不能冒称用户先前手动回放。旧严格配速源端失败继续保留在motion_quality_audit_20261116/source_matched_entry/。

剩余问题：候选入lift前仍丢速，抬轮/落轮期间仍短暂后退，正向动量路径尚未对齐；基座也没有保持得更高。不得宣称“无停滞反摔动作已修好”，不得进入示范池/蒸馏。当前仅保留前段定位候选，不晋升默认教师或模型。

## 保留的前段实现

1. NativeContacts在400Hz积分真实轮-环境接触，沿用4ms确认/6ms释放/12ms轮矩爬升；50Hz只读其物理时间状态。记录证明部分空档确实持续20–32ms，不能全部称为虚假断触。
2. 对已真实触碰的环境几何估计微分离，保持宽度由测得法向碰撞速度乘原有接触稳定时间计算。原始接触、几何接近估计、实测力分别保留；墙面/近接触不进入滚动里程计，wheel_odometry_valid仍要求真实向上支撑。
3. 仅idle顶墙区间用编码器qd、闭链雅可比和IMU计算腿长/世界腿角/轮架角速度，替代50Hz差分；无新演员输入。
4. 主轮轴顶墙时共同腿角必须后摆。按接触平面更新共同腿角和推进速度参考，原LQR增益、差动反馈、俯仰/偏航目标不变；不使用绝对世界X触发。
5. idle->lift增加相对触阶平面的COM支撑余量条件；已验证触阶事件等待期间保留pending，但仍要求真实导轮承载和原正向推进条件，不依赖二次冲击重新触发。

CANDIDATE_PROFILE.json明确启用参数。默认run_teacher需显式选择这些参数，不改变c874生产指针。

## 回退与失败

sampled_contact_repair_20261116的Cartesian保持期反解、contact_lift、0.323m站高、临时LQR投影等均退出在用路径。后续保留原轮侧参考、前移一拍参考、额外guide负载扣减、前段轮矩预测反解、radial-rate变体因失败或动作退化撤回，源码和原始RESULT均保留。

清理版v1因漏接geometry_gate配置而实际关闭门控，原失败保留并标CONFIGURATION_ERROR；v2恢复实际开关后逐帧复现6.64°候选。评分通过仅表示旧登台评分，不等于动作质量合格。

| 序号 | 独立ID | 评分通过 | 稳定s | 全程pitch峰值° |
|---:|---|---|---:|---:|
| 1 | step200_contact_lift_center | true | 4.94 | 18.96 |
| 2 | step200_extension_reserve_center | false | 0.00 | 59.36 |
| 3 | step200_full_hold_inverse_center | true | 4.78 | 18.07 |
| 4 | step200_sampled_inverse_center | false | 0.00 | 7.05 |
| 5 | step200_sampled_inverse_center_r2 | true | 5.34 | 17.60 |
| 6 | step200_source_vmc_sampled_center | false | 0.20 | 26.97 |
| 7 | step200_wall_projection_center | false | 0.10 | 27.48 |
| 8 | step200_blocked_exact_rate_center_v1 | true | 4.54 | 14.63 |
| 9 | step200_blocked_hold_reference_center_v1 | true | 0.48 | 27.95 |
| 10 | step200_blocked_reference_gate_center_v1 | true | 4.46 | 6.64 |
| 11 | step200_blocked_reference_no_proximity_center_v1 | false | 0.16 | 25.99 |
| 12 | step200_contact_engagement_gate_center_v1 | false | 0.00 | 7.44 |
| 13 | step200_contact_history_center_v1 | false | 0.00 | 26.24 |
| 14 | step200_encoder_contact_center_v1 | true | 5.34 | 11.34 |
| 15 | step200_guide_load_transfer_center_v1 | false | 0.18 | 26.79 |
| 16 | step200_hip_reference_wheel_drive_center_v1 | false | 0.16 | 23.07 |
| 17 | step200_prelift_candidate_clean_center | false | 0.12 | 24.71 |
| 18 | step200_prelift_candidate_clean_center_v2 | true | 4.46 | 6.64 |
| 19 | step200_prelift_support_margin_center_v1 | false | 0.00 | 7.24 |
| 20 | step200_prelift_traction_inverse_center_v1 | true | 0.72 | 17.36 |

## 验证与文件

- native_runtime.py、native_actuation.py与基线字节一致；Cartesian控制分支与StepClimb lift及后续段归一化文本一致。FINAL_SOURCE_CHECK.json确认最终源码AST与清理复测一致。
- 候选与基线场景XML同SHA256：da375549b9bf016794dcf581efca620dd98085e9ae5b1154b8795f9ad22f7d52。platform/tire碰撞参数未改。
- MOD4v3原MJCF SHA77904c…、c874/iter25362默认指针、35/78/6、原电机/PD、2.5ms/100Hz/400Hz/50Hz均不变；2mm仅诊断。
- SOURCE_BASELINE_PRELIFT_REPAIR_1X.mp4：源端、原始MOD4、前段候选同速播放；候选轨迹与清理v2相同。
- PRELIFT_COMPARISON.png：完整俯仰、速度、腿长、前移曲线，显式显示剩余后退。
- RESULTS.json：精确指标、全试错与物理/默认核对。ARTIFACT_INDEX.json：NPZ、逐帧raw、视频、图片的路径/大小/SHA。
