# Finalize the authorized persistent-teacher PPO experiment.
from pathlib import Path
import json,hashlib,shutil,sys,subprocess,time,traceback
import torch
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/'evidence';P=json.loads((T/'PLAN.json').read_text(encoding='utf8'));C=R/'sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111';ID='stairs200_teacher_retention_40m_20261113'
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def own_block(path,body):
 p=Path(path);s=p.read_text(encoding='utf8');start='<!-- STAIRS_TEACHER_RETENTION_40M_20261113_START -->';end='<!-- STAIRS_TEACHER_RETENTION_40M_20261113_END -->'
 if start in s and end in s:
  a=s.index(start);b=s.index(end,a)+len(end);s=s[:a]+start+'\n'+body+'\n'+end+s[b:]
 else:s+='\n'+start+'\n'+body+'\n'+end+'\n'
 p.write_text(s,encoding='utf8')
def interval(x):
 rows=[v for k,v in x.get('stair_summary',{}).items() if k.startswith('whole') and v.get('mean_first_to_second_s') is not None];n=sum(v['passed'] for v in rows)
 return sum(v['passed']*v['mean_first_to_second_s'] for v in rows)/n if n else 1e9

def forward_error(x):
 path=E/'checkpoint_evals'/Path(x['model']).stem/'flat60/RESULT.json'
 rows=json.loads(path.read_text(encoding='utf8'))['rows'];rows=[r for r in rows if r['task'] in ('forward20','forward22')]
 return sum(r['vx_abs_error'] for r in rows)/len(rows) if rows else 1e9

def flat_task_comparison(evaluations):
 old=R/'sources/local/MOD4V3_STAIRS_NO_PROGRESS_PARENT_40M_20261113'
 inputs=[('健康父iter24692',R/'sources/local/MOD4V3_FLAT_SPEED_REPAIR_20261112/evidence/fixed60_final/RESULT.json',P['teacher_retention']['keep_teacher_sha256']),('源005m',old/'evidence/checkpoint_evals/model_005m/flat60/RESULT.json',P['parent_sha256']),('上一轮040m',old/'evidence/checkpoint_evals/model_040m/flat60/RESULT.json',None)]
 for ev in evaluations:
  if ev.get('complete'):inputs.append(('本轮'+Path(ev['model']).stem,E/'checkpoint_evals'/Path(ev['model']).stem/'flat60/RESULT.json',ev['sha256']))
 rows=[]
 for label,path,expected in inputs:
  if not path.exists():continue
  d=json.loads(path.read_text(encoding='utf8'))
  if expected:assert d['sha256']==expected
  assert len(d['rows'])==60
  tasks={}
  for task in sorted({v['task'] for v in d['rows']}):
   cases=[v for v in d['rows'] if v['task']==task];count=len(cases)
   tasks[task]=dict(passed=sum(v['passed'] for v in cases),requested=count,mean_vx=sum(v['vx_mean'] for v in cases)/count,mean_vx_abs_error=sum(v['vx_abs_error'] for v in cases)/count,mean_wz=sum(v['wz_mean'] for v in cases)/count,mean_wz_abs_error=sum(v['wz_abs_error'] for v in cases)/count,mean_height=sum(v['height_mean'] for v in cases)/count,total_resets=sum(v['reset_count'] for v in cases))
  rows.append(dict(label=label,source=str(path),sha256=d['sha256'],iteration=d['iteration'],passed=sum(v['passed'] for v in d['rows']),tasks=tasks))
 write(E/'FLAT_TASK_COMPARISON.json',dict(scope='Existing same-protocol deterministic flat60 replays only; no added simulation and no rough segments',rows=rows))
 table='| 检查点 | 2.0指令实速m/s | 2.2指令实速m/s | 旋转通过/10 | 平地通过/60 |\n|---|---:|---:|---:|---:|\n'
 for row in rows:
  t=row['tasks'];table+=f"| {row['label']} | {t['forward20']['mean_vx']:.3f} | {t['forward22']['mean_vx']:.3f} | {t['yaw14137']['passed']} | {row['passed']} |\n"
 return table

