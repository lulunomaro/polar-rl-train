# D10 速度推扰适应（2026-11-11）

第二轮已授权；准备源码中，父权重等待 D5 同源评测选择，尚未上传/开训。累计保留 Step7、质量、输出比例与三组材质 DR。直接调用目标机原生 push_by_setting_velocity，通过 EventManager post-step interval 触发，timer 按参考 episode reset 重采样。世界 XY 加性速度增量每轴 ±0.25 m/s、每 env 5–10s；z/角速度保持。评测安排推扰前/恢复/恢复后稳定窗口。
