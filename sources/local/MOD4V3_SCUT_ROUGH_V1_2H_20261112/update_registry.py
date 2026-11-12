from pathlib import Path
import json,hashlib,argparse,torch
T=Path(__file__).resolve().parent;R=T.parents[2];CAT=R/'sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111'
p=argparse.ArgumentParser();p.add_argument('--final',action='store_true');a=p.parse_args()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def put(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
plan=read(T/'EFFECTIVE_RECIPE.json');reg=read(CAT/'MODEL_REGISTRY.json');ids=[]
for path in sorted((T/'weights').glob('*.pt')):
 suffix='first' if path.stem=='model_first_complete' else path.stem.removeprefix('model_');mid='scutroughv1_'+suffix
 sha=hashlib.sha256(path.read_bytes()).hexdigest();data=torch.load(path,map_location='cpu',weights_only=False)
 assert (data['actor_state_dict']['mlp.0.weight'].shape[1],data['critic_state_dict']['mlp.0.weight'].shape[1])==(35,78)
 assert all(k in data for k in ['optimizer_state_dict','cpu_rng','cuda_rng','python_rng','numpy_rng','reset_rng','domain_randomization_state','terrain_curriculum_state'])
 assert data['reward_recipe']['profile']=='rough_scut_v1'
 assert data['terrain_curriculum_state']['attempts'].shape==(11,10)
 assert data['source_asset']['actual_training_assets']['robot.usd']['sha256']==plan['asset_identity']['actual_training_assets']['robot.usd']['sha256']
 row=dict(id=mid,file=path.name,git_path=path.relative_to(R).as_posix(),bytes=path.stat().st_size,sha256=sha,iteration=data['iter'],optimizer_entries=len(data['optimizer_state_dict']['state']),complete_PPO=True,actor_input=35,critic_input=78,parent_model_id='roughv0_100m',parent_sha256=plan['parent_sha256'],original_remote_path=plan['support'].rsplit('/support',1)[0]+'/'+plan['training_round']['job']+'/'+path.name,recipe_files=[(T/'EFFECTIVE_RECIPE.json').relative_to(R).as_posix(),(T/'PLAN.json').relative_to(R).as_posix()],role='Unified SCUT Rough-v1 full PPO checkpoint; comparison and selection in stage DECISION',git_storage='ordinary Git full PPO PT bytes',aliases=[])
 same=[m for m in reg['models'] if m['id']==mid]
 if same:assert same[0]['sha256']==sha
 else:reg['models'].append(row)
 ids.append(mid)
stage=dict(id='scut_rough_v1_2h',title='SCUT Rough-v1统一跑场与腾空落地2小时',profile='rough_scut_v1',parent_model_id='roughv0_100m',parent_sha256=plan['parent_sha256'],source_directories=[T.relative_to(R).as_posix()],recipe_files=[(T/'EFFECTIVE_RECIPE.json').relative_to(R).as_posix(),(T/'PLAN.json').relative_to(R).as_posix()],training_method=plan['training_round'],sampling_mixture=plan['sampling_mixture'],reward=plan['reward'],model_ids=ids,status='Unified7200s PPO completed; frozen-weight comparison and selection in stage report' if a.final else 'Unified7200s PPO running; full checkpoint every300s',original_tag='trial-20261112-mod4-scut-rough-v1-2h-start-01',final_tag='trial-20261112-mod4-scut-rough-v1-2h-final-01' if a.final else None,terrain=plan['rough_scut_v1'],budget=plan['budget_accounting'])
reg['stages']=[m for m in reg['stages'] if m['id']!=stage['id']]+[stage]
if a.final:reg['current_round_actual_PPO_seconds']=read(T/'evidence/training_round/FINAL.json')['elapsed_seconds']
reg['weights_summary'].update(models=len(reg['models']),unique_sha256=len({x['sha256'] for x in reg['models']}),total_bytes=sum(x['bytes'] for x in reg['models']))
put(T/'evidence/MODEL_ARCHIVE_INDEX.json',dict(stage=stage['id'],models=[m for m in reg['models'] if m['id'] in ids],unique_sha256=len({m['sha256'] for m in reg['models'] if m['id'] in ids}),storage='full PPO PT bytes in ordinary Git blobs; additional smoke aliases preserved under evidence'))
reg['current_training_status']=stage['status'];reg['last_update_tag']=stage['final_tag'] or stage['original_tag'];put(CAT/'MODEL_REGISTRY.json',reg)
path=CAT/'MODELS.md';content=path.read_text(encoding='utf-8');marker='\n\n## SCUT Rough-v1统一科目2小时'
if marker in content:content=content.split(marker)[0]
content+=marker+'\n\n| 模型ID | iteration | bytes | SHA256 |\n|---|---:|---:|---|\n'
for mid in ids:
 m=next(x for x in reg['models'] if x['id']==mid)
 content+=f"| [{mid}](../MOD4V3_SCUT_ROUGH_V1_2H_20261112/weights/{m['file']}) | {m['iteration']} | {m['bytes']:,} | `{m['sha256']}` |\n"
path.write_text(content,encoding='utf-8')
print(json.dumps(dict(stages=len(reg['stages']),models=len(reg['models']),new_course_models=len(ids))))
