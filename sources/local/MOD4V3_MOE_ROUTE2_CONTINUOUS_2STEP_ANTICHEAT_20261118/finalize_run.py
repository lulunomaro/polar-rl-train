"""Summarize actual frozen evaluation without promotion or additional training."""
from pathlib import Path
import json,hashlib,datetime,torch
T=Path(__file__).resolve().parent
E=T/'evidence'
def load(p):return json.loads(p.read_text(encoding='utf8')) if p.exists() else None
final=load(E/'training/FINAL.json');evaluation=load(E/'checkpoint_evals/model_final/EVALUATION.json')
clock=load(E/'training/TRAINING_CLOCK.json');closed=load(E/'training/SAFE_CLOSED.json');error=load(E/'training/ERROR.json')
protected=load(E/'PROTECTED_INPUTS.json')
verification={k:dict(**v,current_sha256=hashlib.sha256(Path(v['path']).read_bytes()).hexdigest()) for k,v in protected.items()}
assert all(v['sha256']==v['current_sha256'] for v in verification.values())
(E/'FINAL_PROTECTED_VERIFICATION.json').write_text(json.dumps(verification,indent=2)+'\n')
ck=torch.load(T/'weights/model_final.pt',map_location='cpu',weights_only=False)if (T/'weights/model_final.pt').exists()else None
if ck is not None:
    final['exact_final_curriculum_from_PT']=ck['curriculum_summary']
    final['actual_Adam_steps_from_PT']=ck['actual_Adam_steps']
rows=[]
for f in sorted((E/'checkpoint_evals').glob('*/EVALUATION.json')):
    d=load(f);rows.append(dict(name=f.parent.name,sha256=d['sha256'],complete=d['complete'],flat60=d.get('flat60_passed'),strict200=d.get('single_step_qualified_passed'),physical_crossed=d.get('physical_crossed'),physical_stable_events=d.get('physical_stable_events'),two_step_formal=d.get('two_step_qualified_passed'),two_step_parked=d.get('two_step_physical_parked'),two_step_s2=d.get('two_step_step2_crossed')))
report=dict(generated_at=datetime.datetime.now().astimezone().isoformat(),training_clock=clock,final=final,closed=closed,error=error,evaluations=rows,final_evaluation=evaluation,promoted=False,automatic_extension=False)
(E/'FINAL_SUMMARY.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
lines=['# MoE路线2连续二级台阶(20cm+20cm=40cm)反作弊PPO：实测收尾','', '默认模型未晋升；本目录仅记录本次独立实验。','',f'训练安全关闭：{bool(closed)}；训练报错：{bool(error)}。']
if final:lines += [f"实际训练计时 {final['elapsed_seconds']:.3f}s；完整PPO更新 {final['checkpoint']['iteration']}；实际Adam小批次 {final['actual_Adam_steps']}。",f"最终SHA {final['checkpoint']['SHA']}。",'']
if final and final.get('early_stop'):lines += ['早停原因：'+json.dumps(final['early_stop'],ensure_ascii=False),'']
if ck is not None:lines += ['最终PT准确训练计数：'+json.dumps(ck['curriculum_summary'],ensure_ascii=False),'']
lines += ['|检查点|flat60|单阶200mm正式|单阶越边|双阶400mm正式|双阶Step2驻车|双阶越边|','|---|---:|---:|---:|---:|---:|---:|']
for d in rows:lines.append(f"|{d['name']}|{d['flat60']} / 60|{d['strict200']} / 5|{d['physical_crossed']} / 5|{d.get('two_step_formal')} / 5|{d.get('two_step_parked')} / 5|{d.get('two_step_s2')} / 5|")
lines += ['', '200mm正式成绩要求纯E1、整程实际水平峰速≤0.6m/s、真实双轮台顶支撑、车身越边和末端连续稳态≥0.4s。物理事件与正式通过分开，MuJoCo名义回放不能当full-DR毕业。','', '完整原始成绩：evidence/checkpoint_evals/；最终1倍速视频：evidence/checkpoint_evals/model_final/single_step/STUDENT_CENTER_1X.mp4。','', 'E0/STD/critic冻结核验、逐高度DR与nominal完成计数及速度档见evidence/training/FINAL.json和每份完整PT。']
(T/'FINAL_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
print(json.dumps(dict(final_training_exists=bool(final),final_evaluation_complete=bool(evaluation and evaluation.get('complete')),training_error=bool(error),promoted=False)))
