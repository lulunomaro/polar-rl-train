# 预检适配失败，均0 PPO更新

1. flat60首个目录：适配hook提前导入JSON模板版运行库，但旧flat60参数提供Torch二进制模板，仿真前UnicodeDecodeError。只在新目录修正导入路径，r2真实60/60。
2. 首次2048-env PhysX预检：上传器只选择support/*.py，漏了原生rough_scut_v1_reference.json；初始化阶段FileNotFoundError，ERROR/SAFE_CLOSED和完整stdout保留native_preflight_r1。未建PPO，未启动7200s时钟。
3. 补齐上传首次尝试：SFTP普通rename不能覆盖既有本实验文件；同步退出，随后启动器重复目录断言拒绝启动。改用原子POSIX rename，仅更新本次未启动训练的实验文件。失败原始命令输出保留在对话工具记录，本页记入Git。没有重放旧训练预算。
