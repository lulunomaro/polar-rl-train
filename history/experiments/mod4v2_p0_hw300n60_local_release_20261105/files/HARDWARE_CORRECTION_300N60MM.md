# 最新硬件确认覆盖历史候选：300N、60mm、伸展孔中心距200mm

用户明确要求修真实小腿/连杆止挡、双主动输出连续轴，并提供300N/60mm/中心距200mm；随后已单次确认200mm为完全伸展时两安装孔中心距。因此真实缸行程是**140～200mm**。

## 必须更正此前推论

此前只按上游USD历史边界恢复gas upper +35.203334mm的第一候选，现为**superseded pre-hardware-clarification**，不发布、不覆盖、不重跑原once。原SHA/receipt和所有准备错误保留。

同源中性眼距179.3605589098706mm，对应新hardware gas_slide范围：

- 压缩端140mm → **−39.360558909870585mm**；
- 伸展端200mm → **+20.639441090129412mm**。

此前确认的wrapper数值收紧事实仍成立，但**不能再由此断言20.639mm上界对这根200mm实物弹簧过小**。新硬件规格恰对应这个伸展上界。旧截图同源反解208.153908mm与200mm硬件有8.153908mm冲突，需追查安装锚点/模型版本/所指姿态，而不是把真实缸最大长度改大来凑截图通过。v2回归应如实拒绝该超行程状态，同时验证正确行程端点与连续电机动作。

气缸最短140mm与机构低折止挡不是同一件事：低折止挡可能在缸长尚约152.6mm时已经接触，机构可行域是缸行程与真实止挡/闭链的交集；不再把CAD止挡时的gas坐标硬当气缸压缩端。

## 300N力学模型边界

按常规标称约定，把300N放在全伸展200mm端。用户没有给压缩端力、实测刚度或阻尼，因此新spec明确保留原工程近似k=2000N/m、d=3Ns/m，但**不把它标作新硬件实测参数**。位置drive目标改为`slide_max+300/k=.1706394410901294m`，两格式一致：

`F = k*(target-slide) - d*slide_velocity`。

零速伸展端300N；零速压缩端420N是该工程近似推算，不是厂家已确认数据。force_curve_calibrated=false/damping_calibrated=false独立保留；后续实测力曲线可以更新，不应再通过篡改几何行程来调力。

## 当前交付分支

- 历史第一候选：[原package](<F:/RMPOLAR-RL/mod4v2_p0_mechanical_limits_20261105/package>)与[原receipt](<F:/RMPOLAR-RL/mod4v2_p0_mechanical_limits_20261105/BUILD_RECEIPT.json>)仅供失败/假设演进追溯，runtime选择已禁用。
- 当前唯一权威：[HW300N60规格](<F:/RMPOLAR-RL/mod4v2_p0_mechanical_limits_20261105/MECHANICAL_LIMITS_SPEC_V2_HW300N60.json>)；目标独立目录`candidates/HW300N60/package`。
- 主动与跟随轴连续；被动等效止挡使用真实CAD来源的一侧值，而非旧operating extrema。rocker CAD端点元数据2e−7rad不一致以同源几何在CADδ处回算统一，不另外加经验裕度。

没有追加训练/自动迁移旧专家，旧v1和Registry保持；实际完整模型回归/PhysX/hardware状态以新receipt为准，不以本说明代替验证。
