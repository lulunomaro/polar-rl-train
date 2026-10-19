"""Use the corrected prepared templates only after the real two-slot closure."""
from pathlib import Path
import ast,hashlib,json,shutil,time
B=Path(__file__).resolve().parent;P=B.parent/'MOD4_SCUT_FUDAN_ELEVENTH_HOUR_20261019';R=B/'reports';R.mkdir(exist_ok=True)
f=json.loads((P/'reports/PARTIAL_HOUR_ACTUAL_GO_FINALS_AND_NEXT_SOURCES_CPU_ACTUAL.json').read_bytes());assert f['passed_next_three_sources_whole_model_CPU'] and f['passed_all_actual_GO_final_models_CPU'] and f['all_actual_owner_nodes_children_out_canonicalNone_real_locks_free']
assert f['actual_owned_new_final_experts']==['e2','recovery'] and f['experts']['h1']['current_hour_production_updates']==0 and f['experts']['h1']['retained_previous_healthy_final_hour']==10
assert not (R/'TWELFTH_CORRECTED_TEMPLATES_AFTER_PARTIAL_CLOSED_ACTUAL.json').exists()
source=P/'future_partial_hour_repair_templates_V2';files=[]
for p in sorted(source.glob('*.py')):
 target=B/p.name;assert not target.exists();shutil.copy2(p,target);ast.parse(target.read_text('utf8'));files.append(dict(path=str(target),SHA=hashlib.sha256(target.read_bytes()).hexdigest()))
assert len(files)==5
with (R/'TWELFTH_CORRECTED_TEMPLATES_AFTER_PARTIAL_CLOSED_ACTUAL.json').open('x',encoding='utf8') as stream:json.dump(dict(epoch=time.time(),actual_previous_owner318576_out_original_cost_once_settled=True,H1_source_retained_hour10_not_new_hour11_final=f['experts']['h1']['final'],E2_E3_source_actual_hour11_finals={k:f['experts'][k]['final'] for k in ('e2','recovery')},corrected_unused_V2_files=files,no_GPU_Task_native_or_account_write=True,no_H1_behavior_replay_since_source_unchanged=True),stream,indent=2)
print(json.dumps(dict(corrected_templates_after_actual_partial_closure=True,retained_H1_SHA=f['experts']['h1']['final']['SHA'])))
