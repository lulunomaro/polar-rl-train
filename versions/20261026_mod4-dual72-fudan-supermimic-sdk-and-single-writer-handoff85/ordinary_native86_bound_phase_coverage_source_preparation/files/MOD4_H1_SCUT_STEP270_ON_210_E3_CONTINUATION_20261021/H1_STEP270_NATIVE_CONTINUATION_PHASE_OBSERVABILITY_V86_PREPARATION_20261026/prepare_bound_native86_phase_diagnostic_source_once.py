"""New source-only bundle: qualified85 native lineage + optional Pi phase counts."""
from pathlib import Path
import ast,hashlib,importlib.util,json,shutil,time,traceback
F=Path(__file__).resolve().parent;T=F.parent;J=T/'MOD4_UNISUPERMIMIC_FUDAN_JUMP_REFERENCE_TRANSFER_20261026';N=T/'H1_STEP270_DUAL72_FUDAN_SUPERMIMIC_E3_MIGRATED_V85M2_20261026';R=F/'reports';R.mkdir(exist_ok=True)

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(name,value):
 with (R/name).open('x',encoding='utf8') as out:json.dump(value,out,ensure_ascii=False,indent=2)

def main():
 assert not (F/'NATIVE_CONTINUATION_BINDING_ACTUAL.json').exists()
 C=J/'agent_native_Fudan_continuation86_cpu'
 assert sha(C/'h1_supermimic_bridge_continuation86_candidate.py')=='538012ae49154e0e05e940bbcb9f1881b1efe87bd2af917149dbe7587b2b6a1f'
 assert sha(C/'native_continuation_v1.py')=='bea3228562e517f2c652c5e3b134a46912287f57b3007d82310d0c1d17d4edb9'
 shutil.copyfile(C/'native_continuation_v1.py',F/'source/native_continuation_v1.py')
 original=(C/'h1_supermimic_bridge_continuation86_candidate.py').read_bytes().decode('utf8')
 anchor="    put(out / 'NATIVE_CONTINUATION_STARTUP_ACTUAL.json', restore_receipt)\n"
 extra="    from native_policy_phase_coverage_v1 import attach_optional_policy_phase_coverage\n    bridge.phase_sampling_diagnostic = attach_optional_policy_phase_coverage(learner, out / 'NATIVE_POLICY_PHASE_SAMPLE_COVERAGE_ACTUAL.json')\n"
 assert original.count(anchor)==1
 changed=original.replace(anchor,anchor+extra)
 target=F/'source/h1_supermimic_bridge_native86_with_phase_sampling.py';target.write_bytes(changed.encode('utf8'))
 tree=ast.parse(changed);base=ast.parse(original)
 run=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='run')
 added=[];kept=[]
 for node in run.body:
  if isinstance(node,ast.ImportFrom) and node.module=='native_policy_phase_coverage_v1':added.append(node)
  elif isinstance(node,ast.Assign) and isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Name) and node.value.func.id=='attach_optional_policy_phase_coverage':added.append(node)
  else:kept.append(node)
 assert len(added)==2
 run.body=kept
 assert ast.dump(tree,include_attributes=False)==ast.dump(base,include_attributes=False)
 metadata=F/'native_source_metadata';metadata.mkdir()
 paths=dict(final=N/'current_three_closed_text/e2/job0/production/FINAL.json',
 full_cpu=N/'reports/V85M2_SINGLE72_NATIVE_E3_AND_ACTUAL_COST_CPU_ACTUAL.json',
 collector=N/'reports/V85M2_SINGLE72_NATIVE_E3_AND_ACTUAL_COST_RETURNED_ACTUAL.json',
 runtime_order=N/'current_three_closed_text/e2/job0/production/NATIVE_FUDAN_REFERENCE_RUNTIME_ORDER_ACTUAL.json')
 b=json.loads((C/'NATIVE_CONTINUATION_BINDING_PENDING_TEMPLATE.json').read_bytes())
 for key,path in paths.items():
  dst=F/b['metadata'][key]['relative'];shutil.copyfile(path,dst)
  pin={'final':'FINAL_metadata_SHA','full_cpu':'full_CPU_report_SHA','collector':'collector_report_SHA','runtime_order':'runtime_order_metadata_SHA'}[key]
  b[pin]=sha(dst)
 final=json.loads(paths['final'].read_bytes());cpu=json.loads(paths['full_cpu'].read_bytes());order=json.loads(paths['runtime_order'].read_bytes())
 pub=final['final'];assert pub['SHA']=='94e7f272176b4a7c485b50c1ac61f95a3ecd4460ee6a73034f9e7a47a57045af'
 assert cpu['passed'] and cpu['remaining_actual_snapshot']==587957.6840648651
 b.update(status='ACTUAL_CLOSED_CPU_QUALIFIED',source_run_id=order['original_run_id'],checkpoint_SHA=pub['SHA'],producer=pub['producer'],actual_qualified=True,
          not_TASK_GO_or_source_admission=True,integration_note='This binds qualified85 source evidence only. No86 target SDK/readback/controller/payload/GO exists; actual new target checks remain mandatory.')
 (F/'NATIVE_CONTINUATION_BINDING_ACTUAL.json').write_text(json.dumps(b,ensure_ascii=False,indent=2),'utf8')
 # Only pure metadata admission is exercised, using saved85 runtime evidence as
 # an explicit same-order CPU fixture. It is not a fresh86 SDK/readback.
 spec=importlib.util.spec_from_file_location('bound_native86_source',F/'source/native_continuation_v1.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 bound,records=m.read_pinned_metadata_bundle(F/'NATIVE_CONTINUATION_BINDING_ACTUAL.json')
 objective=json.loads((N/'current_three_closed_text/e2/job0/production/NATIVE_FUDAN_REFERENCE_OBJECTIVE_CONTRACT_ACTUAL.json').read_bytes())
 admitted=m.admit_closed_source(bound,**records,current_runtime_order=records['runtime_order'],current_runtime_objective=objective)
 assert admitted['admitted'] and admitted['checkpoint_SHA']==pub['SHA']
 put('CLOSED85_NATIVE_METADATA_BINDING_SOURCE_ONLY_CPU_ACTUAL.json',dict(epoch=time.time(),closed85_metadata_compatible=True,fixture_current_order_is_saved85_not_actual86_readback=True,
     actual86_target_SDK_or_admission=False,no_PT_hash_load_copy=True,no_controller_payload_Task_GO_or_fee=True,source=pub['SHA'],original_cost=cpu['actual_cost_sumonce'],closed_balance=cpu['remaining_actual_snapshot'],binding_SHA=sha(F/'NATIVE_CONTINUATION_BINDING_ACTUAL.json'),
     source_AST_only_optional_import_and_attach=True,added_AST_nodes=2,physical_reward_actions_original_learner_configuration_and_native_restore_unchanged=True,
     E3_latest_source=cpu['models']['recovery']['final'],H1_PPO_and_normalE2_latest='qualified83B, no native promotion'))
 files=[p for p in F.rglob('*') if p.is_file() and p.suffix.lower() in ('.py','.json')]
 put('SOURCE_ONLY_NATIVE86_BOUND_PHASE_MODULE_MANIFEST_ACTUAL.json',dict(epoch=time.time(),files=[dict(path=str(p),bytes=p.stat().st_size,SHA=sha(p)) for p in sorted(files)],
     frozen_source_only=False,training_ready=False,need_actual_installed_SDK_fullsource_CPU_resources_account_and_controller_protocol=True))
 print(json.dumps({'passed':True,'source_only':True,'binding_SHA':sha(F/'NATIVE_CONTINUATION_BINDING_ACTUAL.json'),'bridge_SHA':sha(target),'no86_GO':True}))

if __name__=='__main__':
 try:main()
 except BaseException:
  put('ORIGINAL_SOURCE_BINDING_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_runtime_or_model_or_budget_change=True));raise
