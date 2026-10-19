# MOD4 混合MoE策略轻量包

本包用于集成推理，不含GUI、机器人或场地资产。要直接试玩，请使用同批 `MOD4_HybridMoE_20261020_Full.zip`。

最新完整来源：H1第16小时、E2/E3第17小时，保留原E0/W35 gate148。当前E3第18小时未闭合，不使用其中途模型。

安装Python3.12和依赖后运行：

```powershell
python -m pip install -r requirements_policy.txt
python check_package.py
python infer.py
```

程序接口：`from infer import HybridMoE`，`HybridMoE()(obs)`。输入float32 `[batch,35]`，输出已裁剪六维动作；35维语义和动作适配见 `policy/interface.json` 和 `完整使用说明_含播放器操作.md` 第二部分。动作不是扭矩。

组合策略为 `policy/hybrid_moe.onnx`，另附五个独立专家ONNX；专家单独输出需要裁剪。普通模式使用原学习门控，跳跃/恢复/自旋采用手动分派，不是新五路学习门控或动作平均。

`policy/manifest.json` 记录来源SHA、确定性导出和1400行一致性结果；本包不是技能毕业或实车认证。
