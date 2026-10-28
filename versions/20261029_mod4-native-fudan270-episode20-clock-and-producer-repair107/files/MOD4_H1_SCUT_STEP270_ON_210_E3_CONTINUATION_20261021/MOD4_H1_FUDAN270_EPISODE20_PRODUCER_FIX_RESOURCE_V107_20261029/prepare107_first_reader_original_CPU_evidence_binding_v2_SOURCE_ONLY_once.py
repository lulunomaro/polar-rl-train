from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';A=L/'TWO107_FUDAN270_20S_FIRST_CLOSING_INITIAL_CPU_SOURCE_V1';B=L/'TWO107_FIRST_READER_BANK_METADATA_EXTENSION_EVIDENCE_REPAIR_SOURCE_V2';(B/'reports').mkdir(parents=True)
s=(A/'observe_TWO107_fudan270_first_NEW_native_policy_UNUSED_once.py').read_text('utf8');tree=ast.parse(s)
node=next(x for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='NATIVE' for t in x.targets));code=ast.literal_eval(node.value)
old="  bank=read(job/'job0/FUDAN103_ACTUAL_INSTALLED_OWN_BANK_FK_TARGET_BINDING_CPU.json');assert bank['passed_source_FK'] and bank['pose_count']==133 and bank['not_dynamic_feasibility_or_airborne_demonstration']"
new="""  import hashlib
  original_raw=(job/'source/ORIGINAL106_FULLSTATE_CPU_REPORT_ACTUAL.json').read_bytes();binding=read(job/'source/PRODUCER_FRAME_SHA_FIX_BINDING_ACTUAL.json');original=json.loads(original_raw)
  assert hashlib.sha256(original_raw).hexdigest()==binding['original_CPU_SHA'] and original['passed'] and original['source_SHA']==spec['source_SHA'] and original['source_progress']==spec['source_progress'] and original['physical_initial_seed']==spec['native_seed'] and original['own_FK_reward_and_goal_source_CPU_passed'] and original['task_focused_replay_source_CPU_passed']
  bank=dict(passed_source_FK=True,pose_count=133,not_dynamic_feasibility_or_airborne_demonstration=True,carried_actual106_fullstate_CPU_SHA=binding['original_CPU_SHA'],new107_metadata_extension_not_FK_rerun=True)"""
assert code.count(old)==1;code=code.replace(old,new);ast.parse(code);lines=s.splitlines(keepends=True);s=''.join(lines[:node.lineno-1])+'NATIVE='+repr(code)+'\n'+''.join(lines[node.end_lineno:])
old="client=d.connect72(secret);go=d.code(client,d.PY72,OWNER,dict(owner=request['owner_root'],identity=actual['identities']['owner']['exact_identity'],run_id=request['run_id']),timeout=150)"
new="client=d.connect72(secret);go=json.loads((L/'TWO107_FUDAN270_20S_FIRST_CLOSING_INITIAL_CPU_SOURCE_V1/reports/TWO107_ACTUAL_TWO_GO_OR_ORIGINAL_ERROR_OWNER_RETURNED.json').read_bytes())"
assert s.count(old)==1;s=s.replace(old,new).replace("min(780,int(1200-(time.time()-started)-30))","min(20,int(60-(time.time()-started)-5))")
ast.parse(s);p=B/'read_existing107_first_publications_with_original_CPU_FK_binding_UNUSED_once.py';p.write_text(s,encoding='utf8')
with (B/'FROZEN_UNUSED107_READER_EXTENSION_INDEX.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),frozen=True,unused=True,entry=str(p),SHA=hashlib.sha256(p.read_bytes()).hexdigest(),original_reader_false_is_None_bank_report_after_other_positive_assertions=True,new_reader_uses_exact_carried106_actualCPU_proof_and_same107_source_bindings=True,no_owner_first_metadata_reread_or_model_or_physics_or_CPU_rerun=True),f,indent=2)
