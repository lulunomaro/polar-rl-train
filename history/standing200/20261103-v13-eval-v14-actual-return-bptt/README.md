200mm站姿攀爬：V13实际失败与V14学习修复准备

V13最终模型2bc1c10b51252d93b80f224eaffaaaae2015f184a230c233f4a42c384aa14a40已完整保存、安全关闭。原独立评测已实际完成并取回：80首episode、seed9137、新DR、最多500控制拍10秒、台沿0.8m/台高0.2m，0/80严格成功，80姿态终止，平均0.5115秒，范围0.36–0.80秒，双轮台顶支持峰值0。原评测与传回once已消费，不得再执行。

当前模型已原生审8张实际bodypose侧/俯视图和两张曲线；半速视频是已记录姿态渲染，0新模型读取、0新physics。四个选例的前0.2秒左右轮目标约7.73–9.98/59.35–59.41rad/s；还距台沿0.25–0.47m就达到约−40度pitch、19–21度roll。初始depth正确识别200mm；降低了精确tanh饱和但没有获得轮腿协调。选例不能外推为all80视觉，也不证明唯一因果。

定向改动：保留全部最终V13网络/四Adam/teacher/normalizers/replay/RNG，冻结恢复后的actor观测和goal归一化；每次新采64个实际控制拍、512环境，共32768新样本，原std0.1高斯采样与原动作裁剪不改，使用裁剪前样本的精确似然。原实际reward与done进入GAE(gamma0.99/lambda1，done无reset bootstrap)，一次PPOclip0.2目标加0.1原H32 BPTT目标、0.1原latent抗饱和项。后Adam实际Gaussian均值KL≤0.01、归一化动作delta≤0.05/logitdelta≤0.25；拒绝完整回滚weights+Adam，仅接受一次提交。原H32和全部物理/DR/奖励/验收保持；不是脚本对称控制或力矩克隆。

已过本地合成CPU数学与接口测试：终止截断、概率/梯度、候选回滚、一次计数、H32跨时梯度、stop-before-action保存边界。合成fixture不等于实际robot rollout，不是技能通过。check_full_restore.py尚未执行；FROZEN/新生产GO尚不存在。control.py cpu复用原有限CPU控制器，只改小文件查找路径；必须等已知controller全部释放、freshLOCAL/serialFREE、原canonical-none和3EX准入。其后prepare/gpu/launch/first各仅一次；资源检查覆盖72两卡、210、86全部四卡。既有canonical reserve/3900save3600exit300不变。

owner/evaluator通过小wrapper执行SHA固定原源码，__file__绑定新任务位置；不能直接symlink owner让resolve回到已消费V13。共用依赖只引用，不复制完整运行树。当前无新watcher/新SSH/新GPU作业；其它scope不操作。

接续：读CURRENT_WORK_ORDER和actual once。通道释放后运行Python314 -B -X utf8 repair_v14/control.py cpu；读取真实返回。通过才prepare、四卡gpu检查、原准入launch。FIRST确认实际32768新样本actor梯度、H32真实跨时梯度、acceptedKL/四Adam和首完整保存。相同原owner完整保存/关闭后立即独立80评测，取回实际contact/bodypose，原生审图并对比早期轮差速/姿态/轮净空/台顶支持；0严格成功仍不得毕业。
