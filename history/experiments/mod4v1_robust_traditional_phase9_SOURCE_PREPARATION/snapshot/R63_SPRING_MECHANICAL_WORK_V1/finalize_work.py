"""Saved-only report and small-source/stat receipt. No raw reopen/model execution."""
from pathlib import Path
import json,hashlib
O=Path(__file__).resolve().parent;ROOT=O.parent
S=json.loads((O/'SOURCE_LOCK.json').read_bytes());X=json.loads((O/'SUMMARY.json').read_bytes())
def rec(p):
 b=p.read_bytes();return dict(path=str(p.resolve()),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def link(label,p,anchor=''):return '['+label+'](<'+p.resolve().as_posix()+anchor+'>)'
assert X['status']=='PASS_SINGLE_RAW_PASS_STAGE_CHECKED_MECHANICAL_WORK_ANALYSIS_ONLY'and X['error']is None and X['rows_read']==33600 and all(x==1 for x in X['raw_opens'].values())
refs=[]
for r in S['small_refs']:
 a=rec(Path(r['path']));assert a==r;refs.append(a)
rawmeta=[]
for c in S['cases']:
 for s in c['streams']:
  stat=Path(s['path']).stat();assert stat.st_size==s['bytes']and stat.st_mtime_ns==s['mtime_ns'];rawmeta.append(s)
a,b=X['cases'];assert a['complete']and b['complete']
phases=[('timed_push','push'),('predicted_flight_retract','predicted flight'),('timed_capture','capture'),('whole_episode','whole8s')]
fmt=lambda g:'/'.join(f'{g[k]:+.6f}'for k in('net_work_J','positive_work_J','negative_work_J'))
clock=max(c['clock_max_abs_error_s']for c in X['cases']);prefix=X['prepush_public_prefix'];delta={}
for phase,label in phases:
 delta[label]={group:{key:b['work'][phase]['groups'][group][key]-a['work'][phase]['groups'][group][key]for key in('net_work_J','positive_work_J','negative_work_J','net_mean_power_W')}for group in('legs4','wheels2')}
lines=['# R63气弹簧反补偿：两条既有nominal flat机械功（只读）','',
'**只分析R58 baseline flat与R63 release nominal flat；原门两案均pass照旧。不触碰正在运行的paired波次，不新增PHY/单位测试/模型/FK/driver执行、gain或第三假说。**','',
'## 1. 方法与阶段核对',
'- '+link('METHOD',O/'METHOD.json')+'和'+link('SOURCE锁',O/'SOURCE_LOCK.json')+'先于raw；4个精确allowlist raw各open一次，总33600行（2×800控制+2×16000物理）。10小文件SHA/10producer代码SHA关联核对，raw只复用producer SHA与size/mtime，不算大hash、不归档raw。',
'- '+link('PRE记录:43–60',ROOT/'MINIHOP_AUDIT_V2/contact_grade_v2.py','#L43-L60')+'在同一captured PRE保存velocity6_rad_s与actual_tau6_Nm；'+link('active apply:11–16',ROOT/'MINIHOP_AUDIT_V2/physics_bridge_minihop_flat_v2.py','#L11-L16')+'显示它在限幅/增益后、ctrl赋值/step之前，root POST另列。它是模型driver-point命令，不是独立电机反馈。',
'- 瞬时机械P_i=τ_PRE·dq_PRE（W），功W_i≈ΣP_i×0.0005（J），采用left-Riemann；正/负先逐轴每sample分开，再聚合leg[0,1,3,4]/wheel[2,5]。不是精确离散能量，也不是电气母线功率/回充。',
f'- 验sample_index/drive tick/drive timestamp/PRE→POST/20:1与control command/post时间，最大钟差 {clock:.12g}s（预锁1e−8s）。没有混入rootPOST速度或重建q。',
'- 实际两案phase均195 approach、15 push、25 predicted-flight、565 capture：push [1.95,2.10)为300cells/0.15s，虽cfg名义push=.14s也不强裁14帧；flight [2.10,2.35)，capture [2.35,8)。',
'- 包含最后index15999的[7.999499999998286,7.999999999998286)；16000个完整500us权重合8s，无丢尾/半格补点。whole还含approach，不等于只加下表三个动作段。','',
'## 2. 100Hz prepush公共前缀（不是2k bit证明/资格门）',
f'- 实际首push控制index195；比较此前195行（command0..1.94s）的13公共sensor/estimate/request字段共{prefix["scalar_values"]}标量，maxdiff={prefix["max_abs_difference"]:.1f}，binary64解析值bit差{prefix["binary64_value_mismatches"]}，phase差{prefix["phase_mismatches"]}。',
'- 字段为time/command/forward/sensor time与age、estimated14/roll、raw gyro/proper、encoder q/dq、wheel mean rate、requested_tau6；不是物理2k全状态逐bit对照，未拿名义FF差替代actual τ差。','',
'## 3. 实际clip后机械功：每格“净/正/负”，单位J',
'|实际控制段(时长)|R58腿4|R63腿4|R58轮2|R63轮2|',
'|---|---:|---:|---:|---:|']
for phase,label in phases:
 duration=a['work'][phase]['duration_s'];lines.append('|'+label+f' ({duration:g}s)|'+fmt(a['work'][phase]['groups']['legs4'])+'|'+fmt(b['work'][phase]['groups']['legs4'])+'|'+fmt(a['work'][phase]['groups']['wheels2'])+'|'+fmt(b['work'][phase]['groups']['wheels2'])+'|')
lines+=['- 负功按带负号记；同时有轴做正功/轴做负功时不先抵消。'+link('小SUMMARY',O/'SUMMARY.json')+'保留6轴与分组full precision、net_mean_power_W、各段PRE/POST边界和source域。',
'- push腿净功反而减少1.204919J：正功仅增加0.154286J，负功多1.359205J；push轮净功增加0.190845J。不能以“加回FF→push腿净正功必然更多”解释高度变化。',
'- predicted-flight腿净功增加4.530170J、轮增加3.800983J；capture腿更负2.043579J、轮少2.921213J。即使这些阶段方程未改，push后的状态/速度与真实限幅轨迹已不同，机械作用被重分配。',
'- whole腿净+1.281672J、轮净+1.070614J；whole四腿均功率0.968466→1.128675W，两轮9.274604→9.408431W。它们是机械平均功率，不能转换为电池省电/耗电/再生结论。','',
'## 4. 已记录事件与峰值，保持原grade解释',
'|case|air区间开始PRE(s)|20ms确认POST(s)|main-mesh峰高(m)/cache PRE(s)|首landing PRE/POST(s)|身份|',
'|---|---:|---:|---|---|---|']
for c,label in((a,'R58'),(b,'R63')):
 e=c['observed_first_qualified_air'];p=c['observed_all_qualified_air_main_mesh_peak'];l=c['observed_first_landing'];ids=', '.join(x['robot_geom']+'→'+x['environment_geom']for x in l['contacts'])
 lines.append(f'|{label}|{c["reported"]["first_air_s"]:.4f}|{e["confirmation_POST_s"]:.4f}|{p["clearance_m"]:.9f} / {p["cache_PRE_s"]:.4f}|{l["stage_PRE_s"]:.4f} / {l["root_POST_s"]:.4f}|{ids}|')
lines+=['- main-mesh qualified-air峰高增加10.457124mm，不是COM势能或单独根高度。air条件来自既有全world法向合计定义，不新增评分/接触许可。',
'- 实际air区间在push内开始、确认也仍属push；首landing在capture内。表中predicted-flight只是控制phase，capture积分5.65s也不是只取撞击瞬间。',
'- 记录到的六轴正机械瞬时峰544.963243→603.332973W，均出现在predicted-flight；与原result一致到舍入误差，不是母线峰功率/过流证据。','',
'## 5. 结论与unknown',
'同prepush公共记录下，反补偿改变了后续实际driver-point机械功分布与几何air峰；这两条nominal轨迹只支持上述机制观察，不推出唯一因果/DR泛化。实际gas做功、弹簧势能变化、重力/接触/阻尼完整能量账与电气损耗未从该记录分解；不重建q或用nominal tauGas冒充实测。原分数/源/阈值保持，完成即停止，不设计第三假说。']
# Keep file mentions clickable; no report-driven raw/body read.
report='\n'.join(lines)+'\n';report=report.replace('不能以','不宜以').replace('不能转换','不作转换');assert len(report.splitlines())<=60
with(O/'REPORT.md').open('x',encoding='utf-8',newline='\n')as f:f.write(report)
receipt=dict(status='SEALED_TWO_NOMINAL_FLAT_SINGLE_PASS_PRE_MECHANICAL_WORK_ONLY',report=rec(O/'REPORT.md'),report_lines=len(report.splitlines()),summary=rec(O/'SUMMARY.json'),method=rec(O/'METHOD.json'),source_lock=rec(O/'SOURCE_LOCK.json'),extractor=rec(O/'extract_once.py'),extract_log=rec(O/'extract_001.log'),raw_open_counts=X['raw_opens'],rows_read=33600,small_refs_unchanged=refs,producer_source_matches=S['producer_source_matches'],raw_stat_stable_producer_SHA_reused=rawmeta,raw_SHA_recomputed=False,raw_reopened_after_extraction=False,prefix_public_fields=13,prefix_rows=195,prefix_values=8190,prefix_maxdiff=0.,clock_max_abs_error_s=clock,work_deltas_new_minus_old=delta,old_passes_preserved=[c['reported']['original_pass']for c in X['cases']],physics_model_FK_driver_oldQA_new_gain_actions=0,unique_cause_or_electrical_power_claim=False,third_hypothesis=False)
with(O/'RECEIPT.json').open('x',encoding='utf-8',newline='\n')as f:json.dump(receipt,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
print(json.dumps(dict(status=receipt['status'],report=receipt['report'],report_lines=receipt['report_lines'],summary=receipt['summary'],receipt=rec(O/'RECEIPT.json'),max_clock_error_s=clock,small_refs_unchanged=len(refs),raw_opens=receipt['raw_open_counts'],rows=33600),indent=2))
