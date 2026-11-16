"""Close this finite trial with all raw successes/failures and no promotion or new PPO."""
from pathlib import Path
import json,time,hashlib,csv
T=Path(__file__).resolve().parent;E=T/'evidence';W=T/'weights'
monitor=json.loads((E/'MONITOR_COMPLETE.json').read_text());evaluations=[]
for f in sorted((E/'checkpoint_evals').glob('*/EVALUATION.json')):
 d=json.loads(f.read_text())
 if d.get('closure_guard_contract')!='SCUT_NO_2MM_RESET_V1':continue
 d['evaluation_path']=str(f)
 raw=f.parent/'single_step/RESULT.json'
 step=json.loads(raw.read_text())if raw.exists()else{}
 valid=step.get('contact_protocol')=='SINGLE_STEP_TOP_GEOMETRY_V2'
 d['single_step_metric_valid']=valid
 for key in ('single_step_by_height','single_step_qualified_passed','single_step_requested'):d.pop(key,None)
 if valid:d.update(single_step_by_height=step['by_height'],single_step_qualified_passed=sum(x['success']for x in step['rows']),single_step_requested=len(step['rows']))
 evaluations.append(d)
parent=next((d for d in evaluations if Path(d['model']).stem=='parent_comprehensive'),None)
rows=[]
for d in evaluations:
 row=dict(checkpoint=Path(d['model']).stem,sha256=d['sha256'],complete=d['complete'],single_step_metric_valid=d['single_step_metric_valid'],flat60=d.get('flat60_passed'),straight_20cm_two_step=d.get('straight_passed'),descent=d.get('descent_passed'),oblique=d.get('actual_oblique_passed'),qualified_single_step=d.get('single_step_qualified_passed'))
 for height,stats in d.get('single_step_by_height',{}).items():row['height_'+height]=str(stats['passed'])+'/'+str(stats['requested'])
 rows.append(row)
keys=list(dict.fromkeys(k for row in rows for k in row))
with(E/'CHECKPOINT_CURVE.csv').open('w',encoding='utf-8-sig',newline='')as f:
 writer=csv.DictWriter(f,fieldnames=keys);writer.writeheader();writer.writerows(rows)
final=json.loads((E/'training/FINAL.json').read_text())if(E/'training/FINAL.json').exists()else None
result=dict(epoch=time.time(),promoted=False,automatic_extension=False,no_new_PPO=True,training_has_error=monitor['training_has_error'],full_PT_count=len(monitor['models']),fixed_evaluations=len(evaluations),all_evaluations_complete=all(d['complete']for d in evaluations),parent_sha256=parent['sha256']if parent else None,actual_training_seconds=final['elapsed_seconds']if final else None,checkpoints=rows,native_full_DR_graduation=False,current_default_unchanged=True)
(E/'FINAL_SUMMARY.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
lines=['# 两小时逐环境低速单台阶课程结果','',f"实际PPO秒数：{result['actual_training_seconds']}；完整PT：{result['full_PT_count']}；固定评测：{result['fixed_evaluations']}组。",'',f"训练错误：{result['training_has_error']}；所有固定评测完整：{result['all_evaluations_complete']}。",'','父模型为当前采用的c874/iter25362。每个检查点均采用相同9个单阶高度×5起点，指令0.4m/s且真实入阶/接近速度、双轮上层接触、车身越边和0.4秒稳定共同判定。名义MuJoCo不等于原生完整DR毕业；训练随机课程累计通过次数也不是固定成功率。','','| 检查点 | 5cm | 7cm | 9cm | 11cm | 13cm | 15cm | 17cm | 19cm | 20cm | 平地 | 旧两阶 | 下阶 |','|---|---|---|---|---|---|---|---|---|---|---|---|---|']
for row in rows:
 values=[row['checkpoint']]+[row.get('height_'+str(h),'旧接触判定无效' if not row['single_step_metric_valid'] else '未完成')for h in [.05,.07,.09,.11,.13,.15,.17,.19,.2]]+[str(row.get('flat60')),str(row.get('straight_20cm_two_step')),str(row.get('descent'))]
 lines.append('| '+' | '.join(values)+' |')
lines+=['','早期单台阶回放误认step_1而实际碰撞体为step_2，相关接触/通过统计已标为无效，不能读作0通过。修复后按实际上层碰撞体高度识别，协议SINGLE_STEP_TOP_GEOMETRY_V2；原生课程计数不受此命名错误影响。每个高度的真实入阶速度、接触、失败原因和原始曲线见各checkpoint_evals目录。完整课程等级分布、升降级和低级复习记录见training/LATEST_PROGRESS.json与inspections；各环境前沿等级表示下一挑战高度。','','本轮保存全部检查点供比较，未自动更改默认模型、部署或延长训练。原生探针的接口/读者错误与后续修复并列保留。']
(T/'FINAL_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf8');print(json.dumps(result),flush=True)
