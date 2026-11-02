"""Purelocalmetadata roleassembler for unconsumed E2/E3 original finite20.
Historical native proof validation only: no checkpoint pathstat/read, SDK or GO.
Role names are data; native0pt/family/interface keys never text-replaced.
"""
from pathlib import Path,PurePosixPath
import json,hashlib
ROLES=('E2','E3')
USD='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3'
CONTRACT='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755'
COLLECTIONS={'E2':'reports/E2_b3_no_update_final_20261102_024838/COLLECTION.json','E3':'reports/E3_1cd_no_update_final_20261102_031620/COLLECTION.json'}

def ref(path,relative=None):
 p=Path(path);assert p.suffix in('.json','.py'), 'Source/metadataonly';raw=p.read_bytes()
 return dict(path=str(p),relative=relative or p.name,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest())

def build_role_spec(role,*,task_root,job_root,run_id):
 assert role in ROLES
 R=Path(task_root);D=R/'POSTTRAIN_EIGHT_EXCLUDING_H1_20261102';S=D/'source_e0_e2_e3';J=PurePosixPath(job_root);assert J.is_absolute()and'..'not in J.parts
 dp=S/(role+'_POSTTRAIN_DESCRIPTOR_SOURCE_ONLY_V1.json');desc=json.loads(dp.read_bytes());pin=desc['pinned_source'];assert desc['expert']==role and desc['num_envs']==20000 and desc['H1_training_enabled']is False
 proof=R/COLLECTIONS[role];raw=proof.read_bytes();c=json.loads(raw);final=c['files']['FINAL.json'];close=c['files']['PARENT_EXIT_SCOPE.json'];assert final['passed']and close['all_own_children_waited']and not close['errors']
 joined=[r for r in final['rows']if(r.get('data')or{}).get('source_SHA')==pin['source_SHA']];assert len(joined)==1
 row=joined[0];n=row['data'];assert row['returncode']==0 and row['actual_waited']and n['passed']and n['execution_scope']=='EVAL_ONLY_NO_OPTIMIZER'
 assert n['num_envs']==20000 and n['controls']==24 and n['physics_callbacks']==192 and n['feedback_samples']==48
 assert n['source_iteration']==pin['source_iteration']and n['source_Adam17']==pin['source_Adam_step']and n['source_LR']==pin['source_LR']
 assert n['core_actor_critic_STD17Adam_before_after_exact']and n['source_iteration_and_LR_unchanged']and n['one_original_fresh_reset']==1
 assert all(n['forbidden_calls'][k]==0 for k in('alg_update','optimizer_step','runner_learn'))
 g=n['new_nominal_guard'];assert g['usd_sha256']==USD and g['contract_sha256']==CONTRACT and g['num_envs']==20000 and g['original_fresh_reset_calls']==1
 assert g['new_constructor_nominal_caches_preserved']and g['fresh_D0_mass_inertia_based_on_new_asset']and g['observation_shapes_checked']
 assert g['closure_episode_m']==.01 and g['mimic_rad']==.01
 proofref=dict(path=str(proof),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),relative='evidence/ORIGINAL_EXACT_SOURCE_FULL20K_RAW.json')
 historical=dict(kind='EXACT_HISTORICAL_NATIVE20K_REFERENCE_NOT_NEWTRAINING_READY',actual_not_mock=True,source_SHA=pin['source_SHA'],asset_USD_SHA=USD,asset_contract_SHA=CONTRACT,num_envs=20000,whole_state_restore_passed=True,all_own_children_waited=True,one_original_reset=1,zero_original_optimizer_updates=True,raw_reference=proofref['relative'],raw_SHA=proofref['SHA'],historical_reference_not_newtrainingpass=True)
 runtime=[ref(S/n)for n in('posttrain_fullstate_common_v1.py','worker_posttrain_'+role.lower()+'_v1.py',role+'_POSTTRAIN_DESCRIPTOR_SOURCE_ONLY_V1.json','construct_source_task_go_v1.py')]
 seal=Path(desc['exact_sealed_overlay']);required=[]
 for name in('MOD4V1_ASSET_DIFF.json','MOD4V1_DERIVATION_INDEX.json'):
  f=ref(seal/name);runtime.append(f);required.append(dict(relative=name,SHA=f['SHA']))
 required.append(dict(relative='original_run_manifest.json',SHA=pin['original_manifest_SHA']))
 source=dict(path=pin['model_path'],SHA=pin['source_SHA'],bytes=pin['source_bytes'],iteration=pin['source_iteration'],Adam17=pin['source_Adam_step'],LR=pin['source_LR'])
 return dict(role=role,source_family='e0_e2_e3',source_pin=source,source_model_metadata=source,base_root=desc['historical_actual_full20k_stage_without_models'],job_root=str(J),run_id=run_id,runtime_source_files=runtime,required_immutable_files=required,historical_raw_proof=proofref,normalized_proof=historical,task_template={},go_template={},worker_argv=['{JOB}/worker_posttrain_'+role.lower()+'_v1.py','--mode','train','--num-envs','20000','--run-id','{RUN}','--out','{JOB}/production'],final_file='production/FINAL.json',stop_relative='production/STOP_AFTER_SAVE.json',final_updates_key='actual_new_PPO_updates',task_kind=pin['original_kind'],seed=20260928,source_only_no_Task_GO_or_Ready=True)
