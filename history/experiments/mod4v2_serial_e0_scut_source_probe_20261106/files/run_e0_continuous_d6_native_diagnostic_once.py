"""New no-policy N16 diagnostic under unchanged original frozen-resource lifecycle."""
from pathlib import Path
import ast,json,time,hashlib,shlex,posixpath
D=Path(__file__).resolve().parent;mark=D/'E0_D6_NATIVE_DIAGNOSTIC_ONCE.json';result=D/'E0_D6_NATIVE_DIAGNOSTIC_CLOSED_RESULT.json';assert not mark.exists()and not result.exists()
build=json.loads((D/'CONTINUOUS_D6_BUILD_RECEIPT_V1.json').read_bytes());assert build['added_backend_regular_closures']==4 and build['active_and_follower_continuous_axes']==8 and build['SDK_or_simulation_or_training_started']is False
train=json.loads(Path(json.loads((D/'E0_SINGLE_ADMISSION3_CLOSED_RESULT_PATH.json').read_bytes())['path']).read_bytes());exit=train['metadata']['OWNER_EXIT_ACTUAL.json'];assert train['closed']is True and exit['all_own_children_waited']is exit['original_cost_settled']is exit['original_private_finite_authority_leases_released']is True and train['metadata']['OUTER_OWNER_WAIT_ACTUAL.json']['original_owner_reaped']is True
base=(D/'E0_SINGLE_FROZEN_parent.py').read_text(encoding='utf8');tree=ast.parse(base);lines=base.splitlines(keepends=True)
make='''def make_task(r,plan,deadline,fds):
 require(r['role']=='E0' and len(fds)==2,'Single diagnostic original two EX descriptors')
 t=dict(plan['task_template']);t.update(role='E0',num_envs=16,controls=60,seed=20260928,diagnostic_members=['E0'],eval_members=['E0'],run_id=plan['group_id'],group_id=plan['group_id'],group_root=str(B),output_dir=str(B/'cases/E0'),owner_pid=os.getpid(),GPU_UUID=plan['GPU_UUID'],absolute_worker_deadline_epoch=deadline,helper_root=str(B/'helpers'),max_additional_updates=1,steps_per_env=24,save_deadline=deadline,stop_file=str(B/'STOP_DIAGNOSTIC.json'),eval_admission=dict(group_id=plan['group_id'],GPU_UUID=plan['GPU_UUID'],private_GPU_EX_held=True,global_finite_EX_held=True,inherited_lock_fds=fds))
 return t
'''
qual='''def qualify_waited_e0(out,pid,rc,plan):
 checks={};errors=[]
 try:
  f=own_json(out/'E0_MIMIC_DIAGNOSTIC_FINAL.json');i=own_json(out/'E0_MIMIC_DIAGNOSTIC_APP_CLOSE_INTENT.json');raw=(out/'task.json').read_bytes();fr=(out/'E0_MIMIC_DIAGNOSTIC_FINAL.json').read_bytes()
  checks['actual_wait_rc0']=rc==0;checks['execution']=f['execution']is True and f['passed_execution']is True;checks['worker_parent_PID']=f['worker_pid']==i['worker_pid']==pid and f['parent_pid']==i['parent_pid']==os.getpid();checks['task_final_binding']=f['task_sha256']==i['task_sha256']==hashlib.sha256(raw).hexdigest() and i['final_sha256']==hashlib.sha256(fr).hexdigest() and i['final_bytes']==len(fr)
  checks['no_policy_or_PT']=f['source_opens']==f['source_decodes']==f['PPO_updates']==f['actor_calls']==0 and f['actor_critic_optimizer_created']is False;checks['original_clock']=f['controls']==60 and f['physics_callbacks']==480 and f['feedback_samples']==120;checks['only_E0']=f['role']=='E0' and f['group_id']==plan['group_id'];checks['env_close']=i['env_close_returned']is True and (out/'ENV_CLOSE_RETURNED.json').exists();checks['original_App_close']=i['error_before_close']is False and i['original_app_close_arguments']==[] and i['original_fast_shutdown_unchanged']is True and i['original_bound_close']['fast_shutdown']is True;checks['no_ERROR']=not list(out.glob('*ERROR*.json'))
 except BaseException:errors.append(traceback.format_exc());checks['required_evidence_complete']=False
 return dict(kind='E0_NO_POLICY_MIMIC_DIAGNOSTIC_ACTUAL_WAIT_V1',qualified=bool(checks)and all(checks.values()),checks=checks,errors=errors,actual_child_wait_returned=True,actual_child_PID=pid,skill_graduation=None)
'''
for n in sorted([x for x in tree.body if isinstance(x,ast.FunctionDef)and x.name in('make_task','qualify_waited_e0')],key=lambda n:n.lineno,reverse=True):lines[n.lineno-1:n.end_lineno]=[(make if n.name=='make_task'else qual)]
parent=''.join(lines).replace('V2_FROZEN_EVAL_FINAL.json','E0_MIMIC_DIAGNOSTIC_FINAL.json').replace('ONEGPU_SINGLE_E0_FRESH80_FINITE_EVAL_NO_LEARNING','ONEGPU_E0_N16_MIMIC_DIAGNOSTIC_NO_POLICY').replace('ACTUAL_SINGLE_GPU_E0_FRESH80_FROZEN_FINITE_EVAL','ACTUAL_E0_NO_POLICY_MIMIC_DIAGNOSTIC');ast.parse(parent);compile(parent,'diagnostic_parent.py','exec')
worker=(D/'worker_e0_mimic_native_diagnostic_v1.py').read_bytes();ast.parse(worker.decode());compile(worker,'worker_e0_mimic_native_diagnostic_v1.py','exec')
run='MOD4V2_E0_CONTINUOUS_D6_NATIVE_DIAG_'+time.strftime('%Y%m%d_%H%M%S')+'_'+str(time.time_ns());remote='/home/lc01/Zonglin Li/zonglin2/tasks/'+run;pkg=Path(build['package']);payload={'diagnostic_parent.py':parent.encode(),'worker_e0_mimic_native_diagnostic_v1.py':worker}
for name in('app_close_semantics_v6.py','resume_runtime_contracts_v3.py'):payload['helpers/'+name]=(D.parent/'e3_fudan_recovery_alignment_20261104/source_fudan_frozen_native_eval_v8_resume55'/name).read_bytes()
for p in pkg.rglob('*'):
 if p.suffix in('.pyc','.pyo')or'__pycache__'in p.parts:continue
 if p.is_file():payload['v2_package/'+p.relative_to(pkg).as_posix()]=p.read_bytes()