def rough_comparison(reports,candidate_sha):
 rows=[];table='| 原rough科目 | 条件 | 指标 | 健康父 | 实验候选 |\n|---|---|---|---:|---:|\n'
 for report in reports:
  path=Path(report['result'])
  if not path.exists():continue
  d=json.loads(path.read_text(encoding='utf8'));assert d['input_sha256']['parent']==P['teacher_retention']['keep_teacher_sha256'] and d['input_sha256']['candidate']==candidate_sha
  for variant in ['nominal0','Step7_all_remaining_DR']:
   groups={model:[r for r in d['rows'] if r['model']==model and r['variant']==variant] for model in ['parent','candidate']};metrics={}
   for model,cases in groups.items():
    requested=sum(r['requested'] for r in cases)
    if report['skill']=='gyro':
     count=sum(r['gyro_metrics']['first_episode_survived6s'] for r in cases);samples=sum(r['gyro_metrics']['prepush_first_episode_samples'] for r in cases);mae=sum((r['gyro_metrics']['prepush_first_episode_wz_MAE'] or 0.)*r['gyro_metrics']['prepush_first_episode_samples'] for r in cases)/samples if samples else None
     metrics[model]=dict(count=count,requested=requested,prepush_yaw_MAE=mae,metric='first physical episode survived6s and separately yaw MAE')
    elif report['skill']=='landing':metrics[model]=dict(count=sum(r['landing_metrics']['command_recovered'] for r in cases),requested=requested,observed_clearance=sum(r['landing_metrics']['observed_clearance'] for r in cases),posture_recovered=sum(r['landing_metrics']['posture_recovered'] for r in cases),metric='first-episode landing then command recovery')
    else:metrics[model]=dict(count=sum(r['crossed_count'] for r in cases),requested=requested,metric='first-episode terrain crossing')
   label=report['skill']+' L'+str(report['level']);condition='名义' if variant=='nominal0' else '完整DR';metric='越过地形' if report['skill']=='traverse' else '旋转存活6s；角速度MAE' if report['skill']=='gyro' else '落地后指令恢复'
   text={k:str(v['count'])+'/'+str(v['requested'])+(f"；{v['prepush_yaw_MAE']:.3f}rad/s" if report['skill']=='gyro' and v['prepush_yaw_MAE'] is not None else '') for k,v in metrics.items()}
   table+=f"| {label} | {condition} | {metric} | {text['parent']} | {text['candidate']} |\n";rows.append(dict(skill=report['skill'],level=report['level'],variant=variant,source=str(path),input_sha256=d['input_sha256'],metrics=metrics))
 write(E/'ROUGH_COMPARISON.json',dict(rows=rows,note='Actual paired frozen replay counts; survival/crossing/recovery are distinct metrics and not automatic graduation'))
 return table

