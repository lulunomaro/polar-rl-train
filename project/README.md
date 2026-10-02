# 当前项目代码快照

`isaac/mod4` 和 `train` 是归档时正式自转生产目录的固定源码副本；映射与 SHA256 见 CURRENT_VERSION.json。完整来源包含更多运行快照，见 ../sources/remote/MOD4_scut_spin_rate_20261002。

本目录不是自动安装器。运行依赖原目标机的 Isaac Lab / Isaac Sim、PyTorch、rsl_rl 和 USD 合同/资产；版本见保存的 run_manifest。部分配置仍是原绝对路径，模型权重是外部索引，因此未经路径/版本核对不可直接运行，更不能把旧 one-shot 交接/恢复脚本直接再跑一遍。

本机播放器来源在 sources/local/mod4-onnx-mujoco-launcher-git 及 MOD4_LOCAL_LATEST_SPIN_20261003；原播放器仓库和当前窗口均未因本次归档改动。