task=json.loads(json.dumps(train['cases']['E0']['GO_PRODUCTION.json'])) if False else dict(role='E0',original_runtime_root=train['root']+'/roles/E0',original_entry='runtime/isaac/mod4/train_mod4v1_e0.py',original_run_manifest=train['root']+'/roles/E0/original_run_manifest.json',migration_worker=train['root']+'/worker_mod4v2_expert_migration_v4.py',v2_package=remote+'/v2_package',source_path='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_POSTTRAIN_EIGHT_NOH1_PAIR1_V4_20261102_120158_1793592118216803700/roles/E0/production/model_final_complete.pt',source_SHA='6cdac1e4b84df407d41a38444b87eaa91309ed898af05fe95a6c80f6ac3fd693',source_bytes=14035411,source_iteration=32004,expected_asset_SHA=build['USD_sha256'],expected_contract_SHA=build['contract_sha256'])
plan=dict(group_id=run,GPU_UUID='GPU-16828f91-2b45-b646-8dc0-9481138e2842',roles=[dict(role='E0',worker='worker_e0_mimic_native_diagnostic_v1.py')],migration_cohort_close_receipt=dict(roles=['E0'],all_closed=True,actual_wait_complete=True,resources_released=True,original_cost_settled=True,semantic_qualified=True,closed_epoch=train['metadata']['OUTER_OWNER_WAIT_ACTUAL.json']['epoch']),task_template=task,worker_files=[dict(relative=k,bytes=len(v),SHA=hashlib.sha256(v).hexdigest())for k,v in payload.items()]);payload['GROUP_PLAN.json']=json.dumps(plan,indent=2).encode()
mark.write_text(json.dumps(dict(root=remote,task_scope='E0 N16 diagnostic no actor/source/PPO',planned_controls=60,old_sources_unchanged=True),indent=2),encoding='utf8')
import sys
sys.path.insert(0,str(D.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
client=connect72();sftp=client.open_sftp()
def mkdir(path):
 try:sftp.stat(path)
 except FileNotFoundError:mkdir(posixpath.dirname(path));sftp.mkdir(path)
try:
 try:sftp.lstat(remote);raise AssertionError('New diagnostic root already exists')
 except FileNotFoundError:pass
 mkdir(remote)
 for rel,raw in payload.items():
  mkdir(posixpath.dirname(remote+'/'+rel))
  with sftp.open(remote+'/'+rel,'wb')as f:f.write(raw)
 # Read only the already-created original TASK env path, not any checkpoint.
 with sftp.open(train['root']+'/roles/E0/TASK.json','rb')as f:tt=json.loads(f.read())
 plan['task_template']['original_run_manifest']=tt['original_run_manifest'];payload['GROUP_PLAN.json']=json.dumps(plan,indent=2).encode()
 with sftp.open(remote+'/GROUP_PLAN.json','wb')as f:f.write(payload['GROUP_PLAN.json'])
 outer="from pathlib import Path\nimport subprocess,json,time,os\nB=Path(__file__).resolve().parent\nlog=(B/'PARENT_STDOUT_STDERR.log').open('xb');p=subprocess.Popen(['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-u','-B',str(B/'diagnostic_parent.py')],cwd=B,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);(B/'OUTER_IDENTITY.json').write_text(json.dumps(dict(controller_pid=os.getpid(),parent_pid=p.pid,epoch=time.time())));rc=p.wait();(B/'OUTER_WAIT.json').write_text(json.dumps(dict(epoch=time.time(),actual_wait_returncode=rc,original_parent_reaped=True,controller_pid=os.getpid(),parent_pid=p.pid)));log.close()\n"
 with sftp.open(remote+'/OUTER.py','wb')as f:f.write(outer.encode())
 launch="import subprocess;from pathlib import Path;B=Path("+repr(remote)+");log=(B/'CONTROLLER.log').open('xb');p=subprocess.Popen(['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-u','-B',str(B/'OUTER.py')],cwd=B,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);print(p.pid)"
 i,o,e=client.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(launch));i.close();stdout=o.read().decode();stderr=e.read().decode();assert o.channel.recv_exit_status()==0,(stdout,stderr);print(json.dumps(dict(root=remote,submitted=True,controller_pid=stdout.strip(),native_or_diagnostic_result_not_yet_observed=True)))
 deadline=time.monotonic()+4600;cache={}
 def get(rel):
  assert rel.endswith('.json')
  try:
   with sftp.open(remote+'/'+rel,'rb')as f:return json.loads(f.read())
  except FileNotFoundError:return None
 while time.monotonic()<deadline:
  outer=get('OUTER_WAIT.json')
  if outer is not None:
   data={name:get(name)for name in('ACTUAL_GROUP_ADMISSION.json','PARENT_EXIT_SCOPE.json','TERMINAL_ROWS.json','E0_SINGLE_FROZEN_PARENT_FINAL.json','PARENT_ORIGINAL_ERROR.json','cases/E0/E0_MIMIC_DIAGNOSTIC_FINAL.json','cases/E0/E0_MIMIC_DIAGNOSTIC_APP_CLOSE_INTENT.json','cases/E0/WORKER_ERROR.json')};r=dict(root=remote,outer_actual_wait=outer,metadata=data,closed=True,training_or_skill_pass_not_claimed=True);result.write_text(json.dumps(r,indent=2,allow_nan=False),encoding='utf8');print(json.dumps(dict(path=str(result),outer=outer,qualification=[r.get('semantic_qualification')for r in(data['TERMINAL_ROWS.json']or[])],maxima=(data['cases/E0/E0_MIMIC_DIAGNOSTIC_FINAL.json']or{}).get('maxima_over_60_controls'),native_diagnostic_not_training=True)));break
  time.sleep(15)
 else:raise TimeoutError('Own bounded diagnostic collector expired; no original parent extension')
finally:sftp.close();client.close()
