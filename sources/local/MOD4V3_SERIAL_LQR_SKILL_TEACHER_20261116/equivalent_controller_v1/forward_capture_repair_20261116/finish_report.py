from pathlib import Path
import sys,json,numpy as np,hashlib,subprocess,datetime
P=Path(__file__).resolve().parent;E=P.parent;R=E.parents[3];NL=chr(10)
sys.path.insert(0,str(P));from analyze import metrics,interval
now=datetime.datetime.now().astimezone().isoformat()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def save(name,value):
 (P/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+NL,encoding='utf8')
rows=[]
for mm in [-60,-30,0,30,60]:
 pair=[]
 for label in ['baseline_v2','final_clean_v2']:
  d=P/f'{label}_{mm:+04d}mm';a=metrics(d);z=np.load(d/'trace.npz');i=np.searchsorted(z['trace'][:,0],a['exit_capture_time']);a['after_exit']=interval(z['trace'],z['qvel'][:,0],i,len(z['trace'])-1);a['path']=str(d);pair.append(a)
 old,new=pair;z0=np.load(Path(old['path'])/'trace.npz');z1=np.load(Path(new['path'])/'trace.npz');i=np.flatnonzero(z0['phases'][:,0]=='capture')[0]
 assert np.array_equal(z0['trace'][:i],z1['trace'][:i]);assert np.array_equal(z0['actions'][:i],z1['actions'][:i]);assert(Path(old['path'])/'scene.xml').read_bytes()==(Path(new['path'])/'scene.xml').read_bytes()
 rows.append(dict(offset_mm=mm,baseline=old,candidate=new,pre_capture_exact=True,scene_equal=True))
pointer=R/'deliveries/CURRENT_COMPREHENSIVE_MODEL.json';pind=json.loads(pointer.read_text(encoding='utf8'));weight=R/pind['full_PT_git_path']
checks=dict(baseline_commit='92e8cdbe529d34de1acd39cad0ede5fb4014d39b',baseline_profile_preserved=(P/'BASELINE_PROFILE.json').read_bytes()==(E/'prelift_contact_repair_20261116/CANDIDATE_PROFILE.json').read_bytes(),native_runtime_bytes=(E/'native_runtime.py').read_bytes()==(P/'baseline_code/native_runtime.py').read_bytes(),native_actuation_bytes=(E/'native_actuation.py').read_bytes()==(P/'baseline_code/native_actuation.py').read_bytes(),native_contacts_bytes=(E/'native_contacts.py').read_bytes()==(P/'baseline_code/native_contacts.py').read_bytes(),scene_sha256=sha(Path(rows[0]['candidate']['path'])/'scene.xml'),default_pointer=pind,default_pointer_same_as_HEAD=pointer.read_bytes()==subprocess.check_output(['git','show','HEAD:deliveries/CURRENT_COMPREHENSIVE_MODEL.json'],cwd=R),actual_default_weight_sha256=sha(weight),physics_dt=.0025,leg_hz=100,wheel_hz=400,policy_hz=50,actor_critic_actions=[35,78,6],closure_2mm='diagnostic only; no new reward/reset/stop gate')
assert checks['actual_default_weight_sha256']==pind['sha256'];assert all(checks[k]for k in ['baseline_profile_preserved','native_runtime_bytes','native_actuation_bytes','native_contacts_bytes','default_pointer_same_as_HEAD'])
for row in rows:
 c=json.loads((Path(row['candidate']['path'])/'MODEL_CHECK.json').read_text());assert all(c['physical_coefficients_unchanged'].values());assert c['physics_dt']==.0025 and c['leg_hz']==100 and c['wheel_hz']==400 and c['policy_hz']==50
trials=[]
for f in sorted(P.glob('*/RESULT.json')):
 z=json.loads(f.read_text(encoding='utf8'));m=metrics(f.parent);trials.append(dict(id=f.parent.name,case=z['case'],pass_teacher_stair=z['pass_teacher_stair'],stable_hold_s=z['max_continuous_top_hold_s'],whole_pitch_peak_deg=z['pitch_peak_deg'],metrics=m,actor_calls=z['actor_calls'],optimizer_steps=z['optimizer_steps'],wall_seconds=z['wall_seconds'],error=z['error'],source=str(f.parent/'SOURCE.json')))
