# 当前23509地形完整30关节复位、真实地面与低速前方扫描组件回读

DR实际18份完成后，在独立G=/home/egde/rl_candidates/MOD4_ROUGH_STAGE1_PREPARE_20261006准备下一科目。使用固定SCUT b8ff79f3df855faf9dc92f4a282bd80c42649466已核验五类intro子集tiny_step、slope_for_rm_high、inv_slope_for_rm_low、plane_for_rm、random_uniform_for_rm，2×5诊断网格、初始level0。此子集排除15cm起步大台阶、cliff、跳跃和空中复位，不能称完整SCUT Rough或全地形。

现有20261002 terrain Warp/CPU/PhysX及31体30关节FK组件明确复用原资产SHA证明，本次是真实当前F167/full23509的新动态reset与扫描读回。USD/contract当前SHA与完整133姿态/25200表面采样点库一致；完整30关节按真实名字重排、qd/root速度清零、根姿态顺地面法向、整个采样碰撞点云在实际mesh射线求根高，miss显式拒绝，不用缓存地面或藏无限Plane。实际根Z约.025951–.462964m及非零坡面法向均记录；低世界Z不等于姿态被压低。完整写入回读误差0；表面采样仍不是连续实体非穿透保证。

独立10env300步3秒站立10/10存活、closure最大0.000070469m/mimic0.001691456rad；新±.3BODY低速3秒和前方15点扫描10/10存活、closure0.000082385m。真实/World/ground/terrain/mesh上root/body/双轮/前方查询均命中，初末white_v3实际参数读回通过，12项独立CPU合同通过。观察35actor/38critic、6动作和硬件包络保留；只在隔离进程cfg换地形/完整reset/地面查询，未改F生产文件。

运动结果仅有限短样本，不声称走场技能已完成。env1请求BODY−.3而3秒世界X净+0.224109m，保留原raw；其余有符号方向在本短窗相符。这是未训练新地形的能力差异，不能拿physical_pass当方向达成或依新质量数字阻止合理后续学习。

首次候选在任何动态步前把USD_PATH字符串当Path读取，第二次正确路径版本在完整点云query处遇SDK view要求连续tensor；两错误原样保留，只在新显式入口依次修Path和调用边界contiguous，不改数学/物理参数、不改旧rough_ground组件。最终named layout版本及不同新任务move/scan组件均真实通过。旧once入口均未重跑，Kit退出码0仍按error/actual result判定，未冒称首次成功。

整个canonical字节三attempt及move/scan均不变，PPO0、预算操作0、无trainer/active。原DR父/guardian计划退出保持，全部新组件父/孩子也完成退出且锁已释放。当前只是组件准备，没安装可训练Rough task/课程controller，没运行地形128/20k PPO、没有使用预检权重。下一步需要重基可训练任务的真实地面/完整reset接入、根/轮/前方查询生命周期和地形指令/边界、地面相对奖励及rolling proxy语义审查，保留旧平地/4π/world回归，再完整PPO合同及同canonical安全接管。未适配空中复位/跳跃/大台阶不可自动混入。

首轮准备固定white_v3；实际地形material用参考配方static/dynamic1、multiply，相对于原平地地面材料单列，是隔离场景差异，不能混说生产Physics没改等于场景相同。DR分布/奖励/PPO/机器人硬件和弹簧未改。实物force-stroke、感知延迟、全地形小陀螺、云台/MoE仍未认证。

总130h及五原扩展、余173120.341627秒≈48h5m20s保持。保留已完成DR18份结果和所有原raw/旧质量布尔，只归档本新组件结果，不重复已有terrain/FK/DR trial。所有大库和完整权重仅SHA索引，两小时监控继续。
