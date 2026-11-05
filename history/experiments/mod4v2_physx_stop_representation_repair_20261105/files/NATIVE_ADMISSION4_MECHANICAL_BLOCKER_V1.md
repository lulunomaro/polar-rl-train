# A4原生实测：10个被动CAD有限端没有映射到PhysX

真实来源：[闭合metadata](<F:/RMPOLAR-RL/mod4v2_expert_normalization_20261105/reports/MOD4V2_NINE_FULL_LEARNER_MIGRATION_ADMISSION4_20261105_221136_1793887896378695000/CLOSED_RESULT.json>) / [metadata-only逐轴汇总](<F:/RMPOLAR-RL/mod4v2_expert_normalization_20261105/ADMISSION4_NATIVE_LIMIT_FAILURE_SUMMARY.json>)。不是本地MuJoCo/source PASS。

A3原1800资源等待自然0GO结束后，只读summary在1793888612.9295957观察原ownerNone（非lease）；A4新根 `MOD4V2_NINE_FULL_LEARNER_MIGRATION_ADMISSION4_20261105_221136_1793887896378695000` 由原fresh门控实际先启动H1，controller1676829/owner1676836/worker1676962。SDK已实际构造20000环境、sole fresh reset；在读取policy源之前用同一次 `omni.physics.tensors.api.ArticulationView.get_dof_limits()` 得到[20000,30,2]并落盘完整20轴前4值、min/max和非有限分类。

|每侧被动轴|应生效CAD有限端（rad）|实际全N20000有限端读回|
|---|---:|---:|
|rocker_pin lower|−0.7828279184955527|−3.4028234663852886e38|
|coupler_pin upper|0.9027785273324023|+3.4028234663852886e38|
|knee lower|−0.7613787030122099|−3.4028234663852886e38|
|distal_pin upper|0.8152830434591931|+3.4028234663852886e38|
|gas_pin upper|0.15599963671374795|+3.4028234663852886e38|

左右共10个有限机械端呈现完全开放的FLT_MAX sentinel；不是1e-6误差或度弧换算的小量。连续主动/跟随轴和双有限gas行程也保留在原readback，不据此声称gas刚阻目标或100Hz通过：限位断言已先失败，后续gas drive getter/one-zero 8physics2feedback未执行。模型/source权重打开与decode0、PPO0；H1 rc0仍被error+semantic检查正确拦截。共享D0 gate阻止另8家族启动，故没有重复8次相同native失败。

原owner1793889164.9934886全children实际wait/costsettle/authority-private-finite释放true，outer1793889165.0090177实际rc0/reaped，errors保留。A4 observer38fe7f8506774acd completed0/fulloutput collected。没有worker仍在运行；旧母版、Registry、预算/阈值/资产没有为此次诊断改动，分数null不是0%。

下一步仅修正新包的native表示：保留全部真实CAD有限端、主动8轴无限、140–200mm/300N/k2000d3/target/原31体几何MCI闭链传动，不削弱native检查。为原None的被动反向端给明确backend finite representation，必须由原neutral-signed branch的canonical相对坐标域证明不截掉可达姿态；它不是新硬件机械止挡，也不冒全3D碰撞/任意passive winding证明。硬件one-sided和native实现bounds分开记录，旧P0包/所有失败不覆盖。新builder与局部检查仍不等于PhysX成功，后续新purpose须实际native读回重证，才放行learner源与其余8专家。新改动尚未生成资产/未调度；goal664仍active。

本实际A3资源timeout、readonly release、A4 native读回与阻断、修复计划及子任务源进展待下一meaningful feature-only归档；前阶段3703a54已远端核验，不为Git或状态重开weights/raw，不重放旧once，不改main。
