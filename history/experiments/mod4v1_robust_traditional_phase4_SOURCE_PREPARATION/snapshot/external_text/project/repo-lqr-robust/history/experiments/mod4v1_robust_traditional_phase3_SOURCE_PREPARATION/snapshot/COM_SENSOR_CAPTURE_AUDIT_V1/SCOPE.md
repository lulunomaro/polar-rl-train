# COM Sensor Capture Audit v1 — sensor-only shadow，非放宽置信

只读SENSOR_CAPTURE_CLOOP_V1的manifest与4个严格allowlist projection，4400rows；不回完整trace/episode DRreceipt或root/contact/真实姿态/envelope。原case仅sourceSHA引用。旧DYNAMIC_COM/CONTACT/FSM/PH2及父文件保持封存；0physics/Git/newagent/真实IO。

公共D1 source只用于相同的synthetic-benchmark噪声范围与固定作用scope假设，不调用FullDR/RNG，不读取或反算具体D0–D7参数；不是硬件标定。可纯数学replay frozenV4的sampleomega/alpha/properRoot作baseline；60ms alpha LP与采样aperture时延不冒瞬时。

关键时间：epoch t处gyro/proper/qd为20×.5ms窗口[t−.010,t−.0005]均值，center=t−.00525；q4是endepoch值。相同epoch只表示共享queueepoch，不代表这些量瞬时同步。相邻均值差分的qdd/alpha还落在两个mean-center中点；boot instant→mean边界与D3重复首包不赚新差分样本。

分析strict-unbound与显式声明window/model/error假设分支，均保留默认置信门槛、不伪称.8或硬件校准；properIMU按lever(.03,0,.04)和alpha转换到origin，wheel无phase按冻结COM模块缺失项界。输出逐case时钟/aperture/重复观察、可计算率/有界率/cue/误差半径/时延及最小采集绑定建议，真值grading留给父独立执行。