assert all(t['actor_calls']==0 and t['optimizer_steps']==0 for t in trials)
report=dict(recorded_at=now,status='FIVE_START_STABILITY_PASS_RECOIL_REMAINS_NOT_MOTION_QUALIFIED',baseline_passed=sum(x['baseline']['pass_scoring']for x in rows),final_passed=sum(x['candidate']['pass_scoring']for x in rows),requested_starts=5,rows=rows,checks=checks,optimizer_steps=0,ppo_updates=0,front_wait_loss_repaired=False,extended_matrix_started=False,total_saved_rollouts=len(trials),rollout_wall_seconds_sum=sum(t['wall_seconds']for t in trials))
save('RESULTS.json',report);save('TRIALS.json',trials);save('CONTRACT_CHECK.json',checks)
shared={n:dict(path=str(E/n),sha256=sha(E/n),bytes=(E/n).stat().st_size)for n in ['native_geometry.py','native_full_mjcf_gains.npz','data/lqr_gain_fit.py','native_runtime.py','native_actuation.py','sim/lqr_governor.py']};save('SHARED_DEPENDENCIES.json',shared)
lines=['# 200mm 五起点：保留前段，修复落台接管与停车回拉',f'记录时间：{now}。前段来源：92e8cdbe / prelift candidate clean center v2。','', '**结论：原版五起点2/5；本轮接管修复后5/5稳定登台。仍有短暂回缩，未达到“无明显倒溜”的动作质量要求；前段等门控丢速也未修好。不扩矩阵，不蒸馏，不PPO。**','', '## 原版摸底（十秒完整轨迹，失败完整保留）','', '| 起点 | 原版通过 | 最长稳定(s) | 触阶后最大俯仰(°) | 最低前向速度(m/s) | 最大峰谷后退(mm) |','|---|---|---:|---:|---:|---:|']
for q in rows:
 a=q['baseline'];v=a['full'];lines.append(f"| {q['offset_mm']:+d}mm | {'通过'if a['pass_scoring']else'失败'} | {a['stable_hold_s']:.2f} | {v['pitch_peak_deg']:.2f} | {v['min_vx']:.3f} | {v['max_retreat_mm']:.1f} |")
lines+=['','- 原先失败过的−30mm，在未改动的本版v2已经通过；不能说成本轮修复首次把−30mm教会上阶。','- −60、+30、+60mm落台后退回台沿并掉台/失稳；+30mm曾短暂满0.4s，但后续失败，原协议pass_teacher_stair=false，保留失败。','- 最低速度为qvel[:,0]有符号前向速度，不是无符号水平范数。后退为历史最高X到随后最低X的最大差，非仅首尾位移。','', '## 相同前段，修复后五起点实测','', '| 起点 | 稳定登台(s) | 前段峰值(°) | 整段峰值(°) | 整段最低vx(m/s) | 整段最大后退(mm) | 最小轮心越边量(mm) |','|---|---:|---:|---:|---:|---:|---:|']
for q in rows:
 a=q['candidate'];v=a['full'];lines.append(f"| {q['offset_mm']:+d}mm | {a['stable_hold_s']:.2f} | {a['prelift']['pitch_peak_deg']:.2f} | {v['pitch_peak_deg']:.2f} | {v['min_vx']:.3f} | {v['max_retreat_mm']:.1f} | {a['min_top_wheel_margin_mm']:.1f} |")
lines+=['','五个起点开始至首个capture之前，trace和actions与各自原版逐帧完全相同。因此前段质感和lift/swing/plant路径未被替换，其他起点9～11°峰值也未隐藏。','', '## 落台接管段（首个capture记录到退出capture）','', '| 起点 | 最低vx 原→新(m/s) | 最大后退 原→新(mm) | 峰值俯仰 原→新(°) |','|---|---:|---:|---:|']
for q in rows:
 a=q['baseline']['capture'];b=q['candidate']['capture'];lines.append(f"| {q['offset_mm']:+d}mm | {a['min_vx']:.3f} → {b['min_vx']:.3f} | {a['max_retreat_mm']:.1f} → {b['max_retreat_mm']:.1f} | {a['pitch_peak_deg']:.2f} → {b['pitch_peak_deg']:.2f} |")
