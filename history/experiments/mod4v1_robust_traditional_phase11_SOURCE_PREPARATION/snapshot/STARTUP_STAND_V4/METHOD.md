# V4 支撑几何变换—有限姿态捕获—返回名义：新TRAIN假设

父已actual read新9行[几何报告](<../STARTUP_SUPPORT_GEOMETRY_V1/REPORT.md>)18行和[receipt](<../STARTUP_SUPPORT_GEOMETRY_V1/RECEIPT.json>)28行。以下是父此后选择的新策略/参数，不是研究者提前选的、不是稳定性或承载证明。V3A/B、旧gain/模型/driver/估计器/原验收门全部不改；本V4与新研究均不属于PH10至C6 cutoff。

## 几何依据与限制
- V3实际约.60rad倾角时，nominal delta0的假想轮底放平姿态guide minZ为-.004214m；仅delta20也仍有约+.1245m COMx偏置，且rootZ .295082m。
- 在初始.3836868rad角，public delta20共同角减body pitch的单个静态点，假想rootZ .366144m、guide gap .129005m、COMx-tireMid -.012418m；反号明显更差。仅解释新传感器参考假设，不把几何间隙当卸载证据。未验证连续相位/载荷/碰撞路径/动力学。
- 采用已经存在的TALL_ROUGH_BANK_V1/gain_delta20.json的q和tau作支撑参考/trim，不采用其K，不生成gain或在线DARE；最终仍返回同原gain_delta0 nominal GroundController。

## 默认与API
V3的operator_enable/recovery_tracking_enable保留，alignment_wheel_enable必须False；新增exact-bool support_geometry_enable默认False。关闭该功能或operator关闭时严格delegate原V3，packet/observer/额外support数据不额外读取。True路径显式提供support_reference，只接受研究过的左右对称h=.0025360756709216082、delta=.2公共点。调用顺序仍prepare_estimator→原100Hz packet/update→command；upright_prior=False，不重置估计器q/v/P/distance，无真值/接触/模型/FK输入。

## 有限状态与参考
1. OBSERVE原静态proper/gyro/qd/tilt一致性.25s，保留实际q，只有reference-only tiny投影。超时仍从启动计6s，原有限pitch<=1/roll<=.25、age/clock/相对driver盒均不变。
2. LIFT_WORLD_SUPPORT 2.20s：支撑q4加共同h=clip(-estimated pitch, all4 active boxes交集)。参考desired=(1-s)*locked_q0+s*support_goal，s为quintic；对每次desired使用单一gamma线段投影，使整个q4以最多.999rad/s移动，再仅参考roundoff投影。相对delta盒和active盒是凸集；该同步gamma不分别扭曲hip/crank路径。vref用实际参考差/实际validated dt，不用陀螺替代参考导数。2.20s大于研究端点理论min2.02715762s，移动goal仍受率限制，不保证该时刻已可达。
3. CAPTURE_WORLD_SUPPORT继续传感器共同角参考；不把主轮接触当已知。首次同包fresh、q跟踪误差<=.08、qd<=.40、proper norm .8..1.2g、wheel max<=2才允许latch原名义K的pitch/rate轮common；每个姿态轮命令还要同包fresh/qerr<=.08/qd<=.40/proper norm窗口，否则退回quiet damping。这些都不是接触证书。
4. CAPTURE内估计pitch/roll<.12、support_goal qerr<=.08、qd及参考速度<=.20、omega<=.50、wheel<=2且fresh连续.25s后RETURN_NOMINAL 1.00s。把已发布参考锁为return_from，quintic到原nominal target；相同gamma/rate/盒约束，名义与支撑trim同quintic插值。不是强行写joint/root。允许return超1s直到reference实到target，6s超时不放宽。
5. VERIFY严格用原V3_ready（原.15rad/nominal qerr.04/qd.20/omega.50/fresh并wheel<=2）连续.50s；BLEND原.50s且ready丢失即fault，再BALANCE。只BALANCE后下一prepare恢复wheelKF/ground constraint，不改旧observer策略。

## 扭矩、guard与日志
- 所有recover阶段仅120*(qref-q)+4*(vref-qd)+选定trim及原roll20/2±8，绝不再叠leg K。轮在lift仅-.30*same-packet rate限2Nm；允许pose时仅旧K wheel行的pitch/rate共同项减同damping、限3Nm，保留old>12rad/s且还同向加速时反向damping替代。不是物理转速保证。
- 最后统一40Nm腿/5.775909774436091Nm轮请求限幅；原inverse-PD/D4/随机PD/gain/signed-DC/物理约束链完全由原runner持有，不把0request称真实0torque。
- encoder rotation proxy仍dt*.0625*mean(abs(wheel))、recover全段至最后VERIFY→BLEND计入，>.50m粘性INHIBIT；非真实路径。旧trueXY/private gate均不改。
- 每次记录实际发布qref/vref、参考目标/common clip/gamma、phase、support trim混合、actual output、capture条件/软限、travel；fault时current参考不假填，用last_published字段单列。contact_or_support_trusted=False/hardware_send_permission=False。

## 本次新增验证预算/后续
新preflight最多600 enabled commands、40 disabled/oracle total commands、16 typed cases，全部fresh synthetic；fake GroundController/analytic tracking会明确标识，不是robot/gain/physics测试。新增unit/model/FK/PHY/旧QA0，原proof不重跑。
entry只在原V5模板上独立派生新kind/ID/config/import/support参考绑定与provenance，核心for-loop/driver/private gates AST不改。新physics尚未批；只在新preflight/独立源码review/父source冻结和one-case approval以后，才允许同一个front自然落稳fixture的一次新nominal10s TRAIN，不自动DR/back/侧卧。
