from pathlib import Path
import ast,json,shutil,time
B=Path(__file__).resolve().parent;P=B.parent/'MOD4_SCUT_FUDAN_EIGHTH_HOUR_20261019'
f=json.loads((P/'reports/THREE_HOUR_ALL_CLOSED_FINAL_MODELS_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes())
assert f['passed_all_three_whole_final_models_CPU'] and f['all_actual_owner_nodes_children_out_canonicalNone_real_locks_free']
(B/'reports').mkdir()
rows=[]
for p in (P/'future_same_recipe_hour_templates').glob('*.py'):
    q=B/p.name;assert not q.exists();ast.parse(p.read_text('utf8'));shutil.copy2(p,q);rows.append(str(q))
with (B/'reports/NINTH_STAGE_CREATED_ONLY_AFTER_EIGHTH_ACTUAL_CLOSED_CPU.json').open('x',encoding='utf8') as stream:
    json.dump(dict(epoch=time.time(),previous_full_CPU_report=str(P/'reports/THREE_HOUR_ALL_CLOSED_FINAL_MODELS_ORIGINAL_COST_CPU_ACTUAL.json'),copied_existing_same_recipe_templates=rows,no_new_reward_physics_or_account_change=True),stream,indent=2)
print(json.dumps(dict(created=True,files=len(rows))))
