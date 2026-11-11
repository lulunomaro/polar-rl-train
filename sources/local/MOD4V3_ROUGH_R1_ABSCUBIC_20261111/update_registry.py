"""Register available full PPO checkpoints without changing accepted frozen identities."""
from pathlib import Path
import json,hashlib,argparse,torch
T=Path(__file__).resolve().parent;R=T.parents[2];CAT=R/'sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111'
p=argparse.ArgumentParser();p.add_argument('--final',action='store_true');a=p.parse_args()
def read(p):return json.loads(p.read_text(encoding='utf8'))
def put(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
plan=read(T/'PLAN.json');reg=read(CAT/'MODEL_REGISTRY.json');ids=[]
for path in sorted((T/'weights').glob('*.pt')):
 suffix='first' if path.stem=='model_first_complete' else path.stem.removeprefix('model_');mid='r1cubic_'+suffix
 sha=hashlib.sha256(path.read_bytes()).hexdigest();data=torch.load(path,map_location='cpu',weights_only=False)
 assert (data['actor_state_dict']['mlp.0.weight'].shape[1],data['critic_state_dict']['mlp.0.weight'].shape[1])==(35,78)
 assert all(k in data for k in ['optimizer_state_dict','cpu_rng','cuda_rng','domain_randomization_state'])
 row=dict(id=mid,file=path.name,git_path=path.relative_to(R).as_posix(),bytes=path.stat().st_size,sha256=sha,iteration=data['iter'],optimizer_entries=len(data['optimizer_state_dict']['state']),complete_PPO=True,actor_input=35,critic_input=78,parent_model_id='r1sq2_015m',parent_sha256=plan['parent_sha256'],original_remote_path=plan['support'].rsplit('/support',1)[0]+'/'+plan['training_round']['job']+'/'+path.name,recipe_files=[(T/'PLAN.json').relative_to(R).as_posix()],role='RoughR1 complete PPO checkpoint',git_storage='ordinary Git full PPO PT bytes',aliases=[])
 same=[m for m in reg['models'] if m['id']==mid]
 if same:assert same[0]['sha256']==sha
 else:reg['models'].append(row)
 ids.append(mid)
stage=dict(id='rough_r1_abscubic',title='RoughR1平方加绝对三次项接续',profile=plan['profile'],parent_model_id='r1sq2_015m',parent_sha256=plan['parent_sha256'],source_directories=[T.relative_to(R).as_posix()],recipe_files=[(T/'PLAN.json').relative_to(R).as_posix()],training_method=plan['training_round'],sampling_mixture=plan['sampling_mixture'],reward=plan['reward'],model_ids=ids,status='R1 authorized40min segmented round completed; see paired report' if a.final else 'R1 cubic continuation740s in same authorized40min running; no promotion',original_tag='trial-20261111-mod4-rough-r1-abscubic-start-01',final_tag='trial-20261111-mod4-rough-r1-abscubic-final-01' if a.final else None)
stage['terrain']=plan['rough_r1'];stage['budget']=plan['budget_accounting']
reg['stages']=[m for m in reg['stages'] if m['id']!='rough_r1_abscubic']+[stage]
reg['weights_summary'].update(models=len(reg['models']),unique_sha256=len({x['sha256'] for x in reg['models']}),total_bytes=sum(x['bytes'] for x in reg['models']))
reg['last_update_tag']=stage['final_tag'] or stage['original_tag'];put(CAT/'MODEL_REGISTRY.json',reg)
path=CAT/'MODELS.md';content=path.read_text(encoding='utf8');marker='\n\n## RoughR1平方加绝对三次项接续'
if marker in content:content=content.split(marker)[0]
content+=marker+'\n\n| 模型ID | iteration | bytes | SHA256 |\n|---|---:|---:|---|\n'
for mid in ids:
 m=next(x for x in reg['models'] if x['id']==mid)
 content+=f"| [{mid}](../MOD4V3_ROUGH_R1_ABSCUBIC_20261111/weights/{m['file']}) | {m['iteration']} | {m['bytes']:,} | `{m['sha256']}` |\n"
path.write_text(content,encoding='utf8');print(json.dumps(dict(stages=len(reg['stages']),models=len(reg['models']),r1_models=len(ids))))
