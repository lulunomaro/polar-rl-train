# MOD4采样吞吐：可优化位置与CPU准备结果

结论：有两条值得先试的具体路径：H1保持全部记录的NPZ低级别无损压缩；E3对固定13种reset recipe预计算几何。通用SDK reset读回也值得分层计时，但尚无足够证据安全重写。生产FP32、当前窗口68和所有物理/health/保存保护均未修改，两个候选helper都未安装。现场训练收益尚未测量。

## 已有真实瓶颈

复用已经闭合的M3 FP32四个稳态update，M4 BF16/FP16仅用于确认相同结构的瓶颈。所有计时都是CPU wall，含隐式GPU等待，不是GPU kernel占比。

| 科目/阶段 | 每update中位秒 | 占collection中位百分比 | 解释 |
|---|---:|---:|---|
| H1全cycle | 27.9377 | — | 20k×24=480000 transitions；cycle不含logger后的保存等工作 |
| H1 trace persist | 9.9666 | 35.935% | stack、ZIP压缩、写盘、full SHA、paired retention合计 |
| H1 selected reset | 8.4692 | 31.299% | 每update调用24次，含父reset及D0-D7适配器 |
| H1 physics | 7.3457 | 26.412% | 原96次2.5ms物理步，不降低频率或漏callback |
| E3全cycle | 49.8040 | — | 仍是20k×24；控制50Hz×8 |
| E3 selected reset | 34.8017 | 70.106% | 每update24次；selected数量/trajectory是重要混淆变量 |
| E3 physics | 10.5450 | 21.192% | 原192次物理步 |

H1神经网络推理约0.0161s、0.058% collection；preupdate checkpoint和observation capture约0.0883s、0.318%。已有M4 BF16 H1 PPO本身约1.90倍而全cycle仅+0.140%，不能把4090的TFLOPS或MLP提速视为整训倍数。E3 BF16的+15.53%同时发生轨迹/reset变化，不能认作纯compute收益。FP16暖身少5个Adam step的原问题保留，不主张生产采用。

## 第一项：H1 NPZ保真压缩

实际代码位置是M4已保存文本 `benchmark_closed_text/h1/h1_production_control_prefix_trace_v1.py:38-43`，其中`:41`一次构建所有字段stack，再`np.savez_compressed`；`:9`用read_bytes计算full SHA。`h1_prefix_pair_retention_v1.py:25-80`仍核验/保留原成对策略，删除旧完整pair前又full SHA。

未安装helper `trace_npz_writer_unused_v1.py` 通过公开的 NPY/ZIP API显式使用DEFLATE1或3，并可逐字段stack。没有删字段、降dtype、截帧、降环境数、减少preupdate或异步落盘。旧原件和producer SHA保留；未来新文件必须记录自己的真实新SHA。chunked SHA仍读完整文件，只降低临时内存。

CPU实际结果（本机i9-13900HX，Python3.13.13/NumPy2.4.6/zlib；BytesIO，非磁盘测试）：

| 输入 | 方案 | 中位秒 | CPU序列化速度因子 | 文件字节增幅 |
|---|---|---:|---:|---:|
| 已保存小派生24×91、27原字段，3次 | 原全部stack/default6 | 0.099924 | 1.000 | 0 |
| 同上 | 逐字段level3 | 0.077753 | 1.285 | +1.453% |
| 同上 | 逐字段level1 | 0.072495 | 1.378 | +3.201% |
| private Generator synthetic24×20000同shape、2次 | 原全部stack/default6 | 32.5544 | 1.000 | 0 |
| 同上 | 逐字段level3 | 25.6316 | 1.270 | +1.177% |
| 同上 | 逐字段level1 | 20.2843 | 1.605 | +2.538% |

全部25份样本的每个字段均通过dtype/shape/tobytes精确往返，输入digest不变；还检查特殊NaN payload、±0、inf、大端、空数组、scalar、非连续和Fortran数组。synthetic是独立PCG64 seed20261025，借用原字段shape及粗略分布参数，缺少真实20k轨迹相关性，不能代表实际训练数据或现场CPU。它没有使用全局RNG，也没有运行策略或物理。所有NPZ输出仅存在测试内存，报告保留每次大小、SHA、计时；原小派生文件原位保留，没有生成需复制的大型raw。

同level6时，逐字段在小派生仅1.040倍、synthetic仅1.008倍，速度差很小；确定的静态收益是额外stack从535,680,000B变为最大字段97,920,000B，理论少437,760,000B（417.5MiB）。这是暂存上限推算，不是采集到的生产RSS峰值。测试的BytesIO输出缓冲也不对应现场磁盘写入路径。

