"""Build the R0 report and complete PT index from already saved evidence."""
from pathlib import Path
import json,hashlib,torch,collections
ROOT=Path(r'D:/claude2/fangzhen/_mod4v2_src_20261106')
TRIAL=ROOT/'sources/local/MOD4V3_ROUGH_R0_20261111';E=TRIAL/'evidence';M=E/'training_round';W=TRIAL/'weights'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def put(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
rows=[];known={}
for f in sorted(W.glob('*.pt')):
 sha=hashlib.sha256(f.read_bytes()).hexdigest()
 if sha in known:known[sha]['aliases'].append(f.name);continue
 d=torch.load(f,map_location='cpu',weights_only=False)
 required=('actor_state_dict','critic_state_dict','optimizer_state_dict','cpu_rng','cuda_rng','domain_randomization_state','terrain_curriculum_state')
 assert all(k in d for k in required),f
 assert d['actor_state_dict']['mlp.0.weight'].shape[1]==35 and d['critic_state_dict']['mlp.0.weight'].shape[1]==78
 course=d['terrain_curriculum_state'];nominal=d['domain_randomization_state']['nominal_env_mask'];flat=course['flat_mask']
 row=dict(file=f.name,git_path=f.relative_to(ROOT).as_posix(),bytes=f.stat().st_size,sha256=sha,iteration=d['iter'],optimizer_entries=len(d['optimizer_state_dict']['state']),complete_PPO=True,terrain_state_fields=list(course),local_policy_steps=course['local_policy_steps'],level_counts=torch.bincount(course['terrain_levels'],minlength=4).tolist(),groups=dict(nominal_flat=int((nominal&flat).sum()),nominal_rough=int((nominal&~flat).sum()),DR_flat=int((~nominal&flat).sum()),DR_rough=int((~nominal&~flat).sum())),aliases=[])
 rows.append(row);known[sha]=row
put(E/'MODEL_ARCHIVE_INDEX.json',dict(models=rows,unique_models=len(rows),total_bytes=sum(x['bytes'] for x in rows),storage='ordinary Git full PPO PT blobs, not LFS pointers; byte-identical final alias noted'))
flat_path=E/'paired_flat_final_r1_RESULT.json';rough_path=E/'paired_rough_final_r1_RESULT.json'
if not flat_path.exists() or not rough_path.exists():
 print('Checkpoint archive updated; final paired results pending',len(rows));raise SystemExit()
flat=read(flat_path);rough=read(rough_path);final=read(E/'TRAIN_FINAL.json');candidates=[]
for model,sha in flat['input_sha256'].items():
 modelrow=dict(model=model,sha256=sha)
 for variant in ('nominal0','Step7_all_remaining_DR'):
  f=[x for x in flat['rows'] if x['model']==model and x['variant']==variant]
  post=[x for x in flat['recovery_rows'] if x['model']==model and x['variant']==variant]
  formal=[x for x in f if x['capability_gate']];formalpost=[x for x in post if x['task'] not in ('combo_0.9_1.2','forward_2.7_diagnostic')]
  forward=[x for x in post if x['task'] in ('forward_2.0','forward_2.2')]
  error=[abs(v[0]-(2. if x['task']=='forward_2.0' else 2.2)) for x in forward for v in x['per_env_post_stable']]
  r=[x for x in rough['rows'] if x['model']==model and x['variant']==variant]
  modelrow[variant]=dict(flat_passed=sum(x['post_push_passed'] for x in formalpost),flat_requested=sum(x['requested'] for x in formalpost),flat_resets=sum(x['resets'] for x in formal),flat_diagnostic_resets=sum(x['resets'] for x in f if not x['capability_gate']),flat_forward_MAE=sum(error)/len(error),flat_post_rows=post,rough_crossed=sum(x['crossed_count'] for x in r),rough_requested=sum(x['requested'] for x in r),rough_resets=sum(x['resets'] for x in r),rough_rows=r)
 candidates.append(modelrow)
summary=dict(training=final,models=candidates,flat_num_envs=flat['num_envs'],rough_num_envs=rough['num_envs'],flat_numerical=sum(x['reasons']['numerical'] for x in flat['rows']),rough_numerical=sum(x['reasons']['numerical'] for x in rough['rows']),flat_action_error=flat['action_slot_max_error'],rough_action_error=rough['action_slot_max_error'],flat_envelope=flat['motor_envelope_violation_nm'],rough_envelope=rough['motor_envelope_violation_nm'])
put(E/'ROUND_SUMMARY.json',summary)
print('MODEL | fullDR Flat passed/reset/forwardMAE | fullDR Rough crossed/reset | nominal Rough crossed')
for m in candidates:
 f=m['Step7_all_remaining_DR'];n=m['nominal0']
 print(m['model'],f['flat_passed'],f['flat_resets'],round(f['flat_forward_MAE'],4),f['rough_crossed'],f['rough_resets'],n['rough_crossed'])
print('training',final['elapsed_seconds'],final['last_progress']['done_totals'])
print('unique PT',len(rows),'total bytes',sum(x['bytes'] for x in rows))
