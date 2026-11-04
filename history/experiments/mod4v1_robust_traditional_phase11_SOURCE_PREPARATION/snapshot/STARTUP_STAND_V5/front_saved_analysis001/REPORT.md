# V5 首案：实际pose REQUEST与quiet gate的单流诊断

- 原结果不改：188 control/3760 physics，OBSERVE31/LIFT156/INHIBIT1；stop=controller_fault，原门False、BALANCE无、末stable0。
- [READCOUNTS_001.json](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/STARTUP_STAND_V5/front_saved_analysis001/READCOUNTS_001.json>)先保留，再[MINIMUM_001.json](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/STARTUP_STAND_V5/front_saved_analysis001/MINIMUM_001.json>)：唯一新trace一次188行/1201204B，11 bounded事件；physics/旧V4raw/其他raw/rawSHA均0，随后只读saved minimum。
- feature timing flag188/188=True不等于力矩起用：LIFT真正pose REQUEST38/156=24.36%，quiet118/156=75.64%；全部156条按logged common/轮mean/softguard复核REQUEST，maxerror0，38条都与quiet不同。
- 首次gate/latch/pose=0.31s：估计pitch=0.440510880、源rate=-2.84892847e-06，common=12.396457507Nm→轮REQUEST[3,3]；该20子采样bin双主轮并非全时>1N，gate不是支撑证书。
- latch在156条LIFT都True但current gate仍控制输出；最后pose=0.83s，.84–1.86连续103条quiet。可见失格分区：proper-only11、qd-only37、qd+qerror70=118；不是未激活，也不是整个LIFT持续body-feedback。
- first-off=0.40s先因proper norm14.434713398>11.772，qd仅0.083681267；首次qd失格0.71s/max|qd|=0.444340085。qd>.4共107/156（70同时qerr>.08），是moving LIFT中充分的排除项，不推唯一动态原因。
- fresh本身未独立log：188条sensor_age均0，38条AND-gate True证明其fresh；other可见项全过却gateFalse=0。其余118已有可见失格项，fresh仍UNKNOWN，失格总项数107+70+11不能直接相加。
- 12rad/s softguard首次0.70s，源轮mean=[12.174674439,11.818714195]→REQUEST[-.052402332,3]；logged guard5条，mean轮>12共9条，峰[13.046208350,13.334727512]；非物理速度/actual DC限制证明。
- 轮转proxy首次≥.1在.58s/≥.25在.80s，末max=0.381835390m<.50；不是true路程，.50/6s未触发。目标h首clip=0.91s：-0.502885632→-0.502536082；clip96条，gamma limit35条/首次1.30s。
- 末valid PRE=1.86s：估计pitch/rate=0.999842082/0.506214202，qerr=0.096067251、maxqd=0.766151261，轮REQUEST[-.157653817,-.161616938]。
- guard PRE=1.87s估计pitch=1.004482443>1→INHIBIT，REQUEST6全0；true POST=1.88s/pitch=0.974530825；last published ref仍1.86，fault的current gate/common/gamma是null，不能当新reference或零applied。
- private grade：双主轮全部20采样承重115/188，nonwheel全部≤1N=0，两者同时0；whole guide3710/hard0。只用原bin/小result，不猜接触身份或作用阶段。
- 仅对照旧V4 saved摘要：193条/capture eligibleFalse、轮REQUEST峰.188839/.188061与轮mean峰.629465/.626869；V5峰3/3、13.046208/13.334728。true最大XY .076305426→.352945073m、高度增量.068776234→.068183005m，旧/新原门仍False；非固定qref/唯一wheel因果或泛化结论。
- PRE command/年龄view估计pitch、源window-held rate/gyro/encodermean，与true POST+10ms以及该20×.5ms private支撑bin单列；[FACTS_001.json](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/STARTUP_STAND_V5/front_saved_analysis001/FACTS_001.json>)及11完整事件保留q/qd/ref/vref/common/REQUEST6/epochs。
- actual2k applied/电流/DC mask/instant drive速度、接触身份/impact/唯一失效原因UNKNOWN；不从±3请求推actual saturation，不把quiet传感gate当可信接触或源rate当瞬时。
- 本轮0新控制/调参/新case/模型/FK/PHY/DR/旧QA/solver/compile/link/Git/agent/Goal/Mnemon；C15文件未碰；PH11pending，停交父，不作下一增益/门限/病例决定。
