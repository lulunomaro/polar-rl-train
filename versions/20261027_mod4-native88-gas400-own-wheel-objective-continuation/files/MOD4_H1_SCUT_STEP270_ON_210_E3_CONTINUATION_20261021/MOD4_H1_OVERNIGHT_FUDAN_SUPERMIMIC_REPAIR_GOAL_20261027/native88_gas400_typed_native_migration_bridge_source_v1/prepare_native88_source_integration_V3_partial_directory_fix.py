"""NEW source-only exact derivation; no assets, model, Task/GO or SDK execution."""
from pathlib import Path
import ast,hashlib,json,sys,traceback
HERE=Path(__file__).resolve().parent;L=HERE.parent;T=L.parent;N=T/'H1_STEP270_THREE_GPU_OWN_FUDAN_NATIVE_V87_20261027';B=N/'payloads_r5/h1';SRC=B/'source'
PRIMITIVE=L/'native87_same_architecture_continuation_preparation_v1/same_architecture_native_continuation_candidate_v1.py'
GAS=L/'HARDWARE_GAS_SPRING_400N_L200_S60_HUMAN_20261027/agent_nominal400_target_source_candidate_v1'
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(name,value):
 with (HERE/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2,allow_nan=False)
def copy_source(source,relative):
 raw=source.read_bytes();p=HERE/relative;p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():assert p.read_bytes()==raw,'existing partial source differs'
 else:
  with p.open('xb') as f:f.write(raw)
 return dict(source=str(source),relative=relative,bytes=len(raw),old_SHA=H(source),new_SHA=H(p),byteexact=True)
def write_new_or_verify(p,text):
 raw=text.encode('utf8')
 if p.exists():assert p.read_bytes()==raw,'partial generated source changed'
 else:
  with p.open('xb') as f:f.write(raw)
def replace(text,old,new):
 assert text.count(old)==1,repr(old);return text.replace(old,new,1)
