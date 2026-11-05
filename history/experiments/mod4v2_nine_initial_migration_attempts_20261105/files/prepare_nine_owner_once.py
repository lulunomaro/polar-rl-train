"""Derive a new nine-role owner; keep original locking, budget, scheduling, actual wait and cleanup."""
from pathlib import Path
import ast
D=Path(__file__).resolve().parent;out=D/'source_owner_v1/migration_nine_original_owner_v1.py';assert not out.exists()
src=D.parent/'mod4v1_experts_fulldr_rm70_20261101/POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/PAIR4_GENERIC_V2_DATA_PAYLOAD/eight_posttrain_original_owner_v1.py';s=src.read_text(encoding='utf8');tree=ast.parse(s)
verify='''def verify_sources(plan):
 require(b.C.resolve()==C.resolve(),'Original canonical path only')
 require(plan['kind']=='MOD4V2_NINE_ORIGINAL_OWNER_SOURCE_PLAN_V1'and plan['H1_excluded']is False,'User authorized all9 migration including separate H1 candidate')
 entries=plan['entries'];require(1<=len(entries)<=9 and len({e['role']for e in entries})==len(entries)and all(e['role']in ROLES for e in entries),'Unique authorized roles')
 require(len({e['role_key']for e in entries})==len(entries),'Unique original charge keys')
 for e in entries:
  job=Path(e['job_root']);job.resolve().relative_to(B.resolve());require(not(job/'GO_PRODUCTION.json').exists(),'Unused own role')
  require(e['max_additional_updates']==20 and e['num_envs']==20000 and e['max_parent_seconds']==3900 and e['save_after_seconds']==3600 and e['exit_headroom_seconds']==300,'Original finite20 windows')
  m=json.loads((job/e['manifest_file']).read_text());require(m['source_PT_copied']is False and m['native0PT_status']=='PENDING_ACTUAL_FRESH_V2_WORKER_INITIALIZATION','Source stage is not SDK or restore proof')
  for f in m['files']:
   p=job/f['relative'];p.resolve().relative_to(job.resolve());require(p.suffix.lower()not in('.pt','.pth','.ckpt','.safetensors','.onnx'),'No source model stat/hash');raw=p.read_bytes();require(len(raw)==f['bytes']and hashlib.sha256(raw).hexdigest()==f['SHA256'],'Exact staged own role input')
  for f in m['shared_files']:
   p=B/f['relative'];p.resolve().relative_to(B.resolve());require(p.suffix.lower()not in('.pt','.pth','.ckpt','.safetensors','.onnx'),'No shared model input');raw=p.read_bytes();require(len(raw)==f['bytes']and hashlib.sha256(raw).hexdigest()==f['SHA256'],'Exact shared V2 package/worker/close helpers')
  require(e['source_SHA']==m['source_SHA']and e['source_bytes']==m['source_bytes']and e['source_iteration']==m['source_iteration'],'Formal frozen metadata binding, no source-byte operation')
 require((B/'v2_package/assets/robot.usd').is_file()and hashlib.sha256((B/'v2_package/assets/robot.usd').read_bytes()).hexdigest()==USD,'Actual V2 asset identity')
 require(hashlib.sha256((B/'v2_package/assets/import_contract.json').read_bytes()).hexdigest()==CONTRACT,'Actual V2 contract identity')
 local=json.loads((B/'V2_LOCAL_VALIDATION.json').read_bytes());require(local['passed']is True and all(local['checks'].values()),'Local validation distinct from mandatory live worker native checks')
'''
taskgo='''def task_and_go(e,uuid,c,run,global_fds,private,finite,resource):
 job=Path(e['job_root']);now=time.time();bind=dict(canonical_path=str(C),authority_generation=c['authority_generation'],owner_run_id=run,owner_parent_pid=os.getpid(),one_original_writer=True)
 put(job/'ACTUAL_CANONICAL_READ.json',dict(canonical_SHA=hashlib.sha256(C.read_bytes()).hexdigest(),remaining_training_seconds=c['remaining_training_seconds'],charged_training_seconds=c['charged_training_seconds'],reserve_seconds=RESERVE,run_id=run,owner_parent_pid=os.getpid(),original_two_EX_locks_held=True))
 put(job/'ACTUAL_RESOURCE_LEASES.json',dict(GPU_UUID=uuid,parent_pid=os.getpid(),original_owner_EX_held=True,private_GPU_EX_held=True,finite_environment_SH_held=True,inherited_global_fds=global_fds,private_GPU_fd=private.fileno(),finite_fd=finite.fileno()))
 admission=dict(kind='ROOT_MOD4V2_NINE_MIGRATION_ACTUAL_ADMISSION_V1',run_id=run,role=e['role'],parent_pid=os.getpid(),GPU_UUID=uuid,num_envs=20000,canonical=bind,fresh_resource_checks=resource,USD_SHA=USD,contract_SHA=CONTRACT,original_two_EX_owner_locks_held=True,original_private_GPU_EX_held=True,original_shared_finite_environment_held=True,original_budget_currently_admitted=True,fullrestore_proof_reused_as_history_not_new_training_restore=True,new_V2_native0PT_passed=False,worker_native_before_source_read_required=True,v1_source_checkpoint_complete_history_only=True,new_budget_or_ledger=False)
 put(job/'ROOT_ADMISSION_ACTUAL.json',admission);ah=hashlib.sha256((job/'ROOT_ADMISSION_ACTUAL.json').read_bytes()).hexdigest();mh=hashlib.sha256((job/e['manifest_file']).read_bytes()).hexdigest();fds=global_fds+[private.fileno(),finite.fileno()]
 task=dict(e);task.update(kind='MOD4V2_EXPERT_ORIGINAL_PPO_MIGRATION_V1',run_id=run,GPU_UUID=uuid,canonical_path=str(C),canonical_binding=bind,owner_pid=os.getpid(),actual_parent_pid=os.getpid(),inherited_lock_fds=fds,root_admission_file=str(job/'ROOT_ADMISSION_ACTUAL.json'),root_admission_SHA=ah,source_manifest_SHA=mh,original_runtime_root=str(job),original_entry=e['entry'],original_run_manifest=str(job/e.get('original_run_manifest_relative','original_run_manifest.json')),v2_package=str(B/'v2_package'),helper_root=str(B/'helpers'),max_parent_seconds=3900,save_after_seconds=3600,exit_headroom_seconds=300,max_additional_updates=20,num_envs=20000,steps_per_env=e.get('steps_per_env',24),seed=20260928,stop_file=str(job/'STOP_AFTER_SAVE.json'),save_deadline=now+3600,nominal_end_epoch=now+3900,go_file=str(job/'GO_PRODUCTION.json'),job_root=str(job),source_read_purpose='NEW_V2_'+e['role']+'_FULL20K_ORIGINAL20_'+run)
 go=dict(kind='MOD4V2_NINE_ORIGINAL_OWNER_GO_V1',run_id=run,role=e['role'],GPU_UUID=uuid,parent_pid=os.getpid(),source_SHA=e['source_SHA'],num_envs=20000,actor_obs=35,critic_obs=38,action_dim=6,physics_dt=.0025,TGS=[32,4],policy_hz=50,feedback_hz=100,USD_SHA=USD,contract_SHA=CONTRACT,manifest_SHA=mh,root_admission_SHA=ah,canonical=bind,learning_started_epoch=now,save_deadline=now+3600,nominal_end_epoch=now+3900,exit_headroom_seconds=300,stop_file=str(job/'STOP_AFTER_SAVE.json'),native_validation_pending_not_false_claim=True)
 put(job/'TASK.json',task);return task,go
'''
changes={'verify_sources':verify,'task_and_go':taskgo}
for node in sorted([n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in changes],key=lambda n:n.lineno,reverse=True):
 lines=s.splitlines(keepends=True);s=''.join(lines[:node.lineno-1])+changes[node.name]+''.join(lines[node.end_lineno:])
