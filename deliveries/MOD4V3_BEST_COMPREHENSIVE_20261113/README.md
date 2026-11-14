# 11月13日最牛逼模型

**用户重点指定的综合优选模型：db6e9ccf。以后查找或继续训练这份综合模型，从本目录进入。**

模型所属日期为2026年11月13日；2026年11月14日按用户要求重点命名并归档。原始权重和历史实验记录保持原样。

| 身份 | 内容 |
|---|---|
| 用户名称 | **11月13日最牛逼模型** |
| 模型编号 | `stairs200_max_height_40m_20261113_005m` |
| 检查点 | 最高站姿连续200 mm登阶40分钟轮次的005m，iteration **25331** |
| 完整权重 | [model_full_ppo.pt](model_full_ppo.pt)，18,478,395字节，普通Git二进制文件 |
| SHA256 | `db6e9ccf5c6d4d05a68633fd82861d903c4c52fcc1a6dd89132e55e2a4bf1283` |
| 固定Git标签 | `best-20261113-comprehensive-db6e9ccf` |
| 接口 | actor观测35维、critic训练输入78维、动作6维；完整PPO检查点 |
| 角色 | 当前冻结综合优选、后续综合训练的初始化和回退模型 |

## 权重、配方与继续训练

- [完整PT本体](model_full_ppo.pt)：保留actor、critic、STD、Adam与RNG等原完整PPO状态；与原冻结PT逐字节一致。
- [原训练配方](PARENT_RECIPE.json)、[原启动回读](PARENT_STARTUP.json)：保存当时的环境、DR、奖励、时序、任务占比、教师保留和恢复参数。
- [原选优记录](PARENT_SELECTION.json)、[原轮次评测报告](PARENT_EVALUATION_REPORT.md)、[原来源证明](PROVENANCE.json)。这些复制件保留当时措辞，本次重点名称和用途以本页及[MODEL_IDENTITY.json](MODEL_IDENTITY.json)为准。
- [原训练源码及整轮记录](../../sources/local/MOD4V3_STAIRS_MAX_HEIGHT_40M_20261113/README.md)、[原模型登记表](../../sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/MODEL_REGISTRY.json)。

后续需要从这个模型继续训练时，使用本目录的`model_full_ppo.pt`完整恢复。这个名称固定指向上述SHA，不随最新检查点自动变化。

## 已有能力记录

| 科目 | 已有成绩 | 协议 |
|---|---:|---|
| 平地前进、后退、旋转、高低站姿 | **60/60** | MuJoCo名义工况，六项各10初态 |
| Rough-v1 L9穿越 | **173/200** | 原生PhysX完整DR，规定地形穿越 |
| Rough小陀螺 | **99/100** | 原生PhysX完整DR，首6秒存活；转速误差另计 |
| 腾空后落地与指令恢复 | **79/80** | 原生PhysX完整DR，受控空中初始化 |
| 正向连续两个200 mm台阶 | **4/5** | MuJoCo名义工况，0.42 m高度指令 |
| 保持斜向触阶并通过两阶 | **0/20** | MuJoCo名义工况，实际触阶角度判据 |
| 原生连续登阶 | **0/100** | 独立PhysX完整DR配对测试 |
| 低速卡阶后向后收腿恢复 | 尚未解决 | 最新修复学生未替换本模型 |

这些是各自已有测试的成绩，不能合并成统一通过率。0.42 m为原接口的高度指令上限。重点命名不新增实车部署验收，也不将专项教师的成绩计入本模型。

[同SHA综合父与专项教师的后续对照](../../sources/local/MOD4V3_STAIRS_SPECIALIST_TEACHER_40M_20261113/FINAL_REPORT.md) · [原生rough、旋转与落地补测](../../sources/local/MOD4V3_STAIRS_SPECIALIST_TEACHER_40M_20261113/evidence/retained_abilities_r1/REPORT.md) · [最新修复轮结论](../../sources/local/MOD4V3_REARWARD_CONTACT_REPAIR_40M_20261114/DECISION.json)
