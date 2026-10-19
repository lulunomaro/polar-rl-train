"""Copy only the five prepared templates after actual partial closure and whole CPU."""
from pathlib import Path
import ast,hashlib,json,shutil,time
B=Path(__file__).resolve().parent;N=B.parent/'MOD4_SCUT_FUDAN_EIGHTEENTH_HOUR_20261019';H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=json.loads((B/'reports/PARTIAL_HOUR_ACTUAL_GO_FINALS_AND_NEXT_SOURCES_CPU_ACTUAL.json').read_bytes());p=json.loads((B/'reports/PARTIAL_THREE_GO_CLOSING_RETAINED_H1_AND_EMPIRICAL_MEMORY_GUARD_CPU_ACTUAL.json').read_bytes())
assert f['passed_next_three_sources_whole_model_CPU'] and f['all_actual_owner_nodes_children_out_canonicalNone_real_locks_free'] and set(f['one_original_writer_actual_segment']['experts'])=={'h1','e2','recovery'} and f['experts']['h1']['current_hour_actual_GO'] and f['experts']['h1']['current_hour_production_updates']==0 and f['experts']['h1']['current_hour_charged_seconds']>0
assert not N.exists();rows=[]
for x in p['future_templates']:
 q=Path(x['path']);assert q.is_file() and H(q)==x['SHA'];ast.parse(q.read_bytes())
N.mkdir();(N/'reports').mkdir()
for x in p['future_templates']:
 q=Path(x['path']);dest=N/q.name;shutil.copy2(q,dest);assert H(dest)==x['SHA'];rows.append(dict(source=str(q),path=str(dest),bytes=dest.stat().st_size,SHA=H(dest),copy2_exact_bytes=True))
assert len(rows)==5
with (N/'reports/EIGHTEENTH_TEMPLATE_COPY_AFTER_ACTUAL_PARTIAL_CLOSURE_CPU_ACTUAL.json').open('x',encoding='utf8') as stream:json.dump(dict(epoch=time.time(),source_actual_closed_owner=413504,source_partial_CPU=str(B/'reports/PARTIAL_HOUR_ACTUAL_GO_FINALS_AND_NEXT_SOURCES_CPU_ACTUAL.json'),source_H1_retained_hour16_not_new_hour17_final=True,files=rows,H1_added_empirical_headroom15669_and_previous_postGO_out_guard_preserved=True,no_remote_GPU_or_account_mutation=True),stream,indent=2)
print(json.dumps(dict(new_unused_eighteenth_local_stage=str(N),five_templates_exact=True)))
