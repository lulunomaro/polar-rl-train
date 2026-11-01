# model2050 原完整PPO接续到400N50Hz：实际240

人类已选择从model2050适配到总计划400N、50Hz。旧E0跳跃后代停止续训，原冻结E0与所有历史保留。DR0两份源仅未选源码，没有实际新开DR0。

选中输入为3060 deploy/mod4_fudan_recovery_model2050.pt，386869B，SHA aac0ef67b8dc7e2b616e45952bf71e09b1ffb24bfcb84644f4d68550ed228869。初次与训练目录同编号PT的字节hash不相同，原false保留；不伪称二者模型相同或不同。后续新的必要身份目的：一次所选PT CPU decode和一次实际ONNX解析/外部initializer解码，证明actor8个权重与偏置张量全部相同。该PT完整actor35/critic38/STD6/17Adam通过，68tensor finite，源iter2050/Adam41240/LR0.00011390625000000006。没有为了统计/Git重复读旧模型。

新目标使用ownMOD4原400N工程k2000、50Hzpolicy/100Hzfeedback/400Hzphysics、2.5msTGS32/4/F32、D0white_v3及D1-D7、clip6/原PD与扭矩转速/真实延迟/2mm每env闭链/.01mimic。保留输入128/64/32网络、全部actor/critic/learnedSTD/17Adam与实际LR；全新物理episode/DR/queue/采样RNG明确fresh，输入未保存RNG，不假精确续态。原100Hz的48步rollout适配到50Hz的24步，均.48s；gamma.9801/lam.9025按物理时间折扣。

2000个平地环境使用独立原E0奖励/命令，18000个JUMP环境使用pinned Fudan原19方法/完整config/16权重逐字相同的原奖励。clip2.5*dt.02/不total正裁剪/原contact与air-time跨reset记忆保留；只在外层映射own真实状态并抵消Lab额外dt。不继承另一AI手工移植的reset/几何适配，不加脚本力/速度/teacher动作，不放宽guard。

新source接口5groups/29reject，normal reader接口2groups/7reject。原接口V1非法诊断keyword导致语法拒绝在执行前；V2仅改keyword。原80env准入V1误用裸sys.executable绕开已存在glibc240 loader，GLIBC_2.33在SDK构造前拒绝，0PT/0NN/0PPO、wait1/EX释放；独立V2只换回原run-python.sh及新输出命名空间，真实80env/native8=64physics/16feedback/原奖励8calls，wait0/allownOUT/EX释放通过。没有安装/修改系统依赖。

唯一原owner PID1018842/create1793502495.27，实际cwd=/home/lc01/Zonglin Li/zonglin2，任务owner根另存；node PID1018851/create1793502495.68。原HMAC/twofcntl/raw收费函数沿用原源码，3900/save3600/exit300，不新grant/退款/补款/改账/复制canonical。源CPU资格是实际选中PPO CPU+实际0PT target，非伪造native loaded-model资格；完整CUDA复原与20k native24在实际新PPO前完成。

真实FIRST：新增1PPO/480000 own transitions，iter2051/17Adam41260；native24=192physics/48feedback；完整first 22099209B SHA 24ff11b18b424981aa333890a34b8047758da20236f8a9a577cb2ff0dd197f30。只代表当时更新/保存快照，不是连续健康或跳跃/270技能。

GO 2026-11-01T11:08:19.217688+08:00；SAVE 2026-11-01T12:08:19.217688+08:00；NOMINAL 2026-11-01T12:13:19.217688+08:00；正常采集最早 2026-11-01T11:58:19.217688+08:00。原normal collector与NEWformal CPU已冻结未用。仅到原双900门禁后采集一次原收尾/一笔rawfee与1NEWformal/两hostSHA，再完整CPU一次；旧输入与旧once均0。后续无自动加时。

所有ROOT控制SSH最终关闭/SESSION恢复/globalleaseFREE。未来任何remote先fresh72精确当前owner/run/fullGO，再关闭72后访问其他目标；actual240关闭后binding历史化。保持当前训练，不加健康watcher或startup空GPU复查，不热改、重开旧GUI或称旧录像为live。W35/RM70/E2E3/完整SuperMimic与最终真实270稳定验收仍待完成。

本实际240唯一phase：mod4-model2050-onnx-matched-literal-fudan-jump400n50-ground10-ppo240。保留所有原错误、source、CPU、SDK、FIRST和完整UTF8；PT/ONNX/data/NPZ/USD/media仅真实path/bytes/已有producerSHA。后续正常收尾普通append，不重record/retag；保护所有1513旧tag对象/peels。
