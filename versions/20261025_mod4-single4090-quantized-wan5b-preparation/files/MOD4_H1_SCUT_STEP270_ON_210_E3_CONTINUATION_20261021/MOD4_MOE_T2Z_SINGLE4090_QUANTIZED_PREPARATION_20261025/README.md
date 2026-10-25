# 单4090量化基座准备

人类最新范围是整套MoE混合RL的T2-z迁移，准备在双4090主机进行，但一个模型必须按单张24GB卡设计。旧13文件/44.253GB完整权重下载取消。本阶段只选一个Q8量化档，不下载其他量化档、完整T5或未量化BWM检查点。

- 模型：`QuantStack/Wan2.2-TI2V-5B-GGUF`，`Wan2.2-TI2V-5B-Q8_0.gguf`。
- 固定revision：`57437632ddd08bdcbd1508c866aa22e126ed51d2`。
- 大小：5,400,179,040 bytes；官方SHA256：`57bece983817ab2f957546683bb670f13be7d99022d45674840cd999a050ea8f`。
- 目标：72主机独立research root的`models/quantized/`；本机仅以内存转发，不另存权重副本。
- 是否完整，以`reports/Q8_WINDOWS_MEMORY_RELAY_*_RETURNED_ACTUAL.json`为准。只有完整大小、官方全SHA与GGUF header均核真，才算下载完成。部分文件不是模型成功回执。

它是Wan视觉基座。BWM的机器人动作条件和本项目的整套MoE条件需要另外接入及训练；没有下载就获得机器人预测能力的结论。原T2-z使用DiffSynth，本阶段尚未证明其完整GGUF加载、真实动作条件、latent适配或单卡峰值显存。模型文件约5GB也不等于运行只需5GB显存，后续还涉及中间激活、解码器、时长与分辨率。

`q8_frozen_linear_candidate_v1.py`是未安装的反传原型，只冻结Q8权重、给输入传梯度，backward重新解量化以避免每层保留完整浮点权重。CPU合成测试覆盖普通/带时序维度的输入，以及32维latent的非零梯度和下降的合成损失。它没有加载真实Wan/BWM、构建机器人scene或使用GPU，不能作为完整模型可用、真实适配质量或论文结果。

后续单卡验证应从batch1、受控短片段和offload/activation checkpointing开始，并记录分辨率、帧数、显存及latent梯度。量化基座迁移与原BWM初始化的T2-z要在论文中明确区分。真实RGB/action数据、full-model key映射和实际测试仍是待办，不能写成已有结果。

旧主训练、canonical预算、未知peer、物理与270mm成功标准均未修改。本轮子代理已经全部交付；从本轮结束后暂时不再调用子代理，直到人类重新允许。

来源：[量化模型卡](https://huggingface.co/QuantStack/Wan2.2-TI2V-5B-GGUF)、[固定文件与官方SHA](https://huggingface.co/QuantStack/Wan2.2-TI2V-5B-GGUF/blob/57437632ddd08bdcbd1508c866aa22e126ed51d2/Wan2.2-TI2V-5B-Q8_0.gguf)、[BWM模型卡](https://huggingface.co/BLM-Lab/Boundless-World-Model)、[公开量化线性层实现](https://github.com/city96/ComfyUI-GGUF/blob/main/ops.py)。
