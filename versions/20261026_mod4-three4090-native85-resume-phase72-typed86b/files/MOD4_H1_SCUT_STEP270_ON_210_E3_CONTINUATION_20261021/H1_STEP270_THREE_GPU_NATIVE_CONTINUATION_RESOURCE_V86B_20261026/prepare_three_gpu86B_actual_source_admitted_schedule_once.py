from pathlib import Path
import hashlib,importlib.util,json,time
N=Path(__file__).resolve().parent;R=N/'reports'
native=json.loads((R/'NATIVE86_TARGET_INSTALLED_SOURCE_SDK_REFERENCE_CPU_FINITE_RETURNED_ACTUAL.json').read_bytes());normal=json.loads((R/'NORMAL86B_BOTH_H1_E3_SOURCE_SDK_CPU_FINITE_RETURNED_ACTUAL.json').read_bytes())
assert native['actual_finite_returned'] and native['actual_source_SDK_CPU'] and normal['actual_finite_returned'] and normal['passed']
base=json.loads((R/'NATIVE86B_FINALIZED_LOCAL_PAYLOAD_V6_SOURCE_PREPARED_ACTUAL.json').read_bytes())
roles={}
for name in ('NORMAL86B_H1_EXISTING_PREPARED_PAYLOAD_LOCAL_METADATA_ACTUAL.json','NORMAL86B_E3_EXACT_PAYLOAD_LOCAL_NONMODEL_V2_SOURCE_PREPARED_ACTUAL.json'):roles.update(json.loads((R/name).read_bytes())['roles'])
specs={'h1':roles['h1']['spec'],'e2':base['spec'],'recovery':roles['recovery']['spec']}
payloads={'h1':roles['h1']['payload'],'e2':base['payload'],'recovery':roles['recovery']['payload']}
roots={'h1':roles['h1']['root'],'e2':base['root'],'recovery':roles['recovery']['root']}
for key,spec in specs.items():
 assert not set(spec).intersection(('token','password','owner_ssh_password'))
 manifest=Path(payloads[key])/'THREE_SLOT_COMPLETE_MANIFEST_V1.json';assert hashlib.sha256(manifest.read_bytes()).hexdigest()==spec['manifest_SHA']
sp=importlib.util.spec_from_file_location('actual_prepared_source_schedule',N/'controllers_v2/mixed86_protocol_v1.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
cfg=dict(experts=specs,deferred_experts=[],scheduling_authority='human_requested_available_experts',authority_generation='MOD4_SINGLE_WRITER72_20261026');assert m.validate_schedule(cfg)
sources={'h1':roles['h1']['source'],'e2':base['native_source'],'recovery':roles['recovery']['source']}
q=dict(epoch=time.time(),passed=True,actual_three_target_source_SDK_CPU_passed=True,preparation_scope='ACTUAL_TARGET_CPU_ADMITTED_NOT_GO',specs=specs,payloads=payloads,roots=roots,sources=sources,owner_root='/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_three_gpu_native_cont_2610v86b/owner',
 owner_script='three_slot_finite_owner_V86_authority72.py',deferred_experts=[],authority_generation=cfg['authority_generation'],scheduling_authority=cfg['scheduling_authority'],closed_balance_snapshot=587957.6840648651,
 source_role_scopes=dict(h1='normal_PPO83B',e2='native_Fudan85_continuation_WM680_Pi58_iteration68',recovery='normal_PPO85M2'),no_native_promotion_to_normal_E2=True,no_actual_GO_yet=True,
 actual_source_ready_envelopes={'h1':normal['results']['h1']['ready_envelope'],'e2':native['ready_envelope'],'recovery':normal['results']['recovery']['ready_envelope']})
with (R/'THREE_GPU86B_SOURCE_ADMITTED_PREPARED_ACTUAL.json').open('x',encoding='utf8') as out:json.dump(q,out,indent=2)
print(json.dumps({'all_three_actual_source_CPU_admitted':True,'roles':q['source_role_scopes'],'GO':False}))
