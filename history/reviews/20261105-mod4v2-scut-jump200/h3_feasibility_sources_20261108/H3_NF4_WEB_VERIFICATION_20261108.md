# H3-NF4模型卡网页核验说明

日期：2026-11-08，Asia/Shanghai。

出处：https://huggingface.co/DiffSynth-Studio/MiniMax-H3-NF4

网页读取工具成功打开模型卡，定位Training Code内的消费级GPU段落。该段明确列举RTX4090、24GB显存、分离缓存与训练两个阶段，以及gradient checkpointing/offload。两条命令分别使用sft:data_process和sft:train任务；前者使用条件编码器/VAE，后者使用NF4主生成器。此为模型卡给出的配置声明，并非本机训练实测。

单独通过Python请求raw/main/README.md发生两次超时，均在SOURCE_FETCH_INDEX.json保留。本文是网页内容的调查摘要，不是原始模型卡下载，不声明原件字节SHA。此前保存的GitHub训练脚本为普通NF4 LoRA示例，不能单靠那个脚本证明分离缓存配方。

网页所述任务为音视频SFT，不能外推成完整MOD4长轨迹及多步采样反传已在24GB通过。