lines+=['','1. 仍在承载也被capture约0.32s超时赶回plant，重复落轮。改为有可信双轮承载时继续LQR接管；总Cartesian时限也不抢断这段已承载的平衡，原姿态/卸载与数值保护保留。','2. 原来前45ms腿沿用旧Cartesian力矩、轮子立即切新LQR。去掉仅腿的旧力矩偏移，让完整LQR同时接管，center接管后退约44.8→25.2mm，前段不变。','3. 松油即把位置目标锁在松油点，刹车前移后位置环会再拉回去。本轮仅对台阶capture退出后的停车，先以零速度参考刹车、位置参考随当前里程计更新，等速度到零反向再锁位置，避免退回台沿。退出capture后的实测后退均为0；十秒末仍约0.02～0.03m/s微正速度，不宣称精确原地停车。','', '## 前一段丢速：定位到来源，但没有合格修复','', 'center约4.30～4.40s与原版完全一致：真实vx约0.560→0.392；首个lift后记录约0.276m/s。前段峰值2.824°、爬阶峰值6.644°保留。','', '400Hz原生几何/接触数据表明，左轮在4.30～4.34s真实离墙约7～10mm，并非单纯50Hz漏采样；不应伪造承载继续加轮矩。右轮负轮矩来自原LQR腿角速度和俯仰角速度等反馈，非target_x被误写成台阶后方的绝对世界坐标。导轮承载及俯仰外力矩也明显变化，不能只看reqW负值就认定它是全部减速原因。','', '等待期腿速参考、墙面单向轮矩、统一高度参考、保持进场速度，以及落台降速、腿速/速度缓接管、传感器和轮速同步等探针均保留独立结果。有的单起点变好却让center掉台或增大俯仰，已全部撤出当前代码；没有把失败方案叠成当前控制器。','', '仍欠：等待期不能提前丢掉这么多速度；center与−30mm短暂回缩仍可见，整段分别约41.5和45.7mm。5/5不能当作动作质量已合格。','', '## 回放与曲线','', '- FIVE_STARTS_V2_VS_CAPTURE_REPAIR_1X.mp4：全部五点原版/修复并列，25fps、1×，首次触阶对齐，每例包含失败或停车后过程。','- FIVE_STARTS_COMPARISON.png：五点俯仰、真实vx、机身位移和轮心越边量。','- CENTER_REFERENCE_DIAGNOSTIC.png：等门控丢速、接管轮矩与停车位置参考。','- replay_clean_v1/：上一清理版回放保留。最终v2的−30mm受总capture时限修复影响，已重出视频，未复用不一致回放。','', '## 保持的合同与证据','', '场景XML SHA256：'+checks['scene_sha256']+'。native_runtime/native_actuation/native_contacts与保留v2字节相同。原电机、PD与动作边界，物理2.5ms/腿100Hz/轮400Hz/策略50Hz、35/78/6不变；2mm仍只诊断。默认指针与HEAD字节一致，实际权重SHA仍为'+checks['actual_default_weight_sha256']+'。',f"本阶段保存{len(trials)}次独立回放，各进程wall time合计{sum(t['wall_seconds']for t in trials):.2f}s（并行进程时间相加，非墙钟耗时）。所有actor_calls与optimizer_steps为0。",'', 'TRIALS.json列全部成功、失败、对照与清理复测及源码路径。ARTIFACT_INDEX.json索引大型原件真实路径/大小/SHA。按项目要求使用record_experiment归档到当前分支及唯一annotated trial，不合并main。']
(P/'REPORT.md').write_text(NL.join(lines)+NL,encoding='utf8')
mem=f'''## 2026-11-16 {datetime.datetime.now().strftime('%H:%M')} 五起点授权与接管修复：5/5稳定，仍未无倒溜验收

最新人类授权保持92e8cdbe前段候选，先跑200mm五起点[-60,-30,0,+30,+60]mm。原版v2实测2/5（−30与center过，另三例落台后退失稳）；保留其CANDIDATE_PROFILE。当前forward_capture_repair_20261116候选仅修capture承载时错误重入plant/超时、去除仅腿45ms旧力矩偏移、退出capture后停车位置参考回拉，五点5/5稳定4.60/5.24/5.26/5.36/5.38s。五例首次capture之前状态/动作与各自v2原版逐帧相同。

仍未动作质量合格：center前段2.824°、整段6.644°不变，等待期vx .560→.392、首lift记录.276m/s仍未修好。center接管后退44.8→25.2mm，−30约23mm；含lift/swing等整个上阶过程分别仍后退约41.5/45.7mm。三个原失败点均稳定；停车后不再退回松油位置，但末端仍约.02～.03m/s微正速度，非精确原地停车。失败探针已全部退出在用代码、记录并列保留。五点稳定通过不等于无明显倒溜，也不等于技能教师毕业。

硬边界不变：scene/platform/tire、原PD/电机、35/78/6、2.5ms/100Hz/400Hz/50Hz、2mm仅诊断、默认c874不变。无学生/PPO更新、无大矩阵；下一步只修剩余丢速与短暂回缩，视频未获人类确认前不扩验收/蒸馏/PPO。证据：sources/local/MOD4V3_SERIAL_LQR_SKILL_TEACHER_20261116/equivalent_controller_v1/forward_capture_repair_20261116/REPORT.md。下方旧“只准单点/不能五起点”由本轮五点授权覆盖；旧通过率不继承。

'''
for file in [R/'AGENTS.md',R.parent/'AGENTS.md',E.parent/'README.md',E.parent/'MEMORY_ENTRY.md']:
 text=file.read_text(encoding='utf8');assert not text.startswith(mem.splitlines()[0]);file.write_text(mem+text,encoding='utf8')
(P/'MEMORY_UPDATE.md').write_text(mem,encoding='utf8')
save('REPORT_TOOLING_REPAIR.json',dict(status='repaired',scope='report generation only',error='Nested Python triple quote in initial writer; no file written and no physics repeated'))
print(json.dumps(dict(rollouts=len(trials),actual_default_sha256=checks['actual_default_weight_sha256'],rows=[dict(offset=q['offset_mm'],capture=q['candidate']['capture'])for q in rows]),ensure_ascii=False))
