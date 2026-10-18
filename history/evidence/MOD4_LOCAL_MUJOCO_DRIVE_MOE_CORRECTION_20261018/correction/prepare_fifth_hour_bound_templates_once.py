from pathlib import Path
import ast,json,time
W=Path(__file__).resolve().parent.parent
F=W/'MOD4_THREE_GPU_HOUR4_CONTINUATION_20261018'
G=W/'MOD4_THREE_GPU_HOUR5_CONTINUATION_20261018'
assert not G.exists()
G.mkdir();(G/'reports').mkdir()
def write(n,s):
    ast.parse(s)
    with (G/n).open('x',encoding='utf-8') as f:f.write(s)
write('closed_production_continuation_CPU_v2.py',(F/'closed_production_continuation_CPU_v2.py').read_text('utf-8'))
s=(F/'prepare_next_three_closed_sources_one_hour_CPU_once.py').read_text('utf-8').replace("T=W/'MOD4_THREE_GPU_HOUR3_CONTINUATION_20261018'","T=W/'MOD4_THREE_GPU_HOUR4_CONTINUATION_20261018'").replace('T3h4_1810v4/','T3h5_1810v5/').replace('THREE_GPU_CLOSED_HOUR4_','THREE_GPU_CLOSED_HOUR5_')
write('prepare_next_three_closed_sources_one_hour_CPU_once.py',s)
s=(F/'deploy_three_next_closed_source_hours_once.py').read_text('utf-8').replace("SOURCE='/mnt/mod4_linux_durable_20261013/T3h4_1810v4/owner'","SOURCE='/mnt/mod4_linux_durable_20261013/T3h5_1810v5/owner'").replace("A=Path('/mnt/mod4_linux_durable_20261013/T3h3_1810v3/owner')","A=Path('/mnt/mod4_linux_durable_20261013/T3h4_1810v4/owner')").replace('162530','174112')
write('deploy_three_next_closed_source_hours_once.py',s)
write('collect_next_three_actual_learning_metadata_finite_once.py',(F/'collect_next_three_actual_learning_metadata_finite_once.py').read_text('utf-8'))
(G/'reports/FIFTH_HOUR_BOUND_TEMPLATES_AST_ACTUAL.json').write_text(json.dumps(dict(epoch=time.time(),previous_actual_owner=174112,actual_fourth_hour_final_CPU_required=True,only_namespace_source_filename_Adam_bindings_changed=True,no_new_math_physics_or_budget=True),indent=2),encoding='utf-8')
print(G)
