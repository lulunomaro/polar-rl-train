2026-11-03：轮世界高度奖励466已完成完整保存与安全退出，独立467评测为0/80严格成功、0首次整轮越沿、0leadingcross。80例都曾腾空，30例姿态终止，50例跑满8秒，平均5.5535秒。全部保存的400Hz轮胎台顶manifold力最大0N，没有双轮台顶支持。原owner/node/worker均已ownwaited、原账段结清、private/shared释放；SSH关闭且SESSION恢复。最终模型41,341,082B，SHA fbf0c86e802e5b867123635b81b5b059626d17f4b2d276b9e9c8d7e0bbaa0022，43次PPO/Pi/critic、WM52554，actorAdam56761/critic13821。单次最终CPU1645个tensor有限检查通过，完整teacherSTD17Adam42940/三Adam/EMA/normRNG/savedorigin保留。原normal/CPU/eval/once不重放。

当前模型原生view_image已审8张早期侧/俯视图、6张1.5–8秒侧/俯视图、6组叠加曲线和映射曲线。四例起跳后轮子仍低于台顶，首次任一轮回地面时尚未到台沿。长案例env0/1/41后期在台前下方撑住，未见台顶恢复；env40在1.68秒姿态终止。姿态图仅为四例，all80结论取实际评测与接触记录。

|案例|0.4秒yaw|0.4秒pitch|低轮底峰值估计|首任一轮ground>1N|落地前最前轮心x|
|---|---:|---:|---:|---:|---:|
|env0|23.67°|21.84°|0.1915m|1.1200s|0.6104m|
|env40|21.23°|22.02°|0.1623m|1.1100s|0.5350m|
|env1|19.57°|22.09°|0.2097m|1.1425s|0.7376m|
|env41|18.75°|22.29°|0.1986m|1.1550s|0.6112m|

台顶z=0.27m、台沿x=0.8m。轮心减0.0637m仅作净空定位，验收仍用实际完整轮廓及400Hzmanifold。0.4秒两轮残差均值仍为左−5.22..−6.15、右+3.39..+4.25rad/s，早期差速未消除，后期路线由电机输出形成；没有显式路线planner。不能归为初始深度盲视。新旧DR不是逐环境配对，不把表格差异称单一奖励因果。未保存完整非轮manifold，不声称此前绝无机身碰撞或唯一碰撞原因。

奖励按保存pose/motor/contact逐拍重建，各项均值最大误差7.63e-6；高度项实际进入计算，但净空没有改善。当前exp(-totalcost/5)在1.12秒只有0.000914–0.03119，三个长案例4秒约0.00018–0.00020，较大误差下的局部改进被压得很小。这是具体奖励信号诊断，不是已证明的唯一失败原因。

下一项468只把映射改为1/(1+totalcost/5)，现有姿态464、高度466及其它cost项/尺度/权重全部保持。零误差仍得1，正cost严格单调下降，小误差斜率仍−0.2；后段衰减较慢。对同保存轨迹假设双轮同时上移10mm，1.12秒的奖励差约为原来的1.5–14.5倍，4秒约47–51倍；部分0.9秒改善差反而较小，完整样本保留在RECIPROCAL468_OFFLINE_CANDIDATE.json。假设扰动只是离线重分，不是可达的实际动作、新onpolicy数据或技能提升。独立平均指数项曾离线考虑，未采用，避免一个好分项抵偿其它差分项。

6项CPU单元检查通过。必要final466一次完整恢复后，用114条保存坐标重复成128步并生成新syntheticlatent/重分奖励作CPU fixture，actorgrad2.69978、critic15.2704；半LR候选KL0.00432835、最大归一化残差差0.0213091，全部候选weights及Adam已恢复。CPU没有生产优化、SDK或物理；deterministic接口/动作差0、terminalGAE和回报窗检查通过。不重复解码源模型。

468位于scope/runs/h1_reward_tail_20261103，只4个source、4个control及小eval，104个共享文件按SHA引用，模型/参考/资产不复制。INDEX d5040ffdd8c30e4d0c61ccd318ef234f3bfce2de60f74af5cbabe5ef281348ea。尚未GO；唯一localtimer63124等原standing200 V8 nominal+900，即2026-11-03T07:08:26.627297+08，再freshLOCAL核精确原owner退出/结清/释放/CNone/sharedfree，才执行尚未发生的468launch/FIRST/bind。训练与独立469评测继续原唯一canonical3900/save3600/exit300，物理及270首次飞行整轮越沿双轮稳定门槛保持。

本次本地读者失败保留：late renderer参数prefix被历史archive prefix覆盖导致FileNotFoundError；原partial/false保留，修共享reader后补齐原目录6张图。一次apply_patch重复目标被校验拒绝、无改动，后正确应用；一次spawn包装器把自己的Python进程算成别的controller，断言在timer/once/network前拒绝，后仅排除exact currentPID完成首次spawn。都没有派生生产namespace、重跑旧once或改冻结466包。

实际运动图在466/evaluation/recorded_native与recorded_native_late，曲线和离线候选在本目录，数值在analysis.json/motion_curves.csv。大型raw、PT、NPZ和media只索引真实路径/大小/已有SHA，原件保留。所有失败、源代码、CPU、timer、交接和automation纳入新阶段Git；旧466及更早trial标签不改写。
