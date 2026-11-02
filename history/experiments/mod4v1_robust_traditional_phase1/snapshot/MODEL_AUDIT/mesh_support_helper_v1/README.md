# 编译轮Mesh支持包络 helper v1

## 交付与边界

- [核心helper](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MODEL_AUDIT/mesh_support_helper_v1/mesh_support.py>) 只读取已有MjModel/MjData；不创建state，不调用forward/step，也不改qpos、qvel或模型。仅用于初始化与真值几何评分，不接入可部署传感器观测。
- [静态测试脚本](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MODEL_AUDIT/mesh_support_helper_v1/test_static_forward.py>) 使用11组FK姿态＋64轮角：98次mj_forward、0physicssteps、所有data.time=0。原源/父代码未修改。
- 主MJCF SHA：`0e9ca6854285dc73465a198656fdedd992ffbf205c4ea9ed9d3ce88b905bf324`；helper SHA：`4a85694b73dc79f2a8385c0f4cadfe349ec0064caa94fe38261f4ec77581ba2e`。
- 依赖已安装NumPy/Scipy；后者只在创建helper缓存时构造每轮凸包拓扑。模型mesh顶点有变化时重建helper。两轮为源USD/MuJoCo凸包碰撞；本helper不冒称适用于SDF/非凸三角碰撞。

## 接口

```python
from MODEL_AUDIT.mesh_support_helper_v1.mesh_support import (
    TireMeshSupport, StepPatch,
)

support = TireMeshSupport(model)  # 每个编译模型一次
# data必须已由调用者mj_forward，或来自现有物理回合的当前完整状态。
wheel = support.envelopes(data, forward_xy=(1., 0.))
left = wheel['left_tire']
# left: world_vertices / min_xyz_m / max_xyz_m /
# lowest_z_m / highest_z_m / front_x_m / rear_x_m /
# forward_min_m / forward_max_m / footprint_xy_ccw_m。

# 只在初始化时使用；绝不在已开始的物理回合中用它修正root。
hint = support.root_z_translation(data, plane_z_m=0., clearance_m=0.)
free_q = int(model.joint('floating_base').qposadr[0])
data.qpos[free_q + 2] += hint['root_dz_m']
mujoco.mj_forward(model, data)

# 精确的有限台阶投影；当前父step box为x[0,3], y[-1,1], z[0,.27]。
step = StepPatch(edge_xy=(0., 0.), forward_xy=(1., 0.),
                 width_m=2., depth_m=3., top_z_m=.270, base_z_m=0.)
score = support.step_envelope(data, step)
```

`root_dz_m = plane_z + clearance - min(所有轮mesh世界顶点z)`，是令全部轮顶点不穿平面的唯一**最小**root世界Z平移；非对称腿/roll时左右轮未必同时相切，`tire_gap_after_shift_m`与`two_tire_lowest_z_difference_m`明确返回残余差。不检查非轮碰撞，不宣称静态平衡或实际承重。

`StepPatch.forward_xy`指向台阶内部，`edge_xy`为前沿中点。`front_x_m`固定指世界X前沿；`forward_max_m`按调用者指定的水平方向。

评分返回连续余量：
- `rear_crossing_margin_m`：整个轮凸包后沿相对台阶前沿的余量。
- `leading_front_margin_m`：轮最前顶点到前沿的有符号位置。
- `entire_wheel_bottom_above_top_m`：整轮最低点相对270mm顶面的高度。
- `footprint_margins_m`、`footprint_containment_margin_m`：凸XY投影相对有限台顶矩形四边的余量。
- `z_min/max_over_top_footprint_m`：**仅轮凸包投影与有限台顶相交部分**的世界z极值，包含边/面与台阶竖直裁剪平面的交点，不用AABB角或整轮最低点替代。
- `top_clearance_where_overlapping_m`、`step_solid_z_overlap_span_m`：该相交部分相对顶面的高度/台阶实体z区间重叠跨度；投影不相交时前者为None。

包含几何boolean只是余量的数学非负判断；不新增物理验收门槛。接触力、接地/腾空、支撑类别、稳定窗口、健康条件与成功定义仍由父评分系统独立记录，helper不推断。

## Mesh PCA核定

世界顶点严格为：

```text
V_world = model.mesh_vert[vertadr:vertadr+vertnum] @
          data.geom_xmat[geom_id].reshape(3,3).T + data.geom_xpos[geom_id]
```

MuJoCo编译已把缩放、mesh质心/主轴处理到local顶点与geom变换；再次叠乘`model.mesh_pos/mesh_quat`会重复处理PCA。静态测试用提取STL的body-local原点数据，经`data.xmat/xpos`作独立oracle，最大双向顶点误差 **2.3644e-16m**。

## 快速测试

完整结果：[STATIC_FORWARD_RESULTS.json](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MODEL_AUDIT/mesh_support_helper_v1/STATIC_FORWARD_RESULTS.json>)；摘要：[QUICK_TEST_SUMMARY.json](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MODEL_AUDIT/mesh_support_helper_v1/QUICK_TEST_SUMMARY.json>)。

- 11/11静态姿态通过：neutral、多个轮角、hip/delta折叠、roll/pitch/yaw、非对称左右腿、台顶、跨前沿、台角、横向越界。
- 每姿态闭链最大误差约7.32e-13m，所有姿态均位于实际模型关节限位内。
- root-Z建议后最低轮底到目标plane的残差≤5.552e-17m。
- 有限台顶裁剪z区间与独立凸包线性规划oracle最大差≤5.552e-17m。
- neutral 64轮角精确竖向支持范围 **[0.0631550387601, 0.0636999987328]m**，不是常数0.0637m。
- `rolled`姿态左轮支持高度0.0642083001m；`partial_corner`为0.0644359015m，说明含轮宽后的倾斜支持甚至可能高于0.0637径向值。`.0637`也不是全3D包围球半径。
- 三查询组合（envelopes＋root hint＋step score）100次调用均值4.47ms；包含部分越沿精确多面裁剪，非硬实时保证。父V2可缓存实例，只在初始化调用root hint，按评分频率调用step score，不进入估计器。

原始日志：[STATIC_FORWARD_TEST_001.log](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MODEL_AUDIT/mesh_support_helper_v1/STATIC_FORWARD_TEST_001.log>)。本helper第一次测试即通过，failures=[]；测试中的1e-7/1e-10断言仅是独立数值oracle的浮点一致性检查，不是新物理验收门槛。
