# 华南虎公开教师与伸腿站高上阶实测

2026-11-06，北京时间。人类先要求“你验证一下华南虎教师能否跳台阶”，随后追加“测试一下站着腿伸直上台阶”。本阶段实际运行华南虎原机器人、公开1000轮检查点与原动作接口，不训练或蒸馏MOD4。

## 实测结论

公开策略可以在原机器人上运动、伸腿站高，并沿其原生生成地形升高。但是本次没有证据证明它能跳上单个200mm直角台阶：已纠正已知配置差异的高站姿测试8组，0整轮越沿、0双轮落台稳定。固定检查点和有限条件的失败不构成硬件或策略绝不可能成功的证明。

伸腿测试使用原训练范围内0.38/0.42m高度命令，四档前进命令0.6/1.2/1.8/2.4m/s；保留原机器人、PD/力矩/弹簧、观测噪声/延迟和原DR。以原IK设置0.32m伸展初态，初始水平速度0，先给零速度与高度渐变，再于2.5s允许前进。24组由8平地、8五级40mm直角小阶梯、8单级200mm组成；每组11s、仅首次episode计成绩，200Hz记录真实物理状态及接触。原策略可在零速度命令时漂移，因此“先等待”不能冒称“已经站稳”。

`extended_saved02`起步前1.5–2.4s实测投影腿长多数0.30–0.33m，腿轴接近竖直；它是伸展高站姿，不是将关节强制锁直。200mm组部分双轮高度超过台面，但仍未向前整轮越沿。延伸站姿后的五级40mm台阶也未整轮到顶。

另加`standing_saved02`24组真实站稳后才允许前进：双轮各>1N、水平/竖直速度均<0.05m/s、roll/pitch<10°持续0.5s。24组均未满足，0次主动前进指令。该结果记为站稳前提未达，不能计成24次上阶失败。自由漂移碰到台阶仍保留原轨迹。

## 原生地形与200mm的区别

`native_saved03`在原inverse-mid生成器上真实运行8个首次episode，全部活到10s，多数沿地形升高。此次保存了实际三角网格。网格内部三角面倾角为0°、19.290°、26.334°，0竖直三角面；该范围排除外圈border。原高度场横向采样0.1m、约35mm高差和slope threshold0.5会形成倾斜连接，不能把地形名称stair或升高轨迹当作跳越200mm竖沿。`NATIVE_TERRAIN_GEOMETRY_SCOPE.json`的CPU源重建只是补充，主证据是`native_saved03/ACTUAL_TERRAIN.npz`实际保存网格。

## 来源与复现边界

- 作者仓库`scutrobotlab/wheeled-legged_RL`固定commit `1a26356d6f591734d4f6f666f5cead1a6925da67`。
- 检查点`pretrained/26_infantry/rough_rotation_stair/2026-07-23_16-23-21/model_1000.pt`，1,367,221B，SHA256 `d19492be858ffd431a67e5aa40afb4a4c51dc9a1c914c5c92022ed46d5868db7`。
- 导出`policy.pt`，215,122B，SHA256 `7a2ba09cb1d61ae59467bdba12f97f5b0f26f7565a2ad68ea88446da7eadfa15`。其全部actor权重与model1000逐tensor最大误差0；Identity观测归一化，35输入/6输出。
- 原USD SHA256 `48f2d53ac589391a37f3df550e8e537af3ecb5bdb6ebb632fb8c7b83fa9af325`。本地REF为b8ff79f，但任务及资产对固定commit的Git diff为空。使用本地Isaac Sim5.1、PhysX、200Hz物理/50Hz策略、RTX5070Ti Laptop；不是MOD4 Newton运行。
- 用对应保存env.yaml覆盖参数并仅调整评测场地、命令、初态、环境数和记录。最初严格字典更新拒绝None/tuple/已删除字段，兼容读取的错误和改动均保留。
- 后续发现当前源默认额外启用旧YAML未保存的gimbal heading PD及startup增益随机化，亦新增spin-translate与height clip字段。初批`matrix01/extended01/standing_gate01/native_rough02`保留并标探索，不称严格复现。`extended_saved02/standing_saved02/native_saved03`显式关闭这些未保存的新控制/事件；没有擅自修改公开源码。旧训练时完整环境commit尚不能仅靠保存YAML恢复，因此仍不称原作者当时环境逐字复现。

## 全部尝试与原错误

运行根目录为`N/scut_teacher_verify`，N=`F:/RMPOLAR-RL/mjcf_mod4_h1_archive_01a1967f_20261102/runs/mod4v2_scut_jump200_20261105`。`VERIFICATION_SUMMARY.json`列各环境首次episode成绩、真实腿长及来源。

- config01：EULA非交互启动EOF，0物理。
- config02：Kit后加载tensordict触发本机access violation，0物理；随后进程内提前导入解决。
- config03：保存配置严格合并拒绝，0物理；原错误保留。
- flat01：默认地面USD远端不可下载，0评测；改本地等摩擦平面网格。
- flat02：4原机器人10s平地运行通过接口基本检查，不能称精准速度/停车已通过。
- matrix01、extended01、standing_gate01、native_rough02为已知混合默认探索，raw完整保留。
- native_rough01：地形dict与typed config不一致，0评测；02后使用原Hf配置实例。
- extended_saved02：纠正已知新增默认后24组，单200mm8组0wholeclear。
- standing_saved02：纠正默认后24组，0满足站稳前提/0主动前进，不混进上阶成功率。
- native_saved03：纠正默认后8组原生成地形，保存实际三角面供几何判定。
- render01/02：USD实例遍历未展开，未产出图片；原日志保留。render03过密三角绘图仅精确终止本地渲染进程62308，无物理或策略重跑；改逐mesh投影轮廓，04完成。后续使用独立USD库，不启动仿真。图像为原USD几何在实际保存姿态上的投影轮廓，非相机截图；原生视觉已审阅，不能当作新物理。

本次全部新训练/optimizer/SSH为0，未接入华南虎教师蒸馏，未修改当前MOD4冻结训练包、foreign或账本。结果应支持下一步选择教师，而不是因为仓库说明称“上台阶好”就假定它是合格200mm跳跃专家。
