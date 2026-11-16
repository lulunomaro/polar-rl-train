# 手动WASD播放器已打开

2026-11-17。按人类要求打开刚才64步离线副本（faec0177337a832fbce81f59aaff393ccf5173ff9287610215f0660da7b79baa）的MuJoCo交互画面与原项目WASD控制台。默认stair模式、200mm单台阶、起始暂停、前进档0.47m/s、站高指令0.4091m。下拉框可切repair10m/28360ac4或normal模式；每次切换暂停并复位。没有默认模型晋升。

纯35→6 MLP，无LQR辅助、无优化器。只复用原控制台UI与按键逻辑；独立wrapper保持物理2.5ms、腿100Hz、轮400Hz、策略50Hz、原PD/电机动作计算。scene直接只读复用原评测XML，SHA见READY.json；闭链2mm只诊断，>1m及非有限保护保留。

已通过桌面读取确认两个窗口：MOD4v3 WASD · 刚才实验策略 · 200mm单台阶；MuJoCo : MOD4v3_HW300N60_SCUT_V14_semantics。截图中控制台展示faec0177、stair与PAUSED，MuJoCo显示MOD4v3高站姿。未代替用户驾驶。用户输入出现后未继续抢占焦点。

按键：P开始/暂停；W/S前后；A/D转向；Q/E站高；R复位；Space清零行走指令；Esc退出。键盘应聚焦WASD控制台，MuJoCo窗口保留原快捷键。手动试玩不计作固定回放通过率。

已有c874、原010m、原8391帧、repair10m和离线副本权重均不改写。播放器动态日志留在本目录，初始启动与选择记录独立快照归档。
