"""New E3-only continuation branch. Sources/metadata staging only; no PT/SDK/GO/C writes."""
from pathlib import Path
import ast,json,sys,time,hashlib,shlex,pprint
D=Path(__file__).resolve().parent;T=D.parent/'mod4v1_experts_fulldr_rm70_20261101';P=T/'POSTTRAIN_EIGHT_EXCLUDING_H1_20261102';S=P/'source_e0_e2_e3';H=lambda b:hashlib.sha256(b).hexdigest();assert not(D/'STAGE_ONCE.json').exists()
summary=json.loads((P/'reports/PAIR3_GENERIC_V2_ACTUAL_FULLSTATE_TRAINING_CLOSED_SUMMARY_V1.json').read_bytes());old=json.loads((P/'reports/PAIR3_GENERIC_V2_TRAIN_CLOSED_20261102_142813/roles/E3/production/FINAL.json').read_bytes());f=old['final'];assert old['passed_execution']and old['actual_new_PPO_updates']==20 and f['SHA']=='67ee37cf39a9b82f7e45eab68f2fa0e46bd0eec95ffbe063bedfd7bfe810d81a'and f['saved_iteration']==43110 and f['saved_17Adam']==[866460]and f['full_live_core_STD_optimizer_DR_history_RNG_queue_verified']and summary['original_actual_cost_settled']and summary['original_leases_released']and not summary['parent_errors']
run='MOD4V1_E3_PPO_CONTINUE67EE_W1_'+time.strftime('%Y%m%d_%H%M%S')+'_'+str(time.time_ns());root='/home/lc01/Zonglin Li/zonglin2/tasks/'+run;job=root+'/roles/E3';payload=D/'payload';payload.mkdir();(payload/'uploads/E3/evidence').mkdir(parents=True);u=payload/'uploads/E3'
def save(p,b):
 p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists();p.write_bytes(b)
def cp(a,b,expected=None):
 a=Path(a);assert a.suffix.lower()not in('.pt','.pth','.ckpt','.onnx','.safetensors','.npz','.npy');v=a.read_bytes();assert expected is None or H(v)==expected;save(b,v)
