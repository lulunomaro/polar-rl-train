# 最小2k noisy-IMU窗口提案 — 只提案，未实现父publisher

## 目的和边界

100Hz BODY boxcar保留一阶mean，但没有R(t)路径或R与proper的窗口相关项。有限窗口恒等式本身精确，不会凭均值凭空补出丢掉的信息。新的2k资料可减少此项缺失，但它是**信息增强、相关噪声**的新benchmark branch，不冒称旧400N/100Hz baseline、旧H1/H2或硬件采集。

本子任务不生成新physics/父capture、不改controller/旧source/Git。父可独立实现并grade。

## 最小字段

每个窗口包：window/source sequence、acquisition begin/end、每条2k sample的真实采集timestamp/weight/validity、arrival/D3queueepoch、dropped/duplicate信息；boot1sample与steady20sample形状分开。

控制器可见：

1. noisy gyro_BODY3和noisy proper_at_IMU_BODY3（每2k sample）；明确单位、方向、IMU位置/方向绑定和滤波/量化阶段。
2. endpoint q4、qd4、gyro必须明确**同一端点时间**。只增强IMU并未自动把原mean qd变成instant endpoint速度；若端点qd尚为boxcar，继续传其aperture和误差，不假同步。
3. wheel phase/rate可选；无phase仍用nominal径向MCI full-circle边界，wheel端点rate也有自己的采集/误差声明。
4. authoritative原100Hz noisy mean及其数学weight metadata可并列供一致性核验；不能用这个mean代替未知intrawindow correlation。

禁止控制器可见：clean raw、D1 offset、episode DRreceipt/seed系数、root/world/contact/true姿态/envelope。私有producer grading信息与sensor-only projection物理隔离。

## 同窗共同offset构造与均值证明

对channel c、同window w，用原100Hz D1-aftermean已经抽出的offset b_wc（私有）：

```text
y_i = x_i + b_wc                 # 每个sample都加同一offset，不是独立重抽
sum_i weight_i*y_i / sum_i weight_i
  = sum_i weight_i*x_i / sum_i weight_i + b_wc
  = 原noisy mean
```

proper维度若原noise在gravity3 dimensionless域，必须沿用完全相同的9.81映射、坐标和加噪阶段；不可换量纲或重抽噪声。整窗（含所有raw、mean和metadata）按原D3epoch一起延迟；重复首包复用同一已经加噪的window，不重抽、不拼新旧数据。

这是实数加权恒等式。若宣称浮点**逐bit**等同，需要核验旧/新求和顺序、量化、权重和rounding；先加offset再求mean与先求mean再加offset一般仅到roundoff相等，不能未经验证写bit-identical。若publisher保留原authoritative mean，可在报告中明确raw重算mean差的真实roundoff。若采用精确fixedpoint/rational accumulation保证一次量化一致，也应作为新数值管线另列，不悄悄改旧benchmark。不要调整最后一条raw来伪造同offset模型的精确相等。

## 噪声相关性和信息增强必须明示

同窗b完全相关，故mean噪声仍是b，**没有1/sqrt20降噪**。相反，

```text
y_(i+1)-y_i = x_(i+1)-x_i
```

在同窗内共同offset消去，intrawindow变化被近乎干净地暴露；这是比原mean记录更强的信息，不能叫成旧benchmark的等价难度，更不能冒实机2k独立噪声。跨窗offset跳变仍在，不能把跨边界差分当无噪声。

gyro共同offset仍使relativeR积分漂移；proper共同offset运输到不同R也不自动抵消。固定model误差的时间相关性用明确传播矩阵/最坏界，不凭空独立或抵消。

## producer必须给出的证明/验收记录（非硬件资格）

- 同一实际source window的20weights/noisemean与oldmean逐channel逐window误差、实际最大差；原SHA/source sequence绑定，缺窗口/boot/duplicate单列。
- 检查offset在同窗一致、跨窗保持原D1 draws与作用scope；这项producer-private检查不把offset写进controller projection。
- 证明D3整窗延迟与原noisymean序列相同，无fresh gyro/old proper混包、无重复包重抽或变更payload。
- controller-only projection严格allowlist测试，人工注入clean/offset/root/contact键时失败；公开producerSHA/bytes/rows，不公开隐藏参数。
- 先数学回放验证relativeR/SO3transport与端点u边界，再由父独立真值grade窗口平均specific force。若要当前瞬时cue，另绑定时间变化，不把T/2年龄删掉。
- 新ID/新目录/新假设/新成本与旧记录并列；不覆盖旧失败或把新branch通过写成原模型/旧H1/H2通过。
