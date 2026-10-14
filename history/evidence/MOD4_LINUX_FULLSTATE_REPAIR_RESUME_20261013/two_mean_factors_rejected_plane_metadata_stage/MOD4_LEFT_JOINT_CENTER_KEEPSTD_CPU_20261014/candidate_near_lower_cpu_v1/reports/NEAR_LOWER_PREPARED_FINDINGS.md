# 原完整2b来源的近下限初始化：CPU候选准备

原中点factor实际由22/27正、25/27倒降至4/27正、0/27倒，ordinary179，无改善，已明确拒绝生产。数学合法条件概率高不能代表机构稳定或通过性。原中点权重、source、false/raw/完整失败prefix全部保留。本候选唯一来自原完整20k `2b9c3c36eaa47120e5c86753bc5b24684a9c8106d07c560d8403f26a7d372971`，未继承中点checkpoint。

新的CPU候选为 `own20k_left_joint_lower_margin005_keep_saved_std_CPU_prepared.pt`，19058207字节，SHA `6235d44aa144a73e46d8326187c7fdf1e406a2d0b00ee6d21922b18f198f3bce`。

只将left最终mean Wrow0复制本来源的actualhip Wrow1，bias减2×(1.0843−.005)=2.1586。实际新left bias为−1.8248130083084106；保持全部六std（left .6773233413696289）和std optimizer moments，仅清Adam7/8 meanrow0 exp_avg/exp_avg_sq，全部17个step计数保持。其它五头、trunk、critic、99项20k DR/RNG/history、原13身份KEY全exact；195个继承tensor与父来源storage全部独立。新profile `left_initial_joint_lower_margin005_keep_saved_std_v1`采用独立KEY，metadata无新增tensor；107floating finite/99perenv保持。

CPU磁盘roundtrip通过，源完整状态树与原文件SHA前后相同、Torch/NumPy RNG未消耗，无CUDA。7个身份负例严格拒绝，其中直接对实际失败中点checkpoint作为parent的SHA检查拒绝，而不是用中点数据重造来源。

在原120000个actual saved hip mean上，反事实同hidden均值数学映射经过原clip±6/.5scale后，crank−hip范围为 `[−1.079300046,−1.079300016]`，距原CAD下限约0.005rad。对任意实数hip raw，由clip单调且1-Lipschitz可证差范围 `[−1.079300031,0]`，全域最小lower余量0.004999969rad、upper余量0.85rad。原6action、clip、scale及CAD processor未修改。

与原保存的effective guarded left target相比，新数学target差median0.005000010rad、mean0.004999604rad；只有env67有一个control原本不在CAD下限，该control差为−0.043180645rad。不能说“所有target精确保持”，更不能把target差当作实际q姿态、完整物理路径或机械生效的精确保持。由于复制hip row会丢失原left头独有特征，未来动作还会影响last_action、其它头输出和后续轨迹。

固定原actual hip mean、保持actual left std .677323时，条件合法左raw输入概率仅约0.50588972，约一半探索请求仍会投影到原CAD下限。这是条件初始化数学，不是完整hip/crank随机联合概率、执行生效概率、通过率或晋级线；原可能poststep更新的policy_obs没有被伪作同control actor输入。

候选只CPU prepared。root下一仅独立新3060原50mm完整80环境冻结单因素，对照原2b全部firstphysics root/q30、参数配方assignment/captured RNG/队列，并核实际GPU actor来源与query/contact/COM/hardware；这些未来合同均尚未通过。本候选不能作为生产PPO来源。其它三skill的nativePlane query严格拒绝仍在诊断中，不放宽1e−6或其它物理阈值。

原1500controls/15s/6000callbacks、.4m接近、十波2.406422727m、两轮1N前后200mm及全部有效prefix原样。无SSH、GPU、PPO、预算、Gitcommit或安装SDK变更；本目录source、manifest和回执待根代理普通supplement归档。后续依真实冻结factor决定，不盲生产PPO/第三duration/70。
