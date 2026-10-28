from pathlib import Path
import ast,json,hashlib,time
N=Path(__file__).resolve().parent;R=N/'reports'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
v=json.loads((R/'TWO100_TARGET20_EXACT_QUALIFIED99_PAYLOADS_PREPARED_ACTUAL.json').read_bytes())
saved=R/'target20_pre_final_binding_original_bytes';saved.mkdir()
for mode,row in v['payloads'].items():
 B=Path(row['payload'])
 for rel in ['source/native88C_to_flat_migration_v1.py','source/native_flat5cm_training_entry_candidate_v4_typed_producer.py','FLAT90_SOURCE_CONTRACT_ACTUAL.json','job0/TASK.json','THREE_SLOT_COMPLETE_MANIFEST_V1.json']:
  (saved/(mode+'_'+rel.replace('/','_')+'.txt')).write_bytes((B/rel).read_bytes())
 p=B/'source/native88C_to_flat_migration_v1.py';s=p.read_text();needle="source=validate_role_source(key,task['source_SHA'],task['source_progress'])";assert s.count(needle)==1;s=s.replace(needle,needle+"\n require(task['flat_jump_target_m']==go['flat_jump_target_m']==.20 and task['user_authorized_height_change_5_to20'] and go['user_authorized_height_change_5_to20'],'explicit signed user20cm target')");p.write_text(s,encoding='utf8')
 p=B/'source/native_flat5cm_training_entry_candidate_v4_typed_producer.py';s=p.read_text();needle='flat_counter_installed_before_first_control=True';assert s.count(needle)==1;s=s.replace(needle,"actual_flat_counter_height_m=flat_counter.height_m,flat_goal_height_m=provider.phase.height_m,"+needle);p.write_text(s,encoding='utf8')
 c=json.loads((B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json').read_bytes());c['approved_python']={p.relative_to(B).as_posix():H(p) for p in B.rglob('*.py')};(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json').write_text(json.dumps(c,indent=2),encoding='utf8')
 task=json.loads((B/'job0/TASK.json').read_bytes());task['flat_source_contract_SHA']=H(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json');(B/'job0/TASK.json').write_text(json.dumps(task,indent=2),encoding='utf8')
 m=json.loads((B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())
 for x in m['files']:
  p=B/x['relative']
  if p.suffix.lower() in ('.pt','.pth','.npz','.usd','.usdc','.zip'):continue
  x.update(bytes=p.stat().st_size,SHA=H(p))
 (B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').write_text(json.dumps(m,indent=2),encoding='utf8');row.update(task=task,manifest_SHA=H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),source_contract_SHA=H(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json'))
 for p in B.rglob('*.py'):ast.parse(p.read_bytes())
v.update(epoch=time.time(),prior_prepared_bytes_preserved=str(saved),explicit_signed_height20_and_precontrol_readback_bound=True)
with (R/'TWO100_TARGET20_EXACT_QUALIFIED99_PAYLOADS_PREPARED_V2_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
print(json.dumps(dict(prepared_v2=True,no_GO_or_model_read=True)))
