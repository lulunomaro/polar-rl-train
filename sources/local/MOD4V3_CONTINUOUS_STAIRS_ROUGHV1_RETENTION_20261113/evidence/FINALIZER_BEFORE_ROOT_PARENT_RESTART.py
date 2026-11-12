"""Finalize both segments of the same7200s experiment and preserve all actual models."""
from pathlib import Path
import json,hashlib,shutil,sys,subprocess,time,traceback
import torch
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/'evidence';P=json.loads((T/'PLAN.json').read_text(encoding='utf8'));OLD=R/P['previous_stage'];C=R/'sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111';ID='continuous_stairs200_roughv1_retention_20261113'
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def own_block(path,body):
 s=path.read_text(encoding='utf8');start='<!-- CONTINUOUS_STAIRS_ROUGHV1_RETENTION_20261113_START -->';end='<!-- CONTINUOUS_STAIRS_ROUGHV1_RETENTION_20261113_END -->'
 if start in s and end in s:
  a=s.index(start);b=s.index(end,a)+len(end);s=s[:a]+start+'\n'+body+'\n'+end+s[b:]
 else:s+='\n'+start+'\n'+body+'\n'+end+'\n'
 path.write_text(s,encoding='utf8')
def elapsed_mean(x):
 rows=[v for k,v in x.get('stair_summary',{}).items() if k.startswith('whole') and v.get('mean_first_to_second_s') is not None];n=sum(r['passed'] for r in rows)
 return sum(r['mean_first_to_second_s']*r['passed'] for r in rows)/n if n else float('inf')
