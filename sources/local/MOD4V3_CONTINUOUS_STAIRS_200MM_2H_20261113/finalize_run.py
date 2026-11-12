"""Finalize the actually closed run, index full PPO saves, select by measured results, archive."""
from pathlib import Path
import json,hashlib,shutil,sys,subprocess,time,traceback
import torch
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/'evidence';C=R/'sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111';PLAN=json.loads((T/'PLAN.json').read_text());ID='continuous_stairs200_2h_20261113'
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def own_block(path,body):
 s=path.read_text(encoding='utf8');start='<!-- CONTINUOUS_STAIRS_200MM_20261113_START -->';end='<!-- CONTINUOUS_STAIRS_200MM_20261113_END -->'
 if start in s and end in s:
  a=s.index(start);b=s.index(end,a)+len(end);s=s[:a]+start+'\n'+body+'\n'+end+s[b:]
 else:s+='\n'+start+'\n'+body+'\n'+end+'\n'
 path.write_text(s,encoding='utf8')

def main():
 assert (E/'training/SAFE_CLOSED.json').exists()
 final=json.loads((E/'training/FINAL.json').read_text()) if (E/'training/FINAL.json').exists() else None
 latest=json.loads((E/'training/LATEST_PROGRESS.json').read_text()) if (E/'training/LATEST_PROGRESS.json').exists() else {}
 actual=final['elapsed_seconds'] if final else latest.get('training_elapsed_seconds',0.)
 records=[];required=['actor_state_dict','critic_state_dict','optimizer_state_dict','cpu_rng','cuda_rng','python_rng','numpy_rng','reset_rng','domain_randomization_state']
 for p in sorted((T/'weights').glob('model_*.pt')):
  d=torch.load(p,map_location='cpu',weights_only=False);assert all(k in d for k in required);assert len(d['optimizer_state_dict']['state'])==17;assert d['actor_state_dict']['mlp.0.weight'].shape[1]==35 and d['critic_state_dict']['mlp.0.weight'].shape[1]==78 and d['actor_state_dict']['mlp.6.weight'].shape[0]==6
  assert all(bool(torch.isfinite(v).all()) for v in d['actor_state_dict'].values())
  records.append(dict(id='stair200_'+p.stem.removeprefix('model_'),file=p.name,git_path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),iteration=d['iter'],optimizer_entries=17,complete_PPO=True,actor_input=35,critic_input=78,action_output=6,parent_model_id='flat_speed_full_final',parent_sha256=PLAN['parent_sha256'],root_parent_model_id='flat_speed_full_final',root_parent_sha256=PLAN['parent_sha256'],original_local_path=str(p),original_remote_path=PLAN['root']+'/train120m_r1/'+p.name,recipe_files=[(T/'PLAN.json').relative_to(R).as_posix(),(T/'README.md').relative_to(R).as_posix()],role='Continuous200mm stair bounded2h experiment; see fixed evaluations and retained limits',git_storage='ordinary full PPO PT blob',aliases=[]))
 evaluations=[]
 for p in sorted((E/'checkpoint_evals').glob('*/EVALUATION.json')):
  ev=json.loads(p.read_text());ev['evaluation_path']=p.relative_to(R).as_posix();evaluations.append(ev)
 candidates=[x for x in evaluations if x.get('complete')]
 def elapsed_mean(x):
  rows=[v for k,v in x.get('stair_summary',{}).items() if k.startswith('whole') and v.get('mean_first_to_second_s') is not None];n=sum(r['passed'] for r in rows);return sum(r['mean_first_to_second_s']*r['passed'] for r in rows)/n if n else float('inf')
 candidates.sort(key=lambda x:(x['whole_stair_passed'],-elapsed_mean(x),x['flat60_passed']),reverse=True)
 selected=candidates[0] if candidates else None;selected_record=None
 if selected:
  selected_path=Path(selected['model']);selected_record=next(r for r in records if r['sha256']==selected['sha256']);alias=T/'weights/selected_continuous_stair_candidate.pt';shutil.copy2(selected_path,alias);selected_record['aliases'].append(alias.relative_to(R).as_posix())
  write(T/'weights/SELECTED_MODEL.json',dict(display_name='本轮连续200mm台阶综合实验候选',model_id=selected_record['id'],iteration=selected_record['iteration'],sha256=selected_record['sha256'],full_PPO=True,source=selected_record['git_path'],alias=alias.relative_to(R).as_posix(),whole_stair_passed=selected['whole_stair_passed'],whole_stair_requested=selected['whole_stair_requested'],mean_first_to_second_s=elapsed_mean(selected) if elapsed_mean(selected)!=float('inf') else None,flat60_passed=selected['flat60_passed'],flat60_requested=selected['flat60_requested'],stair_summary=selected['stair_summary'],controller=dict(wheel_Hz=400,leg_Hz=100,policy_Hz=50,physics_Hz=400),status='Experimental; original mature parent retained; nominal MuJoCo selection does not equal fullDR native or real-car graduation'))
 status='completed bounded two-hour training' if final and actual>=7195 else 'closed early or failed; actual duration retained'
 decision=dict(status=status,planned_seconds=7200,actual_seconds=actual,last_iteration=latest.get('iteration'),selected_model_id=selected_record['id'] if selected_record else None,selection='Whole two-step fixed ascent success count first,then first-to-second time,flat60 tie-break; all skill retention reported',original_mature_parent_retained=True,selected_is_experimental=True,native_fullDR_fixed_graduation=False,real_car_deployed=False,automatic_extension=False)
 write(T/'DECISION.json',decision);write(E/'MODEL_ARCHIVE_INDEX.json',dict(models=records,evaluations=evaluations,decision=decision))
 reg=json.loads((C/'MODEL_REGISTRY.json').read_text());old_ids={r['id'] for r in records};reg['models']=[x for x in reg['models'] if x['id'] not in old_ids]+records
 stage=dict(id=ID,title='连续200mm台阶两小时：俯仰奖励修复与抬轮接续',profile='continuous_stairs200_level3',parent_model_id='flat_speed_full_final',parent_sha256=PLAN['parent_sha256'],source_directories=[T.relative_to(R).as_posix()],recipe_files=[(T/'PLAN.json').relative_to(R).as_posix()],training_method=PLAN['training_round'],geometry=PLAN['continuous_stair'],model_ids=[r['id'] for r in records],experimental_candidate_model_id=decision['selected_model_id'],retained_model_id=None,status=status,report_file=(T/'FINAL_REPORT.md').relative_to(R).as_posix(),budget=dict(planned_seconds=7200,actual_seconds=actual),original_tag='trial-20261113-mod4-continuous-stairs-200mm-complete-01')
 reg['stages']=[s for s in reg['stages'] if s['id']!=ID]+[stage];reg['weights_summary'].update(models=len(reg['models']),unique_sha256=len({r['sha256'] for r in reg['models']}),total_bytes=sum(r['bytes'] for r in reg['models']));reg['latest_continuous_stair_experimental_model_id']=decision['selected_model_id'];reg['latest_continuous_stair_decision_file']=(T/'DECISION.json').relative_to(R).as_posix();reg['last_update_tag']='trial-20261113-mod4-continuous-stairs-200mm-complete-01';write(C/'MODEL_REGISTRY.json',reg)
 table='| 检查点 | iteration | 完整两级 /10 | 一级至二级 s | 平地 /60 | 下阶 /5 |\n|---|---:|---:|---:|---:|---:|\n'
 for ev in evaluations:
  row=next((r for r in records if r['sha256']==ev['sha256']),None)
  if ev.get('complete'):
   tm=elapsed_mean(ev);table+=f"| {Path(ev['model']).name} | {row['iteration'] if row else '?'} | {ev['whole_stair_passed']} | {tm:.3f} | {ev['flat60_passed']} | {ev['stair_summary']['descent']['passed']} |\n"
  else:table+=f"| {Path(ev['model']).name} | {row['iteration'] if row else '?'} | 评测失败，保留日志 | — | — | — |\n"
 chosen=(f"候选：{selected_record['id']}，iter{selected_record['iteration']}，完整两级{selected['whole_stair_passed']}/10，平地{selected['flat60_passed']}/60，SHA{selected_record['sha256']}。" if selected else '尚无完整固定评测，不能据此选出验证过的最优候选。')
 report=f'''# 连续200mm台阶训练收尾（2026-11-13）

状态：{status}。计划7200秒，实际{actual:.3f}秒；最后iteration{latest.get('iteration')}。实际保存{len(records)}个完整PPO文件，每个17项Adam及actor/critic/STD、LR/RNG/DR状态。第一/5分钟/最终原件均保留。

{chosen}

原冻结父iter24692在相同新固定协议中完整两级2/10（h0.365:0/5、h0.40:2/5），中间恢复0/5、下阶5/5；原六项60/60使用同SHA既有记录。

{table}

选模先看完整两级通过数，再看成功样本一级至二级落轮耗时；中间平台起步与下阶不混入完整两级分母。该协议为各条件5种x/y/yaw初态、名义MuJoCo，轮400Hz/腿100Hz、实际轮落台与0.3秒保持、原高度/倾斜阈值和2mm闭链保护。旧机身投影高度跳变版本的失败原件单独保留。

20%平地用于技能保留；具体60例结果公开。若平地或下阶退步，不能把该候选写成原成熟包的全能力替代。训练中的完整DR计数不是固定fullDR通过率，本次未完成新的跨引擎/实车毕业，不覆盖原成熟包。固定协议、完整原始轨迹、所有未通过案例和启动缺依赖的失败都保留。

本轮实际修改为取消附加进展奖励25.8度俯仰/瞬时高度门控，新增与轮越阶绑定的收腿、新距离进展、真实落轮、稳定连续完成与阶间耗时；原速度−1.5e²和指数项、完整DR范围、35/78/6、原plant/电机/数值保护保持。PLAN.json和support为执行配方，support_baseline保留父版本。原生训练资料在evidence/training与inspections，完整权重在weights。

''' 
 (T/'FINAL_REPORT.md').write_text(report,encoding='utf8')
 s=(T/'README.md').read_text(encoding='utf8');s=s.replace('当前状态为进行中；','启动时状态为进行中；');s+='\n## 收尾结果\n\n'+chosen+f' 实际训练{actual:.3f}秒，完整PPO文件{len(records)}个。[逐检查点结果和限制](FINAL_REPORT.md)。\n';(T/'README.md').write_text(s,encoding='utf8')
 body='## 2026-11-13 连续200mm台阶两小时专项（已闭合）\n\n'+chosen+f' 实际{actual:.3f}秒，完整PPO文件{len(records)}个。原成熟包保留，完整DR原生/实车毕业未宣称。'
 own_block(R/'README.md',body+' [完整配方、权重与结果](sources/local/MOD4V3_CONTINUOUS_STAIRS_200MM_2H_20261113/README.md)。');own_block(R/'docs/DR_TRAINING_INDEX_20261111.md',body+' [完整报告](../sources/local/MOD4V3_CONTINUOUS_STAIRS_200MM_2H_20261113/FINAL_REPORT.md)。')
 md=C/'MODELS.md';s=md.read_text(encoding='utf8');s+='\n## 连续200mm台阶两小时完整PPO\n\n'+chosen+'\n\n| 模型 | iteration | 字节 | SHA256 |\n|---|---:|---:|---|\n'
 for r in records:s+=f"| [{r['id']}](../../../{r['git_path']}) | {r['iteration']} | {r['bytes']} | {r['sha256']} |\n"
 md.write_text(s,encoding='utf8')
 if (T/'monitor.log').exists():shutil.copy2(T/'monitor.log',E/'MONITOR_LOG_AT_FINALIZE.log')
 with (E/'ARCHIVE_COMPLETE.log').open('wb') as out:r=subprocess.run([sys.executable,'-X','utf8',str(T/'archive_run.py'),'--phase','complete'],cwd=R,stdout=out,stderr=subprocess.STDOUT)
 if r.returncode:raise RuntimeError('Complete archive/push pending; see ARCHIVE_COMPLETE.log; retry existing objects, do not re-record tags')
 print(json.dumps(dict(status=status,actual_seconds=actual,models=len(records),selected_model_id=decision['selected_model_id'],git_complete=True)),flush=True)

if __name__=='__main__':
 try:main()
 except Exception:
  write(E/'FINALIZE_ERROR.json',dict(epoch=time.time(),traceback=traceback.format_exc(),status='Finalization or Git sync pending; training results remain on disk'));raise
