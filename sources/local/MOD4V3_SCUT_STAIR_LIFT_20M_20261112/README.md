# 从11月12日选定120m权重接续：台阶抬高底盘20分钟试验

父：Rough-v1 120m/iter24482，SHA7cc1fc6deeee3d3aba8ae8d2da31dce200079fb229a145f1cbb1cd3bfabea103。单开1200秒PPO，每300秒完整PT；不自动追加训练。开始前短原生探针无优化器更新。

保留完整DR、11类地形全部10档、20%名义/20%平地、35/78/6接口、2.5/10/20ms时序、TGS32/4、2mm单环境保护、原−1.5e²速度项与指数1.2、LR3e-5/clip0.1/3epochs/rollout24。

修改限于宽台阶上行示范：两类宽阶的50% reset从外侧平地x±3.75m、y±0.3m以可行站姿出发，面向中央；站立高度指令从0.28m按0.06m/s缓慢升至0.365～0.40m，3秒后给1.5～2.2m/s前进指令。其他reset、下行与其他地形的原指令保持。高度用原35维观测槽，既有高度奖励保留。

额外奖励：真正向中央推进到新的最远位置，并保持相对地面高度接近指令，给每米1.0的进展奖励（速率clip2.2，按step_dt积分）；从真实地形射线地面高度识别新台阶，每级一次0.5奖励。高度是相对地面，不把站上高台的世界z当成抬高底盘。来回摆动不重复领取同一段进展。原摔倒、闭链和数值保护保留。

本轮训练统计不是固定验收；轮末与父权重比较上阶、下阶和原平地能力，所有保存点和失败原件保留。配方见PLAN.json/EFFECTIVE_RECIPE.json，执行实现为support/mod4v3_ppo_v1/scut_rough_stair_lift_env.py。

## 当前结果与完整权重

已核实PPO10分36秒，5m/10m与首次完整PT已取回；远端SSH随后失联，15/20/final及完整DR原生对照待收。低阶抬高上阶保留，平地前向超速增加，未替换原命名父模型。详见[实验报告](REPORT.md)、[结构化原始结果](evidence/PARTIAL_RESULT.json)。

- [weights/model_005m.pt](weights/model_005m.pt)：iter24517，11753379字节，SHA `e9db6807bcff9c4604a2c8b493c9d9dbb4cf13298146370a8711d9d4c034294d`。
- [weights/model_010m.pt](weights/model_010m.pt)：iter24551，11753379字节，SHA `0b168a5e3cb7b903a7dc3ad9e4f9c9794b7023633b0ed5f6e403e99b5d046caa`。
- [weights/model_first_complete.pt](weights/model_first_complete.pt)：iter24483，11753379字节，SHA `7293732270cabb83381c72bb904e89e35666365e59f7cdeba76e21fcf19c5b03`。

## 后续只读原因调查

93例冻结回放已定位腿—轮闭环迁移，详见[平地超速调查](../MOD4V3_STAIR_SPEED_AUDIT_20261112/REPORT.md)。原末段训练状态仍待目标机恢复连接取回。
