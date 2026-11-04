# attempt08小阶梯完整结果及目标纠正

本轮20,000环境在17:52:48 actualGO后有效训练49次PPO、23.52M onpolicy样本、980新Adam，final为iteration80、9,408本轮physics ticks、FULL_V4/37,849,673B，SHA `f6b6b649b78752a89c0688850ae89e93afd0a87fe21eb6b6705f9b02ecf81da4`。原owner1609081于18:54:15 ownwait/settled/released，collector63276正常结束，三个正式文件SHA核验完成。原deadline18:52:48/NOMINAL18:57:48均未延长。

完整WORKER.log172,603B SHA `ee75eeabd796f405ffab1e87957766024ea5326c545c4c453ff21956ca448d1f`，EVAL.log15,451B SHA `60bc5a6cece933ccf45198a90a9d42307ec2e1570f33f8b27f026dd6c8e4a89c`。无实际error/cooking失败/pairs或patch丢失/OOM；保留两条大三角面警告。完整日志只在本地无其它controller后有限读回，没有重生产或读PT。

原生保存的4个tile均500水平面、1010–1016竖直面、0斜面；本轮确实修复了此前heightfield斜坡。但它仍是25–40mm小阶梯，**偏离人类所说单个200mm台阶跳跃**，不能用本轮累计爬高称200mm跳跃。

独立80首局，seed9137/newDR/400Hz/最多400controls：43局至少一次双轮升到更高踏面、56局至少单轮，0局连续.5s完整稳定；双轮支持最长.395s、稳定最长.255s。75局8秒评测cap、5局原20controls连续接触终止，mean7.81675s；0任务timeout/terrainboundary、0闭链/mimic/数值/raw异常重置。5局终态分别为env7导轮05、env12导轮06、env20/56导轮07、env71导轮05。最后20步均接触>1N、counter1..20，姿态未达40°，据此确认接触终止。

target/CAD全部合规；四腿motor目标MAE约.117/.087/.104/.088rad，左/右hip上限命中90.57%/57.93%。body相对实际raycast地面平均.2586m，命令平均.2968m，平均误差-.0382m、MAE.0589m。负world z本身不是高度错误。支持中断与姿态/竖直速度尚存，不能据hip饱和单独断言奖励唯一根因。

当前模型已查看全部早晚侧顶4图。env0全零命令在中央；env1接近台沿晚且yaw命令重采样；env40在首级附近调整/停滞；env41连续驶过多个小踏面，最大累计支持升高.6456m。图像来自本轮真实pose与本轮真实mesh，wxyz已正确保存。renderer原先依赖y=0顶点，新boxmesh没有该顶点，因此先修为真实三角形截面；晚图摄像机跟随真实机身，0NN/0新physics。

原始POSTROUND_COMPLETED中的visualpending保持原回执；完成审图后另记`ACTUAL_RIGHTANGLE08_FINAL_NATIVE_REVIEW.json`。人类现在明确“机器人跳上去200mm的台阶，不是碎台阶”，后续使用独立`jump200`，见`TODO_JUMP200.md`。不再原样续小阶梯小时。
