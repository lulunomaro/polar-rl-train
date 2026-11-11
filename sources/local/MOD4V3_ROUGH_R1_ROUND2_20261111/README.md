# R1 第二轮：原平方奖励＋完整 DR 续训

2026-11-11，用户明确授权新40分钟轮，每5分钟完整保存并检查。

- 父模型：R1_010m，iter22925，SHA `959dc6a5a0ce1b221f8f7c489437b81da3149a712a96d2b8c319a1b3c496e022`。
- 原R1速度项 `−1.5e²`，指数速度奖励权重1.2；完整DR与20%名义、20%平地保持。
- 完整PPO与已有R1地形课程状态恢复，新物理episode；4096env、LR3e-5 fixed、clip0.1、epochs3。
- MOD4、35actor/78critic/6action、物理2.5ms/PD10ms/策略20ms、TGS32/4、2mm单env闭链重置与电机包络保持。
- 本轮仍是R1浅地形/中级正反阶梯课程；R2是后续腾空落地预训练，待本轮结果判断。
- 状态：训练已结束，实际2404.901秒/iter23197，8个5分钟保存点与最终完整PT均保存；固定权重同批评测全部完成。实际启动、恢复与保存收据见evidence。

配方见 [PLAN.json](PLAN.json)，每5分钟检查见evidence/training_round，完整PT见weights。按越障进度、耗时、重置和有实际恢复机会后的跟踪评判；0.5–3s混合窗口不直接作为稳态或退化结论。

## 最高档地形截图

[正阶全景](terrain_screenshots/r1_level3_mid_overview.png)、[正阶近景](terrain_screenshots/r1_level3_mid_close.png)、[反阶全景](terrain_screenshots/r1_level3_inv_mid_overview.png)、[反阶近景](terrain_screenshots/r1_level3_inv_mid_close.png)。本地MuJoCo渲染，来自PhysX level3实际网格5cm采样重建；机器人只作比例参考，不是当前PhysX训练视窗。截图不占用远端训练GPU。源数据、渲染脚本、相机与图像SHA均保存在terrain_screenshots。

## 地图在哪个阶段训练

Rough主训练使用Isaac Lab/PhysX。Flat阶段只训平地；R0开始接入低等级栅格、坡面、浅正反阶梯和随机起伏；R1增加中级正反阶梯并使用level0–3课程。本轮是R1第二轮，启动记录时间2026-11-11 22:19:27（北京时间），恢复父模型已有课程进度。

本轮地图由Isaac Lab地形生成器和保存的华南虎地形族配方生成，共4排难度×70列、每块9×9m。环境在episode边界升降级并选择相应地块；地图整体不是一条必须一次跑完的赛道。上面的图是R1最高档level3中级正反阶梯的本地MuJoCo采样重建展示，不代表另开了MuJoCo训练。

## R0能力、权重和地形分配的准确说明

没有直接使用某份R0权重，不等于没有R0浅地形能力。R1首轮父Flat1.5_020m在当时的R0浅地形同批评测已有120/120（是首次episode原进度判据，不代表所有后续episode无reset）。R1首轮和本轮使用同一策略同时训练旧地形类型和新增中级正反阶梯，各类型内独立升难度。

实际4096环境：R0已有类型2230（54.4%）、R1新增中级正反阶1047（25.6%）、平地819（20.0%）；仅Rough组内约68.05%旧类型/31.95%新中阶。R1首轮与本轮相同，不能写成30%旧R0。旧类型在R1也会向更高level推进，不等同只复习R0最低档。

完整截图见[全部地形图](terrain_all/README.md)。

## 本轮完成与候选

优先保留r1round2_005m（iter22959，SHA0dcc15f5…）作较均衡实验候选；10m为最高实测L3穿越对照。40m不是全面最优；旧六类低档首次穿越均120/120。详情见[最终报告](FINAL_REPORT.md)、[模型选择](DECISION.md)和[PT索引](evidence/MODEL_ARCHIVE_INDEX.json)。9份不同字节完整PT，加40m/final同字节别名，全部保留Git实体；主冻结未覆盖，未开下一轮训练。
