from pathlib import Path
import json,hashlib,subprocess,datetime,ast,numpy as np,imageio.v2 as imageio
P=Path(__file__).resolve().parent;E=P.parent;R=E.parents[3];NL=chr(10)
def save(name,data):(P/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+NL,encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
source=json.loads((P/'SOURCE.json').read_text());checks={rel:sha(E/rel)==value for rel,value in source['sha256'].items()};assert all(checks.values())
profile_path=E/'forward_capture_repair_20261116/CANDIDATE_PROFILE.json';assert profile_path.read_bytes()==(P/'FROZEN_PROFILE.json').read_bytes()
rows=[]
for deg in [-20,-10,10,20]:
 d=P/f'oblique_{deg:+04d}deg_v1';z=json.loads((d/'OBLIQUE_EVAL.json').read_text());raw=json.loads((d/'RESULT.json').read_text());z['contact_yaw_deg']=raw['entry']['yaw_deg'];z['path']=str(d);z['closure_peak_m']=raw['closure_peak_m'];z['wall_seconds']=raw['wall_seconds'];z['phase_counts']=raw['phase_counts'];z['physical_climb_sustained']=bool(raw['pass_stair']and z['final_top']);assert z['entry_angle_valid']and z['error']is None and z['optimizer_steps']==0 and z['actor_calls']==0
 model=json.loads((d/'MODEL_CHECK.json').read_text());assert all(model['physical_coefficients_unchanged'].values());assert model['physics_dt']==.0025 and model['leg_hz']==100 and model['wheel_hz']==400 and model['policy_hz']==50
 z['scene_sha256']=sha(d/'scene.xml');rows.append(z)
assert len(set(r['scene_sha256']for r in rows))==1
pointer=R/'deliveries/CURRENT_COMPREHENSIVE_MODEL.json';assert pointer.read_bytes()==subprocess.check_output(['git','show','HEAD:deliveries/CURRENT_COMPREHENSIVE_MODEL.json'],cwd=R)
reader=imageio.get_reader(P/'OBLIQUE_FOUR_ANGLES_1X.mp4');meta=reader.get_meta_data();reader.close();assert meta['fps']==25 and abs(meta['duration']-5.8)<.05
for p in [P/'run_case.py',P/'run_four_angles.py',P/'render_probe.py',P/'finish_report.py']:ast.parse(p.read_text(encoding='utf-8-sig'))
save('VERIFICATION.json',dict(frozen_controller_checks=checks,original_candidate_profile_unchanged=True,default_pointer_same_as_HEAD=True,default_model=json.loads(pointer.read_text()),scene_sha256=rows[0]['scene_sha256'],scene_same_as_previous='da375549b9bf016794dcf581efca620dd98085e9ae5b1154b8795f9ad22f7d52'==rows[0]['scene_sha256'],physics_dt=.0025,leg_hz=100,wheel_hz=400,policy_hz=50,video_fps=25,video_duration_s=meta['duration'],video_dimensions=meta['size'],video_1x=True,visual_qa='Native MuJoCo four-panel frames inspected; failures retained.',actor_calls=0,optimizer_steps=0))
save('RESULTS.json',dict(source_commit=source['commit'],status='NOT_RELIABLE_OBLIQUE_STAIR',passed=sum(z['pass_oblique']for z in rows),requested=4,each_angle_runs=1,rows=rows,controller_modified=False,training_started=False))
lines=['# 冻结当前教师：200mm台阶斜向四角度摸底',f"来源commit：{source['commit']}。按人类最新请求，仅测试现有教师，不进行控制器修复或训练。",'', '**四次里仅−10°成功稳定登台；+10°短暂登台后掉台；±20°从未进入lift。当前不能可靠斜向上200mm。**','', '## 条件与真实角度','', '200mm台阶，center起点x=0、y=0；腿长0.3466m；速度指令0.47m/s；每例10s。四例初始偏航及保持目标均为−20/−10/+10/+20°，不会先转正再拿正向成绩冒充斜向。冻结的控制器/增益、scene、原PD/电机、35/78/6和2.5ms/100Hz/400Hz/50Hz不变，2mm仅诊断，c874默认不变。','', '| 指令角度 | 触阶实际角度 | 入阶100ms均速(m/s) | 稳定台顶(s) | 全程最大俯仰(°) | 全程最大横滚(°) | 全程最大后退(cm) | 结果 |','|---|---:|---:|---:|---:|---:|---:|---|']
for z in rows:
 deg=z['case']['yaw_deg'];outcome='通过，末帧仍在台顶'if z['pass_oblique']else('短暂登台后掉台'if deg==10 else'未触发lift，未登台')
 lines.append(f"| {deg:+d}° | {z['contact_yaw_deg']:+.2f}° | {z['entry_speed_mps']:.4f} | {z['stable_top_s']:.2f} | {z['pitch_peak_deg']:.2f} | {z['roll_peak_deg']:.2f} | {z['max_backward_mm']/10:.2f} | {outcome} |")
lines+=['','触阶实际角度来自原始entry的首个触阶后记录；OBLIQUE_EVAL还保存触阶前100ms平均机身朝向和实际速度方向。上表角度不拿初始设定代替实测。后退按指定进场方向投影的峰谷位移，最大倾角包含失败/掉台过程。速度表列实际值，未宣称严格同实际入阶速度配对。','', '## 四例实际发生了什么','', '- −10°：实际触阶约−8.75°，走完lift→swing→plant→capture，连续稳定台顶5.10s，末帧双轮仍在台顶。最大相对航向误差4.19°；仍有约2.87cm短暂回缩。','- +10°：实际触阶约+7.40°。完成前摆落轮并曾连续双轮台顶0.40s，但capture又回plant，随后掉台；不能记通过。最大横滚63.63°，不是仅仅旧评分的航向不合格。入阶速度0.5236略超旧0.52测速窗，实际掉台独立构成失败。','- ±20°：全程500个控制帧均idle，没有lift/swing/plant/capture；双轮台顶支撑帧均为0。已经碰到台阶、导轮出现承载，但抬腿触发没有成功，随后被顶退；两例仍在台下。下一步若修复，应先定位触发条件与两侧触阶配合，不能把结果归为抬腿后力量不足。','', '现有小样本显示正负方向表现不对称。每角度仅一次，不扩展成多起点/扰动矩阵，不从正向5/5继承斜向能力。','', '## 评分与原始记录','', '原run_teacher的RESULT.json包含“相对世界0°偏航≤5°”，对真正斜向命令不适用，四份原始RESULT完全保留。独立OBLIQUE_EVAL用相对指定航向的同一5°误差、原入阶速度窗、原>=0.4s支撑标准及末帧仍在台顶，另检查实际斜角达成；不改写原RESULT。+10°即使曾满0.4s，也因末帧不在台顶判失败。','', '每例完整trace/STEP_DIAGNOSTICS、原始结果、新评分、HEADING_COMMAND、源码快照与SHA均保留。仿真无数值异常，闭链峰值全部小于2mm，本轮仍不启用2mm门控。','', '## 回放','', '- OBLIQUE_FOUR_ANGLES_1X.mp4：四例同屏、首次触阶对齐、25fps/1×，含失败过程。','- OBLIQUE_COMPARISON.png：机身俯仰/横滚、真实前向速度、实际偏航与目标、台顶承载轮数。','', '所有actor_calls和optimizer_steps为0；无学生蒸馏、无PPO。代码和实验记录按项目政策使用record_experiment归档，raw大文件保留路径/大小/SHA索引。']
(P/'REPORT.md').write_text(NL.join(lines)+NL,encoding='utf8')
mem=f'''## 2026-11-16 {datetime.datetime.now().strftime('%H:%M')} 人类授权斜向摸底：200mm四角仅1/4稳定

按最新人类“测试斜着能否上台阶”授权，仅冻结476006f4当前候选做center起点−20/−10/+10/+20°四例，航向目标等于初始斜角，全程保持，不先转正。−10°实际触阶−8.75°通过，连续稳定5.10s；+10°实际+7.40°仅短暂台顶0.40s后掉台（最大横滚63.63°）；±20°触阶实际−19.27/+15.66°，全程idle未触发lift，台顶支撑0。当前不能可靠斜上200mm，不能从正向5/5推断斜向已会。

控制器、原候选profile、scene/碰撞、PD/电机、35/78/6、2.5ms/100Hz/400Hz/50Hz和默认c874均未改；仅独立测试脚本设置初始/目标航向并按相对指定航向评分，原世界零航向RESULT保留。无学生/PPO更新，不扩大矩阵。证据：sources/local/MOD4V3_SERIAL_LQR_SKILL_TEACHER_20261116/equivalent_controller_v1/oblique_probe_20261116/REPORT.md。本轮最新人类授权覆盖下方旧“暂不扩斜向”范围，仅限这四例测试。

'''
for rel in ['AGENTS.md','sources/local/MOD4V3_SERIAL_LQR_SKILL_TEACHER_20261116/README.md','sources/local/MOD4V3_SERIAL_LQR_SKILL_TEACHER_20261116/MEMORY_ENTRY.md']:
 old=subprocess.check_output(['git','show','HEAD:'+rel],cwd=R);(R/rel).write_bytes(mem.encode('utf8')+old)
root=R.parent/'AGENTS.md';root.write_bytes(mem.encode('utf8')+root.read_bytes());(P/'MEMORY_UPDATE.md').write_text(mem,encoding='utf8')
print(json.dumps(dict(passed=sum(z['pass_oblique']for z in rows),total=4,controller_frozen=all(checks.values()),video_seconds=meta['duration']),ensure_ascii=False))
