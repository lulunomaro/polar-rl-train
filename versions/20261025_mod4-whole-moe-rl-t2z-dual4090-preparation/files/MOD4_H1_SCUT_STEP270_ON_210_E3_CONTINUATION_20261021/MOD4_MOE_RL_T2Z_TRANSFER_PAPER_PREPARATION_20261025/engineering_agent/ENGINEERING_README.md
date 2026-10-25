# 整套 MoE＋RL 的 T2-z 迁移工程准备

用户已明确目标是**整个 MoE 混合 RL 的 T2-z**。H1 仅是其中一个专家。本包是新目标的独立 v1，旧 `MOD4_T2Z_H1_TRANSFER_PAPER_PREPARATION_20261025/engineering_agent` 全部保持冻结，作为范围修正前历史。旧 H1 root 尚未部署；新建议72目录为：

`/home/lc01/Zonglin Li/zonglin2/research/T2Z_MOE_RL_TRANSFER_PREP_20261025`

本次只做本地源码/元数据/registry/脚本准备，没有连接72、安装环境、下载权重、读取PT或ONNX内容、模型推理、GPU探测、物理rollout、改播放器/主训练/预算或Git操作。全部文件仍为 **LOCAL_PENDING_ROOT_GIT_ARCHIVE**。root 是唯一远端执行者，M4 collector 未结束前不部署、不安装、不下载，避免争CPU/IO。

## 可直接审查的准备包

固定 T2-z 上游 `c72f051f5cffcb1f372a32bc488df273556d39b9`。本地 `source_snapshot/` 14个小文件与 `metadata/` 从冻结H1包按字节复制，带来源SHA；仅是定向审阅快照，不是假装完整仓库。远端源码脚本使用精确commit fetch，不请求GitHub API。

`WEIGHTS_MANIFEST.json` 新MoE ID/root，保留相同13个必需官方文件、revision和digest：

- Wan `921dbaf3f1674a56f47e83fb80a34bac8a8f203e`：3个DiT分片与索引、T5、VAE、tokenizer、小配置。
- BWM `738a8d3c008e637b8b1b18d5e98a82f6de9c04aa`：`step-12000.safetensors`。
- 合计 **44,253,006,084 bytes（41.214GiB）**，两份均required。不下载assets/examples、DINO、其他Wan、官方整套任务数据或ZIP，不造重复完整HF cache。
- Wan模型卡Apache2；BWM模型卡/API未声明checkpoint许可。作者BWM代码LICENSE是Apache2，并不能替权重补声明，unknown保留。

把本工程文本包放到新root的 `engineering_bundle/`，由root在资源释放后逐步执行；不会串联启动训练：

```bash
R='/home/lc01/Zonglin Li/zonglin2/research/T2Z_MOE_RL_TRANSFER_PREP_20261025'
P='/home/lc01/Zonglin Li/zonglin2/run-python.sh'
nice -n 19 "$P" "$R/engineering_bundle/scripts/prepare_isolated.py" source
nice -n 19 "$P" "$R/engineering_bundle/scripts/prepare_isolated.py" environment --command-timeout 600
nice -n 19 "$R/run-t2z-python.sh" "$R/engineering_bundle/scripts/cpu_import_interface_check.py"
nice -n 19 "$P" "$R/engineering_bundle/scripts/check_moe_registry.py" --registry "$R/engineering_bundle/MOE_POLICY_REGISTRY.json" --outdir "$R/receipts"
nice -n 19 "$P" "$R/engineering_bundle/scripts/download_required.py" --manifest "$R/engineering_bundle/WEIGHTS_MANIFEST.json"
nice -n 19 "$P" "$R/engineering_bundle/scripts/download_required.py" --manifest "$R/engineering_bundle/WEIGHTS_MANIFEST.json" --verify-only --max-seconds 600
```

source/environment为两个独立stage。只在新root `bootstrap311` 安装Python3.11，再创建`.venv`，官方torch2.8/vision0.23/audio2.8 cu128 wheel与上游requirements；浮动依赖的实际freeze/pipcheck收据由实机生成。默认历史conda候选`/home/lc01/miniconda3/bin/conda`，缺失便失败，不自动修其他环境。只允许binarywheel，缺wheel不静默编译CUDA/C++。新wrapper只读现有`compat/glibc240/ld-linux-x86-64.so.2`并使用新prefix库，不改现有run-python/compat/系统库/driver/mod4环境。

下载每次默认180秒、1个新文件、2GiB新字节，`.part`原地续传；root可按当时资源显式给有限`--max-seconds`（10..1800）、`--max-files`（1..13）、`--max-new-bytes`（最多50GiB）。新完成文件立即大小与官方SHA校验；续传时跳过既存完整文件以免反复读大文件，最后必须verify-only收据 `all_required_verified_in_this_receipt=true`。匿名读公开URL，不token/cookie/login，不将凭据放argv/日志，网络异常不记signedCDN地址。所有安装/失败/部分下载/校验收据都需root后续归档。

CPU import隐藏设备并在该检查进程内stub CUDA可用性/设备数，禁初始化；只检查官方依赖与`dim16`小型官方动作编码器形状，不载模型。registry检查仅读JSON，14组stub-gate模式/时钟合同与非法模式负例，不做真实门控/专家推理，不冒称MoE adapter已集成。

## 整体策略接线索引

`MOE_POLICY_REGISTRY.json` 有两个明确分离的池：