def main():
 assert (E/'training/SAFE_CLOSED.json').exists()
 final=json.loads((E/'training/FINAL.json').read_text(encoding='utf8')) if (E/'training/FINAL.json').exists() else None
 latest=json.loads((E/'training/LATEST_PROGRESS.json').read_text(encoding='utf8')) if (E/'training/LATEST_PROGRESS.json').exists() else {}
 phase_seconds=final['elapsed_seconds'] if final else latest.get('training_elapsed_seconds',0.);total=P['cumulative_training_seconds_before']+phase_seconds
 records=[];evaluations=[]
 for stage,label,stageplan in [(OLD,'continuous_stairs200_2h_20261113',json.loads((OLD/'PLAN.json').read_text(encoding='utf8'))),(T,ID,P)]:
  for p in sorted((stage/'weights').glob('model_*.pt')):
   d=torch.load(p,map_location='cpu',weights_only=False);required=['actor_state_dict','critic_state_dict','optimizer_state_dict','cpu_rng','cuda_rng','python_rng','numpy_rng','reset_rng','domain_randomization_state'];assert all(k in d for k in required)
   assert len(d['optimizer_state_dict']['state'])==17 and d['actor_state_dict']['mlp.0.weight'].shape[1]==35 and d['critic_state_dict']['mlp.0.weight'].shape[1]==78 and d['actor_state_dict']['mlp.6.weight'].shape[0]==6
   assert all(bool(torch.isfinite(v).all()) for v in d['actor_state_dict'].values())
   records.append(dict(id=label+'_'+p.stem.removeprefix('model_'),file=p.name,git_path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),iteration=d['iter'],optimizer_entries=17,complete_PPO=True,actor_input=35,critic_input=78,action_output=6,parent_sha256=stageplan['parent_sha256'],root_parent_model_id='flat_speed_full_final',root_parent_sha256=P['root_parent']['sha256'],recipe_files=[(stage/'PLAN.json').relative_to(R).as_posix(),(stage/'README.md').relative_to(R).as_posix()],role='Experimental continuous stairs; phase1 special80/flat20; phase2 special50/rough30/flat20; all retention limits reported',git_storage='ordinary full PPO PT blob',aliases=[]))
  for p in sorted((stage/'evidence/checkpoint_evals').glob('*/EVALUATION.json')):
   ev=json.loads(p.read_text(encoding='utf8'));ev['phase']=1 if stage==OLD else 2;ev['evaluation_path']=p.relative_to(R).as_posix();evaluations.append(ev)
 candidates=[x for x in evaluations if x.get('complete') and x['phase']==2];candidates.sort(key=lambda x:(x['whole_stair_passed'],-elapsed_mean(x),x['flat60_passed']),reverse=True)
 selected=candidates[0] if candidates else None;selected_record=None;retention=[]
 if selected:
  source=Path(selected['model']);selected_record=next(r for r in records if r['sha256']==selected['sha256']);alias=T/'weights/selected_continuous_stair_retention_candidate.pt';shutil.copy2(source,alias);selected_record['aliases'].append(alias.relative_to(R).as_posix())
  write(T/'weights/SELECTED_MODEL.json',dict(display_name='连续200mm台阶＋Rough-v1保留实验候选',model_id=selected_record['id'],iteration=selected_record['iteration'],sha256=selected_record['sha256'],full_PPO=True,source=selected_record['git_path'],alias=alias.relative_to(R).as_posix(),whole_stair_passed=selected['whole_stair_passed'],whole_stair_requested=selected['whole_stair_requested'],flat60_passed=selected['flat60_passed'],flat60_requested=selected['flat60_requested'],status='Experimental; original mature package retained; measured regression disclosed'))
  sys.path.insert(0,str(T));from run_retention_replays import main as replay
  retention=replay(alias)
 aggregate=[]
 for job in retention:
  if not job['complete']:continue
  data=json.loads(Path(job['result']).read_text(encoding='utf8'))
  for model in data['input_sha256']:
   for variant in ['nominal0','Step7_all_remaining_DR']:
    rows=[r for r in data['rows'] if r['model']==model and r['variant']==variant]
    aggregate.append(dict(job=job['job'],model=model,variant=variant,requested=sum(r['requested'] for r in rows),crossed=sum(r['crossed_count'] for r in rows),without_termination=sum(r['completed_without_termination'] for r in rows),gyro_survived6s=sum((r.get('gyro_metrics') or {}).get('first_episode_survived6s',0) for r in rows),landing_pose=sum((r.get('landing_metrics') or {}).get('posture_recovered',0) for r in rows),landing_command=sum((r.get('landing_metrics') or {}).get('command_recovered',0) for r in rows)))
 write(E/'ROUGH_RETENTION_SUMMARY.json',dict(reports=retention,aggregate=aggregate,scope='Original Rough-v1 geometry/commands/guards; matched400Hz wheel; paired initialDR/wrench/push/noise; no optimizer; no automatic graduation'))
 status='completed original7200s across two segments' if final and total>=7195 else 'closed early or failed; actual two-segment seconds retained'
 decision=dict(status=status,total_budget_seconds=7200,phase1_seconds=P['cumulative_training_seconds_before'],phase2_seconds=phase_seconds,total_training_seconds=total,selected_model_id=selected_record['id'] if selected_record else None,selected_flat60=selected['flat60_passed'] if selected else None,selected_stairs10=selected['whole_stair_passed'] if selected else None,rough_replays_complete=sum(x['complete'] for x in retention),rough_replays_requested=4,original_mature_parent_retained=True,automatic_mature_or_realcar_promotion=False,selection='Phase2 fixed whole-ascent count then successful stair interval then flat60; original rough retention results disclosed')
 write(T/'DECISION.json',decision);write(E/'MODEL_ARCHIVE_INDEX.json',dict(models=records,decision=decision))
 reg=json.loads((C/'MODEL_REGISTRY.json').read_text(encoding='utf8'));ids={r['id'] for r in records};reg['models']=[x for x in reg['models'] if x['id'] not in ids]+records
 reg['stages']=[x for x in reg['stages'] if x['id']!=ID]+[dict(id=ID,title='连续200mm台阶＋原Rough-v1保留：同一两小时预算',profile='continuous200mm_roughv1_retention',parent_sha256=P['parent_sha256'],source_directories=[OLD.relative_to(R).as_posix(),T.relative_to(R).as_posix()],recipe_files=[(OLD/'PLAN.json').relative_to(R).as_posix(),(T/'PLAN.json').relative_to(R).as_posix()],model_ids=[x['id'] for x in records],experimental_candidate_model_id=decision['selected_model_id'],retained_model_id=None,status=status,budget=dict(planned_seconds=7200,actual_seconds=total),report_file=(T/'FINAL_REPORT.md').relative_to(R).as_posix())]
 reg['weights_summary'].update(models=len(reg['models']),unique_sha256=len({x['sha256'] for x in reg['models']}),total_bytes=sum(x['bytes'] for x in reg['models']));reg['latest_continuous_stair_experimental_model_id']=decision['selected_model_id'];reg['latest_continuous_stair_decision_file']=(T/'DECISION.json').relative_to(R).as_posix();write(C/'MODEL_REGISTRY.json',reg)
 table='| 段 | 检查点 | 完整连续两阶/10 | 阶间耗时s | 平地/60 | 下阶/5 |\n|---|---|---:|---:|---:|---:|\n'
 for ev in evaluations:
  if ev.get('complete'):table+=f"| {ev['phase']} | {Path(ev['model']).name} | {ev['whole_stair_passed']} | {elapsed_mean(ev):.3f} | {ev['flat60_passed']} | {ev['stair_summary']['descent']['passed']} |\n"
  else:table+=f"| {ev['phase']} | {Path(ev['model']).name} | 评测未完成，见原日志 | — | — | — |\n"
 chosen=f"候选{selected_record['id']}，iter{selected_record['iteration']}，连续两阶{selected['whole_stair_passed']}/10、平地{selected['flat60_passed']}/60。" if selected else '没有完成可选的接续段固定评测。'
 report=f'''# 连续台阶与Rough-v1能力保留实际结果（2026-11-13）

状态：{status}。原预算7200秒；专项段{P['cumulative_training_seconds_before']:.3f}秒，混合接续段{phase_seconds:.3f}秒，合计{total:.3f}秒，不另开两小时。保留{len(records)}份实际完整PPO，actor35/critic78/action6、17项Adam、LR/RNG/DR均读回核验。

{chosen}

阶段一80%连续台阶/20%平地；用户纠正后阶段二50%连续200mm台阶＋30%原Rough-v1非平地＋20%平地，十类粗糙地形/十级，原速度/转向/高度/落地恢复采样。附加登阶奖励与定制起点/指令仅限专项环境。完整DR、MOD4 R3资产、电机包络、400Hz轮/100Hz腿/50Hz策略、原速度−1.5e²＋指数项、2mm单环境保护未改。

根父iter24692固定连续两阶2/10、平地60/60；阶段一30m平地40/60已退化。环境占比代表实际训练分布，不能证明能力恢复。原成熟模型保留，无自动晋升。

{table}

原Rough-v1父子同条件固定回放完成{sum(x['complete'] for x in retention)}/4组。原始逐地形、逐方向、名义/完整DR、穿越/旋转/落地结果及轨迹在evidence/rough_retention，聚合在evidence/ROUGH_RETENTION_SUMMARY.json；失败和未收齐均不写通过。使用原Rough-v1地形和判定，轮反馈匹配当前400Hz。本实验名义MuJoCo台阶和平地结果不能代替完整DR或实车毕业。

执行配方、切换保存点、前后预算、来源、恢复和实际环境分布分别在PLAN.json、evidence/SWITCH_COMPLETE.json、evidence/training/RESTORE.json与TERRAIN_STARTUP.json。两段全部保存点、失败和报告随Git保存，PT为完整普通blob。
'''
 (T/'FINAL_REPORT.md').write_text(report,encoding='utf8')
 own_block(T/'README.md','## 实际收尾\n\n'+chosen+f' 两段实际合计{total:.3f}秒；原Rough-v1固定保留回放{sum(x["complete"] for x in retention)}/4组。[完整结果](FINAL_REPORT.md)。')
 nav='连续台阶已补回原Rough-v1，接续段50%台阶/30%粗糙地形/20%平地。'+chosen+f' 同一预算实际{total:.3f}秒；[配方与结果]({T.relative_to(R).as_posix()}/README.md)，所有完整PT原件归档；原成熟包保留。'
 own_block(R/'README.md',nav);own_block(R/'docs/DR_TRAINING_INDEX_20261111.md',nav)
 own_block(C/'MODELS.md','## 连续200mm台阶与Rough-v1保留\n\n'+chosen+f' 完整PPO共{len(records)}份，逐文件SHA/bytes/配方在MODEL_REGISTRY.json；原成熟基座不替换。')
 with (E/'ARCHIVE_COMPLETE.log').open('wb') as log:result=subprocess.run([sys.executable,'-X','utf8',str(T/'archive_run.py'),'--phase','complete'],cwd=R,stdout=log,stderr=subprocess.STDOUT)
 if result.returncode:raise RuntimeError('Complete archive failed; see ARCHIVE_COMPLETE.log; retry same existing objects')
 write(E/'FINALIZATION_COMPLETE.json',dict(epoch=time.time(),decision=decision,models=len(records),archive_exit=0))
if __name__=='__main__':
 try:main()
 except BaseException:
  write(E/'FINALIZE_ERROR.json',dict(epoch=time.time(),traceback=traceback.format_exc()));raise
