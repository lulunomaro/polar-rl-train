"""Report measured two-hour results; preserve the frozen comprehensive default."""
from pathlib import Path
import json,time,hashlib
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/'evidence'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def put(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+chr(10),encoding='utf8')
p=read(T/'PLAN.json');final=read(E/'training/FINAL.json');actual=final['elapsed_seconds'];total=p['cumulative_training_seconds_before']+actual;selected=read(T/'weights/SELECTED_STUDENT.json');rank=read(E/'STUDENT_FIXED_RANKING.json');collection=read(E/'MODEL_COLLECTION.json')['models'];frozen=p['frozen_comprehensive_parent_sha256']
rows=['# 2026-11-15 后摆收腿台阶两小时实验结果','',f'授权总计7200秒PPO，实际{total:.3f}秒，含最初坐标错误阶段292.226秒；当前接续{actual:.3f}秒。准备和评测不计PPO。','',f'实验候选{selected["model_id"]}，SHA {selected["sha256"]}。综合默认db6e9ccf仍冻结，未自动晋升。','',f'低速完整两阶{selected["low_whole_passed"]}/{selected["low_whole_requested"]}；早期辅助一级落轮{selected["supported_first_passed"]}/2，后摆中段辅助一级落轮{selected["late_supported_first_passed"]}/3。辅助初态不计全程通过。','','| 检查点 | 低速两阶/4 | 辅助早/2 | 辅助晚/3 | 平地/60 | 快速正向/5 | 实际斜向/20 | 下阶/5 |','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
for row in sorted(rank,key=lambda x:x['source_file']):rows.append('| '+row['source_file']+' | '+' | '.join(str(row[k])for k in ['low_whole_passed','supported_first_passed','late_supported_first_passed','flat60_passed','straight_passed','actual_oblique_passed','descent_passed'])+' |')
rows+=['','## 原生PhysX配对复核','', '父与学生同初态、同DR；名义/完整DR及原任务Rough-v1保留能力分别列出。']
for d in sorted((E/'post_native').iterdir()):
 if d.is_dir()and(d/'RESULT.json').exists():
  data=read(d/'RESULT.json');rows+=['','### '+d.name,'','~~~json',json.dumps(data.get('summary',data.get('summaries',{})),ensure_ascii=False,indent=2),'~~~']
rows+=['','## 训练范围','', '只延长预算。接续前段有效学生完整actor/critic/STD/Adam/RNG并开始新的物理episode，未从db6重复起训。训练源码字节与已过探针的前段相同。完整DR、40/35/25任务占比、速度奖励、电机、MOD4资产、时序及原2mm单环境保护保持。','', '顺序仍为站高接近、真实触阶后向后摆腿、上层支撑后收腿抬轮、落轮站稳。旧后摆参考损失0；保留教师all6系数1.0，高站姿腿锚0.25。35/78/6接口保持。','', '检查点累计计时包含最初292.226秒错误阶段；错误阶段失败证据独立保存。本轮保存后关闭，无继续训练授权。']
(T/'FINAL_REPORT.md').write_text(chr(10).join(rows)+chr(10),encoding='utf8')
decision=dict(default_comprehensive_parent_sha256=frozen,experimental_candidate=selected,promoted=False,low_speed_whole_observed=selected['low_whole_passed']>0,continuation_PPO_seconds=actual,total_round_PPO_seconds=total,authorized_budget_seconds=7200,invalid_initial_PPO_seconds=292.2261128425598,all_training_and_evaluations_closed=True,no_further_training=True)
put(T/'DECISION.json',decision);put(E/'ARTIFACT_INDEX.json',[dict(path=str(q),bytes=q.stat().st_size,sha256=hashlib.sha256(q.read_bytes()).hexdigest(),storage='local original; indexed in Git')for q in E.rglob('*.npz')])
regpath=R/'sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/MODEL_REGISTRY.json';reg=read(regpath);sid='ordered_rearward_2h_20261115';assert not any(x.get('id')==sid for x in reg['stages']);model_ids=[]
for row in collection:
 mid=sid+'_'+Path(row['file']).stem.removeprefix('model_');model_ids.append(mid);reg['models'].append(dict(id=mid,file=row['file'],git_path=(T/'weights'/row['file']).relative_to(R).as_posix(),sha256=row['sha256'],bytes=row['bytes'],complete_PPO=True,actor_input=35,critic_input=78,action_output=6,root_parent_sha256=frozen,continuation_parent_sha256=p['parent_sha256'],recipe_files=[(T/'PLAN.json').relative_to(R).as_posix()],role='Experimental ordered low-speed stair checkpoint; not promoted',git_storage='ordinary full PT blob'))
reg['stages'].append(dict(id=sid,title='触阶后向后摆腿、支撑后收腿：总计两小时',parent_sha256=frozen,retained_model_id=selected['model_id'],other_model_ids=model_ids,status='Completed; actual results in final report',total_PPO_seconds=total,source_directories=[T.relative_to(R).as_posix()],decision_file=(T/'DECISION.json').relative_to(R).as_posix()));reg['active_ordered_rearward_2h_training_20261115'].update(status='completed',total_PPO_seconds=total,promoted=False);reg['active_ordered_rearward_fix_training_20261115'].update(status='completed_segment_continued_in_two_hour_round',two_hour_directory=T.relative_to(R).as_posix());put(regpath,reg)
for q in [T/'README.md',R/'README.md',R/'docs/DR_TRAINING_INDEX_20261111.md']:
 with q.open('a',encoding='utf8')as f:f.write(chr(10)+'2026-11-15两小时轮完成：累计PPO '+str(round(total,3))+'秒；低速完整两阶'+str(selected['low_whole_passed'])+'/'+str(selected['low_whole_requested'])+'；综合db6仍冻结。结果见 '+(T/'FINAL_REPORT.md').relative_to(R).as_posix()+'。'+chr(10))
print(json.dumps(decision,ensure_ascii=False),flush=True)