def main():
 assert(E/'training/SAFE_CLOSED.json').exists()
 final=json.loads((E/'training/FINAL.json').read_text(encoding='utf8')) if(E/'training/FINAL.json').exists() else None
 latest=json.loads((E/'training/LATEST_PROGRESS.json').read_text(encoding='utf8')) if(E/'training/LATEST_PROGRESS.json').exists() else {}
 seconds=final['elapsed_seconds'] if final else latest.get('training_elapsed_seconds',0.);records=[]
 health=dict(done_totals=latest.get('done_totals'),teacher_updates=latest.get('teacher_retention',{}).get('updates'),teacher_max_parameter_change=latest.get('teacher_retention',{}).get('keep_teacher_max_parameter_change'),teacher_no_grad=latest.get('teacher_retention',{}).get('keep_teacher_no_grad'),last_losses=latest.get('losses'),source='evidence/training/LATEST_PROGRESS.json');write(E/'TRAINING_HEALTH.json',health)
 for path in sorted((T/'weights').glob('model_*.pt')):
  d=torch.load(path,map_location='cpu',weights_only=False);required=['actor_state_dict','critic_state_dict','optimizer_state_dict','cpu_rng','cuda_rng','python_rng','numpy_rng','reset_rng','domain_randomization_state','teacher_retention'];assert all(k in d for k in required)
  assert len(d['optimizer_state_dict']['state'])==17 and d['actor_state_dict']['mlp.0.weight'].shape[1]==35 and d['critic_state_dict']['mlp.0.weight'].shape[1]==78 and d['actor_state_dict']['mlp.6.weight'].shape[0]==6
  assert all(bool(torch.isfinite(v).all()) for v in d['actor_state_dict'].values());assert d['teacher_retention']['keep_teacher_max_parameter_change']==0.
  records.append(dict(id=ID+'_'+path.stem.removeprefix('model_'),file=path.name,git_path=path.relative_to(R).as_posix(),bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),iteration=d['iter'],optimizer_entries=17,complete_PPO=True,actor_input=35,critic_input=78,action_output=6,parent_sha256=P['parent_sha256'],root_parent_model_id='flat_speed_full_final',root_parent_sha256=P['root_parent']['sha256'],recipe_files=[(T/'PLAN.json').relative_to(R).as_posix(),(T/'README.md').relative_to(R).as_posix()],teacher_retention=d['teacher_retention'],role='Persistent teacher-guided PPO from005m; joint flat and stair retention experiment',git_storage='ordinary full PPO PT blob',aliases=[]))
 evaluations=[json.loads(p.read_text(encoding='utf8')) for p in sorted((E/'checkpoint_evals').glob('*/EVALUATION.json'))]
 complete=[x for x in evaluations if x.get('complete')];joint=[x for x in complete if x['flat60_passed']>=40 and x['whole_stair_passed']>=5];pool=joint or complete
 pool.sort(key=lambda x:((x['flat60_passed'],x['whole_stair_passed'],-forward_error(x),-interval(x)) if joint else (min(x['flat60_passed']/40.,x['whole_stair_passed']/5.),x['flat60_passed'],x['whole_stair_passed'],-forward_error(x),-interval(x))),reverse=True)
 selected=pool[0] if pool else None;selected_record=None;retention=[]
 if selected:
  source=Path(selected['model']);selected_record=next(r for r in records if r['sha256']==selected['sha256']);alias=T/'weights/selected_teacher_retention_candidate.pt';shutil.copy2(source,alias);selected_record['aliases'].append(alias.relative_to(R).as_posix())
  write(T/'weights/SELECTED_MODEL.json',dict(display_name='持续教师保留PPO40分钟实验候选',model_id=selected_record['id'],iteration=selected_record['iteration'],sha256=selected_record['sha256'],source=selected_record['git_path'],alias=alias.relative_to(R).as_posix(),full_PPO=True,whole_stair_passed=selected['whole_stair_passed'],whole_stair_requested=selected['whole_stair_requested'],flat60_passed=selected['flat60_passed'],flat60_requested=selected['flat60_requested'],joint_source005m_retention=bool(joint),forward_tracking_MAE_m_s=forward_error(selected),selection_order='joint floor then flat count, stair count, lower forward MAE, shorter stair interval',status='Experimental; healthy parent and source005m retained; no automatic deployment promotion'))
  sys.path.insert(0,str(T));from run_retention_replays import main as replay
  retention=replay(alias)
 rough_table=rough_comparison(retention,selected_record['sha256'] if selected_record else None)
 registry=json.loads((C/'MODEL_REGISTRY.json').read_text(encoding='utf8'));known={x['id'] for x in registry['models']};registry['models'].extend(r for r in records if r['id'] not in known);registry['updated_at_epoch']=time.time();write(C/'MODEL_REGISTRY.json',registry)
 state='completed2400s' if final and seconds>=2400 and not(E/'training/ERROR.json').exists() else 'incomplete; see original error and saved checkpoints'
 decision=dict(status=state,actual_training_seconds=seconds,budget_seconds=2400,selected_model_id=selected_record['id'] if selected_record else None,selected_flat60=selected['flat60_passed'] if selected else None,selected_stairs10=selected['whole_stair_passed'] if selected else None,joint_source005m_retention=bool(joint),baseline005m=dict(flat60=40,stairs10=5),rough_replays_complete=sum(x['complete'] for x in retention),rough_replays_requested=4,original_healthy_parent_retained=True,source005m_retained=True,automatic_mature_or_realcar_promotion=False)
 write(T/'DECISION.json',decision)
 table='| 检查点 | 平地/60 | 连续两阶/10 | 成功阶间耗时s | 下阶/5 |\n|---|---:|---:|---:|---:|\n'
 for ev in evaluations:
  if not ev.get('complete'):table+=f"| {Path(ev['model']).name} | 未完成，见原错误 | — | — | — |\n";continue
  dt=interval(ev);text=f'{dt:.3f}' if dt<1e8 else '无成功样本'
  table+=f"| {Path(ev['model']).name} | {ev['flat60_passed']} | {ev['whole_stair_passed']} | {text} | {ev['stair_summary']['descent']['passed']} |\n"
 flat_table=flat_task_comparison(evaluations)
 chosen=f"候选{selected_record['id']}，平地{selected['flat60_passed']}/60、两阶{selected['whole_stair_passed']}/10。" if selected else '没有完整可选回放。'
 report=f'''# 持续教师保留PPO40分钟实际结果（2026-11-13）

状态：{state}，实际{seconds:.3f}秒，原预算2400秒，每300秒完整保存。{chosen} 是否同时达到源5m的40/60平地与5/10两阶：{bool(joint)}。该条件只用于结果选模，不阻断训练，不是新物理门槛。同通过数时先比较两档前进MAE，再比较成功阶间耗时。

训练计数：{json.dumps(health['done_totals'],ensure_ascii=False)}。教师指导共{health['teacher_updates']}次PPO更新，冻结教师最大参数变化{health['teacher_max_parameter_change']}。普通闭链保护重置与数值保护重置分别记录。

起点005m iter24737 SHA{P['parent_sha256']}，完整actor/critic/STD/Adam/LR/RNG恢复。冻结健康父iter24692作为原技能指导，冻结005m原生成功登阶片段作为动作参考。具体成功数、数据SHA与采样在reference和evidence/demo_collection；教师参数变化和实际损失在每个完整PT的teacher_retention字段及训练日志。

本轮算法新增项为原PPO同一次反向传播中的持续动作MSE，lambda0.25，保留/成功登阶各半；没有额外imitation-only训练段，未使用自动任务采样或多头critic。不是论文整套复现。原40/35/25任务分配、20%nominal/80%fullDR、奖励、速度投影定义、2.5ms/100Hz腿/400Hz轮/50Hz策略、MOD4 R3资产、电机与2mm单环境保护沿用。flat-only稳态诊断为日志，不改环境奖励。原健康父及源5m保持。

{table}

固定平地单项比较（同协议10例平均速度；仅平地，不混入坡面或台阶）：

训练内新增的平地稳态日志要求回合持续8秒，而原地形边界为距中心4m；高速直行回合通常先触发边界，当前forward20/forward22样本为0。因此本轮前进速度结论采用原固定平地60例回放，日志空样本不记为0误差。原边界、回合与奖励不改。

{flat_table}

原生rough对照完成{sum(x['complete'] for x in retention)}/4组，对比冻结健康父与所选实验候选；候选实际SHA在每组input_sha256，不能外推未测检查点。完成不等于满分，原始RESULT和逐环境轨迹保留。固定MuJoCo平地与V3两阶仍使用原门槛；没有自动晋升实车。

{rough_table}

完整源、配方、成功/失败探针、教师与数据实际PT、本轮所有完整PPO和回放结果通过7897代理Git普通blob归档。
'''
 (T/'FINAL_REPORT.md').write_text(report,encoding='utf8');own_block(T/'README.md','## 实际收尾\n\n'+chosen+f' 实际{seconds:.3f}秒，联合源5m保留={bool(joint)}。[完整结果](FINAL_REPORT.md)。')
 navigation='持续教师保留PPO，从005m起步；'+chosen+f' 实际{seconds:.3f}秒，联合源5m保留={bool(joint)}；[配方与结果]({T.relative_to(R).as_posix()}/README.md)。'
 own_block(R/'README.md',navigation);own_block(R/'docs/DR_TRAINING_INDEX_20261111.md',navigation.replace(']('+T.relative_to(R).as_posix(),'](../'+T.relative_to(R).as_posix()));own_block(C/'MODELS.md','## 持续教师保留PPO\n\n'+chosen+' 原健康父与源5m保留，完整PT/教师/数据见本轮目录及MODEL_REGISTRY.json。')
 write(E/'FINALIZATION_COMPLETE.json',dict(epoch=time.time(),decision=decision,models=len(records),archive_receipt='evidence/GIT_COMPLETE_RECEIPT.json; completion requires successful archive log'))
 with(E/'ARCHIVE_COMPLETE.log').open('wb') as log:result=subprocess.run([sys.executable,'-X','utf8',str(T/'archive_run.py'),'--phase','complete'],cwd=R,stdout=log,stderr=subprocess.STDOUT)
 if result.returncode:raise RuntimeError('Archive failed; inspect original log and retry existing objects, never rerun training')
 print('FINALIZATION_AND_ARCHIVE_COMPLETE',flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  write(E/'FINALIZE_ERROR.json',dict(epoch=time.time(),traceback=traceback.format_exc()));raise
