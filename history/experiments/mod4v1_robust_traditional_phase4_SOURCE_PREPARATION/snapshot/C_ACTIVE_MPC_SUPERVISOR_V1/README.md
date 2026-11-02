# C主动集QP + 独立C-LQR回退的host supervisor V1

**当前状态：UNSEALED / 预检通过，等待sealed host QP IO绑定与新物理TRAIN。** 不是完整嵌入式MPC或目标板实时性资格。

## 边界

[supervisor](<supervisor.py>)不读取MuJoCo、DR或真值。输入为sealed C3的STATE14/REF14/MATH_TAU/GUARDED_TAU/SHAPER_V及同包row6编码器速度。C3提前独立计算的GUARDED_TAU是回退，不在Python内另算一套LQR。

局部模型沿用已冻结的fixed-leg 8状态+名义输入半步lag第9状态，N15、DARE终端；H32与既有实际H15**逐bit一致**，不添加正则或从新轨迹改变H。梯度/参考轨迹和mux目前由Python/NumPy计算，仅QP是C核心，未来嵌入式部署仍需额外移植和验证。

## 与旧MPC的变化，明确列出

- 采用sealed ACTIVE_BOX_QP_V3，64全局pivots、同一f32绝对KKT tolerance=.002；不把MAX/CYCLE当可用解。
- 不再用abs(v/r)构造对称推力盒；由当前传感器轮速构造原物理signed四象限DC上下界，与独立LQR的yaw差扭矩求common输入交集。上下界向内量化f32，保留overspeed仅制动情形。
- 这是**当前点限制冻结到整个N15**，未预测未来轮速/状态/接触/耦合功率约束，不能宣称整个预测域满足真实动态电机包络。
- 所有非成功、畸形证书、传输故障、模型域外和时间超支均选C3 GUARDED回退；传输/证书故障锁存该worker路径，不自动重启。无效C基线输出零。
- warm只在成功且最终mux前通过deadline后接受；失败的私有iterate不当可用warm或控制量。

## 时间语义

调用者传入完整控制周期wall起点，应在C3 RPC之前采样。supervisor将剩余整数微秒预算交给QP，过期前不调用；回包后、证书验证后、mux前再次检查。QP内部START相对clock只是全周期的一部分。host RPC/OS调度/驱动提交仍由调用者最终检查，这不是ARM硬截止或WCET证明。

## 最终输出域

MPC选择时，输出为 **C_ASQP_SEQUENCE_PYTHON_MUX**，并非原C3已校验的最终enqueue；C3的enqueue计数仍只代表独立P25路径。新物理runner必须明确这一点，不能沿用H4“最终C dispatch实际执行”标签。plant仍执行原inversePD→D4→随机PD/motorGain→逐physics signedDC，MPC输出不取消随机量或接触。

## 已完成预检

[attempt001结果](<attempts/001/RESULT.json>)：42检查、0失败、0物理步；H32 bit-exact、模型域/显式禁用、调用前截止、回包后截止、剩余预算、时钟回退、QP nonconvergence/坏证书锁存、无效C基线、overspeed冲突、日志JSON序列化。测试回调只是mux单测oracle，**不是C IO/物理验证**。

## 最终截止检查修订（仍非生产IO）

新增[supervisor v2](<supervisor_v2.py>)覆盖disabled/domain等所有有效C基线路径的最终wall采样，并把MPC accepted计数/warm提交推迟到最终检查之后。若解在mux与返回之间过期，恢复独立C3 GUARDED，warm与accepted计数不提交。时间字段改为`supervisor_final_poll_elapsed_ns`，只表示该最终poll，不包含之后序列化/驱动提交；runner仍须管理真正完整周期。

[新attempt003](<attempts/003/RESULT.json>)58检查/0失败、0物理步，加入final-return过期回退、warm/计数回滚和最终时钟错误测试。v1与[attempt001](<attempts/001/RESULT.json>)保持不变。[attempt002错误](<attempts/002/ERROR.txt>)为旧测试预期仍写generic QP reason、新代码返回更具体caller-clock-at-return reason的断言不匹配；实际旧run未打印该值，未追认重建。003只改新测试预期，v2核心不再修改。

独立HOST_ACTIVE_QP_IO_V1目前为**BLOCKED/NOT SEALED**：生产worker生成后未保留，归因未知；186帧未发送，不接入草稿SDK，不启动R37。后续产物条件改善并通过真正IO资格再绑定，保留旧H1/H2/H4，不用改名/改防护或同源反复编译碰运气。
