# H1 T2-z 迁移：72 双 4090 隔离工程准备

本阶段只准备后续直接 H1 迁移。官方视觉代码作为参考路径；轻量状态 latent 候选是另一个方法，不能用其可运行性冒充原 T2-z 已可在 24GB 卡运行。当前 20k、100Hz PPO 不改，现有训练未完成前不启动 T2-z 训练。此目录由 root 统一 Git 归档，当前为 **LOCAL_PENDING_ROOT_GIT_ARCHIVE**。

唯一建议远端根目录：`/home/lc01/Zonglin Li/zonglin2/research/T2Z_H1_TRANSFER_PREP_20261025`。不占原 tasks、forensic、model、预算锁目录。子代理只访问本地及公开小型源码/模型元数据，未连接 210/72，未安装环境、下载权重、使用 GPU、推理或物理 rollout。实际远端执行仍由 root 串行安排，先等 M4 benchmark CPU/IO 释放。

## 已固定的来源与最小模型资源

- T2-z 上游 commit：`c72f051f5cffcb1f372a32bc488df273556d39b9`，Apache-2.0；`source_snapshot/` 是 14 个定向读取文件，不是完整可执行仓库。完整源在远端通过精确 commit fetch 获得，不请求已 rate limit 的 GitHub API。
- Wan：`Wan-AI/Wan2.2-TI2V-5B`，revision `921dbaf3f1674a56f47e83fb80a34bac8a8f203e`，HF 模型卡声明 Apache-2.0。
- BWM：`BLM-Lab/Boundless-World-Model`，revision `738a8d3c008e637b8b1b18d5e98a82f6de9c04aa`。HF 模型卡/API 未给 checkpoint 许可证；链接的作者代码库 LICENSE 为 Apache-2.0，但不能直接把代码许可等同于权重许可。记录 unknown，不替作者补声明。
- `WEIGHTS_MANIFEST.json` 精确列出 13 个必需文件，44,253,006,084 bytes（41.214 GiB）：Wan 三个 DiT 分片与索引、T5 文本编码器、VAE、四个 tokenizer 文件和小配置，另加 BWM `step-12000.safetensors`。两份模型均 required；不因有 BWM 而删 Wan 的初始 DiT 文件。
- 大文件使用官方 LFS SHA256，小文件用官方 git blob SHA1；实际下载完成后另算 SHA256。当前只有官方 metadata 的哈希，**权重尚未下载**。不下载 assets/examples、其他 Wan、DINO 对照或官方全任务数据/ZIP。

## 可审查的有限执行顺序

把本 engineering_agent 文本包送到隔离根目录的 `engineering_bundle/`。root 使用现有受控 transport；本包不含 transport/SSH 代码。下列命令是后续执行说明，**本地未运行这些远端步骤**；每一步独立返回，失败保存收据，不自动串联训练。

```bash
R='/home/lc01/Zonglin Li/zonglin2/research/T2Z_H1_TRANSFER_PREP_20261025'
P='/home/lc01/Zonglin Li/zonglin2/run-python.sh'
# 所有调用均由 root 在 benchmark 结束、当前资源许可后执行。
nice -n 19 "$P" "$R/engineering_bundle/scripts/prepare_isolated.py" source
nice -n 19 "$P" "$R/engineering_bundle/scripts/prepare_isolated.py" environment --command-timeout 600
nice -n 19 "$R/run-t2z-python.sh" "$R/engineering_bundle/scripts/cpu_import_interface_check.py"
# 默认每次至多1文件、180秒、2GiB新数据；未完成.part保留，下次续传。
nice -n 19 "$P" "$R/engineering_bundle/scripts/download_required.py" --manifest "$R/engineering_bundle/WEIGHTS_MANIFEST.json"
# 完成后验证收据；--verify-only 不联网也不自动补下载。
nice -n 19 "$P" "$R/engineering_bundle/scripts/download_required.py" --manifest "$R/engineering_bundle/WEIGHTS_MANIFEST.json" --verify-only
```

需要更大有限下载窗时，root 可按当时空闲容量显式设置 `--max-seconds`（10..1800）、`--max-files`（1..13）、`--max-new-bytes`（最多50GiB）。新完成文件立即校验；续传调用跳过既存完整文件以避免每次重读全部大权重，最后必须 `--verify-only` 并取得 `all_required_verified_in_this_receipt=true` 的13文件收据。脚本匿名读公开固定 URL，不读取 token/cookie、不写 HF 登录、不把凭据放 argv/日志。网络错误只保留 HTTP status/error 类型，不记 signed CDN URL。每个调用保存唯一 receipts；不得将这些收据遗漏在 root Git 补归档之外。

