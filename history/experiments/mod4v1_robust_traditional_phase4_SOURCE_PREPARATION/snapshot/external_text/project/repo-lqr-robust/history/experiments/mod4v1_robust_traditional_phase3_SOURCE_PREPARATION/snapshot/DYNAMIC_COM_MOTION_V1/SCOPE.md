# Dynamic COM Motion v1 — 新独立传感器原型

在PH2commit02b5ff84b905a4e40f207a44b0491aeff2f79b7e完成后开始。本目录是PH3pending；仅public31bodyFK/MCI与传感器q/qd/qdd、proper_origin/omega/alpha，以及可选wheel angle/rate/acc和声明误差界。旧CONTACT/FSM/父源码/模型/物理/H1/H2/Git保持不变，无新代理。

目标：rCOM(q)、rDot/rDDot全运动项；proper_COM_B = proper_origin + alpha×r +omega×(omega×r)+2omega×rDot+rDDot。输出只是带置信/误差原因的COM-specific-force估计与freefall-like/nonfreefall-like/uncertain cue，不识别接触位置/全表面air。guide支承的非零COM proper不视作自由落体。

wheel偏心按public MCI计算，不假定balanced；wheel状态缺失时显式算可声明bounds下的缺失项界，bound未给则uncertain，不强行.8或.9置信。真实packet差分仅使用已记录的传感器字段；若日志缺失，不从rootGT/contacts补，未知如实保留。只做静态/合成0Step验证，不重跑旧评测/物理。
