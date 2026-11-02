# Integrated COM Window v1 — finite-window identity, conditional shadow

**现已封存：磁盘attempt001的15/15synthetic与4400projection-shadow均完成，执行源码/原source snapshots/旧依赖SHA已核。宿主重启前仅中途状态、未有INDEX；本次仅补齐文档和seal，没有重跑测试/物理。全部可信cue仍UNKNOWN、hardwarebinding=false，PH3pending。**

## 精确恒等式与用途

IMU固定lever s，完整COM r(q)，BODY量`u=omega×(r−s)+rDot`：

```text
vCOM^W-vIMU^W = R u
mean_window properCOM^W = integral_window(R fIMU_B)/T
                         + (R_end u_end-R_start u_start)/T
```

它不加g、不求alpha/qdd测量；对Ru求导恰含alpha×rho、omega×omega×rho、2omega×rDot及rDDot，所以movingleg的Jqdd/convective项不曾被丢弃，只转换成速度边界。rDot来自public31body FK的J(q)qd。

窗口首relativeR=I，仅gyro积分；未知world常旋转只左旋结果，不改变norm。每bin解析S(omega,h)=integral exp([omega]t)dt对其piecewise-constant模型精确，**不是对原boxcar真实transport精确**。详[公式/坐标/预算](<THEORY_AND_BUDGET.md>)与[mean信息缺失反例](<BOXCAR_INFORMATION_LIMIT.md>)。

## 50/100/150ms结果

数值窗口从contiguous mean epoch取N个完整bin及两个端点，boot/重复首包不赚新窗口。radius是显式smoothness/geometry/端点噪声假设下的局部工程scale，不是实际global error保证。

|case|T ms|可算窗口|radius p50 m/s²|radius p95|平均量nominal age ms|可信cue|
|---|---:|---:|---:|---:|---:|---:|
|r29_C_MATH_TAU_stand_0|50|794|9.245028|9.257901|25.00|0|
|r29_C_MATH_TAU_stand_0|100|789|5.185950|5.192975|50.00|0|
|r29_C_MATH_TAU_stand_0|150|784|3.915580|3.921461|75.00|0|
|r29_C_MATH_TAU_forward_0|50|1194|9.354256|9.603908|25.00|0|
|r29_C_MATH_TAU_forward_0|100|1189|5.242553|5.372554|50.00|0|
|r29_C_MATH_TAU_forward_0|150|1184|3.954476|4.049382|75.00|0|
|r31_C_MATH_TAU_forward_101|50|1193|9.698917|9.905101|35.00|0|
|r31_C_MATH_TAU_forward_101|100|1188|5.417043|5.526387|60.00|0|
|r31_C_MATH_TAU_forward_101|150|1183|4.073691|4.152097|85.00|0|
|r31_C_MATH_TAU_forward_102|50|1193|9.743003|9.980608|35.00|0|
|r31_C_MATH_TAU_forward_102|100|1188|5.439915|5.558090|60.00|0|
|r31_C_MATH_TAU_forward_102|150|1183|4.090627|4.170688|85.00|0|

150ms下conditional interval排除zero并符合nonfreefall proposed区间的窗口数量是747/301/136/116，仅为**条件区间诊断**，不是接触身份、可靠contactcue或FSM资格；confidence cap仍.50低于冻结.60，所有返回cue保持UNKNOWN。50/100ms的该条件诊断数量均为0。

端点误差/T确实随长窗缩小；例如stand的boundary p50约8.366/4.183/2.789m/s²。proper噪声项约.424785m/s²不随N缩小，gyro路径/transport误差随时间增长。更长窗口还增加T/2年龄，不是当前瞬时cue。DR队列观测10ms使25/50/75ms变成35/60/85ms；原20point leftsample firstmoment另比窗口中点早.25ms，已记录。重叠窗口不是独立物理试验。

对旧point-COM sphere约12m/s²，长窗条件sphere较小是数学上有前景的方向，但temporal target/transport假设不同，**不等于当前point精度或真实benchmark成功率提升**。

## 没有偷掉的误差与边界

- PUBLIC D1同半宽用于全部case，不读或反推D0–D7receipt，不按nominal标签置0，更没有除sqrt20/窗口N。
- q是endepoch，qd/gyro仍是前20sample均值；端点误差含5.25ms异时与声明rate-slope envelope，没冒成同步瞬时。
- 20point boxcar未保留intrawindow R/proper相关项；conditional用预先写定alpha/qd/proper slope envelope作transport预算。没有用midpoint R乘mean proper叫作精确。
- 固定BODY model bias传播矩阵`[R1[omega1]−[omega0]]/T`另列；默认triangle界不要求独立性、不自动抵消。
- wheel phase未知按nominal非零径向MCI fullphase/速度缺项界，不假balanced；硬件MCI/零点/lever/滤波校准仍未绑定。
- 这仅是窗口平均specific-force候选，不是全表面air/contact/guide身份、270mm/RM/board资格。

## 已保存证据

- [核心window math](<window_math.py>)、[shadow实现](<shadow_windows.py>)、[15单测源码](<test_window.py>)、[runner](<run_checks.py>)。
- [首次RESULT和全部sourceSHA](<attempts/001/RESULT.json>)、[unit log](<attempts/001/unittest.log>)、[完整shadow summary](<attempts/001/shadow/SUMMARY.json>)。
- [每case/window表](<CASE_WINDOW_TABLE.json>)、[逐窗口derived output/producerSHA](<DERIVED_OUTPUT_MANIFEST.json>)、[假设](<ASSUMPTIONS.json>)、[source manifest](<SOURCE_MANIFEST.json>)、[validation](<VALIDATION.json>)、[INDEX](<INDEX.json>)。
- [重启中途恢复记录](<SEAL_INTERRUPTION_RECEIPT.json>)：从已落盘字节核对后seal，未把中途状态冒成已sealed。

15项数学覆盖static、rigid spin freefall、movingleg/public31body、constant net force、坐标变换/norm、完整rDDot/Coriolis展开、解析SO3积分、fixed-bias传播、噪声不随N缩小及相关raw均值恒等式。fixture生成器可有解析导数用于造信号；估计器接口没有alpha/qdd/world yaw输入。

## 2k最小提案与后续

[2k提案](<MINIMUM_2K_CAPTURE_PROPOSAL.md>)仅提出字段/证明要求，未实现父publisher/新physics。same-window D1offset加到各raw使weightedmean代数一致，但同窗差分offset消去，属于**信息增强/相关噪声新branch**，不冒旧benchmark或IID20降噪。控制器只见noisyraw，不见clean/offset，整窗按D3延迟；endpoint q/qd同步仍需绑定。浮点逐bit一致与实数恒等式分开说明。

[PH3准备交接](<PH3_PREPARATION_HANDOFF.json>)保持待父书面cutoff确认：当前seal不追active source、不snapshot/commit、不重record Phase1/2。全部0physics/Git/newagent/完整原trace/DR/GT；旧保护SHA不变，整体Goal继续active。
