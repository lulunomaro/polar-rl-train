"""Read-only model/data audit and final reporting; never launches optimization."""
from pathlib import Path
from datetime import datetime
import json,hashlib,shutil
import numpy as np
import torch
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/'evidence';A=E/'final_closure';A.mkdir(exist_ok=True)
torch.set_num_threads(1)
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def put(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
final=load(E/'training/FINAL.json');clock=load(E/'training/TRAINING_CLOCK.json');evaluation=load(E/'checkpoint_evals/model_final/EVALUATION.json');remote=load(A/'REMOTE_FINAL_CLOSURE.json')
assert load(E/'FINALIZE_RECEIPT.json')['exit_code']==0 and evaluation['complete']
assert all(x['exit_code']==0 for x in evaluation['results'].values())
assert not any(x['alive']for x in remote['processes'].values()) and remote['gpu_compute_processes']==''
assert remote['files']['SAFE_CLOSED.json']['scene_closed'] and remote['files']['ERROR.json']is None and remote['files']['DEADLINE_GUARD.json']is None
assert 0<final['elapsed_seconds']<clock['strict_max_seconds']==2400
model=T/'weights/model_final.pt';assert sha(model)==final['checkpoint']['SHA']==remote['final_PT_sha256']
ck=torch.load(model,map_location='cpu',weights_only=False);ref=torch.load(T/'c874_reference.pt',map_location='cpu',weights_only=False);initial=torch.load(T/'weights/model_step000.pt',map_location='cpu',weights_only=False)
e0={}
for part in ['actor','critic']:
 xa=ck[part+'_state_dict'];xb=ref[part+'_state_dict'];e0[part]=max((xa['mlp.e0.'+k[4:]]-v).abs().max().item()for k,v in xb.items()if k.startswith('mlp.'))
e0['STD']=(ck['actor_state_dict']['distribution.e0_std']-ref['actor_state_dict']['distribution.std_param']).abs().max().item();assert all(x==0 for x in e0.values())
e1={}
for label,part,prefix in [('head','actor','mlp.e1.head.'),('encoder','actor','mlp.e1.encoder.'),('STD','actor','distribution.e1_log_std'),('critic','critic','mlp.e1.')]:
 xa=ck[part+'_state_dict'];xb=initial[part+'_state_dict'];e1[label]=max((v-xb[k]).abs().max().item()for k,v in xa.items()if k.startswith(prefix));assert np.isfinite(e1[label])and e1[label]>0
protected={k:dict(expected=v['sha256'],actual=sha(Path(v['path'])))for k,v in load(E/'PROTECTED_INPUTS.json').items()};assert all(x['expected']==x['actual']for x in protected.values())
pre=load(E/'native_dense_probe_v1_r3/ROUTE2_NATIVE_PREFLIGHT.json');sources={k:sha(T/'support'/k)==v for k,v in pre['source_sha256'].items()};assert all(sources.values())
curr=ck['curriculum_summary'];completions=sum(sum(x)for x in curr['completions_DR_then_nominal']);attempts=sum(sum(x)for x in curr['attempts_DR_then_nominal']);assert completions==ck['success_replay_summary']['new_saved_episodes']==78
raw=[];histmax=prevmax=0.
raw_root=E/'train_dense_top_replay/success_replay'
for name,info in sorted(remote['manifest']['files'].items()):
 f=raw_root/name;assert sha(f)==info['sha256']
 with np.load(f,allow_pickle=False)as z:
  frames=z['frames'];meta=json.loads(str(z['metadata_json']));assert frames.ndim==2 and frames.shape[1]==461 and np.isfinite(frames).all();assert meta['accepted_native_success']and not meta['teacher_assistance']and not meta['actual_full_DR']and not meta['truncated']
  histmax=max(histmax,float(np.abs(frames[:,:35]-frames[:,35:455].reshape(-1,12,35)[:,-1]).max()))
  if len(frames)>1:prevmax=max(prevmax,float(np.abs(frames[1:,22:28]-frames[:-1,455:461]).max()))
  raw.append(dict(path=f.relative_to(T).as_posix(),sha256=info['sha256'],bytes=info['bytes'],frames=len(frames),policy_update=meta['policy_update'],actual_full_DR=False,speed_limit_m_s=meta['speed_limit_m_s']))
assert len(raw)==78 and histmax==prevmax==0
put(A/'FINAL_ONLINE_SUCCESS_INDEX.json',raw)
retained=ck['success_replay_state']['episodes'];retained_update0=sum(item[2].get('policy_update',0)==0 for item in retained)
rows=[];checkpoint_index=[]
for f in sorted((T/'weights').glob('model_*.pt')):
 if f.name in ['model_first_complete.pt','model_step000.pt','model_collect010.pt']:continue
 z=torch.load(f,map_location='cpu',weights_only=False);c=z['curriculum_summary'];p=z['success_replay_summary'];name=f.stem
 row=dict(name=name,minutes=z['training_elapsed_seconds']/60,PPO=z['PPO_updates_in_experiment'],Adam=z['actual_Adam_steps'],train_completions=sum(sum(v)for v in c['completions_DR_then_nominal']),train_attempts=sum(sum(v)for v in c['attempts_DR_then_nominal']),replay_phases=p['phase_frame_counts'],replay_frames=p['kept_frames'],strict_training_count=c['strict_completions_all_heights'])
 q=E/'checkpoint_evals'/name/'EVALUATION.json'
 if q.exists():
  ev=load(q);row.update(strict_independent=ev['single_step_qualified_passed'],crossed=ev['physical_crossed'],stable_events=ev['physical_stable_events'],flat60=ev['flat60_passed'])
  ss=load(q.parent/'single_step/RESULT.json');row['center_pitch_peak_deg']=next(v['pitch_peak_deg']for v in ss['rows']if v['start_offset_mm']==0);row['all_offsets_pitch_peak_deg']=max(v['pitch_peak_deg']for v in ss['rows'])
 rows.append(row);checkpoint_index.append(dict(path=f.relative_to(T).as_posix(),bytes=f.stat().st_size,sha256=sha(f)))
rows.sort(key=lambda x:x['minutes']);put(A/'TRAINING_AND_EVAL_CURVE_DATA.json',rows)
x=[v['minutes']for v in rows];fig,axs=plt.subplots(2,2,figsize=(12,8),layout='constrained')
axs[0,0].plot(x,[v['train_completions']for v in rows],'o-',label='0DR training stable completions');axs[0,0].set_ylabel('Cumulative completions');axs[0,0].set_title('Training: center only, speed tier 1.5 m/s');axs[0,0].legend(fontsize=8)
for i,label in enumerate(['settle','approach','top support']):axs[0,1].plot(x,[v['replay_phases'][i]for v in rows],'o-',label=label)
axs[0,1].set_ylabel('Frames in bounded BC replay');axs[0,1].set_title('FIFO evicted all settle frames after 25 min');axs[0,1].legend(fontsize=8)
evrows=[v for v in rows if 'strict_independent'in v];xx=[v['minutes']for v in evrows]
for key,label in [('crossed','Bilateral crossed'),('stable_events','Physical stable event >=0.4s'),('strict_independent','Formal <=0.6 m/s')]:axs[1,0].plot(xx,[v[key]for v in evrows],'o-',label=label)
axs[1,0].set_ylim(-.2,5.2);axs[1,0].set_ylabel('Cases out of 5');axs[1,0].set_title('Independent pure E1 MuJoCo evaluation');axs[1,0].legend(fontsize=8)
for key,label in [('center_pitch_peak_deg','Center'),('all_offsets_pitch_peak_deg','Maximum over 5 offsets')]:axs[1,1].plot(xx,[v[key]for v in evrows],'o-',label=label)
axs[1,1].set_ylabel('Peak absolute pitch (deg)');axs[1,1].set_title('Single 200 mm step');axs[1,1].legend(fontsize=8)
for ax in axs.flat:ax.set_xlabel('Actual training minutes');ax.grid(alpha=.25)
fig.suptitle('MOD4v3 MoE Route 2: dense top reward + replay, 40-minute budget');fig.savefig(A/'TRAINING_AND_EVAL_CURVES.png',dpi=170);plt.close(fig)
ss=load(E/'checkpoint_evals/model_final/single_step/RESULT.json');points=ss['rows'];last=final['last_progress'];st=last['startup_diagnostics'];n=sum(st[k]['episodes']for k in ['DR','nominal']);bad=sum(st[k]['collapsed']for k in ['DR','nominal'])
verification=dict(generated_at=datetime.now().astimezone().isoformat(),artifact_closure_verified=True,all_frozen_evaluations_executed=True,E1_formal_graduated=False,decision='not_adopt',promoted=False,training_PID_exited=True,watchdog_PID_exited=True,scene_closed=True,GPU_released=True,deadline_guard_fired=False,final_model_sha256=sha(model),training_elapsed_seconds=final['elapsed_seconds'],complete_PPO_updates=ck['PPO_updates_in_experiment'],actual_Adam_steps=ck['actual_Adam_steps'],partial_rollout_without_extra_Adam=ck['partial_update']and ck['actual_Adam_steps']==12*ck['PPO_updates_in_experiment'],E0_vs_true_c874=e0,E1_trainable_group_changes=e1,protected_inputs=protected,prechecked_source_hashes=sources,actual_fullDR_population=curr['E1_DR_curriculum']['actual_fullDR_population'],zeroDR_population=curr['E1_DR_curriculum']['zeroDR_population'],training_completions=completions,training_attempts=attempts,training_internal_strict_count=curr['strict_completions_all_heights'],new_online_success_files=len(raw),new_online_success_raw_frames=sum(v['frames']for v in raw),history_alignment_max_error=histmax,aprev_alignment_max_error=prevmax,final_replay_phases=ck['success_replay_summary']['phase_frame_counts'],final_replay_retained_update0_episodes=retained_update0,settle_FIFO_eviction_proven=True,FIFO_causal_effect_not_isolated=True,full_evaluation=evaluation,final_points=points,last_complete_progress_first1s=dict(collapsed=bad,episodes=n,rate=bad/n,elapsed=last['training_elapsed_seconds']),automatic_extension=False,automatic_restart=False,new_optimizer_steps_in_closure=0)
put(T/'FINAL_VERIFICATION.json',verification);put(A/'FINAL_VERIFICATION.json',verification)
files=checkpoint_index+[dict(path=f.relative_to(T).as_posix(),bytes=f.stat().st_size,sha256=sha(f))for f in (E/'checkpoint_evals').rglob('*.mp4')]
files.append(dict(path=(A/'TRAINING_AND_EVAL_CURVES.png').relative_to(T).as_posix(),bytes=(A/'TRAINING_AND_EVAL_CURVES.png').stat().st_size,sha256=sha(A/'TRAINING_AND_EVAL_CURVES.png')));put(A/'FINAL_BINARY_ARTIFACT_INDEX.json',files)
auto=T/'FINAL_REPORT.md';backup=A/'INITIAL_AUTOMATIC_FINAL_REPORT.md'
if not backup.exists():shutil.copy2(auto,backup)
start=datetime.fromtimestamp(clock['epoch']).astimezone();stop=datetime.fromtimestamp(final['epoch']).astimezone();closed=datetime.fromtimestamp(remote['files']['SAFE_CLOSED.json']['epoch']).astimezone();center=next(v for v in points if v['start_offset_mm']==0)
lines=['# 台顶连续奖励与成功回放修复：40分钟冻结结论','', '**结论：本轮不采用，不晋升默认模型。E0保住，E1尚未解决低速200mm五起点上阶。**','',f"实际PPO {start.isoformat()} → 最终保存 {stop.isoformat()}，计时{final['elapsed_seconds']:.3f}s（约39分00秒，按计划预留保存关闭）；场景{closed.isoformat()}安全关闭。完整{ck['PPO_updates_in_experiment']}PPO/{ck['actual_Adam_steps']}真实Adam，末段partial仅未完成rollout，无额外Adam；没有重启/延长/强杀/自动晋升。训练与守护退出，GPU释放，最终PT `{sha(model)}`。",'', '## 独立冻结回归','', '|项目|结果|','|---|---:|',f"|纯E1正式200mm、整程<=0.6m/s|{evaluation['single_step_qualified_passed']}/5|",f"|纯E1真实双轮越边|{evaluation['physical_crossed']}/5|",f"|纯E1 >=.4s物理稳态事件|{evaluation['physical_stable_events']}/5|",f"|E0 flat60|{evaluation['flat60_passed']}/60|",f"|E0正向双阶|{evaluation['straight_passed']}/5|",f"|E0实际斜向|{evaluation['actual_oblique_passed']}/20|",f"|E0下阶|{evaluation['descent_passed']}/5|",f"|E0崎岖/平地急停俯仰峰|{evaluation['pitch_summary']['random_uniform_for_rm']['braking_peak_deg_max']:.5f}° / {evaluation['pitch_summary']['plane_for_rm']['braking_peak_deg_max']:.5f}°|",'', '全部五项套件实际执行exit=0，非沿用中期成绩。E0 actor/STD/critic对真c874参数差全0，原有斜向弱项也原样保留。','', '|起点mm|越边|最长/末端物理稳态s|首秒位移m|整程峰速m/s|俯仰峰°|最大退回m|','|---:|---|---:|---:|---:|---:|---:|']
for v in points:lines.append(f"|{v['start_offset_mm']}|{v['physical_bilateral_crossed']}|{v['physical_max_hold_s']:.2f} / {v['physical_final_hold_s']:.2f}|{v['pre1s_displacement_m']:.5f}|{v['maximum_episode_speed_m_s']:.5f}|{v['pitch_peak_deg']:.3f}|{v['maximum_retreat_m']:.5f}|")
lines += ['',f"只有center物理登台并出现最长{center['physical_max_hold_s']:.2f}s稳态事件，末端仅{center['physical_final_hold_s']:.2f}s；整程峰{center['maximum_episode_speed_m_s']:.5f}m/s超正式上限，其他四点未真实越边，因此不能将0/5只归因超速。零指令首秒后退约9.67cm，静站未守住。",'', '## 训练端与数据','',f"最终PT准确计数：0DR宽档真实完成{completions}/{attempts}（{completions/attempts:.3%}），内部严格计数{curr['strict_completions_all_heights']}。819始终center/1.5首档，实际fullDR人口0、无课程晋级；参考DR/nominal分组的59/19不是实际DR成绩。不能把训练内部计数当独立正式通过。",'',f"78条本轮新成功完整原始NPZ、{sum(v['frames']for v in raw)}帧已下载并逐项SHA验证，队列末帧和真实a_prev误差全0。原补采26条仍独立归档；原旧轮41只是计数，没有虚构成原轨迹。新成功不是教师接管，训练/独立评测均无LQR辅助。最后完整PPO进度的首秒累计塌腿{bad}/{n}={bad/n:.3%}，时间点{last['training_elapsed_seconds']:.3f}s，非最终额外partial采样统计。",'', '## 已证实的回放缺口与诊断边界','',f"25m还有150帧静站，30m与最终静站0；最终池相位为{ck['success_replay_summary']['phase_frame_counts']}，更新0的原补采episode全部被FIFO挤出内存（保留数{retained_update0}）。空settle桶回退全池抽样，20%静站BC配额落空。永久on-policy静站锚8仍生效，磁盘原始数据未丢。当前已证实实现缺口，但尚未隔离它对失败的因果贡献，也不能宣称仅继续增大奖励就能修好。",'', '本轮没有热改补丁或追加训练。默认c874/CURRENT、原010m37dbe178/8391及历史失败保护SHA一致，预检核心源码SHA一致，物理/PD/电机/scene/频率/critic78/6动作和2mm仅诊断合同不变。','', '## 产物','', '- 最终1x中心视频：`evidence/checkpoint_evals/model_final/single_step/STUDENT_CENTER_1X.mp4`。','- 曲线：`evidence/final_closure/TRAINING_AND_EVAL_CURVES.png`，对应原始数值JSON同目录。','- 完整新成功轨迹：`evidence/train_dense_top_replay/success_replay/`。','- 五起点原始失败与全回归：`evidence/checkpoint_evals/model_final/`。','- 最终核验：`FINAL_VERIFICATION.json`；远端退出/GPU证据：`evidence/final_closure/REMOTE_FINAL_CLOSURE.json`。','- 最初自动报告原样保留：`evidence/final_closure/INITIAL_AUTOMATIC_FINAL_REPORT.md`。']
(T/'FINAL_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
mem=f"## {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M')} 台顶连续奖励40m已全部收尾：不采用，E0保住、E1正式0/5\n\nMOD4V3_MOE_ROUTE2_DENSE_TOP_REPLAY_REPAIR_20261117实际2340.442s（39m00s，按计划预留关闭），332PPO/3984真实Adam，最终f2f21eef；训练/守护退出、GPU释放，无强杀/重启/延长/晋升。partial仅未完成rollout，无额外Adam。\n\n全部最终冻结回归exit0：E0 flat60 60/60、双阶5/5、实际斜向1/20、下阶5/5、崎岖/平地急停13.56197/13.37020度；最终PT对真c874 E0 actor/STD/critic差0，保护SHA一致。纯E1正式0/5、真实越边/物理稳态事件各1/5，仅center最长.62s、末端.10s，峰速1.12934；其他四点未越边，不能只归因超速。首秒后退9.67cm，静站未守住。\n\n最终准确0DR训练完成78/9231，内部严格15不算独立正式成绩；819全center/1.5首档、实际fullDR人口0，无晋级。78条在线真实成功完整原始NPZ、{sum(v['frames']for v in raw)}帧已下载SHA/历史/a_prev校验，非原补采26条。FIFO已挤出全部原补采和静站，最终相位[0,29273,2984]；永久on-policy锚8仍生效，尚未隔离唯一根因。\n\n最终视频/曲线/报告齐，FINAL_VERIFICATION artifact_closure_verified=true但E1_formal_graduated=false；本轮不采用，不追加训练。原始自动报告/所有失败保留。默认c874/CURRENT/原010m/8391及物理硬边界不变。见FINAL_REPORT.md、FINAL_VERIFICATION.json及evidence/final_closure。\n\n"
for f in [R.parent/'AGENTS.md',R/'AGENTS.md',T/'AGENTS.md']:
 old=f.read_text(encoding='utf-8')
 if '台顶连续奖励40m已全部收尾'not in old.split('\n\n')[0]:f.write_text(mem+old,encoding='utf-8')
print(json.dumps(dict(closure_verified=True,formal_E1_passed=False,complete_PPO=ck['PPO_updates_in_experiment'],Adam=ck['actual_Adam_steps'],training_completed=completions,training_attempts=attempts,raw_episodes=len(raw),raw_frames=sum(v['frames']for v in raw),normal_evaluation=dict(flat60=evaluation['flat60_passed'],straight=evaluation['straight_passed'],oblique=evaluation['actual_oblique_passed'],descent=evaluation['descent_passed']),E0_diff=e0,final_SHA=sha(model)),ensure_ascii=False))