环境：历史发现 `/home/lc01/miniconda3` 与 `/opt/anaconda3`，默认 conda 候选为前者的 `bin/conda`。只向隔离 `bootstrap311` prefix 安装 Python3.11，再创建独立 `.venv`，使用 torch2.8.0/vision0.23.0/audio2.8.0 的官方 cu128 wheel。只允许 wheel，不静默进行 C++/CUDA 源码构建；缺 wheel 或依赖冲突就失败保留。上游很多依赖浮动，实际 resolver freeze 和 pip check 才产生环境收据；尚无经实机验证的 lock，不能称已安装或导入通过。

新 wrapper 只读用 `compat/glibc240/ld-linux-x86-64.so.2`，library path 指向现有 compat 和新 prefix，绝不借用 `envs/mod4/lib`，不改现有 `run-python.sh`、compat、原环境、系统库或驱动。无 GPU 路径（CPU导入脚本）使用空 CUDA_VISIBLE_DEVICES，不调用 cuda.is_available/device_count/nvidia-smi。若 conda/loader/Python 不符，保留失败并返回，禁止自动修主环境。

## 资源预审与未完成项

`CAPACITY_PLAN.json` 的原 25GiB guard 保留，不是另立新训练门槛。先前 free 494,235,168,768 bytes 仅父任务提供快照，不是永久可用；本地也找到 20261025 更早的 248GB 快照，不能混用为当前容量。准备峰值估算约 88.8GiB：41.214GiB权重 +20GiB环境 +15GiB wheel临时 +1GiB源码 +1GiB日志 +最大单权重11.362GB临时；下载器实际单份原地.part再rename，不主动造第二套完整 HF cache。环境/临时估算有不确定性，不是预留合同。

未来 H1 dataset50GiB、派生cache20GiB、训练检查点60GiB合计130GiB只是计划量，尚未授权分配或采集；实际视频规模/编码/保留策略由方法/数据阶段确定。原始uint8 RGB公式为 Nframes×H×W×3；10,000段×41帧×224²约61.716GB，不含动作、状态或容器。不能将稀疏回放当正式同步训练集，也不复制 canonical/raw。

历史72 driver535.54.03、系统nvcc11.8、glibc2.29（20261015）。CUDA12.x 官方 minor compatibility 下限525.60.13，但 PTX 与新特性有限制；CUDA12.8随附Linux驱动570.86.10。CPU可安装不等于该完整应用GPU可用，不能从历史cu126导入成功推断本模型cu128兼容。此阶段不探GPU或升级驱动，未来释放后的兼容性实测由单独训练准入阶段处理。

2×4090 的48GB不能作为单模型连续显存。官方 DDP 每卡复制模型/梯度/Adam，5B量级仅bf16参数约10GB十进制；若bf16梯度+两个fp32 Adam moments，总静态约60GB十进制/卡，再加激活/临时/VAE/T5；若Adam状态实际bf16则是另一种数值与约40GB量级，仍非24GB证明。精确trainable count/dtype必须按实际实现核实。官方梯度checkpoint仅减少激活；batch1/累积不减少参数/Adam，不能解静态下限。

未来候选（均未实施/未声称可运行）：先预计算固定视频VAE/T5并卸载冻结模块；对直接H1动作编码/latent分组设计明确adapter；若训练全部DiT，评审FSDP FULL_SHARD/ZeRO-3 + optimizer/parameter CPU offload与交替z更新、原checkpoint格式、梯度边界的兼容性。两卡纯分片后仍可能不fit；LoRA/冻结DiT改变训练方法，不能冒充官方全量基线。不要启用fp8、bitsandbytes或compile/PTX作为未经验证默认。

此包的 `launch_training_DISABLED.sh` 无论参数都返回64，永不启动训练。后续真实launch须现有H1完成/完整保存、两个真实GPU UUID各自释放与owner确认、正式H1数据/adapter、可审查显存策略、明确新训练GO与预算；另一张4090当前为unknown peer，不查其PID/身份/不kill，不因旧空卡快照预占。

官方来源：[T2-z固定README](https://github.com/T2-z-latent-optimization/T2-z/blob/c72f051f5cffcb1f372a32bc488df273556d39b9/README.md)、[Wan固定文件](https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B/tree/921dbaf3f1674a56f47e83fb80a34bac8a8f203e)、[BWM固定模型卡](https://huggingface.co/BLM-Lab/Boundless-World-Model/blob/738a8d3c008e637b8b1b18d5e98a82f6de9c04aa/README.md)、[作者BWM代码许可](https://github.com/boundless-large-model/boundless-world-model/blob/main/LICENSE)、[NVIDIA minor兼容](https://docs.nvidia.com/deploy/cuda-compatibility/minor-version-compatibility.html)、[CUDA12.8 release notes](https://docs.nvidia.com/cuda/archive/12.8.0/cuda-toolkit-release-notes/index.html)、[Accelerate FSDP](https://huggingface.co/docs/accelerate/en/usage_guides/fsdp)。
