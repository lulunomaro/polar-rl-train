# 为什么20point mean不决定精确transport积分

精确连续恒等式并不等于从原100Hz记录可以精确恢复它。以下都是纯数学反例，不是新physics、也不是实际case真值grading。

## 即使R路径已知，proper mean仍丢相关项

取单bin长度h、已知恒定omega=(0,0,Omega)，R=Rz(Omega*t)。两种BODY proper：

```text
f_plus(t)  = f0 + A*cos(2*pi*t/h)*ex
f_minus(t) = f0 - A*cos(2*pi*t/h)*ex
```

在20个等权时刻t_i=i*h/20（i=0..19），cos的mean为0；两者具有相同gyro mean和proper mean f0，q/qd/omega端点u也可相同。但

```text
integral R(t)*(f_plus-f_minus)dt
 = 2A * integral Rz(Omega*t)*ex*cos(2*pi*t/h)dt
```

一般非0。令k=2*pi/h，其x/y积分分别为

```text
Ix = .5*[sin((Omega-k)h)/(Omega-k)+sin((Omega+k)h)/(Omega+k)]
Iy = .5*[(1-cos((Omega+k)h))/(Omega+k)
        +(1-cos((Omega-k)h))/(Omega-k)]
```

因此同mean输入可对应不同精确窗口COM proper平均；误差幅度只能由额外smoothness/curvature/covariance信息约束。本文conditional的Lf envelope正是额外假设，不是mean记录给出的事实。

## gyro mean本身也丢旋转次序

前半窗omega沿x、后半沿y，与先y后x的mean相同，但

```text
Rxy = exp([wx]h/2) exp([wy]h/2)
Ryx = exp([wy]h/2) exp([wx]h/2)
```

一般不同，因SO3旋转不交换。即使proper在BODY为常量，transport积分和R_end边界也会受影响。strict分支对未知intrawindow路径/相关项不发有限保证。

## 本实现没有掩盖什么

- piecewise-constant模型的S(omega,h)指数积分是解析精确的，但其作为真实boxcar替代品仍需带缺失项budget。
- 没有把R_mid*meanproper叫作精确，没有把sharedepoch当instantaneous coherence，也没有用World姿态真值补路径。
- 延长T可降低端点噪声/T，却增加relativeR误差和平均cue年龄；样本数不使D1共同offset自动减小。
- 2k相关offset新资料确实给出更多intrawindow形状，因而是信息增强的新branch，不能改名冒旧benchmark。
