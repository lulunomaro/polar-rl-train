"""Append exactactiveStep270Phase source (notflat3cmH1 parent) and horizonGAP.
No oldoutputs edited orSDK/model calls. All V1/V2 preserved.
"""
from pathlib import Path
import ast,csv,hashlib,json
B=Path(__file__).resolve().parent
m=json.loads((B/'ORIGINAL_ACCEPTANCE_CONTRACT_MATRIX_V2.json').read_bytes());plans=json.loads((B/'NEWPLANT_SOURCE_ONLY_REPLAY_PLANS_V1.json').read_bytes());h=m['references']['H1_SDK'];p=Path(h['path']);raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==h['SHA'];text=raw.decode('utf-8-sig');tr=ast.parse(raw);n=next(n for n in tr.body if isinstance(n,ast.ClassDef) and n.name=='Step270Phase');fn=dict(function='Step270Phase',firstline=n.lineno,lastline=n.end_lineno,source=ast.get_source_segment(text,n));ref=dict(h);ref.update(id='H1_ACTIVE_270_PHASE',original_functions=[fn]);m['references']['H1_ACTIVE_270_PHASE']=ref;m['original_function_excerpts'].append(dict(reference='H1_ACTIVE_270_PHASE',**fn));m['schema']='mod4.original_acceptance_contract_SOURCEONLY.v3'
for r in m['rows']:
 if r['lineage']=='H1_NORMAL':
  r['original_reference_ids'].append('H1_ACTIVE_270_PHASE');r['original_replay_window_seconds']=None;r['source_base_episode_default_seconds']=20;r['original_replay_window_gap']='Acceptedoriginalnormal0c1e/71db skillcohort/horizonnotjoined. Mod4EnvCfgdefault20s is source default, notinvented acceptedcohorthorizon.';r['original_metric_predicate']['active_runtime_class']='Step270Phase delegatesStep270Events; itsownpublicage100Hz+=2 at50Hz,notgenericparentflat3cm event proxy.'
for plan in plans['plans']:
 if plan['lineage']=='H1_NORMAL':plan['dependency_table'].append(dict(lineage='H1_NORMAL',reference_id='H1_ACTIVE_270_PHASE',path=ref['path'],SHA=ref['SHA'],bytes=ref['bytes'],role=ref['kind']));plan['physical_seconds_windows'][0]['selected_original_accepted_horizon_seconds']=None
m['metadata_revisions_preserved']='V1/V2 originalmatrices anddescriptorV1 kept; V3adds activeH1delegate/provenance and removes unprovedselected20s horizon whilekeeping sourcedefault20s explicit.'
with (B/'ORIGINAL_ACCEPTANCE_CONTRACT_MATRIX_FINAL_V3.json').open('x',encoding='utf-8') as f:json.dump(m,f,ensure_ascii=False,indent=2)
with (B/'NEWPLANT_SOURCE_ONLY_REPLAY_PLANS_FINAL_V2.json').open('x',encoding='utf-8') as f:json.dump(plans,f,ensure_ascii=False,indent=2)
rows=[d for plan in plans['plans'] for d in plan['dependency_table']]
with (B/'SOURCE_ONLY_REPLAY_DEPENDENCY_TABLE_FINAL_V2.csv').open('x',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['lineage','reference_id','path','SHA','bytes','role']);w.writeheader();w.writerows(rows)
s=(B/'emit_source_only_replay_tasks_v1.py').read_text(encoding='utf-8').replace('NEWPLANT_SOURCE_ONLY_REPLAY_PLANS_V1.json','NEWPLANT_SOURCE_ONLY_REPLAY_PLANS_FINAL_V2.json').replace('ORIGINAL_ACCEPTANCE_CONTRACT_MATRIX_V2.json','ORIGINAL_ACCEPTANCE_CONTRACT_MATRIX_FINAL_V3.json');compile(s,'emitterV2','exec')
with (B/'emit_source_only_replay_tasks_v2.py').open('x',encoding='utf-8') as f:f.write(s)
s=(B/'ACCEPTANCE_CONTRACT_MATRIX_SOURCE_ONLY_V1.md').read_text(encoding='utf-8');s+='\n## 追加元数据复核\nH1 active Step270Phase 原函数补齐，公开100Hz age每50Hz控制+2；直接委托Step270Events。Mod4EnvCfg的20s仅源码默认，不冒充已经保存的0c1e/71db技能验收cohort/horizon。最终机器矩阵使用FINAL_V3、依赖表FINAL_V2，旧V1/V2原样保留。\n\n[最终机器矩阵](<'+(B/'ORIGINAL_ACCEPTANCE_CONTRACT_MATRIX_FINAL_V3.json').as_posix()+'>) · [最终依赖表](<'+(B/'SOURCE_ONLY_REPLAY_DEPENDENCY_TABLE_FINAL_V2.csv').as_posix()+'>)\n'
with (B/'ACCEPTANCE_CONTRACT_MATRIX_SOURCE_ONLY_FINAL_V2.md').open('x',encoding='utf-8') as f:f.write(s)
print(json.dumps(dict(lineages=9,references=len(m['references']),sourcefunctions=len(m['original_function_excerpts']),dependency_rows=len(rows),selected_H1horizon_notinvented=True,model_SDK_operations=0),indent=2))
