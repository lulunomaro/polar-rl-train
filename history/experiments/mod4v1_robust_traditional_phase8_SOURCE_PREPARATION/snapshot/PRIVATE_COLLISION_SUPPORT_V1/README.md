# 私有方向几何包络：编译碰撞shape，不是控制输入

本模块只补充后续评估，**不重跑或重改R62任一分数/阈值**。R62 seed4610旧球包络证书仍FAIL；新工具没有该案例完整实际姿态，未反推其真实mesh净空。

## 已完成的新验证

- [预声明计划](<PLAN.json>)在执行前锁定：1次原XML编译、5次显式mj_forward静态几何姿态、0积分器/episode，不是五个物理跳跃。
- [核心](<support.py>)仅NumPy读取已缓存geom_xpos/xmat，构造后不调用MuJoCo，也不改状态；[新验证](<validate_once.py>)一次运行，结果[815检查/0失败](<validation001/RESULT.json>)。支撑点/角点/端球独立构造最大差4.440892098500626e-16m，原预算2e-12m；不声称形式区间误差证明。
- 真实编译模型nbody32（含world）/ngeom312/nmesh279；原mask OR显式pair规则选择34个非world碰撞geom：8box、16capsule、2轮胎mesh、8guide-cylinder。sphere/ellipsoid另有synthetic支持点验证。
- 5姿态仅改变静态root变换、保持原qpos0其他坐标；不是已约束可行平衡/动态轨迹。计算前后qpos/qvel/ctrl/geom缓存字节不变，time0；所有方向极值被原compiled-rbound球界包住。两轮与旧TireMeshSupport几何接口在本次新姿态逐方向相同；未重跑旧sealed QA。
- [执行前source](<validation001/SOURCE_PREEXEC.json>)与执行后6小源SHA一致；XML SHA仍0e9ca6854285dc73465a198656fdedd992ffbf205c4ea9ed9d3ce88b905bf324。无旧raw/H5、asset重新hash用于归档、controller、model或source修改。

## 几何与使用边界

```python
from PRIVATE_COLLISION_SUPPORT_V1.support import CompiledCollisionSupport
cache = CompiledCollisionSupport(existing_model)
# caller must bind the cached transform stage correctly; no forward here
bounds = cache.bounds(existing_data, stage_time_s=cached_stage_s)
```

- mesh采用**编译后的mesh_vert，经geom_xmat/xpos只变换一次**；不重复mesh_pos/mesh_quat/scale。其他primitive为解析方向支撑，不用rolling radius或球替代其实际方向长度。
- 输出raw全体min/max、1e-8m outward数字padding、各轴argmin/argmax实际geom ID/名称、per-geom极值及原球包络，便于解释谁定义证书。
- 当前选择规则与旧grade_rows一致、依赖当前场景“非world皆机器人”；不是通用多机器人selector。新增几何/模型数据变化须重新构造缓存；同尺寸其他模型不能混用。
- **不包含contact margin/显式pair contact shell**，也不算接触/穿透/支承/稳定。compiled vertex hull有方向支撑精度，但不是任意非凸shape相交算法。
- 此次未接入runner/2k writer，未执行runtime生产行/完整控制循环，也未测CPU/WCET；未来接入必须与force同一PRE缓存stage，并保留原sphere字段和原分数。可在新协议预声明独立精确几何诊断，不把它追填为旧R62通过。
- float64有限精度+数字padding不是全坐标范围的形式interval证书。unsupported/nonfinite/坏rotation输入抛错，不填0或忽略geom；未来producer故障如何中断必须单独测试并保存prefix。

状态：VALIDATED_PRIVATE_GEOMETRY_KERNEL_NOT_RUNTIME_INTEGRATED，PH8pending。815是测试断言，不是机器人试验数或鲁棒通过率。完整RM/270mm/目标板资格不增加。
