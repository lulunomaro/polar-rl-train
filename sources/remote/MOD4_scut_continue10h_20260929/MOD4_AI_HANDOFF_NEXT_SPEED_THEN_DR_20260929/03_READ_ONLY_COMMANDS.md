# 只读命令

连接：`ssh egde@10.24.4.210`。本文件不提供认证秘密。

```bash
cd /home/egde/rl_candidates/MOD4_scut_continue10h_20260929
bash /home/egde/rl_candidates/MOD4_scut_continue10h_20260929/MOD4_AI_HANDOFF_NEXT_SPEED_THEN_DR_20260929/read_live_status.sh
tail -n 60 supervisor_speed.log
tail -n 80 train_3.log
# 晋级后按status.attempt查看train_4.log，而不是一直看旧日志。
```

`read_live_status.sh` 只读取，不启动仿真、训练、评测或修改状态。

```bash
# 查看实际环境配置，不等于运行中进程已重新加载它。
cat isaac/mod4/env.json
# 实际生效配置以当前run的run_manifest.json为准。
# 确认代码指纹
sha256sum isaac/mod4/mod4_task.py isaac/mod4/mod4_env.py isaac/mod4/scut_flat_rescue.py
```

现有监督器会发回放，不要重复运行 validate_speed.py。若评测失败，先看对应.log和.error.txt，确认旧评测已退出，再用相同checkpoint/seed/配置、唯一新输出文件名重试。

界面需要重新打开时才运行 `bash start_tui.sh`，避免堆出多个终端。
