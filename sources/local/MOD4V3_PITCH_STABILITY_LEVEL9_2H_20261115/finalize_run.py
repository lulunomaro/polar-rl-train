"""Report measured pitch comparison and preserve the frozen comprehensive default."""
from pathlib import Path
import json,time,hashlib
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/'evidence'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def put(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=read(T/'PLAN.json');final=read(E/'training/FINAL.json');actual=final['elapsed_seconds'];selected=read(T/'weights/SELECTED_STUDENT.json');rank=read(E/'STUDENT_FIXED_RANKING.json');models=read(E/'MODEL_COLLECTION.json')['models'];frozen=p['parent_sha256'];baseline=read(E/'baseline_parent_pitch/RESULT.json')
lines=['# 难度9随机起伏与启动急停俯仰修复结果','',f'实际PPO {actual:.3f}秒，授权7200秒；是否完成两小时：{actual>=7199}。父为综合冻结db6e9ccf，实验候选未自动晋升。','', '## 父模型与候选固定启停结果','', '| 模型与地形 | 完整无重置/4 | 俯仰RMS° | 启动峰值° | 急停峰值° | 启动速度MAE m/s |','|---|---:|---:|---:|---:|---:|']
for label,summaries in [('父模型',baseline['summary']),('实验候选',selected['pitch_summary'])]:
 for family,v in summaries.items():lines.append('| '+label+' '+family+' | '+str(v['completed_without_reset'])+' | '+' | '.join(str(v[k])for k in ['pitch_RMS_deg_mean','startup_peak_deg_max','braking_peak_deg_max','moving_vx_MAE_mean'])+' |')
lines+=['','标称MuJoCo0ms固定14s启停；level9随机起伏与平地、0.28/0.40m高度、1.2/2.2m/s指令。前2s站稳，随后1s启动、2s急停交替正反向。首次物理episode、原2mm保护；不冒充完整DR部署验收。','', '## 全部检查点保留能力','', '| 检查点 | 启停完整/8 | 平地/60 | 正向上阶/5 | 实际斜向/20 | 下阶/5 | 俯仰评分越低越好 |','|---|---:|---:|---:|---:|---:|---:|']
for row in sorted(rank,key=lambda r:r['source_file']):lines.append('| '+row['source_file']+' | '+' | '.join(str(row[k])for k in ['pitch_complete_cases','flat60_passed','straight_passed','actual_oblique_passed','descent_passed','stability_score'])+' |')
lines+=['','## 配方','', '真实底盘重力投影俯仰与机身omega_y：-dt*[10*relu(abs(pitch)-5deg)^2+0.35*omega_y^2]，只在目标平地/随机起伏且真实轮子接地时应用。专项采用真实阶跃速度指令，未通过命令低通伪造稳定；原速度追踪奖励保留。','', '40%台阶、35%Rough、25%平地；一半Rough定为随机起伏level9，一半平地反复启停；其余保留综合技能并接受冻结父教师指导。目标环境落地启停，其他环境保留落空/旋转/高度等原科目。台阶环境源码恢复综合父配方来源，不训练最新顺序后摆奖励。完整DR、MOD4资产、电机、35/78/6、控制时序及2mm单环境保护沿用。','', '## 原生完整DR配对证据','']
post=E/'post_native'
if post.exists():
 for folder in sorted(post.iterdir()):
  if folder.is_dir()and(folder/'RESULT.json').exists():
   data=read(folder/'RESULT.json');lines+=['### '+folder.name,'','~~~json',json.dumps(data.get('summary',data.get('summaries',{})),ensure_ascii=False,indent=2),'~~~','']
(T/'FINAL_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
decision=dict(status='completed'if actual>=7199 else'ended_before_full_budget',actual_PPO_seconds=actual,authorized_seconds=7200,promoted=False,default_comprehensive_parent_sha256=frozen,experimental_candidate=selected,parent_pitch_summary=baseline['summary'],all_training_and_evaluations_closed=True,no_further_training=True);put(T/'DECISION.json',decision)
put(E/'ARTIFACT_INDEX.json',[dict(path=str(q),bytes=q.stat().st_size,sha256=hashlib.sha256(q.read_bytes()).hexdigest(),storage='original retained; indexed in Git')for q in E.rglob('*.npz')])
regpath=R/'sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/MODEL_REGISTRY.json';reg=read(regpath);sid='pitch_stability_level9_20261115';assert not any(x.get('id')==sid for x in reg['stages']);ids=[]
for row in models:
 mid=sid+'_'+Path(row['file']).stem.removeprefix('model_');ids.append(mid);reg['models'].append(dict(id=mid,file=row['file'],git_path=(T/'weights'/row['file']).relative_to(R).as_posix(),sha256=row['sha256'],bytes=row['bytes'],complete_PPO=True,actor_input=35,critic_input=78,action_output=6,root_parent_sha256=frozen,recipe_files=[(T/'PLAN.json').relative_to(R).as_posix()],role='Experimental pitch stability checkpoint;not promoted',git_storage='ordinary full PT blob'))
reg['stages'].append(dict(id=sid,title='难度9随机起伏与启动急停的真实底盘俯仰稳定',status=decision['status'],total_PPO_seconds=actual,parent_sha256=frozen,retained_model_id=selected['model_id'],other_model_ids=ids,decision_file=(T/'DECISION.json').relative_to(R).as_posix()));reg['active_pitch_stability_level9_training_20261115'].update(status=decision['status'],actual_PPO_seconds=actual,promoted=False);put(regpath,reg)
for path in [T/'README.md',R/'README.md',R/'docs/DR_TRAINING_INDEX_20261111.md']:
 with path.open('a',encoding='utf8')as out:out.write('\n2026-11-15 俯仰稳定轮结束：实际PPO '+str(round(actual,3))+'秒；综合默认仍为db6；结果见 '+(T/'FINAL_REPORT.md').relative_to(R).as_posix()+'。\n')
print(json.dumps(decision),flush=True)
