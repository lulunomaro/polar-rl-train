"""Correct an unused repair template's reference to the actual healthy H1 runtime."""
from pathlib import Path
import ast,hashlib,json,shutil,time,importlib.util
B=Path(__file__).resolve().parent;P=B.parent/'MOD4_SCUT_FUDAN_TENTH_HOUR_20261019';R=B/'reports';F=B/'future_partial_hour_repair_templates';V=B/'future_partial_hour_repair_templates_V2'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not V.exists();shutil.copytree(F,V)
q=V/'prepare_next_three_closed_sources_one_hour_CPU_once.py';s=q.read_text('utf8')
needle="worker=old['specs'][key]['production_script'];oldm=json.loads((prior/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());text=(prior/worker).read_text('utf8');"
replacement="worker=old['specs'][key]['production_script'];binding_prior=(W/'MOD4_SCUT_FUDAN_TENTH_HOUR_20261019/payload/h1') if key=='h1' else prior;oldm=json.loads((binding_prior/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());text=(binding_prior/worker).read_text('utf8');"
assert needle in s;s=s.replace(needle,replacement);ast.parse(s);q.write_text(s,'utf8')
sp=importlib.util.spec_from_file_location('mod4_prepared_binding_normalizer_only',F/'closed_production_continuation_CPU_v2.py');mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod)
name='h1_prelaunch_v2_production_worker_v1.py';healthy=(P/'payload/h1'/name).read_text('utf8');failed=(B/'payload/h1'/name).read_text('utf8');jm=json.loads((P/'payload/h1/THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());km=json.loads((B/'payload/h1/THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());f=json.loads((P/'reports/THREE_HOUR_ALL_CLOSED_FINAL_MODELS_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes())['experts']['h1'];newname='H1_closed_hour'+str(f['updates'])+'.pt'
base=dict(kind='closed_same_backend_production',new_source_filename=newname,Adam=f['all17Adam_after'])
bad=dict(base,previous_source_filename=km['source_filename'],previous_Adam=km['source_Adamstep']);good=dict(base,previous_source_filename=jm['source_filename'],previous_Adam=jm['source_Adamstep'])
new=healthy.replace(jm['source_filename'],newname).replace(str(jm['source_Adamstep']),str(f['all17Adam_after']))
assert ast.dump(ast.parse(new))==ast.dump(ast.parse(failed))
assert ast.dump(ast.parse(healthy))!=ast.dump(ast.parse(mod.normalize_worker(new,bad)))
assert ast.dump(ast.parse(healthy))==ast.dump(ast.parse(mod.normalize_worker(new,good)))
assert 'resource=B/' in s and s.index("for c in C.glob('*.py')")<s.index("resource=B/'three_real_gpu_resource_shared_user_v2.py'")<s.index('m=dict(oldm,source_SHA=')
for p in V.glob('*.py'):ast.parse(p.read_text('utf8'))
out=dict(epoch=time.time(),trial_id='prepared-partial-handoff-H1-healthy-runtime-binding-CPU-review',found_before_remote_or_GPU_attempt=True,original_unused_templates_retained=str(F),corrected_unused_templates=str(V),cause='The retained H1 source is the healthy hour10 final. Its previous_runtime_root is hour10, whose worker originally loaded hour9. The original unused repair preparer normalized against failed hour11 bindings, which would disagree with the healthy runtime worker at target CPU load.',actual_old_binding=dict(source_filename=jm['source_filename'],Adam=jm['source_Adamstep']),actual_new_source=dict(source_filename=newname,SHA=f['final']['SHA'],Adam=f['all17Adam_after']),old_prepared_normalization_mismatch_reproduced_CPU=True,corrected_normalization_matches_healthy_runtime_AST=True,current_worker_new_bytes_unchanged=True,post_controller_copy_sharing_override_retained=True,corrected_preparer=dict(path=str(q),SHA=H(q)),no_live_process_transport_GPU_Task_native_PT_or_account_write=True)
with (R/'PREPARED_H1_HEALTHY_RUNTIME_BINDING_MISMATCH_AND_V2_CPU_ACTUAL.json').open('x',encoding='utf8') as stream:json.dump(out,stream,indent=2)
print(json.dumps(dict(healthy_runtime_AST_binding_corrected=True,templates_V2_only_prepared=True)))
