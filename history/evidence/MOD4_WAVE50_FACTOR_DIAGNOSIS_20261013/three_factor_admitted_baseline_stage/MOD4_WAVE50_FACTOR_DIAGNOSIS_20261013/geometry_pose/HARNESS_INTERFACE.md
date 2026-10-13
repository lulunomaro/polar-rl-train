本机独立 frozen-policy 诊断接口，尚未完成 GPU 测试。

来源唯一绑定 ownmodel32396，SHA `91d428f02d27cdc6c876e30f355e1dcab6c7398042c2f240a1f177e5b3a898f4`。复用已审 Windows 物理后端，权重严格加载，绝不创建 PPO optimizer。每一 case 新独立进程，seed 20260928，默认 8 环境，其中 7 行移动、1 行站立。四向配对分别是 BODY ±0.3m/s × world ±X，初始 yaw 0 或 π。各 case 的初始全部实际逐环境 DR 参数、bias、delay 和 private RNG SHA 必须独立 CPU exact 比较后才允许称 matched。不同初始 yaw、出生一侧、BODY 指令和前平支撑完整 footprint 明确披露。

先 120 控制步 prefix 健康/速度准入，通过后再原 1500 控制步、15s 完整诊断子集。120/300/600 控制步绝非整十波证书；8 环境子集不是 80 环境原生产评测。原 50mm 峰谷十波2.406422727m、root前接近.4m、双轮1N支撑和末端200mm、原 ground/query/contact/COM/hardware/health 容差不得放松。每control原2.5ms×4、TGS32/4、完整30q和pre-reset根、raw actor action、factor action、clip6 policy action、原guarded leg targets、四次实际force、COM/速度/torque/closure/mimic均保存。原float32三角面与source几何/1600assignment严格exact，再独立CPU triangle query期待值<=1e-6。

准备好的单轴旗标互斥：`--feedback-current` 只D3当前noisy返回、原noise/bias RNG与queue仍更新；`--policy-factor` 只left_crank请求列0对齐右腿guarded input difference，原其他5列、动作delay及mechanical guard仍执行。`--sensor-clean` 仅接口预留，为多因素输入对照，不能用于单轴归因。后续新旗标必须新v2文件，不能改已消费的case源码。

只有 root 发实际 lease 且原训练已真实save-exit/shared OSlock free后，执行：

`env_isaaclab/python.exe geometry_pose/run_factor_once.py --lease ABS_LEASE_JSON --attempt ABS_UNIQUE_ATTEMPT`

父进程预launch冻结源码/lease，记录child PID/creation/argv/cwd，每15秒自身guardian，保存唯一parent load-run-save-exit成本（frozen/noPPO，canonical预算不写）。worker在任何GPU/目录前验证root lease与完整源码SHA/所有case参数，并持 `MOD4_LOCAL_WAVE50_TEMP_TRAIN_20261013/LOCAL_GPU_EXCLUSIVE.lock` 的native msvcrt锁直到app自然close退出。锁存在不是held，不删除/kill/热改。once目录与lease绝不重跑或覆盖。失败原件、full raw/成本保留，独立下一case修缺失scope；root统一全部Git归档。

当前已编译冻结worker SHA `8efad28f373947e8024b2d0424a5eb61ecc89adc36ec410f4ae8216f782d5d09`，runtime SHA `1dcd103cd9b0a1604bec85b8ac258aef360a721a4a13ccabcf4f38f0cbf68688`。未来以actual prelaunch snapshot/lease与newreceipt优先。
