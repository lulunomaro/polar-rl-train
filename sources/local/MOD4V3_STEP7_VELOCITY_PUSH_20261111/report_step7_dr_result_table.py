import argparse,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('stage');a=p.parse_args()
r=Path(r'D:\claude2\fangzhen\_mod4v2_src_20261106\sources\local')/('MOD4V3_STEP7_'+a.stage.upper()+'_20261111')
result=r/'evidence/paired_final_r1_RESULT.json'
if not result.exists():raise SystemExit('paired result pending')
d=json.loads(result.read_text(encoding='utf-8'));models=list(d['input_sha256']);variants=list(dict.fromkeys(x['variant'] for x in d['rows']))
print('PHYSX',a.stage,'envs',d['num_envs'],'resets',sum(x['resets'] for x in d['rows']),'numerical',sum(x['reasons']['numerical'] for x in d['rows']))
for var in variants:
 print(var)
 for model in models:
  rows={x['task']:x for x in d['rows'] if x['model']==model and x['variant']==var}
  f=[rows[k] for k in ['forward_2.0','forward_2.2','forward_2.7_diagnostic']]
  other=[rows[k]['passed'] for k in ['backward_1.5','yaw_14.137','height_0.20','height_0.40']]
  error=sum(abs(rows[k]['mean'][0]-v) for k,v in [('forward_2.0',2.),('forward_2.2',2.2)])/2
  print(model,'forward',[(round(x['mean'][0],5),x['passed']) for x in f],'other',other,'reset',sum(x['resets'] for x in rows.values()),'forward_mae',round(error,6))
if 'recovery_rows' in d:
 print('POST PUSH STABLE')
 for model in models:
  rows=[x for x in d['recovery_rows'] if x['model']==model and x['variant']!=variants[0]]
  print(model,[(x['task'],[round(v,5) for v in x['post_push_stable_mean']],x['post_push_passed'],sum(y is not None for y in x['recovery_s']),x['resets']) for x in rows])
print('PHYSICS', {k:d.get(k) for k in ['motor_envelope_violation_nm','action_slot_max_error','contact_material_readback_max_error','selected_material_after32resets_max_change','mass_readback','friction_readback']})
