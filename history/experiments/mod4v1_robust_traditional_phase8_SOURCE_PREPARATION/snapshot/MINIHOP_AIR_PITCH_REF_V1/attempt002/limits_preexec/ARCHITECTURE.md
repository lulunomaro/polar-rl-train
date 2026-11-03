# Attempt002 — 明确授权的一次参考domain修订，非gain拟合

- [Attempt001](<../attempt001/LIMITS_RESULT.json>)真实51点全部完成，FK有限且共旋转成立，但14点违反原XML hip/drive_hip上限，status NOT_READY_DOMAIN；原source/architecture/parameter/锁和失败保留，不称READY。
- 父明确授权且仅此第二假说：kp=.25、kd=.04、rate=1rad/s、100Hz不变；h改为clip(.25*state14[2]+.04*state14[9],**[-.10,+.03]rad**)。依据公开crouch/机械joint上限修参考domain，非DR/GT或单位ddot拟gain；名义正端15.825876mrad余量不保证DR实际关节不越界。
- 原[架构](<../attempt001/ARCHITECTURE.md>)除这一domain和002验证计划外保持：default-off exactdelegate，operator默认False；approach/push/position/launch guard/observer不变；flight临时q_start+h*ones4、finally恢复；firstcapture冻结last h，eq0 hip3/5与真实ctrl.eq/ref在super前设anchored值，delta4/6、K0/K1/ff0/ff1/eq1不动，V3自然桥接，不事后改tau/补日志。
- 先新锁/再51点gate。若002还违反任何原限位或FK gate，停止为NOT_READY，不实施第三版或放松阈值。成功后仅按锁定一次new synthetic/default600、enabled600、全部flight/capture reference FK/limits与受控entry main admission；不PHY/linearize/编译/Git/agents/raw/旧QA。
- 所有代码/entry在本树attempt002内，旧controllers/runner/grade/actuator、001与模型source只读；PH7 cutoff不扩大，未来PHY由父独立安排。
