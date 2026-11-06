# MOD4v3 交付复查 R2

复查从原交付 ZIP 独立解压开始，305 个文件哈希一致，原始 1659 项验证仍通过。
原交付没有覆盖以下接口路径；R2 已修复并加入验证。

1. `ScutRobotView` 原先只转换 joint_pos/vel/acc/applied_torque，关节限位数组仍按运行时原顺序透传。运行时重排关节后，奖励索引会读到其它关节限位。R2 同步转换位置区间、速度上界、力矩上界和 computed_torque；front3 派生区间/上界是保守包络，不是新增实体止挡。无法等价为单关节标量的 stiffness/armature/friction 等明确报错，使用 raw.data 与原始名字读取。
2. `root_state_w`、`body_state_w`、`default_root_state` 等打包状态的四元数没有随 xyzw→wxyz 转换；R2 补齐，保持原输入不被修改，梯度保留。
3. 原动作 helper 返回解剖绝对角，没有目标端 Newton 位移转换。R2 的 decode_actions 必填 position_basis；newton_displacement 对腿目标减一次 authored ref，wheel torque/velocity 不加角偏置。使用原调用方须补参数；未热改其它聊天训练。

实际验证：

- 最终 MuJoCo/USD 验证 1706 项通过，包括新加入的全部30个USD有效关节坐标与MJCF ref，以及4个mimic初始方程。
- host72 CPU、PyTorch 2.10.0+cu128、float64、seed53 的17项检查通过：位置/逆映射/力矩gradcheck、功率守恒、随机名字重排、打包状态、Newton目标角、reward梯度。CUDA_VISIBLE_DEVICES 为空，无训练。
- 原包与R2 `/Robot` 组成后的9698属性与564关系完全一致；重新Flatten生成的USD原型内部编号与二进制SHA可能不同，不代表物理变化。MJCF SHA保持一致。
- 初始USD有效角/位移与MJCF ref最大误差3.191483520345494e-9 SI；4个mimic初始残差为0。
- SDK自带 MimicJointDemo.py 明确说明单自由度关节不依赖instance/refAxis选择，schema也说明single-DOF reference axis被忽略；因此Y轴revolute上保留rotX mimic不是本次发现的缺陷。未改mimic物理或迁移schema。
- 0.2秒直接MuJoCo同源对照最大root差1.850949948867253e-15m，最大闭链1.1794798234937382mm。
- Newton1.7的50ms CPU闭链报告继承R1实测，MJCF字节相同；本次没有重复仿真，不称R2新GPU验证。

保留边界：front3仍为需要ScutRobotView的派生坐标；MOD4缺少的两个云台与八个SCUT导轮仍明确不存在；固定参考仓库无MJCF。完整等价validator需要PROVENANCE的不可变v2来源；runtime helpers本身可移植。此包不宣称原生拓扑完全相同、PhysX/Warp GPU动力学通过、华南虎原任务可零改动运行或奖励已经收敛。

原ZIP和原失败不覆盖，R2独立发布；复查中远端广域文件搜索超时、临时USD Stage生命周期读取失败均记入review_r2报告，未作为验证结果。

R2 ZIP: F:\RMPOLAR-RL\mod4v3_scut_semantics_20261106\MOD4v3_HW300N60_SCUT_semantics_R2.zip
SHA256: a5fc953d09d05cec86e69d870ec037fd3a6ab571029425cd9c76b4c6c56b3c96
Bytes: 20615184

全部原始/新文本与大型原件索引见 ALL_FILES_INDEX.json。