设原cycle T=27.9377s，persist P=9.9666s，其中真正能按CPU压缩比提速的份额c未知，则推算`S = T / (T - P*c*(1-1/r))`。即使假设c=100%，小真实level1的r=1.378也只得到约+10.9% cycle速度；synthetic的r=1.605得到约+15.5%。这两项都是乐观推断，还未扣文件变大引起的写盘、full SHA、retention开销；不能报成实测收益。将整个persist凭空消除的数学天花板约1.555倍，也不是本候选能达到的改动。

## 第二项：E3固定recipe几何和bank缓存

`benchmark_closed_text/recovery/job0/runtime/isaac/mod4/e3_recovery_runtime_v1.py:55-63`每次selected reset重新打开bank、argmin取固定pick、计算joint permutation、读取/解压points_root、传selected points，然后按128环境一块，对相同25200点重复cross/cross/amin。最后又读取32,022,178B bank做SHA。已有text metadata声明133 poses、每pose25200点；NPZ数组成员在切片前会整体解码，因而`bank['points_root'][pick]`会重复解码这个完整成员。这里的大小/复杂度是源码及metadata推断，没有读取该bank二进制。

固定13种recipe可一次用原算式构建quat/minZ/initial表，后续按原recipe索引。原每次复杂度`O(selected×25200)`变为一次`O(13×25200)`加每次`O(selected)`；同源selected q/points也可缓存。所有点、原0.0001m margin、真实reset时机、recipe抽样、root_xy/零速度和SDK setter顺序仍保留。缓存必须绑定实际bank SHA/pick/joint order/device，不能拿其他bank或新fall pose冒充。

未安装helper `e3_fixed_recipe_geometry_unused_v1.py`在纯CPU、独立私有Torch Generator上测试520个selected，涵盖13种recipe、25200个synthetic点。三次原几何1.2761–1.2821s，lookup稳态0.000175–0.000213s，首次lookup为0.00936s，一次建表0.03792s。quat/minZ/initial均torch.equal、max_abs_error=0，全局Torch RNG前后相同。该检查没有读真实bank、调用CUDA/SDK或推进物理，不能外推为现场reset提速或CUDA逐位相等。

## 第三项：通用reset的全表读回与Host等待

生产热路确认使用`spring_pressure_training_env.py:12-27`的LearningSpringPressure，不是fixture中保留全部RNG/other-row记录的SpringPressureSDK.reset。

| 位置 | 实际重复工作 | 候选与边界 |
|---|---|---|
| `mild_dr.py:69-93` | mass/inertia selected写；每次full material表get/clone/CPU | 先测material与setter；CPU friction路径和私有RNG仍保留 |
| `spring_pressure_training_env.py:18-27` | full stiffness getter，再选ids核验 | 可研究同一只读区间快照复用，不移除buffer/drive/model核验 |
| `gas_damping_sdk_adapter.py:41-51` | damping、force、armature full getter与exact检查 | getter是否真的CPU/GPU传输待实测 |
| `chassis_com_pose_roundtrip_sdk_adapter.py:54-97` | reset/apply/audit显式至少5次get_coms，另有full cache刷新和全表rotation检查 | 不跨D0/COM写边界缓存；full-row刷新及当前principal-axis保护不可删除 |
| `explicit_pd_sdk_adapter.py:23-40` | model参数校验及full stiffness/damping getter | 只能研究相同条件的调度/快照复用，保留全部硬件检查 |

这些操作含`O(20k×joints/bodies)`，与selected可能很少不成比例。单次COM f32逻辑表约17.36MB；未实测getter返回设备，不把此推算称为PCIe传输量。GPU上的torch.equal/float会让Host等待，此处CPU wall可能承担之前排队的GPU工作。第一步应把parent reset、MildDR、spring/gas/COM/PD以及E3 geometry分层计时，不能把H1 8.47s/E3 34.80s全部当作可删除审计。

checkpoint的多层torch.load/save、每帧CPU numpy copy、retention全index/ledger线性扫描是后续次序。没有发现trace.persist中的额外shutil复制能直接消掉。checkpoint保存链保留原完整字段与preupdate时刻，不能为省IO去掉原PT；既有cycle不覆盖所有25次/最终保存费用，不能用当前小preupdate计时估计全部生产保存成本。

## 交接

严格的改动边界及最小验证见 `INTEGRATION_BOUNDARY_AND_MINIMUM_VALIDATION_V1.md`；完整source SHA、checkpoint身份、真实计时、每次CPU样本和推算场景见相邻JSON。读者路径猜错、Python alias无输出、fixture误判及“逐字节”措辞补正均单独保留在 `READER_AND_SCOPE_ERRORS_V1_ACTUAL.json`。

本工作没有SSH、远端host、GPU、策略推理、rollout、GUI、kill、新训练、预算/canonical写、Git commit或进一步派代理。未改retention政策、25/8GiB guard、物理/health/成功阈值、32位状态或17Adam。所有新source/errors/reports仅本地pending，由root统一归档并核验remote main/tag/peeled；不把本地文件称为已经Git记录。
