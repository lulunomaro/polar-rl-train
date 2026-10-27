"""Prove failed93 argument mismatch, prepare exact unused source fix only."""
from pathlib import Path
import os,sys,ast,json,hashlib,runpy,dataclasses,time
N=Path(__file__).resolve().parent;T=N.parent;B=N/'payloads/h1_210'
F=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPMIMIC_REPAIR_UNUSED'  # overwritten below; no directory action.
F=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/native94_saved_learning_seed_split_source_v1'
F.mkdir(exist_ok=False);os.environ['CUDA_VISIBLE_DEVICES']=''
sys.path[:0]=[str(B/'source'),str(B/'source/sm_deps')]
from supermimic_wheel_leg_v3.learner import SuperMimicConfig
entry=B/'source/native_flat5cm_training_entry_candidate_v4_typed_producer.py';raw=entry.read_bytes();tree=ast.parse(raw)
fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='config_for');ns={'SuperMimicConfig':SuperMimicConfig};exec(compile(ast.Module(body=[fn],type_ignores=[]),'actual_config_for_source_fixture','exec'),ns)
saved=runpy.run_path(str(B/'source/native91_terminal93_pins_v1.py'))['SOURCE_PINS']['native_args']
physical27=dataclasses.asdict(ns['config_for'](27));physical28=dataclasses.asdict(ns['config_for'](28))
assert physical27==saved
diff={k:dict(saved=saved[k],failed_runtime=physical28[k]) for k in saved if saved[k]!=physical28[k]};assert diff=={'seed':dict(saved=27,failed_runtime=28)}
text=raw.decode('utf8');needle="config_for(int(task['native_seed']))";assert text.count(needle)==2
selected=text.replace(needle,"config_for(int(task['native_learning_seed']))")
producer="goal_encoding_changed_from90B=True,goal_conditioning=task['goal_conditioning'],";assert selected.count(producer)==1
selected=selected.replace(producer,producer+"\n        native_learning_seed=task['native_learning_seed'],fresh_environment_initial_seed=task['native_seed'],",1)
(F/entry.name).write_text(selected,'utf8')
mig=B/'source/native88C_to_flat_migration_v1.py';mraw=mig.read_bytes();s=mraw.decode('utf8');needle="source=validate_role_source(key,task['source_SHA'],task['source_progress'])";assert s.count(needle)==1
s=s.replace(needle,needle+"\n require(task.get('native_learning_seed')==SOURCE_PINS['native_args']['seed']==27 and go.get('native_learning_seed')==task['native_learning_seed'],'saved native learning config seed remains27, distinct fresh physical seed28')",1)
(F/mig.name).write_text(s,'utf8')
for p in F.glob('*.py'):ast.parse(p.read_bytes())
def functions(data):return {x.name:ast.dump(x,include_attributes=False) for x in ast.walk(ast.parse(data)) if isinstance(x,ast.FunctionDef)}
a,b=functions(mraw),functions(s);assert [k for k in a if a[k]!=b[k]]==['assert_declared_admission']
a,b=functions(raw),functions(selected);assert [k for k in a if a[k]!=b[k]]==['run']
import torch
assert not torch.cuda.is_initialized()
def H(x):return hashlib.sha256(x).hexdigest()
result=dict(passed=True,source_only_not_installed=True,actual93_failed_runtime_exact_difference=diff,saved_config27_literal_equals_qualified_source=True,fix_preserves_full_saved_native_configuration_and_all_restore_guards=True,new_field_required_in_future_Task_GO_sourcecontract_and_producer='native_learning_seed=27',fresh_environment_initial_seed_28_retained=True,no_independent_physical_rng_stream_or_PhysX_resume_claim=True,changed_AST_functions=['run','assert_declared_admission'],source_originals=[dict(path=str(entry),SHA=H(raw)),dict(path=str(mig),SHA=H(mraw))],no_model_load_forward_hash_GPU_physics_remote_or_account_IO=True,not_runtime_fix_or_learning_gain_until_new_source_SDK_and_first_GPU_update=True,actual_failed93_fee_no_refund=True,epoch=time.time())
(F/'SOURCE_CPU_ACTUAL.json').write_text(json.dumps(result,indent=2),'utf8')
(F/'HANDOFF.md').write_text('Frozen source-only repair after actual93 source210 failed before new native policy. Actual saved learner configuration equals config_for(27) exactly; config_for(28) differs only at seed. Physical task seed was28 and was incorrectly reused for native learner configuration. Future new namespace must pin native_learning_seed27 separately in Task/GO/source contract/producer while retaining initial physical seed28. No restore guard is relaxed, source model/norms/three optimizers remain unchanged. Old93 root/once must never be rerun or patched, current healthy c27/E2 remain untouched; next training requires a fresh scheduling boundary and full source admission.\n','utf8')
rows=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p.read_bytes())) for p in sorted(F.iterdir()) if p.is_file()]
(F/'FROZEN_SOURCE_INDEX_ACTUAL.json').write_text(json.dumps(dict(frozen=True,files=rows),indent=2),'utf8')
print(json.dumps(dict(passed=True,actual_runtime_arg_mismatch=diff,source_fix_only=True)))
