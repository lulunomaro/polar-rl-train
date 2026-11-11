# 全部已接入R0/R1地形截图

8类Rough＋平地保留组。来自本轮Isaac Lab实际碰撞网格顶点/面，截取每类每级一块代表性9×9m地形，在本地MuJoCo渲染。不是5cm高度场近似，也没有高度夸张；不是实时训练视窗截图。

R0/R1列指类型首次接入阶段，不代表R0已完成该类型所有level。R1对旧类型继续练习并升难度；每类独立level0–3，类型不互相变换。平地组实际固定level0，后几张图中为相同平地对照。

## 四档总览

- [Level 0 总览](rough_all_level0.png)
- [Level 1 总览](rough_all_level1.png)
- [Level 2 总览](rough_all_level2.png)
- [Level 3 总览](rough_all_level3.png)

## 每类独立大图

| 类型 | 首次接入 | level0 | level1 | level2 | level3 |
|---|---|---|---|---|---|
| 交错栅格/小凸条 | R0 | [打开](single/level0__tiny_step_rot.png) | [打开](single/level1__tiny_step_rot.png) | [打开](single/level2__tiny_step_rot.png) | [打开](single/level3__tiny_step_rot.png) |
| 正向缓坡 | R0 | [打开](single/level0__slope_for_rm_low.png) | [打开](single/level1__slope_for_rm_low.png) | [打开](single/level2__slope_for_rm_low.png) | [打开](single/level3__slope_for_rm_low.png) |
| 反向缓坡 | R0 | [打开](single/level0__inv_slope_for_rm_low.png) | [打开](single/level1__inv_slope_for_rm_low.png) | [打开](single/level2__inv_slope_for_rm_low.png) | [打开](single/level3__inv_slope_for_rm_low.png) |
| 浅正阶 | R0 | [打开](single/level0__stair_slope_for_rm_low.png) | [打开](single/level1__stair_slope_for_rm_low.png) | [打开](single/level2__stair_slope_for_rm_low.png) | [打开](single/level3__stair_slope_for_rm_low.png) |
| 中级正阶 | R1 | [打开](single/level0__stair_slope_for_rm_mid.png) | [打开](single/level1__stair_slope_for_rm_mid.png) | [打开](single/level2__stair_slope_for_rm_mid.png) | [打开](single/level3__stair_slope_for_rm_mid.png) |
| 浅反阶 | R0 | [打开](single/level0__inv_stair_slope_for_rm_low.png) | [打开](single/level1__inv_stair_slope_for_rm_low.png) | [打开](single/level2__inv_stair_slope_for_rm_low.png) | [打开](single/level3__inv_stair_slope_for_rm_low.png) |
| 中级反阶 | R1 | [打开](single/level0__inv_stair_slope_for_rm_mid.png) | [打开](single/level1__inv_stair_slope_for_rm_mid.png) | [打开](single/level2__inv_stair_slope_for_rm_mid.png) | [打开](single/level3__inv_stair_slope_for_rm_mid.png) |
| 随机起伏 | R0 | [打开](single/level0__random_uniform_for_rm.png) | [打开](single/level1__random_uniform_for_rm.png) | [打开](single/level2__random_uniform_for_rm.png) | [打开](single/level3__random_uniform_for_rm.png) |
| 平地保留组 | Flat/R0，固定level0 | [打开](single/level0__plane_for_rm_rot.png) | [打开](single/level1__plane_for_rm_rot.png) | [打开](single/level2__plane_for_rm_rot.png) | [打开](single/level3__plane_for_rm_rot.png) |

[随机起伏level3近景](single/level3__random_uniform_for_rm__close.png)；[栅格level3近景](single/level3__tiny_step_rot__close.png)。

源网格/地形列号/等级/相机及渲染脚本均在本目录保留；原始顶点/面见evidence/TERRAIN_MESHES_ALL_LEVELS.npz。R1首轮与本轮地形配方保持，当前评测只做只读网格导出，不更改训练环境。
