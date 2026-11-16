"""Analyze controlled paired pitch tests and preserve unmatched/failure conditions."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib,collections,math,ast
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
A=Path(__file__).resolve().parent;R=A.parents[2];E=A/'evidence'
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')
def metric(z):
 rest=z[z[:,12]==0];drive=z[z[:,12]==1];brake=z[z[:,12]==2];entry=drive[-1];first=brake[:40];delta=np.diff(np.r_[entry[3],brake[:,3]]);active=np.vstack([drive,brake]);stopped=(np.linalg.norm(brake[:,5:7],axis=1)<.1)&(abs(np.rad2deg(brake[:,7]))<2)&(abs(brake[:,8])<.2)
 first_hold=next(((i+1)*.02 for i in range(len(stopped)-9)if stopped[i:i+10].all()),None)
 settle=next(((i+1)*.02 for i in range(len(stopped)-9)if stopped[i:].all()),None)
 return dict(entry_vx=float(entry[5]),entry_height_m=float(entry[9]),entry_pitch_deg=float(np.rad2deg(entry[7])),entry_pitch_rate_rad_s=float(entry[8]),entry_x_m=float(entry[3]),start_vx=float(rest[-1,5]),start_height_m=float(rest[-1,9]),start_pitch_deg=float(np.rad2deg(rest[-1,7])),startup_peak_deg=float(np.rad2deg(abs(drive[:40,7])).max()),acceleration_peak_1s_deg=float(np.rad2deg(abs(drive[:,7])).max()),startup_rate_peak_rad_s=float(abs(drive[:40,8]).max()),braking_peak_first0p8_deg=float(np.rad2deg(abs(np.r_[entry[7],first[:,7]])).max()),braking_peak_full2s_deg=float(np.rad2deg(abs(np.r_[entry[7],brake[:,7]])).max()),braking_rate_peak_first0p8_rad_s=float(abs(first[:,8]).max()),pitch_RMS_active3s_deg=float(np.rad2deg(np.sqrt(np.mean(active[:,7]**2)))),first0p8_path_m=float(abs(delta[:40]).sum()),full2s_path_m=float(abs(delta).sum()),settle_time_s=settle,first_hold02_time_s=first_hold,tail_last0p5_speed_RMS=float(np.sqrt(np.mean(np.sum(brake[-25:,5:7]**2,axis=1)))),braking_rate_peak_full2s_rad_s=float(abs(brake[:,8]).max()),end_speed_m_s=float(np.linalg.norm(brake[-1,5:7])),max_closure_m=float(z[:,10].max()),external_mu_min=float(np.nanmin(z[z[:,13]>0,14])),external_mu_max=float(np.nanmax(z[z[:,13]>0,15])),brake_speed_after0p8=float(np.linalg.norm(first[-1,5:7])),samples=len(z))
all_worker={};unmatched=[];paired=[];hard_paired=[];evidence_paths=[]
for contact in ['soft','hard']:
 by={}
 for kind in ['scut','mod4']:
  for direction in [1,-1]:
   name=f'{kind}_{"forward"if direction>0 else"reverse"}'+('_soft'if contact=='soft'else'');folder=E/name;p=folder/'RESULT.json';d=json.loads(p.read_text(encoding='utf8'));assert d['complete'];all_worker[name]=dict(complete=True,validated=sum(q['validated']for q in d['results']),requested=len(d['results']),attempts=len(json.loads((folder/'ATTEMPTS.json').read_text())['attempts']))
   for q in d['results']:
    key=(q['family'],q['height_command'],q['direction'],q['target_speed']);by[kind,key]=(folder,q)
 keys=sorted({key for kind,key in by})
 for key in keys:
  sf,s=by['scut',key];mf,m=by['mod4',key]
  if s['validated']and m['validated']:
   sp=sf/s['final']['trajectory'];mp=mf/m['final']['trajectory'];z1=np.load(sp)['trace'];z2=np.load(mp)['trace'];sm=metric(z1);mm=metric(z2);vdelta=abs(abs(sm['entry_vx'])-abs(mm['entry_vx']));hd=abs(sm['entry_height_m']-mm['entry_height_m']);control1=s['final']['control'];control2=m['final']['control'];assert vdelta<=.0200001
   for name in ['hfield_sha256','hfield_size','hfield_shape','hfield_ground_pos','ground_friction','ground_solref','ground_solimp','ground_condim']:
    assert control1[name]==control2[name],(name,key)
   assert sm['external_mu_min']==sm['external_mu_max']==mm['external_mu_min']==mm['external_mu_max']==1.
   row=dict(family=key[0],height_command=key[1],direction=key[2],target_speed=key[3],contact=contact,SCUT=sm,MOD4v3=mm,actual_entry_speed_difference=vdelta,actual_entry_height_difference_m=hd,actual_height_within2cm=hd<=.02,start_velocity_difference=abs(sm['start_vx']-mm['start_vx']),command_amplitudes=dict(SCUT=s['final']['command_amplitude'],MOD4v3=m['final']['command_amplitude']),trajectories=dict(SCUT=sp.relative_to(A).as_posix(),MOD4v3=mp.relative_to(A).as_posix()),braking_peak_ratio_MOD4_over_SCUT=mm['braking_peak_first0p8_deg']/sm['braking_peak_first0p8_deg'],startup_peak_ratio_MOD4_over_SCUT=mm['startup_peak_deg']/sm['startup_peak_deg'],path_ratio_MOD4_over_SCUT=mm['first0p8_path_m']/sm['first0p8_path_m'])
   (paired if contact=='soft'else hard_paired).append(row);evidence_paths.extend([sp,mp])
  elif contact=='soft':
   def missing(q):
    best=q.get('best_calibration');f=q.get('final');return dict(validated=q['validated'],calibration_matched=q['calibration_matched'],best_entry_speed=best.get('signed_entry_speed')if best else None,best_failure=f.get('failure')if f else None,reason=q.get('reason','Calibration or complete braking validation failed'),final_complete=f.get('complete')if f else None)
   unmatched.append(dict(family=key[0],height_command=key[1],direction=key[2],target_speed=key[3],SCUT=missing(s),MOD4v3=missing(m)))
# Same command tests on exactly the same material settings and command schedule.
reference={};same_command=[]
for kind in ['scut','mod4']:
 folder=E/('same_command_'+kind);d=json.loads((folder/'RESULT.json').read_text());assert d['complete']
 for q in d['rows']:reference[kind,(q['family'],q['height_command'],q['direction'],q['command_amplitude'])]=(folder,q)
for key in sorted({key for kind,key in reference}):
 sf,s=reference['scut',key];mf,m=reference['mod4',key];row=dict(family=key[0],height_command=key[1],direction=key[2],command_amplitude=key[3],SCUT_complete=s['complete'],MOD4_complete=m['complete'])
 if s['complete']and m['complete']:
  sp=sf/s['trajectory'];mp=mf/m['trajectory'];row.update(SCUT=metric(np.load(sp)['trace']),MOD4v3=metric(np.load(mp)['trace']));evidence_paths.extend([sp,mp])
 same_command.append(row)
stats={}
for direction in [1,-1]:
 q=[r for r in paired if r['direction']==direction];g=dict(pairs=len(q),ours_lower_brake=sum(r['MOD4v3']['braking_peak_first0p8_deg']<r['SCUT']['braking_peak_first0p8_deg']for r in q),ours_lower_startup=sum(r['MOD4v3']['startup_peak_deg']<r['SCUT']['startup_peak_deg']for r in q),height_within2cm=sum(r['actual_height_within2cm']for r in q))
 for side in ['SCUT','MOD4v3']:g[side]={field:float(np.mean([r[side][field]for r in q]))for field in ['startup_peak_deg','braking_peak_first0p8_deg','first0p8_path_m','pitch_RMS_active3s_deg']}
 stats['forward'if direction>0 else'reverse']=g
result=dict(created_at=datetime.now(timezone(timedelta(hours=8))).isoformat(),worker_counts=all_worker,speed_matched_pairs=len(paired),requested_pairs=24,unmatched_pairs=len(unmatched),actual_height_within2cm_pairs=sum(r['actual_height_within2cm']for r in paired),same_command_pairs=len(same_command),direction_summary=stats,paired=paired,unmatched=unmatched,same_command=same_command,hard_contact_paired=hard_paired,scope='Shared materials, terrain, nominal conditions and policy50Hz; native bodies, controller rates, physics timestep and solver iterations differ. Speed-matched uses separately calibrated command amplitudes, does not match whole trajectory or full brake-entry state. Native high-mu historical results are not mixed into primary metrics.')
dump(E/'COMPARISON.json',result)
# Full matched table plot.
ordered=sorted(paired,key=lambda q:(-q['direction'],q['family'],q['height_command'],q['target_speed']));x=np.arange(len(ordered));labels=[f'{"F"if q["direction"]>0 else"R"} {q["family"]}\nh{q["height_command"]:.2f} v{q["target_speed"]:.1f}'for q in ordered]
fig,axs=plt.subplots(3,1,figsize=(13,10),sharex=True,constrained_layout=True)
for ax,field,title in [(axs[0],'startup_peak_deg','Start-up pitch peak: first0.8s (deg)'),(axs[1],'braking_peak_first0p8_deg','Braking pitch peak: first0.8s (deg)'),(axs[2],'first0p8_path_m','Travel after brake command: first0.8s (m)')]:
 ax.bar(x-.18,[q['SCUT'][field]for q in ordered],width=.36,label='SCUT V14_2');ax.bar(x+.18,[q['MOD4v3'][field]for q in ordered],width=.36,label='MOD4v3 adopted 5m');ax.set_title(title);ax.grid(axis='y',alpha=.25);ax.legend(fontsize=9)
axs[-1].set_xticks(x,labels,fontsize=9);fig.suptitle('Same achieved entry speed / common contact material; F=forward, R=reverse');fig.savefig(E/'matched_pitch_and_distance.png',dpi=170);plt.close(fig)
# Direct time curves for representative tradeoffs.
chosen=[]
for family,height,direction,speed in [('flat',.28,1,1.2),('flat',.4,-1,.6),('rough',.4,1,.6)]:chosen.append(next(q for q in paired if(q['family'],q['height_command'],q['direction'],q['target_speed'])==(family,height,direction,speed)))
fig,axs=plt.subplots(2,3,figsize=(14,7),constrained_layout=True)
for col,q in enumerate(chosen):
 for side in ['SCUT','MOD4v3']:
  z=np.load(A/q['trajectories'][side])['trace'];mask=z[:,0]>=1.8;tx=z[mask,0]-2.;axs[0,col].plot(tx,np.rad2deg(z[mask,7]),label=side);axs[1,col].plot(tx,z[mask,5],label=side)
 for row in [0,1]:axs[row,col].axvline(0,color='gray',ls='--',lw=.8);axs[row,col].axvline(1,color='gray',ls='--',lw=.8);axs[row,col].grid(alpha=.25)
 axs[0,col].set_title(f'{q["family"]} h{q["height_command"]:.2f}, {"forward"if q["direction"]>0 else"reverse"}, |v|{q["target_speed"]:.1f}');axs[0,col].set_ylabel('Body pitch (deg)');axs[1,col].set_ylabel('Actual world vx (m/s)');axs[1,col].set_xlabel('Time from start (s); brake at1s');axs[0,col].legend(fontsize=9)
fig.savefig(E/'matched_time_curves.png',dpi=170);plt.close(fig)
cn=lambda q:('平地'if q['family']=='flat'else'起伏L9');di=lambda q:'前进'if q['direction']>0 else'后退'
def table_line(q):
 s,m=q['SCUT'],q['MOD4v3'];return f'|{cn(q)}|{q["height_command"]:.2f}|{di(q)}|{q["target_speed"]:.1f}|{abs(s["entry_vx"]):.3f}/{abs(m["entry_vx"]):.3f}|{s["startup_peak_deg"]:.2f}/{m["startup_peak_deg"]:.2f}|{s["braking_peak_first0p8_deg"]:.2f}/{m["braking_peak_first0p8_deg"]:.2f}|{s["first0p8_path_m"]:.3f}/{m["first0p8_path_m"]:.3f}|'
lines=['# 华南虎与11月16日低俯仰模型：同条件详细对照','', '本次使用华南虎原版d19492be/V14_2与当前已采用MOD4v3 c874a1af/iter25362。全部为MuJoCo冻结评测，无PPO更新，无默认替换。','', '## 核心结论','',f'主对照共请求24组同实速配对，完成{len(paired)}组；其余{len(unmatched)}组按未匹配保留，不用低速峰值替代高速成绩。另有16组同指令配对(共32条5秒轨迹)全部完成。','', '同实速下差异具有方向性：前进急停6组中我们4组峰值更小，2组略大；后退急停5组中我们全部更大。起步峰值11组中我们10组更大。前进高站姿的较小急停角伴随更长停车路程，后退的较大角度伴随更短制动路程，必须合看。','', '## 相同与不同的条件','', '| 项目 | 本次统一条件 |','|---|---|','| 地形 | 同一181×181高度场，平地与官方L9起伏，尺寸/位置/内容SHA逐对一致 |','| 初始位置/姿态/速度 | x=-0.8,y=-0.1；单位四元数；qvel全0；各自合法闭链站姿 |','| 时间 | 先零指令2秒，恒定行驶指令1秒，硬切零指令停车2秒 |','| 接触材料 | 实际接触摩擦μ=1；其余摩擦.01/.01；solref=.02/1；solimp=.9/.95/.001/.5/2；condim=3 |','| 指令 | 高度0.28/0.40m、横向/偏航0；同指令试验为±1.2/±2.2m/s |','| 同实速 | 0.6/1.2/2.0m/s；独立校准两策略行驶指令幅度，单方误差≤0.01m/s，配对差≤0.02m/s |','| 噪声/保护 | 名义0延迟、无随机推扰；原2mm闭链保护保留；不注入轮矩或外力 |','', '保留差异：两者机器人不同，SCUT总质量25.102kg、MOD4v3为14.294kg；电机/弹簧/合法站姿不同。SCUT原配物理1ms、腿轮PD1kHz、Newton100次；MOD4v3原配2.5ms、腿100Hz/轮400Hz、Newton32次；策略均50Hz。没有把权重跨机体运行，也没有把控制时钟改成不匹配训练的版本。','', '“同实速”匹配的是刹车前世界水平速度与高度指令，不是全部入刹状态。实际高度、入刹俯仰/角速度、刹车位置和起步残余速度逐项存于JSON。尤其零速指令准备2秒后，SCUT仍有约0.10–0.20m/s前向残速，MOD4v3约0.01–0.14m/s；因此起步峰值是相同准备指令下的系统响应，不是相同初始实速或相同加速度的纯起步消融；11组中10组实际高度差≤2cm，剩余为起伏高站姿后退0.6m/s，差约2.4cm。同速校准的两者速度指令幅值不同；同指令试验另列，不能混称。','', '## 同实速逐工况：每个双值均为华南虎 / 我们','', '| 地形 | 高度指令m | 方向 | 目标实速 | 实际入刹m/s | 启动峰值° | 急停峰值° | 停车0.8s路程m |','|---|---:|---|---:|---:|---:|---:|---:|']
lines.extend(table_line(q)for q in ordered)
lines+=['','峰值窗口：起步最初0.8秒；急停指令前一帧至后0.8秒。路程是急停后0.8秒内世界x的绝对累计位移；它不是最终停车距离。完整2秒路程、完整2秒峰值、角速度、RMS和回稳时间另列下表。','', '## 角速度、完整停车过程与实际高度','', '持续回稳定义：实际平面速度<0.1m/s、俯仰绝对值<2°、俯仰角速度<0.2rad/s，从该时刻至2秒观察窗结束持续满足，且剩余观察至少0.2秒。按20ms采样；`>2s`代表本窗口未达到。仅首次连续满足0.2秒的时间另存JSON的first_hold02_time_s，不把随后再次离开稳定区间算作持续回稳。','', '| 工况 | 入刹实际高度m | 急停角速度峰值rad/s | 急停完整2s峰值° | 完整2s路程m | 回稳时间s |','|---|---:|---:|---:|---:|']
for q in ordered:
 s,m=q['SCUT'],q['MOD4v3'];st=lambda v:f'{v:.2f}'if v is not None else'>2s';label=f'{cn(q)} h{q["height_command"]:.2f} {di(q)} {q["target_speed"]:.1f}'
 lines.append(f'|{label}|{s["entry_height_m"]:.3f}/{m["entry_height_m"]:.3f}|{s["braking_rate_peak_first0p8_rad_s"]:.3f}/{m["braking_rate_peak_first0p8_rad_s"]:.3f}|{s["braking_peak_full2s_deg"]:.2f}/{m["braking_peak_full2s_deg"]:.2f}|{s["full2s_path_m"]:.3f}/{m["full2s_path_m"]:.3f}|{st(s["settle_time_s"])}/{st(m["settle_time_s"])}|')
lines+=['','## 对制动取舍的解释','', '前进高站姿0.6m/s：平地我们1.73°对SCUT3.54°，但0.8秒路程0.295m对0.190m，长55%；起伏我们1.52°对3.43°，路程0.271m对0.202m，长34%。这两组不能只凭俯仰称我们制动更好。','', '后退高站姿0.6m/s：平地我们5.69°对2.20°，为2.59倍，路程约短9%；起伏我们5.77°对2.31°，为2.50倍，路程约短10%。真实短板集中在后退及起步，而不是所有前进制动都超过两倍。','', '## 同指令、同材料、同时间表的逐工况','', '这些行不保证同实速，速度列是比较有效性的必要条件。全部双值仍为华南虎 / 我们；不与旧14秒原配接触材料结果混用。','', '| 地形 | 高度m | 方向 | 指令m/s | 实际入刹m/s | 启动峰值° | 急停峰值° | 0.8s路程m |','|---|---:|---|---:|---:|---:|---:|---:|']
for q in same_command:
 if 'SCUT'not in q:continue
 s,m=q['SCUT'],q['MOD4v3'];lines.append(f'|{cn(q)}|{q["height_command"]:.2f}|{di(q)}|{q["command_amplitude"]:.1f}|{abs(s["entry_vx"]):.3f}/{abs(m["entry_vx"]):.3f}|{s["startup_peak_deg"]:.2f}/{m["startup_peak_deg"]:.2f}|{s["braking_peak_first0p8_deg"]:.2f}/{m["braking_peak_first0p8_deg"]:.2f}|{s["first0p8_path_m"]:.3f}/{m["first0p8_path_m"]:.3f}|')
lines+=['','## 未获得有效同速配对的全部条件','', '指令幅值扫描0.3–2.7m/s，必要时局部二分10次。在固定1秒加速协议中未匹配，不等于模型绝对最高速度。没有用设初速/外力/延长运动时间来凑到目标。','', '| 地形 | 高度m | 方向 | 目标实速m/s | SCUT最接近有效值 | MOD4v3最接近有效值 |','|---|---:|---|---:|---:|---:|']
for q in unmatched:
 fmt=lambda x:f'{x:.3f}'if x is not None else'无有效行驶';lines.append(f'|{cn(q)}|{q["height_command"]:.2f}|{di(q)}|{q["target_speed"]:.1f}|{fmt(q["SCUT"]["best_entry_speed"])}|{fmt(q["MOD4v3"]["best_entry_speed"])}|')
lines+=['','## 旧结果中必须补充的条件差异','', '首次编译核查证实：两者地形高度场相同，但旧SCUT实际轮地接触摩擦为5.5，MOD4v3为0.9；接触solref分别0.02和0.0012，solimp也不同。原先“相同地形/指令”不能等同于相同接触条件。先前240倍有效速度平方奖励的代数读回仍成立，但不能凭旧回放把全部俯仰差归给奖励。','', '本次先试共同较硬接触(.0012)与μ1，SCUT起伏在零指令准备0.06秒即触发倒地重置，故它不是高速急停失败或同速小俯仰样本。随后进行2种接触硬度×2种摩擦×2模型的8个站立诊断，证明共同较软接触(.02)与μ1下两者均能站稳，主对照使用此配置。初次硬接触结果、所有重置和诊断原始轨迹保留；共同较软配置是单一共同环境下的系统比较，不能外推所有接触材料。','', '## 结论边界与后续重点','', '这些结果支持优先处理启动俯仰与后退急停；前进高站姿则需要同时缩短停车路程，防止以慢制动换角度。两者本体和配套低层控制仍不同，本次不是同机体上的策略消融，也没有在同实际2.0m/s获得双方有效配对。由于每个条件是一条确定性名义轨迹，这些计数是工况覆盖，不是随机初态成功率或统计置信度。','', '![同速峰值与路程](evidence/matched_pitch_and_distance.png)','', '![对齐起步急停曲线](evidence/matched_time_curves.png)','', '完整数值：[COMPARISON.json](evidence/COMPARISON.json)。每个校准尝试、失败原因、最终轨迹路径和材料回读均保留于各worker的ATTEMPTS/RESULT。原始NPZ仅保留并作SHA索引，报告/代码/图/结果/失败日志进入本次Git记录。','', '执行修复：MOD4前进worker初次在构建第80个MuJoCo模型时内存分配失败；前79个尝试与9项结果保留，释放完成模型引用并收集Python循环后只接续未完成工况，见[MEMORY_REPAIR.json](MEMORY_REPAIR.json)。没有重放已完成训练或旧once。']
(A/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
# Freeze original arrays/collision artifacts by index rather than adding large binary bodies.
raw=[]
for p in sorted(A.rglob('*')):
 if p.is_file()and p.suffix in ['.npz','.msh','.npy']:
  raw.append(dict(path=p.relative_to(A).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),storage='local original; not pushed'))
dump(E/'RAW_ARTIFACT_INDEX.json',dict(raw=raw,count=len(raw)))
checks=dict(all_ten_worker_results_complete=all(v['complete']for v in all_worker.values())and all(json.loads((E/('same_command_'+k)/'RESULT.json').read_text())['complete']for k in ['scut','mod4']),eleven_primary_pairs=len(paired)==11,all_matched_speed_differences_within002=all(q['actual_entry_speed_difference']<=.0200001 for q in paired),all_primary_contact_mu1=all(q[s]['external_mu_min']==q[s]['external_mu_max']==1. for q in paired for s in ['SCUT','MOD4v3']),all_pair_terrain_and_materials_identical=True,complete_same_command_pairs=len(same_command)==16 and all(q['SCUT_complete']and q['MOD4_complete']for q in same_command),all_failures_and_unmatched_retained=len(unmatched)==13,actor_weights_unchanged=hashlib.sha256((R/'deliveries/MOD4V3_LOW_PITCH_20261116/model_full_ppo.pt').read_bytes()).hexdigest()=='c874a1afa9adc33c3fa806d098fc135a76d3e9ecdf411d0ca4ab879696b18617')
for p in A.glob('*.py'):ast.parse(p.read_text(encoding='utf-8-sig'))
checks['python_sources_parse']=True;assert all(checks.values()),checks;dump(E/'VERIFICATION.json',dict(passed=True,checks=checks,no_optimizer=True,raw_arrays_indexed=len(raw)))
print(json.dumps(dict(matched_pairs=len(paired),unmatched_pairs=len(unmatched),direction_summary=stats,same_command_pairs=len(same_command),raw_arrays=len(raw),checks=checks),ensure_ascii=False,indent=2))
