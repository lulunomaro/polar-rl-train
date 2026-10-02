# 先读这个

把 `HANDOFF_ISAAC_FIX_V2.md` 作为下一条完整任务指令交给负责 Isaac Lab/RL 的 AI。

关键结论：对方当前版本仍存在约 13 mrad 的机械限位越界，以及约 100 mm 的 MJCF/USD 高度不一致，因此暂时不能开始狗洞 PPO。包内 JSON 和 PNG 是本地 STEP B-Rep、MuJoCo 运动学与 3 秒动力学验证结果。

`scene_hard_stop_audit.xml` 是审计用派生模型，其中 meshdir 指向生成机器的本地 `chassis_mod4/assets`。换机器后应修改 meshdir，或只把它作为结构参考；不要将其直接覆盖正式模型。

SolidWorks、STEP 和原始交付包均未包含在本压缩包中，也未被修改。