s=s.replace("ROLES=('E0','E2','E3','W35','CURB_PROTECTED878','CURB_INDEPENDENT113','SLOPE135','SLOPE_INDEPENDENT50')","ROLES=('E0','E2','E3','H1_normal','W35','CURB_PROTECTED878','CURB_INDEPENDENT113','SLOPE135','SLOPE_INDEPENDENT50')")
s=s.replace('2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3','2237070ddc0a4e33f0c28e23fe5bb3db1f12bb619fddcdd89f9a74d5ac875f18').replace('bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755','00199c26533a9adaca6a35a49d30e8b8b27182230772674bd936d8b527169f4e').replace('H1_excluded=True','H1_excluded=False')
a="if p.returncode!=0:\n     completed=(final or {}).get(e.get('final_updates_key','completed_actual_updates'),0)";assert s.count(a)==1
replacement="if p.returncode!=0 or not(final or {}).get('passed_execution',False) or not(final or {}).get('completed_requested_update_window',False):\n     completed=(final or {}).get(e.get('final_updates_key','completed_actual_updates'),0)";s=s.replace(a,replacement)
# The new worker writes complete/error and pinned original close intent. Qualify only
# after actual child.wait; RC0 alone never proves execution/full save.
a="put(job/'PARENT_WAITED_ACTUAL.json',dict(role=e['role'],worker_pid=p.pid,actual_wait_returncode=p.returncode,actual_parent_terminal_epoch=ended,final=final,all_own_children_waited=True));account(run,go,rows)";assert s.count(a)==1
b="q=qualify_v2_waited(job,e,final,p.pid,p.returncode);rows[key]['semantic_qualification']=q;put(job/'PARENT_WAITED_ACTUAL.json',dict(role=e['role'],worker_pid=p.pid,actual_wait_returncode=p.returncode,actual_parent_terminal_epoch=ended,final=final,semantic_qualification=q,all_own_children_waited=True));account(run,go,rows)";s=s.replace(a,b)
s=s.replace("or not(final or {}).get('completed_requested_update_window',False):","or not(final or {}).get('completed_requested_update_window',False)or not q['qualified']:")
q='''def qualify_v2_waited(job,e,final,pid,rc):
 errors=[];checks={};f=final or {}
 checks['actual_rc0']=rc==0;checks['actual_worker_and_parent']=f.get('worker_pid')==pid and f.get('parent_pid')==os.getpid()
 checks['execution_final']=f.get('passed_execution')is True and f.get('completed_requested_update_window')is True and f.get('error')is None and f.get('close_errors')==[]
 checks['finite20_actual']=f.get('completed_actual_updates')==20
 checks['V2_asset']=f.get('target_asset_SHA')==USD and f.get('target_contract_SHA')==CONTRACT
 io=f.get('source_IO')or{};checks['source_once']=all(io.get(k)==1 for k in('physical_byte_opens','SHA_calculations','CPU_decodes'))
 checks['no_v1_env_applied']=f.get('source_env_state_applied')is False
 latest=f.get('latest_complete_save')or{};checks['complete_source_output']=bool(latest.get('path')and latest.get('bytes',0)>0 and len(latest.get('sha256',''))==64)
 ep=job/'production/V2_MIGRATION_ERROR.json';checks['worker_error_absent']=not ep.exists()
 ip=job/'production/V2_APP_CLOSE_INTENT.json'
 if ip.exists():
  intent=json.loads(ip.read_bytes());fp=job/e['final_file'];checks['intent_final_binding']=intent.get('final_sha256')==hashlib.sha256(fp.read_bytes()).hexdigest()and intent.get('worker_pid')==pid and intent.get('parent_pid')==os.getpid()and intent.get('error_before_close')is False and intent.get('close_errors')==[]
 else:checks['intent_final_binding']=False
 return dict(kind='MOD4V2_MIGRATION_ACTUAL_CHILD_WAIT_QUALIFICATION_V1',role=e['role'],qualified=all(checks.values()),checks=checks,actual_child_wait_returned=True,actual_child_pid=pid,actual_parent_pid=os.getpid(),errors=errors,skill_graduated=False)

'''
pos=s.index('def main():');s=s[:pos]+q+s[pos:];ast.parse(s);compile(s,str(out),'exec')
old=ast.parse(src.read_text(encoding='utf8'));new=ast.parse(s)
for name in('gpu','account','environment'):
 a=next(n for n in old.body if isinstance(n,ast.FunctionDef)and n.name==name);b=next(n for n in new.body if isinstance(n,ast.FunctionDef)and n.name==name);assert ast.dump(a,include_attributes=False)==ast.dump(b,include_attributes=False),name
out.parent.mkdir(parents=True,exist_ok=True);out.write_text(s,encoding='utf8',newline='\n');print('New9-role owner AST/compile; original gpu/account/environment exact; resource/charge/wait/cleanup inherited; no execution or model reads')