put('V3_ENTRY_CONSUMED_SOURCE_ONLY_ACTUAL.json',dict(new_purpose='native88 nominal400 typed R5 restore/world-adaptation/publisher bridge source',no_model_or_asset_or_runtime=True))
try:
 rows=[copy_source(PRIMITIVE,'same_architecture_native_continuation_candidate_v1.py'),copy_source(GAS/'gas400_sdk_admission_candidate_v1.py','gas400_sdk_admission_candidate_v1.py'),copy_source(GAS/'gas400_source_patcher_v1.py','gas400_source_patcher_v1.py'),copy_source(SRC/'native_wheel_leg_bridge_v4.py','native_wheel_leg_bridge_v4.py')]
 # The vendor train's only semantic change is its policy-phase predicate.
 p=SRC/'supermimic_wheel_leg_v3/learner.py';old=p.read_text('utf8');text=replace(old,'if iteration >= self.cfg.wm_only_iters:','if self.native88_migration.allow_policy_update(iteration):')
 dst=HERE/'vendor_candidate/supermimic_wheel_leg_v3/learner.py';dst.parent.mkdir(parents=True,exist_ok=True);write_new_or_verify(dst,text)
 rows.append(dict(source=str(p),relative=dst.relative_to(HERE).as_posix(),old_SHA=H(p),new_SHA=H(dst),semantic_change='only policy-phase predicate; globalLR/sampler/loss/collect/warmup/checkpoint bodies unchanged'))
 # New finalization retains original lifecycle/error/fullsave body and adds
 # window metadata inside the atomic stage before verify/hash/publication.
 p=SRC/'native_finalization_own_v3.py';old=p.read_text('utf8');tree=ast.parse(old);assign=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='NATIVE_CONTRACT' for t in n.targets));lines=old.splitlines(keepends=True)
 text=''.join(lines[:assign.lineno-1])+'from native88_gas400_migration_v1 import NATIVE_CONTRACT,verify_saved_migration\n'+''.join(lines[assign.end_lineno:])
 text=replace(text,'    assert_finite(checkpoint)\n','    assert_finite(checkpoint)\n    verify_saved_migration(checkpoint, expected)\n')
 text=replace(text,"            state['UniSuperMimic_H1_test'] = self.learner._checkpoint(True)","            expected['native88_migration_window'] = self.bridge.native88_migration.snapshot()\n            state['UniSuperMimic_changed_plant_migration'] = expected['native88_migration_window']\n            state['UniSuperMimic_H1_test'] = self.learner._checkpoint(True)")
 text=replace(text,"policy_updates=expected['policy_updates'],\n                not_production_H1_or_E2_source=True,","policy_updates=expected['policy_updates'],\n                native88_migration_window=expected['native88_migration_window'],\n                not_production_H1_or_E2_source=True,")
 dst=HERE/'native_finalization_own88_gas400.py';write_new_or_verify(dst,text);rows.append(dict(source=str(p),relative=dst.name,old_SHA=H(p),new_SHA=H(dst),semantic_change='new typed contract and save-window fields/verification; lifecycle/fullsave/error paths retained'))
 # Entry remains original control/trace/publisher/lifecycle flow, with explicit
 # native-source guard, new plant check, restore before train and window gates.
 p=SRC/'native_own_fudan87_training.py';text=p.read_text('utf8')
 text=replace(text,'from fresh_policy_only_bootstrap87_v1 import BOOTSTRAP_SHA,BOOTSTRAP_ADAM,verify_loaded_policy_only_fresh_environment','from native88_gas400_migration_v1 import (assert_declared_admission,verify_loaded_frozen_RSL_fresh_plant,install_restored_window,observe_first_original_preload_write,RequireNewWindowFinal)\nfrom gas400_sdk_admission_candidate_v1 import check_actual_new_gas\nfrom actual_DR_memory_getter_v1 import tensor\nfrom dataclasses import asdict\nBOOTSTRAP_SHA="0c1edb9603c1cb84fbb894d242dae1b6a7c87fe3237d658dbc486ccbbad3d394"\nBOOTSTRAP_ADAM=832460')
 text=replace(text,'from native_finalization_own_v3 import NativeCheckpointPublisher,run_native_lifecycle,source_sha,atomic_json','from native_finalization_own88_gas400 import NativeCheckpointPublisher,run_native_lifecycle,source_sha,atomic_json')
 start="    if phase!='production' or task['source_SHA']!=BOOTSTRAP_SHA or go['source_SHA']!=BOOTSTRAP_SHA:\n        raise ValueError('exact new method bootstrap Task/GO binding required')\n    if go['source_qualification_kind']!='MOD4_H1_NATIVE87_POLICY_ONLY_SOURCE_SDK_CPU_PRECONTROL_V2':\n        raise ValueError('typed source CPU vs actual GPU precontrol scope required')"
 text=replace(text,start,"    if phase!='production':raise ValueError('production changed-plant source scope required')\n    native_source=assert_declared_admission(task['key'],task,go)")
 oldline=next(line for line in text.splitlines() if line.startswith('    if H(src)!=BOOTSTRAP_SHA:'))
 text=replace(text,oldline,"    if H(src)!=native_source['SHA']:raise ValueError('actual qualified R5 native source differs')")
 text=replace(text,'    bootstrap=verify_loaded_policy_only_fresh_environment(runner,env,source)\n    del source','    bootstrap=verify_loaded_frozen_RSL_fresh_plant(runner,env,source)')
 text=replace(text,"        if publication is not None and publication['policy_updates']>0 and trace.source_models:","        if publication is not None and trace.source_models and holder['window'].qualifies_preupdate(publication,trace.source_models[-1]):")
 text=replace(text,"    holder={'bridge':None,'learner':None,'publisher':None,'curve_iteration':None}","    holder={'bridge':None,'learner':None,'publisher':None,'curve_iteration':None,'window':None}")
 text=replace(text,"                not_frozen_evaluation_or_causal_PPO_comparison=True)","                native88_migration_window=holder['window'].snapshot(),\n                not_frozen_evaluation_or_causal_PPO_comparison=True)")
 text=replace(text,"    holder['learner']=learner;bridge.learner=learner", "    holder['learner']=learner;bridge.learner=learner\n    gas400_admission=check_actual_new_gas(env,expected_joint_names=names,tensor=tensor)\n    window,restore_proof=install_restored_window(learner,bridge,trace,source,key=task['key'],source_SHA=task['source_SHA'],\n        expected_source_contract=task['source_native_contract'],expected_args=asdict(config_for(int(task['native_seed']))),\n        parameter_contract_SHA=task['gas400_parameter_source_contract_SHA'],asset_report_SHA=task['actual_gas400_asset_composition_report_SHA'])\n    holder['window']=window;del source\n    atomic_json(out/'NATIVE88_RESTORED_SOURCE_AND_CHANGED_PLANT_WINDOW_START_ACTUAL.json',dict(restore=restore_proof,actual_new_gas_parameters=gas400_admission,window=window.snapshot()))\n    observe_first_original_preload_write(env,window,expected_joint_names=names,\n        emit=lambda value:atomic_json(out/'NATIVE88_FIRST_ORIGINAL_PRELOAD_PREWRITE_ACTUAL.json',value))")
 text=replace(text,"        original_true_physical_success_unchanged=True,new_native_model_initialization=True,", "        original_true_physical_success_unchanged=True,new_native_model_initialization=False,\n        native88_changed_plant_source_restore=restore_proof,actual_new_gas_parameters=gas400_admission,")
 text=replace(text,"        reference_artifact_SHA=task['native_reference_SHA'],method='MOD4_own_Fudan_native_v3',", "        reference_artifact_SHA=task['native_reference_SHA'],method='MOD4_own_Fudan_native88_nominal400_changed_plant',\n        initial_native_source=window.source,gas400_parameter_source_contract_SHA=window.parameter_contract_SHA,\n        actual_gas400_asset_composition_report_SHA=window.asset_report_SHA,")
 text=replace(text,'        native_architecture_fresh=True,original_source_cost_and_physical_save_chain_preserved=True,','        native_architecture_fresh=False,original_source_cost_and_physical_save_chain_preserved=True,')
 text=replace(text,"        bridge.wm_updates+=1;bridge.last_wm=[float(x) for x in value]", "        bridge.wm_updates+=1;window.completed_world_update();bridge.last_wm=[float(x) for x in value]")
 text=replace(text,'    def pi_update():\n        value=original_pi()', '    def pi_update():\n        window.before_policy_update()\n        value=original_pi()')
 text=replace(text,"        bridge.pi_updates+=1;bridge.last_pi=[float(x) for x in value]", "        bridge.pi_updates+=1;window.completed_policy_update();bridge.last_pi=[float(x) for x in value]")
 text=replace(text,'persist_trace=trace.persist,save=publisher,out=out,','persist_trace=trace.persist,save=RequireNewWindowFinal(publisher),out=out,')
 dst=HERE/'native_own_fudan88_gas400_training.py';write_new_or_verify(dst,text);rows.append(dict(source=str(p),relative=dst.name,old_SHA=H(p),new_SHA=H(dst),semantic_change='typed R5 source restore/new gas check/window-first positive and final gating; original controls/loss/reward/lifecycle unchanged'))
 for p in HERE.rglob('*.py'):ast.parse(p.read_bytes())
 put('SOURCE_DERIVATION_LINEAGE_NOT_ADMITTED.json',dict(source_only=True,rows=rows,source_models_never_read=True,actual_asset_SDK_and_source_admission_pending=True,no_Task_GO_payload_controller_created=True))
 print(json.dumps(dict(prepared=True,files=len(rows),actual_model_or_asset_read=False)))
except BaseException:
 put('V3_ORIGINAL_NATIVE88_SOURCE_PREPARATION_ERROR_ACTUAL.json',dict(error=traceback.format_exc(),partial_sources_preserved=True,no_models_or_assets_touched=True));raise
