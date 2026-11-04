# C1：只读新慢行trace的停车定位
- 仅一次完整流读此新case：1200行；contact_trace/旧420111原raw均0；原代码/门/物理未动。6–12s每0.5s、关键时刻与字段缺失已存analysis.json。
- 9–12s估计vx mean/RMS=-0.0930130822/0.142929512m/s；真实post vx mean/RMS=-0.0915020822/0.13838405m/s；同epoch估计误差mean/RMS=-0.00115004541/0.00625082521m/s。6–12s同epoch速度误差RMS=0.010081358m/s；停车阶段估计已明显看到倒退，并非估计仍认为静止。
- 8s停车边界progress=1.3098995m，停车后峰=1.33938232m（post 8.48s），最终=1.10562614m；峰后回退=0.233756187m；末3s负真实vx样本300/300。
- yaw实际均值从6–6.5s的0.1952rad升到7.5–8s的0.6553rad，末段约0.737rad（42.2°）；同epoch末3s yaw误差RMS仅3.81828e−5rad，真实偏航而非主要由yaw估计错误制造。横偏在8–8.5s到0.240070m后随回退降至0.043312m，低终点横偏不抹去峰值失败。
- 已保存同窗真/估yaw、pitch、侧偏、进度、估计腿速、请求腿/轮矩及末子步applied矩。估计按sensor time与前一row真值对齐；不以PRE/POST错位制造速度偏差。末3s轮请求均值L/R约+0.830/+0.041Nm、末子步actual约+0.825/+0.041Nm；缺实际轴速及扭矩分解，不据此判定能量流/滑移/主动倒车根因。
- 倒退由真实速度与世界route progress交叉判断；轮转滚动/接触滑移/控制器主动倒车的区分仍UNKNOWN。最小新字段：同epoch原wheel_vel2+q/qd/gyro/age；shaped v/active ref/park integral和wheel分解；评分时actual轴速及子步clip统计。
- 本分析不选第二候选，不改控制代码、不读contact或旧raw、不跑物理/model/FK/QA/hash/Git/newagent；父负责后续决策。
