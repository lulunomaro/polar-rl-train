# MOD4 原地小陀螺：正式 model21697

打开 START_SPIN4PI.bat。播放器控制窗和三维画面分别显示；点击控制窗后使用键盘。

- A / D：按住分别左转、右转，松开停车；按钮可保持自转。
- 自转滑块：1 至 4π rad/s，最高约 120 rpm。
- W / S：前进、后退。当前包仅提供直线和原地自转。
- X 或空格：停车；R：重置；P：暂停、继续。

本包固定使用已完成远端双 seed 和 final 原地终验的 model21697，SHA256 为
150f4875c17b4fb07665eea0296fa4b44655a6e0a839d5036d54cfbdda468288。
正式终验原始报告见 AUTONOMY_FINISHED.json；旧质量与滑移布尔均保留。

本机由 Isaac Sim 5.1 / Isaac Lab 2.x 执行 PhysX，MuJoCo 只显示实际 31 个刚体的姿态。
控制使用确定性 actor、名义物理，无探索噪声或平衡辅助；100Hz 控制、0.5ms 物理子步、16/4 solver 和硬件包络保持。
本机 API 兼容改动见 LOCAL_API_COMPATIBILITY.diff。本机版本回放不能代替远端终验或实车验证。

边走边转属于后续科目，不用此检查点冒充该技能。播放器不会启动 PPO 或更改远端训练、预算。