def put(p,v):save(p,json.dumps(v,indent=2,allow_nan=False).encode())
base=P/'parent_source/original_budget_and_asset_refs'
for name in('three_slot_common_v1.py','single_writer72_authority_V85M_source.py'):cp(base/name,payload/name)
owner=(P/'parent_source/eight_posttrain_original_owner_v1.py').read_text(encoding='utf8');line="UUIDS=('GPU-16828f91-2b45-b646-8dc0-9481138e2842','GPU-c27eecbd-6838-7290-1cd2-37e34522213d')";assert owner.count(line)==1;owner=owner.replace(line,"UUIDS=('GPU-16828f91-2b45-b646-8dc0-9481138e2842',)")
gate="proof['whole_state_restore_passed']and proof['all_own_children_waited']";assert owner.count(gate)==1
owner=owner.replace(gate,"proof['producer_input_whole20k_restore_passed']and proof['candidate_full_live20k_save_verified']and proof['producer_actual_PPO_updates']==20 and proof['producer_saved_17Adam']==[866460]and proof['all_own_children_waited']")
owner=owner.replace('Actual same frozen source full20k restored proof reuse','Actual complete20k GPU producer-save history; fresh candidate fullrestore still mandatory in worker')
save(payload/'eight_posttrain_original_owner_v1.py',owner.encode())
stager=(P/'parent_source/stage_generic_nonpt_roles_v2.py').read_text(encoding='utf8');a="len(P['entries'])==2 and len({e['role']for e in P['entries']})==2";assert stager.count(a)==1;stager=stager.replace(a,"len(P['entries'])==1 and len({e['role']for e in P['entries']})==1");save(payload/'stage_e3_continuation_nonpt.py',stager.encode())
common=(S/'posttrain_fullstate_common_v1.py').read_text(encoding='utf8');tree=ast.parse(common);node=next(n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='EXPERTS'for t in n.targets));ns={};exec(compile(ast.Module(body=[node],type_ignores=[]),'<source-data>','exec'),ns);cfg=ns['EXPERTS']['E3'];cfg.update(source_SHA=f['SHA'],source_bytes=f['bytes'],source_iteration=f['saved_iteration'],source_Adam_step=866460,source_LR=f['actual_saved_LR'],source_prior_new_PPO_updates=107,model_path=f['path'],original_kind='MOD4V1_E3_FULLD0D7_RECOVERY13_CONTINUE43110_V1');lines=common.splitlines(keepends=True);newassign='EXPERTS = '+pprint.pformat(ns['EXPERTS'],sort_dicts=False,width=115)+'\n';derived=''.join(lines[:node.lineno-1])+newassign+''.join(lines[node.end_lineno:]);save(u/'posttrain_fullstate_common_v1.py',derived.encode())
# All training/restoration/save/resource functions stay byte-for-byte identical.
def funcs(text):
 tr=ast.parse(text);ln=text.splitlines(keepends=True);return{n.name:''.join(ln[n.lineno-1:n.end_lineno])for n in tr.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
assert funcs(common)==funcs(derived)
for name in('worker_posttrain_e3_v1.py','construct_source_task_go_v1.py'):cp(S/name,u/name)
des=json.loads((S/'E3_POSTTRAIN_DESCRIPTOR_SOURCE_ONLY_V1.json').read_bytes());des['pinned_source']=cfg;des['continuation_note']='67ee actual full20k GPU saved candidate, not previously reloaded as a candidate; worker must freshly restore/verify all state before PPO. Current1cd selected mother remains unchanged.';put(u/'E3_POSTTRAIN_DESCRIPTOR_SOURCE_ONLY_V1.json',des)
spec=next(x for x in json.loads((P/'parent_source/E2_E3_VALIDATED_ROLE_SPECS_V2.json').read_bytes())['rows']if x['role']=='E3')
for r in spec['runtime_source_files']:
 if r['relative']in('MOD4V1_ASSET_DIFF.json','MOD4V1_DERIVATION_INDEX.json'):cp(r['path'],u/r['relative'],r['SHA'])
for name in('NEW_ASSET_NATIVE_ACTUAL.json','RM70_SCOPE_REUSE_ACTUAL.json'):cp(base/'evidence'/name,u/'evidence'/name)
cp(P/'reports/PAIR3_GENERIC_V2_TRAIN_CLOSED_20261102_142813/roles/E3/production/FINAL.json',u/'evidence/PRIOR_E3_PPO_FINAL.json');cp(P/'reports/PAIR3_GENERIC_V2_ACTUAL_FULLSTATE_TRAINING_CLOSED_SUMMARY_V1.json',u/'evidence/PRIOR_COHORT_CLOSED_SUMMARY.json')
USD='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3';CON='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755';assets=D.parent/'mod4_usd_scut_fudan_20261101/candidates/v1/assets'
for name,h in(('robot.usd',USD),('import_contract.json',CON)):cp(assets/name,u/'runtime/assets'/name,h)
proof=dict(kind='ACTUAL_NATIVE20K_GPU_PPO_FULL_SAVE_PRODUCER_HISTORY_NOT_NEWRESTORE',actual_not_mock=True,source_SHA=f['SHA'],asset_USD_SHA=USD,asset_contract_SHA=CON,num_envs=20000,producer_input_source_SHA=old['actual_source_read_counts']['source_SHA'],producer_input_whole20k_restore_passed=f['full_live_core_STD_optimizer_DR_history_RNG_queue_verified'],candidate_full_live20k_save_verified=f['full_live_core_STD_optimizer_DR_history_RNG_queue_verified'],producer_actual_PPO_updates=20,producer_saved_17Adam=f['saved_17Adam'],all_own_children_waited=next(r for r in summary['rows']if r['role']=='E3')['all_own_child_waited'],candidate_has_not_yet_been_freshly_restored=True,new_worker_fullrestore_mandatory_before_any_PPO=True,producer_FINAL_SHA=H((u/'evidence/PRIOR_E3_PPO_FINAL.json').read_bytes()),closed_summary_SHA=H((u/'evidence/PRIOR_COHORT_CLOSED_SUMMARY.json').read_bytes()))
put(u/'evidence/PRIOR_FULL20K_REFERENCE.json',proof);meta=dict(path=f['path'],SHA=f['SHA'],bytes=f['bytes'],iteration=43110,Adam17=866460,LR=f['actual_saved_LR']);entry=dict(role='E3',role_key='continue_e3_67ee_w1_72',source_family='e0_e2_e3',base_root=spec['job_root'],job_root=job,source_SHA=f['SHA'],source_model_metadata=meta,task_template={},go_template={},max_additional_updates=20,num_envs=20000,max_parent_seconds=3900,save_after_seconds=3600,exit_headroom_seconds=300,manifest_file='INSTALL_MOD4V1_POSTTRAIN_ACTUAL.json',actual_prior_full20k_proof_file='evidence/PRIOR_FULL20K_REFERENCE.json',native0pt_evidence_file='evidence/NEW_ASSET_NATIVE_ACTUAL.json',target_source_SDK_receipt_file='evidence/PRIOR_E3_PPO_FINAL.json',historical_geometry_evidence_file='evidence/RM70_SCOPE_REUSE_ACTUAL.json',source_contract_AST_MOCK_passed=True,source_contract_not_SDK_pass_claim=True,required_immutable_files=spec['required_immutable_files'],worker_argv=spec['worker_argv'],final_file='production/FINAL.json',stop_relative='production/STOP_AFTER_SAVE.json',final_updates_key='actual_new_PPO_updates')
put(payload/'SOURCE_PLAN.json',dict(run_id=run,H1_excluded=True,entries=[entry],selected_mother_1cd_unchanged=True,no_new_budget=True,continuation_not_replay=True));put(payload/'SCHEDULE_PUBLIC.json',{'experts':{entry['role_key']:{'max_parent_seconds':3900,'GPU_UUID':'GPU-16828f91-2b45-b646-8dc0-9481138e2842'}}})
files=[]
for p in payload.rglob('*'):
 if p.is_file():
  raw=p.read_bytes()
  if p.suffix=='.py':ast.parse(raw.decode('utf8'))
  files.append(dict(relative=p.relative_to(payload).as_posix(),bytes=len(raw),SHA=H(raw)))
put(D/'SOURCE_DELTA.json',dict(root=root,role='E3',source=meta,source_files=files,all_worker_functions_unchanged=True,owner_changes=['single authorized GPU0 tuple','honest saved-candidate producer eligibility instead of claiming candidate prior GPU reload'],stager_changes=['one E3 entry instead of two-role pair'],original_accounting_resource_close_wait_functions_retained=True,new_native_PPO_claim=False))
put(D/'STAGE_ONCE.json',dict(epoch=time.time(),root=root));sys.path.insert(0,str(T));from project_connector import connect72
c=connect72();s=c.open_sftp();report=dict(root=root,run_id=run,source=meta,models_stat_hash_decode=0,SDK_PPO_GO_C_or_lock_operations=0)
def mkdir(p):
 try:s.stat(p)
 except FileNotFoundError:
  parent=p.rsplit('/',1)[0]
  if parent:mkdir(parent)
  s.mkdir(p)
try:
 try:s.stat(root);raise RuntimeError('New unused remote root required')
 except FileNotFoundError:pass
 mkdir(root)
 for r in files:
  p=payload/r['relative'];raw=p.read_bytes();assert H(raw)==r['SHA'];target=root+'/'+r['relative'];mkdir(target.rsplit('/',1)[0])
  with s.open(target,'wx')as z:z.write(raw)
 cmd=shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B '+shlex.quote(root+'/stage_e3_continuation_nonpt.py')+' '+shlex.quote(root);i,o,e=c.exec_command(cmd,timeout=300);i.close();stdout=o.read().decode();stderr=e.read().decode();rc=o.channel.recv_exit_status();report.update(returncode=rc,stdout=stdout,stderr=stderr);assert rc==0,(rc,stderr)
 for name in('OWNER_PLAN.json','STAGE_COMPLETE.json'):
  with s.open(root+'/'+name,'rb')as z:raw=z.read()
  save(D/name,raw)
 # Exercise only stdlib original owner source verification, not owner.main or SDK.
 cmd=shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote('import sys,json;sys.path.insert(0,'+repr(root)+');import eight_posttrain_original_owner_v1 as o;o.verify_sources(json.loads((o.B/"OWNER_PLAN.json").read_bytes()));print("source verification passed; no SDK/models/GO/C writes")');i,o,e=c.exec_command(cmd,timeout=120);i.close();a=o.read().decode();b=e.read().decode();rc=o.channel.recv_exit_status();report.update(source_verification_rc=rc,source_verification_stdout=a,source_verification_stderr=b);assert rc==0,b
finally:
 s.close();c.close();put(D/'STAGE_RESULT.json',report);print(json.dumps(report,indent=2))
