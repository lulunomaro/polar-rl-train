# 当前边界和最小后续验证

本文件是本地准备意见，不是新增训练、GPU、原 owner GO、预算、S8 或远端连接授权。两个 helper 均为 unused；没有部署，也没有改当前代码、窗口68或既有归档。

## 优先级1：trace序列化

允许的候选内容仅为新 unused 根中的 `trace_npz_writer_unused_v1.py` 加受限调用替换：原 `np.savez_compressed(f, **all_stacked_fields)` 改为逐字段 stack 写同样的 NPY ZIP 成员，并显式指定 DEFLATE1 或3。所有24帧、27字段、dtype、shape、原数组字节、preupdate PT、原producer SHA、控制/物理声明、原完整文字和错误继续保留。

现有 reader `np.load(...,allow_pickle=False)` 不依赖压缩级别；新文件按其真实新字节生成新 SHA，不能挪用旧 SHA。旧原件/旧 index/旧 producer SHA 不重写。helper 自身不承担 rename/index/retention；原 `.partial` 独占创建、完整 ZIP 关闭、原子发布、full SHA、index 和成对 retention 顺序仍须由原 caller 保持。没有异步线程、后台队列或落后于 PPO 的证据提交。

本次已经做的 CPU 检查：真实小派生24×91原27字段与独立 synthetic24×20000同 schema；所有字段的 dtype/shape/tobytes 往返相同，输入未变；特殊 NaN payload、±0、inf、大端、空数组、scalar、非连续和 Fortran 数组也往返相同；非法字段/object array 拒绝。完整结果以同目录实际 JSON 为准。

若未来在已另行授权的新根采用，最低还需：

1. 核验 allowlist diff、原 reader、原子/异常路径、25GiB admission与8GiB saved-stop原样存在；写/关闭/读/SHA失败必须保留 partial、原始异常、当前 incomplete/unpaired/source，不清 rows 或擅自重试消费。
2. 沿用同源 native 和16万查询证据；不增加 FP64、额外物理/逐位门槛。不为文件压缩更改物理、环境数、callback、health或成功阈值。
3. 只有在另有实际性能运行授权时，记录新的独立 case 的 CPU stack/ZIP/文件写入/full SHA/retention 子计时和峰值RSS；同时记录原完整 collection、PPO、logger/checkpoint、退出落盘与原 writer 成本。比较相同输入/字段和同等保存，报告压缩文件增幅、IQR、额外 hash/写盘成本。不能把本次CPU速度倍数直接作为现场整训收益。

`sha256_file` 是 bounded-buffer 内存改法，仍完整读取最终文件；它不消除 SHA 成本，也不复用删除前身份检查。所有NPZ/PT原producer SHA必须继续记录，retention删除前仍完整核验。

## 优先级2：E3固定recipe几何

`e3_recovery_runtime_v1.py:55-63` 的固定bank、固定pick、固定joint order、固定12跌倒方向及normal recipe，适合在确认实际source SHA后缓存selected q/points和13项 quaternion/minZ/initial。表构建仍用原 float32 cross/cross/amin 算式和全部25200点，每次reset只按原recipe取值；原root_xy、0.0001m margin、root/joint零速度、SDK setter、phase.reset及publish顺序保持。

最低新增验证仅覆盖这个改动：

1. 用实际source manifest中的bank SHA `78af9fa47686204ef370271a2da580d762aa9fda1c7a49844ced318b264e6b83` 绑定缓存；实际pick、joint permutation、所有points、dtype/device不变。缓存构建发生于首次实际reset之前，不能在物理回调中做lazy改动。若保留旧每次full SHA，就至少先省重复NPZ解压和重新传selected points；若改为启动冻结，必须明确记录新的immutable输入合同。
2. 在未来另行授权范围内对13种recipe的原/候选输出以及selected/unselected reset语义做同源实际device验证。CPU synthetic结果不充作实际bank或CUDA证据；不把该验证扩张为整个物理任务的新精度门槛。
3. 记录每update selected计数与recipe直方图，分别计时bank read/decompress、points transfer、geometry、SDK reset父链。现有 `_reset_idx` 合计含这些不同项目，不能假定全部34.8s都是几何，更不能把少reset解释为compute提速。

本次没有打开32MB bank原件，只读取其已保存text metadata；没有SDK、GPU、策略推理或物理rollout。CPU synthetic equality为 `torch.equal` + `max_abs_error=0`；不是NaN/signed-zero字节或CUDA逐位结论。

## 优先级3：共用reset读回和同步

先分层计时再改。实际生产是 `LearningSpringPressure.reset/apply`，不是保留完整RNG/other-row fixture检查的 `SpringPressureSDK.reset`。实际热路仍包括：MildDR材料表full read/clone/CPU及mass/inertia写，Spring stiffness读回，Gas damping/force/armature读回，COM父reset后的多次全表get_coms/刷新/rotation校验，ExplicitPD stiffness/damping读回。

可研究同一只读区间内复用同一实际getter快照、仅改变各条件的归约/Host读取调度；保留每条有限性、硬件、selected/unselected、buffer/backend及独立RNG检查，且在下一次物理step前同步得知失败。不能在D0 mass/inertia/COM setter前后的不同状态之间跨界复用。COM的full-row缓存刷新和当前principal-axis orientation保护是防止partial write污染其他body的必要逻辑，不能删除。未实测各getter返回设备和传输路径前，不把逻辑表大小写成实测PCIe流量。

每次reset重读全表，复杂度含 `O(num_envs × joints/bodies)`，即使selected很少。COM full f32逻辑表约20k×31×7×4=17.36MB/次getter；实际explicit get_coms在reset/apply/audit路径至少5处，另有data-cache刷新。该大小是静态推算，不是采集到的GPU事件。`torch.equal`/`float(tensor)`返回Host值可把此前排队的GPU工作计入此处；现有CPU wall不是CUPTI-exclusive归因。现阶段没有安全充分的依据直接重写这条SDK热路。

## 后续次序

checkpoint save chain存在sensor→feedback→action→spring→gas→chassis→step270多层load/save，仍须保留全部字段及preupdate时刻；现有preupdate capture合计约0.088s/update，优先级低于trace压缩和reset。周期25次及最终保存有部分位于已测cycle之外，不能由0.088s推断全部生产checkpoint费用。

trace每帧 `.cpu().numpy().copy()` 与field stack存在重复host复制，但当前未归因尾部只有约0.35s/update；贸然去掉copy或异步写容易破坏不可变preupdate/trace快照。retention的full index/ledger扫描随prefix数线性增长，累计可达二次元数据工作；它仍需保留完整原始index/历史和删除前full SHA，没有本次CPU数据支持把它升为首要收益。

原采样物理部分、100Hz/50Hz、2.5ms TGS32/4、2mm单环境闭链重置、成功/health/hardware/finite及完整保存条件均保持。FP32生产不因本报告切换BF16/FP16；也不从4090 TFLOPS推断整训倍增。

所有本agent source/errors/reports现为本地pending，交root统一用新唯一annotated trial归档并核验remote main/tag/peeled；本agent没有Git commit。
