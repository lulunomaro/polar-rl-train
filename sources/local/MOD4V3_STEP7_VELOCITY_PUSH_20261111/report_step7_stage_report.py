from pathlib import Path
import json,argparse,hashlib
p=argparse.ArgumentParser();p.add_argument('stage');a=p.parse_args()
r=Path(r'D:\claude2\fangzhen\_mod4v2_src_20261106\sources\local')/('MOD4V3_STEP7_'+a.stage.upper()+'_20261111');e=r/'evidence';plan=json.loads((r/'PLAN.json').read_text(encoding='utf-8'))
result=e/'paired_final_r1_RESULT.json'
if not result.exists():raise SystemExit('paired evaluation not complete')
d=json.loads(result.read_text(encoding='utf-8'));models=list(d['input_sha256']);rows=d['rows'];variant=next(x['variant'] for x in rows if x['variant']!='nominal0')
summary=[]
for model in models:
 group={x['task']:x for x in rows if x['model']==model and x['variant']==variant}
 nominal={x['task']:x for x in rows if x['model']==model and x['variant']=='nominal0'}
 forward=[group[k] for k in ['forward_2.0','forward_2.2']]
 summary.append(dict(model=model,sha256=d['input_sha256'][model],forward_means=[x['mean'][0] for x in forward],forward_passes=[x['passed'] for x in forward],forward_mean_abs_error=sum(sum(abs(v[0]-target) for v in group[task]['per_env']) for task,target in [('forward_2.0',2.),('forward_2.2',2.2)])/20,other_passes={k:group[k]['passed'] for k in ['backward_1.5','yaw_14.137','height_0.20','height_0.40']},nominal_forward_mean_abs_error=sum(sum(abs(v[0]-target) for v in nominal[task]['per_env']) for task,target in [('forward_2.0',2.),('forward_2.2',2.2)])/20,resets=sum(x['resets'] for x in group.values()),numerical=sum(x['reasons']['numerical'] for x in group.values())))
print(json.dumps(summary,ensure_ascii=False,indent=2))
(e/'PAIRED_MODEL_COMPARISON.json').write_text(json.dumps({'variant':variant,'models':summary,'selection_note':'No automatic promotion; compare task preservation, forward tracking and nominal results. Original frozen baseline remains immutable.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
