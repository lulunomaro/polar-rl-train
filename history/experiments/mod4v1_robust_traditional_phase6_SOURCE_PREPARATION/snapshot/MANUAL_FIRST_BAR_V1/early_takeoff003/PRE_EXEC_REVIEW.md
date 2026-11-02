# R52 PRE_EXEC_REVIEW

**PASS_STATIC_PRE_EXEC_REVIEW_R52_NOT_LAUNCHED_BY_REVIEWER** — ready_for_physics=true; 此布尔仅表示允许按父准入链试验，不表示将通过。

- 两个case先flat后RM/max1，nominalTrue/seed0，start.2/forward.9/trigger2.0/brake2.5/duration8均传到真实entry。
- 旧V3/V2/V1源锁、predAir.35/obs.5/captureblend.1/landingtransition.2/guard pitch-roll.15/speed1.2未改；noSmooth不是删除原smoothstep。
- 实际runner用原loader、sensor→estimator→hop；private grade/bounds在requested后，只作grade/log，不入控制器。
- 原moving-flat/local gate未放宽：complete+mesh>=.08+guide/hard=0+endstable>=2+maxy<=.3+progress>=.5；RM另要全机器人behindfirstbar且不达nextbar。
- SOURCE_PREEXEC所列small源/preparer SHA全部一致；实际检查路径和完整SHA在JSON.checked_sources。未扫旧tree/279assets。
- 803/0、initialtireRear.101638946m、synthetic capture2.49仅原zero-step证据，不证明实际速度/guard/firstflight间隙或全RM成功。
- 父launcher仍负责flat原moving-flat gate实际PASS后才RM、新ID/目录、软件错误停后续、不替换不改gate；本review未launch。
- 没有import/执行preparer或runner、重跑unit/boot/physics、读取H5/raw/assets、Git/agent/真实IO或修改旧文件。
