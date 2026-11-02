# Integrated COM Window v1 — 先验公式、坐标和误差预算

本目录新建；旧DYNAMIC_COM、capture audit、CONTACT、FSM、PH2保持封存。纯数学/0physics/Git/newagent/真实IO。可读同4个sealed sensor-only projections，不回完整trace/DR/GT；任何shadow结果先视为条件数学模型，不提高硬件binding或原cue门槛。

## 1. 精确连续恒等式

令R(t)将chassis BODY向量转到任意固定惯性坐标，IMU相对origin的固定lever为s_B，整体COM相对origin为r_B(q)，omega为BODY角速度。定义rho=r−s，

```text
u_B = omega_B × (r_B−s_B) + rDot_B
vCOM^W − vIMU^W = d[R(r−s)]/dt = R u
```

proper specific force为a−g。同一重力场下COM与IMU共用g，故

```text
fCOM^W − R fIMU_B = aCOM^W − aIMU^W = d(Ru)/dt
mean_window fCOM^W = integral_window[R fIMU_B] / T
                     + (R_end u_end − R_start u_start) / T
```

**没有加回g，也没有调用alpha或qdd测量。** 若展开右端导数则恰为

```text
R [ alpha×(r−s) + omega×(omega×(r−s))
  + 2omega×rDot + rDDot ]
```

因此moving-leg的J*qdd、convective/Hessian与Coriolis均隐含在速度边界，不是把rDDot或alpha当0。前提是r/rdot来自同一完整COM几何，端点q/qd/omega具有明确同时间或误差模型；rDot可由public31body FK的J(q)*qd求，不需要差分qd。

窗口首定义相对R_start=I；Rdot=R[omega_B]x只需gyro和时间。真正绝对姿态的未知常旋转仅左乘整个结果，不改变norm。这里不是用真实yaw/姿态替代gyro积分。

## 2. 两类数值问题严格区分

1. 对给定piecewise-constant gyro和proper模型，每一bin使用Rodrigues的**精确旋转指数积分**，而不是midpoint R乘mean f。S(omega,h)=integral exp([omega]x*t)dt，累计`I += R_start S f_bin`、`R_end=R_start exp([omega]x*h)`。
2. 原100Hz packet只是20×.5ms的BODY分量boxcar。它**没有给出**intrawindow旋转路径或R与proper的相关项。即使对常值模型积分完全精确，也不是对真实transport精确；conditional budget明确覆盖缺失transport/curvature，strict分支保留unbound。

窗口定义为sensor epoch端点[a,b]、T=b−a=50/100/150ms。使用结束于a+10ms,…,b的均值bins，q/qd/gyro端点取a和b packet但qd/gyro仍是前窗均值，不能冒瞬时。输出是该窗口平均cue，nominal年龄T/2+到达队列年龄，不是当前瞬时；原20点左采样时刻的整体first moment还比窗口中点早.25ms，另列而非抹掉。

boot instant、instant→mean边界与重复D3首包不补成新bin，不跨采集gap凑窗口。

## 3. 先声明conditional smoothness/error假设（非观测拟合）

全部4case同一组：PUBLIC D1每100Hz packet的半宽gyro.125rad/s、q.005rad、qd.25rad/s、wheelqd.5rad/s、proper=.025×9.81m/s²；无÷sqrtN/÷N。未验证encoder零点另留.01rad allowance，nominalCOM position/velocity scale=.005m/.02m/s，lever(.03,0,.04)且位置误差norm .0005m。

为从均值恢复/约束连续transport和端点，先验声明每轴|domega/dt|≤50rad/s²、|dqd/dt|≤100rad/s²、|dfIMU_B/dt|≤50m/s³，wheel spin acceleration≤5000rad/s²；FK局部Jacobian Lipschitz scale≤1m/rad²。它们是显式synthetic/model envelopes，不是通过数据completion推断出的真实上界，也不是计算了alpha/qdd。未成立则radius是条件值，strict始终UNKNOWN。

## 4. 相关误差的预算，不靠独立性抵消

- 令e_f(t)界定proper模型/采样误差、theta(t)界定relative gyro orientation error。取eta(t)=2sin(min(pi,theta)/2)。
  `integral_error/T <= integral[e_f + eta*|f_hat|]/T`。
- 对u端点，rho误差e_rho=e_r+e_s，
  `e_u <= (|omega_hat|+e_omega)*e_rho + e_omega*|rho_hat| + e_rDot`。
  `boundary_error/T <= (e_u_start+e_u_end+eta_end*|u_hat_end|)/T`。
- 因而端点测量误差随1/T缩小，但proper offset一般不随T缩小，gyro相对旋转误差随积分时长增长，时间平均cue的年龄也随T/2增长；不存在无限加窗免费提升。
- 固定BODY COM/lever bias b即使全窗完全相关，也不是自动抵消：边界误差为`[R_end[omega_end]x−[omega_start]x]b/T`。实现额外报告这个相关传播矩阵的operator bound；默认仍用不要求独立性的端点triangle bound，不把固定误差当两份独立随机噪声，也不凭空令其相减为0。
- 每bin D1 offset可在该bin完全相关，跨bin也不假独立。proper噪声预算按sum of operator norms/absolute bounds保留，不使用1/sqrt(5/10/15)；gyro bias积分误差也不除窗口sample数。

20点时刻0,.5,…,9.5ms，对连续10ms bin，平均`E_point E_sample |t−sample_time| =3.3375ms`，端点与mean中心差5.25ms。上述Lipschitz envelopes给出proper transport和gyro积分缺失的保守L1界；端点qd/omega误差分别至少PUBLIC D1+declared slope×5.25ms。没有从均值packet拿到真正intrawindow关联，所有此类界都保持conditional标签。

## 5. 实验顺序

先做static、rigid spinning-freefall、moving-leg、constant net-force、常坐标旋转一致性的合成数学测试，区分连续恒等式与数值积分收敛；再对4projection做数学shadow。所有cue保持原.60门槛，假设输入confidence最多.50/hardwarebinding=false；可报告radius和interval条件标签，但不冒FSM资格。

若100Hz资料仍丢关键transport相关项，只提出2k noisyraw最小新capture证明要求，不实现父publisher/不新physics。`noisy_raw_i=clean_raw_i+same_window_D1meanOffset`是**信息增强且相关噪声**的新branch，控制器不见clean/offset；不能把它写成旧benchmark或IID20样本降噪。
