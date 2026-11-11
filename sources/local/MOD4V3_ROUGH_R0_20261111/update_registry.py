"""Append final R0 provenance and PT paths to the shared training catalog."""
from pathlib import Path
import json,hashlib
ROOT=Path(r'D:/claude2/fangzhen/_mod4v2_src_20261106')
T=ROOT/'sources/local/MOD4V3_ROUGH_R0_20261111';CAT=ROOT/'sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def put(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
idx=read(T/'evidence/MODEL_ARCHIVE_INDEX.json');sel=read(T/'evidence/CANDIDATE_SELECTION.json');plan=read(T/'PLAN.json');summary=read(T/'evidence/ROUND_SUMMARY.json');reg=read(CAT/'MODEL_REGISTRY.json')
assert not any(x['id']=='rough_r0' for x in reg['stages']),'R0 stage already recorded; do not duplicate'
ids=[]
for model in idx['models']:
 name=model['file'];suffix='first' if name=='model_first_complete.pt' else name.replace('model_','').replace('.pt','');mid='rough_r0_'+suffix
 row=dict(model,id=mid,parent_model_id='square1_030m',parent_sha256=plan['parent_sha256'],original_remote_path=plan['support'].rsplit('/support',1)[0]+'/train040m_rough_r0_r1/'+name,actor_input=35,critic_input=78,git_storage='ordinary Git full PPO PT bytes, including terrain state',role='retained R0 experimental candidate' if model['sha256']==sel['sha256'] else 'R0 complete PPO checkpoint',recipe_files=['sources/local/MOD4V3_ROUGH_R0_20261111/PLAN.json'])
 reg['models'].append(row);ids.append(mid)
chosen=next(x for x in reg['models'] if x['sha256']==sel['sha256'])['id']
stage=dict(id='rough_r0',title='MOD4 R0浅地形首轮40分钟',profile='rough_r0',parent_model_id='square1_030m',parent_sha256=plan['parent_sha256'],source_directories=['sources/local/MOD4V3_ROUGH_R0_20261111'],recipe_files=['sources/local/MOD4V3_ROUGH_R0_20261111/PLAN.json'],training_method=dict(plan['training_round'],actual_seconds=summary['training']['elapsed_seconds']),terrain=plan['rough_r0'],sampling_mixture=plan['sampling_mixture'],reward=plan['reward'],retained_model_id=chosen,retained_model_sha256=sel['sha256'],other_model_ids=[x for x in ids if x!=chosen],status='authorized40min completed; experimental candidate retained, no automaticR1',original_tag='trial-20261111-mod4-rough-r0-start-01',final_tag='trial-20261111-mod4-rough-r0-final-01',final_report='sources/local/MOD4V3_ROUGH_R0_20261111/FINAL_REPORT.md',selection_basis=sel['criteria'])
reg['stages'].append(stage);reg['latest_rough_r0_candidate_model_id']=chosen;reg['last_update_tag']=stage['final_tag'];reg['weights_summary'].update(models=len(reg['models']),unique_sha256=len({x['sha256'] for x in reg['models']}),total_bytes=sum(x['bytes'] for x in reg['models']))
put(CAT/'MODEL_REGISTRY.json',reg)
with (CAT/'MODELS.md').open('a',encoding='utf8') as f:
 f.write('\n\n## MOD4 R0浅地形：完整40分钟检查点\n\n| 模型ID | iteration | bytes | SHA256 |\n|---|---:|---:|---|\n')
 for model,mid in zip(idx['models'],ids):f.write(f'| [{mid}](../MOD4V3_ROUGH_R0_20261111/weights/{model["file"]}) | {model["iteration"]} | {model["bytes"]:,} | `{model["sha256"]}` |\n')
full=sel['model_metrics']['Step7_all_remaining_DR'];parent=sel['parent_metrics']['Step7_all_remaining_DR']
note=f'\n\n2026-11-11 R0首轮完成：{summary["training"]["elapsed_seconds"]:.3f}s，保留{chosen}（iter{sel["iteration"]}，SHA`{sel["sha256"]}`）为R0实验候选；完整DR level0浅地形越障{parent["rough_crossed"]}→{full["rough_crossed"]}/120，Flat正式{parent["flat_passed"]}→{full["flat_passed"]}/60。此为同批诊断，不代表Rough全课程毕业；原Flat主冻结保留，R1未启动。报告与全PT见`sources/local/MOD4V3_ROUGH_R0_20261111/FINAL_REPORT.md`，当前总{len(reg["stages"])}阶段/分支、{len(reg["models"])}完整PT。\n'
for rel in ('README.md','docs/DR_TRAINING_INDEX_20261111.md','docs/DR_TRAINING_RESUME_20261111.md','sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/README.md'):
 with (ROOT/rel).open('a',encoding='utf8') as f:f.write(note)
print('Updated catalog:',len(reg['stages']),'stages',len(reg['models']),'models','candidate',chosen)