| 角色 | 播放器冻结池 | 最新完整训练候选池 | 原生Hz |
|---|---|---|---:|
| E0 / W35 / gate148 | 原冻结源 | 同冻结源 | E0/W35 100 |
| H1 | pair47，Adam745740 | closed67，Adam790000 | 100 |
| E2 | cohort52，Adam839920 | 同cohort52 | 50 |
| E3 | pair47，Adam808520 | closed67，Adam837200 | 50 |

每项列真实local/已有remote路径、已有生产报告SHA、bytes与本次只读stat；不重算权重SHA。六份checkpoint总101,876,943bytes，全部local路径存在且stat大小与已有记录一致。播放器ONNX仅索引manifest已有SHA与stat，未打开内容。候选池不是已更新播放器，不live reload，不向研究env复制或导入模型。

接线源码为 `mod4-onnx-mujoco-launcher/export_latest_moe.py` 的Mean35/ManualMoE，以及播放器请求目录的V2 exporter/时钟wrapper，均只读文本。现有观测35、输出6，完整6维动作选一并clamp[-6,6]，不做权重或动作平均。gate148仅在normal_view下argmax E0/W35；mode4→H1、mode3→E3保留原35维输入，mode6→E2先改normal_view；E2/E3在播放器100Hz外循环每两tick更新并保持。不是学习好的五路门控，未新增泛化/技能合格声明。

未来T2-z数据总线必须带实际施加动作/processed target与起止时间、expert/mode/checkpoint身份、原生时钟、同步观测、真实物理配置/重置身份、episode/support/query split；expert ID不能替代物理环境ID。视频WM不能用6维补零14维直接继承机械臂动作语义。新latent若进入router/actor是新接口和新训练方法，不能热改当前35维actor或当前PPO；工程registry不为未来方法做隐式决定。

## 双4090资源受限路径

`MEMORY_AND_WIRING_PLAN.json` 列出未运行方案。文本结构算得5个确定性actor约253,790参数（fp32约1.015MB），但gate/critic/Adam/latent/newadapter均未计入；六份PT约97MiB主要是已有完整训练状态，不能据此推断显存。MoE策略与5B世界模型是完全不同量级。

默认fullWM5B/DDP不作为“已可运行”计划。DDP每卡复制参数/梯度/Adam，2×24GB不能合并为48GB连续显存。5B量级bf16参数约10GB十进制；加bf16梯度和两个bf16/FP32 Adam moments静态约40/60GB每卡；若有FP32 master再加20GB，均未含激活、临时、VAE/T5。实际trainable count/state dtype未载入测量，以上只是条件量级。

受限路径先评审：梯度checkpoint、固定VAE/T5预计算并卸载冻结模块；再看FSDP FULL_SHARD或ZeRO3配合CPU optimizer/parameter offload。纯两路分片静态仍约20/30GB每卡（bf16/FP32 moments假设），加瞬时all-gather/激活后仍可能不fit。需核对交替world-model/z requires_grad、多个optimizer group、DiT wrap和完整save/resume；不能只填FSDP配置就宣称兼容。

可选LoRA、冻结DiT只训练context/action是**明确改变训练方法**，须独立基线标签与批准；轻量state-latent是另一个整套MoE+RL候选，不能冒充原视觉T2-z。默认不引入fp8、8bit optimizer或compile/PTX未知路径。当前没有任何GPU probe、试载、训练或4090成本实测。

## 容量、环境层与后续准入

原25GiB磁盘guard保留；494,235,168,768bytes仅旧快照，执行前freshstatvfs。准备峰值估算约88.8GiB（模型41.214＋环境20＋wheel临时15＋源码1＋日志1GiB＋最大文件临时11.362GB），不是实测/预留合同；下载器不主动复制第二套HF模型。六个现存MoE checkpoint只索引，不增加本阶段占用。旧H1数据50/cache20/检查点60GiB作为历史算例继承并明确不代表整套MoE覆盖预算；整套多技能数据规模未知，不自行扩大采集/训练授权。

独立venv当前只准备官方WM与文本registry工具；不含当前Isaac/RSL/PPO全栈复刻，不能借用原mod4 site-packages。未来RL/simulator版本与WM Py3.11/cu128并存边界须按方法明确，不为“一个env装全”去改原环境。历史72为driver535.54.03、nvcc11.8/glibc2.29；NVIDIA CUDA12.x minor兼容有最低版本与PTX/新特性限制，不能从CPU安装或旧cu126导入推断本应用cu128可运行，不升级driver/syslibs。

`launch_training_DISABLED.sh`始终exit64。后续训练需要原任务完成与完整保存、两张实际GPU UUID各自释放/owner确认、正式整套MoE数据/adapter/split、明确可审查显存策略、新训练GO与预算。unknownpeer不查PID/身份、不kill、不预占。准备收据不是训练准入。

来源：[固定T2-z README](https://github.com/T2-z-latent-optimization/T2-z/blob/c72f051f5cffcb1f372a32bc488df273556d39b9/README.md)、[Wan固定文件](https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B/tree/921dbaf3f1674a56f47e83fb80a34bac8a8f203e)、[BWM固定模型卡](https://huggingface.co/BLM-Lab/Boundless-World-Model/blob/738a8d3c008e637b8b1b18d5e98a82f6de9c04aa/README.md)、[NVIDIA minor兼容](https://docs.nvidia.com/deploy/cuda-compatibility/minor-version-compatibility.html)、[CUDA12.8说明](https://docs.nvidia.com/cuda/archive/12.8.0/cuda-toolkit-release-notes/index.html)、[Accelerate FSDP](https://huggingface.co/docs/accelerate/en/usage_guides/fsdp)。本阶段复用前序已取得的官方文本/元数据，不重复HTTP检索。
