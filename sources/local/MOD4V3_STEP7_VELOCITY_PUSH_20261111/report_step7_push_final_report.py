from pathlib import Path
import json,statistics
r=Path(r'D:\claude2\fangzhen\_mod4v2_src_20261106\sources\local\MOD4V3_STEP7_VELOCITY_PUSH_20261111');e=r/'evidence'
d=json.loads((e/'paired_final_r1_RESULT.json').read_text(encoding='utf-8'));final=json.loads((e/'training_round/FINAL.json').read_text(encoding='utf-8'));models=list(d['input_sha256']);variant=next(x['variant'] for x in d['rows'] if x['variant']!='nominal0');summary=[]
for model in models:
 before={x['task']:x for x in d['rows'] if x['model']==model and x['variant']==variant}
 after={x['task']:x for x in d['recovery_rows'] if x['model']==model and x['variant']==variant}
 nominal={x['task']:x for x in d['recovery_rows'] if x['model']==model and x['variant']=='nominal0'}
 tasks=['forward_2.0','forward_2.2','backward_1.5','yaw_14.137','height_0.20','height_0.40']
 per=20
 row=dict(model=model,sha256=d['input_sha256'][model],pre_forward_means=[before[k]['mean'][0] for k in tasks[:2]],pre_forward_passes=[before[k]['passed'] for k in tasks[:2]],post_forward_means=[after[k]['post_push_stable_mean'][0] for k in tasks[:2]],post_forward_passes=[after[k]['post_push_passed'] for k in tasks[:2]],post_forward_error=sum(sum(abs(x[0]-v) for x in after[k]['per_env_post_stable']) for k,v in [('forward_2.0',2.),('forward_2.2',2.2)])/per,post_other_passes={k:after[k]['post_push_passed'] for k in tasks[2:]},full_resets=sum(x['resets'] for x in before.values()),post_recovery={k:{'recovered':sum(x is not None for x in after[k]['recovery_s']),'median_seconds':statistics.median(x for x in after[k]['recovery_s'] if x is not None) if any(x is not None for x in after[k]['recovery_s']) else None,'individual_seconds':after[k]['recovery_s']} for k in tasks},nominal_post_forward_means=[nominal[k]['post_push_stable_mean'][0] for k in tasks[:2]],nominal_post_forward_passes=[nominal[k]['post_push_passed'] for k in tasks[:2]])
 summary.append(row)
result={'variant':variant,'training_elapsed_seconds':final['elapsed_seconds'],'final_iteration':final['checkpoint']['iteration'],'actual_last_push_progress':final['last_progress'].get('velocity_push'),'models':summary,'protocol':d['velocity_push_protocol']}
(e/'PAIRED_PUSH_MODEL_COMPARISON.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for x in summary:print(x['model'],'pre',x['pre_forward_means'],x['pre_forward_passes'],'post',x['post_forward_means'],x['post_forward_passes'],'other',x['post_other_passes'],'error',x['post_forward_error'],'resets',x['full_resets'],'recovery',[(k,v['recovered'],v['median_seconds']) for k,v in x['post_recovery'].items()])
