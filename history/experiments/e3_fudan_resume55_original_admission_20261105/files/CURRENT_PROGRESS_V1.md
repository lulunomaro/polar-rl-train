# E3/Fudan/video阶段交接 V1

## 最新直接任务与Goal

- 用户15:47要求只继续E3，并对齐复旦训练方法；15:56明确给出[动作视频](<C:/Users/lulu/Downloads/43171186822-1-192.mp4>)。
- 当前持久Goal `goal-c490e4cc-b28b-440e-bde6-30ee956813f0` revision2，active/armed，roundsStarted0/max14。旧20步PPO Goal已complete，不恢复旧八专家SuperMimic/typed capture任务。
- 阶段1方法/视频分析完成；阶段2模型/真实可达初态核对进行中。**新原生训练尚未启动**，没有新梯度/候选/成功率；没有自有原生GPU/SSH/observer后台job在运行。

## 已完成实质工作

1. [方法和视频报告](<METHOD_AND_VIDEO_ALIGNMENT_V1.md>)：真实Fudan参考固定8204e853，PPO + 五帧历史监督速度encoder，不是SM/RNN；原代码jump/plane不是getup课程。独立encoder Adam漏存和两组残留梯度全局clip需要显式本地修正，不能声称原样。
2. [实际视频解码](<extract_reference_video.py>)已消费：9.866625s/1280×720，20原始尺寸关键帧，原PTS 0、.5…9.5；[索引](<video_reference/REFERENCE.json>)与[时间图](<video_reference/TEMPORAL_CONTACT_SHEET.png>)已保存。再次执行会因输出目录已存在停止，不重放。
3. 确认视频目标是机身贴地、两轮触地、腿在同一端，大幅摆腿借接触翻身，随后需落轮稳定；不是之前轮子悬空的扩髋画面。视频本身不证明本车机械行程或训练算法，也不据瞬间直立判成功。
4. 父已读E3 reset/phase/runtime：同一.25m站姿q × 12机身倾角 + normal，不含视频目标腿形；现有signed upright及.5s稳定credit保留，不套jump 1秒倒地reset或对倒立同样为零的姿态平方项。
5. [静态演示/原生模型比对脚本](<compare_local_native_model.py>)已实际执行成功，产物[差异JSON](<LOCAL_NATIVE_MODEL_CORRESPONDENCE.json>)：演示14.2001407kg，原生14.2941403kg；23同名body中chassis/shin MCI不同，部分被动joint与gas范围不同。其local raw range=[0,0]未读jnt_limited，绝不当关节锁死；其余body名称未映射，不当缺失。四个旧顶层XML不匹配原生source_mjcf fbb0393883d31ac96f8cd58a184585470222f7daf96af6aa5d0748a1752c366c。没有原生/物理验证或因果归因。

## 下一步，避免重新陷入大范围审计

- 定位与2c/bae原生资产对应的同源MJCF/配置，先统一MuJoCo演示模型和原生；旧演示[scene](<C:/Users/lulu/Desktop/claude/mjcf/chassis_mod4/scene.xml>)不是该source SHA。已限定列过项目根mod4相关目录，没有继续全盘搜。可优先看chassis_mod4_work的已有生成模型/rolling-idler导出及原700N资产来源，不为状态/hash标签打开旧模型或轨迹。
- 查真实可达的贴地双轮接触初态。现配置hip±.5rad/crank[-1.2,.9]，先区分软件训练包络与真实机械限位；旧扩[-3,3]不是实物证据。气弹簧行程不擅自扩大；必要时询问一个关键本车物理事实，不拿异车参数补猜。
- 按报告固定源做最小Fudan history/encoder/PPO适配；本车raw35不能装成上游25，new architecture明确暖启动/新计数，不切旧Adam假resume；保存主和encoder Adam、RNG/DR/历史/队列。
- 原canonical唯一writer/原资源lease/3900-3600-300/1800preGO/reserve86412.86069250107均保留；只E3，不碰H1/其它专家/Registryv12。母版1cd保留，不晋升坏a3ce。

## 资源和委派

- 唯一聚焦只读子代理3b92c2b6-8850-4ad3-857f-77fc0e518590已完成两项定位并停止，所有结果已收到；无新子代理/测试/SSH/GPU/模型/raw读取由其执行。后半rsl四文件通过固定commit HTTP内存读取，未落盘；实际实现时按固定源获取，避免引用目录名当证据。
- 视频解码及静态比较均前台RC0，无未收集host后台job。
- 旧本地GUI32692/HWND1782888可能由用户操作，最后一次已知是旧扩行程模型；本阶段没有重开/关闭/查询它，不声称现在状态。
- Office/ACL技能无RL/视频匹配，本阶段用现有FS/CLI/FFmpeg/MuJoCo能力。Documents一次搜索已取旧SM方法背景；Recall工具Source Route未提供，本轮不重试/绕路，转用实际项目源。

## Git待合并，勿重跑旧once

最新已核验feature HEAD仍cf86e9105c970e5456e53380901c49648bd2666f；main只读。
待下一次有意义阶段合并：本目录源码/报告 + [第一次全腿演示](<../mod4v1_e3_full_leg_pose_view_20261104/>) + [扩髋贴地演示](<../mod4v1_e3_belly_ground_rear_20261104/>) + 相关旧viewer普通关闭文本。视频/PNG/NPZ/模型/轨迹只作metadata refs，skip-before-stat/read/hash，不为Git重演物理或读模型。尚未创建/消费本阶段record脚本。
