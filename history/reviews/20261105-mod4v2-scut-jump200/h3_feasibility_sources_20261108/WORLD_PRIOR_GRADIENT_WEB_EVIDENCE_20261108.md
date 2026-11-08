# 预训练世界知识到动作梯度：网页证据摘要

日期：2026-11-08，Asia/Shanghai。仅网页阅读与摘要，非机器人试验或原始论文完整副本。

1. Articulated Kinematics Distillation from Video Diffusion Models，CVPR2025。CVF正文与PDF直连均返回403；随后从作者托管地址 https://research.nvidia.com/labs/dir/akd/pdf/AKD_paper.pdf 成功取得正文，作者项目页 https://research.nvidia.com/labs/cosmos-lab/akd/ 同样可读。第3.2、4.3节及图2给出：关节参数控制的角色经可微渲染，预训练视频模型的SDS指导梯度回传到关节运动；该近似梯度省略对去噪器自身求Jacobian。第4.5节进一步通过Warp可微刚体模拟与PD控制优化物理跟踪。因此它不仅有动画姿态，也有简化骨架上的动力学跟踪，但不能等同于已学习MOD4的电机、机构与接触模型，也未使用H3。第5节为CogVideoX-5B、单A100-40GB、每资产10000次SDS优化约25小时；不是4090或H3测量。H3的流匹配参数化需要另外推导/验证，不能直接沿用论文v-prediction公式。

2. Cosmos Policy，原论文：https://arxiv.org/html/2601.16163v1 。第4.1–4.3节将本体状态、动作与价值编码进原生潜帧，并训练统一模型。表4的LIBERO平均成功率为完整预训练模型98.5%、移除预训练权重94.6%；实验支持视频先验的控制价值，不外推为MOD4情感动作收益。其候选采样和价值排序不能写成已通过动作梯度优化。

3. Future Representation Distillation for Imagination-Free World Action Models，DreamFree：https://arxiv.org/abs/2611.04527 。摘要提出把冻结视频模型的预测表征蒸馏进视觉编码器，再提取动作相关信息。支持控制时不必生成未来视频的设计空间；不是H3、SuperMimic式BPTT或机器人完整长动作梯度的验证。

4. H3与量化接口核验：https://github.com/MiniMax-AI/MiniMax-H3 ；https://huggingface.co/DiffSynth-Studio/MiniMax-H3-NF4 。官方H3结构说明主生成器33B及独立编码器；NF4模型卡Training Code段包含4090、24GB、分离缓存训练和offload的适配配方。该配方不是本机MOD4梯度训练测量。

5. SuperMimic作者页：https://supermimic.github.io/ 。方法说明世界模型与策略联合训练，梯度不通过仿真器；用于界定所提组合中的动力学学习部分。

这些来源在本阶段通过实际web工具打开并取得正文；历史活动占位记录不代替本次阅读。本文仅为摘要，不声明原始网页字节SHA；已保存原文的来源见SOURCE_FETCH_INDEX.json。
