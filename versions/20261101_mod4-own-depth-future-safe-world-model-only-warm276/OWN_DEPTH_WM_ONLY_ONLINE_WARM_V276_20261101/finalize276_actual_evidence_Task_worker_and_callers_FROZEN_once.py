from pathlib import Path
import ast,hashlib,importlib.util,json,sys,time
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports';R.mkdir(exist_ok=False)
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def put(p,v):
 with p.open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
P=T/'OWN_DEPTH_WM_ONLY_WARM_PROTOCOL_SOURCE_V275_20261101';ix=P/'INDEX275_WM_ONLY_WARM_PROTOCOL_SOURCE_FROZEN.json';assert H(ix)=='e5e57170aacbd5f580cf918974bcb787793be81b91c153b5633bd67d5bf74736'
for row in read(ix)['files']:
 p=Path(row['path']);assert p.stat().st_size==row['bytes']and H(p)==row['SHA']
for p in(N/'control276/wm_task275.py',N/'source/wm_task275.py'):p.write_bytes((P/'wm_only_task275.py').read_bytes())
worker=(N/'worker276_prefix_from_actual272.txt').read_text('utf8')+(N/'worker276_online_tail.txt').read_text('utf8');ast.parse(worker);wp=N/'source/worker276_online_WM_only.py';wp.write_text(worker,encoding='utf8')
spec=importlib.util.spec_from_file_location('root276_task_source_join',N/'control276/wm_task275.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
D=T/'FUDAN_TERRAIN80_CURRENT_DEPTH_PACKET_V272_20261101';p272=D/'reports/ROOT272_NEW240_MEAN_REGRESSION_PARENT_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json';j272=read(p272);assert j272['passed_execution']
old=next(json.loads(x['UTF8'])for x in j272['full_UTF8']if x['path'].endswith('/TASK272_ADMITTED_ACTUAL.json'))
A=T/'NEW272_FUTURE_SAFE_WM_CUDA_ADMISSION_V274V3_20261101';p274=A/'reports/ROOT274_NEW272_ACTUAL_H32_CUDA_OR_ORIGINAL_ERROR_RETURNED.json';j274=read(p274);assert j274['passed']and j274['result']['actual_WM_updates']==0 and j274['result']['physical_input_pairs']==5120
assert read(A/'reports/ROOT274_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')['global_serial_control_client_lease']=='FREE'
teacher=T/'MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101/reports/ROOT240V2_NEW_FORMAL_INITIAL_WHOLE_CPU_RETURNED_ACTUAL.json';assert read(teacher)['passed']
stamp=str(time.time_ns());run='OWN_DEPTH_WM_ONLY_WARM276_'+stamp;base='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_OWN_DEPTH_WM_ONLY_WARM276_'+stamp
task=m.make_task(dict(run_id=run,job_root=base+'/warm72',owner_root=base+'/owner72',GPU_UUID='GPU-16828f91-2b45-b646-8dc0-9481138e2842',worker_SHA=H(wp),source_CPU_report_SHA=H(teacher),teacher_whole_CPU_receipt_SHA=H(teacher),actual272_receipt_SHA=H(p272),actual274_receipt_SHA=H(p274),qualified240_package_root=old['qualified240_package_root'],model_path=old['model_path'],model_bytes=22099209,model_SHA=m.SOURCE_SHA,model_iteration=2135,model_Adam_step=42940,seed=27,generation='SOURCE276_FROZEN_BEFORE_GO',new_physics_DR_episodes_queues_and_WM_seed=True,teacher_source_RNG_not_restored_for_new_WM_environment=True,actual_learning_GO_pending=True))
put(N/'TASK276_FROZEN.json',task)
tree=ast.parse(worker);first=next(x for x in ast.walk(tree)if isinstance(x,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='receipt'for t in x.targets)and isinstance(x.value,ast.Call)and any(k.arg=='first_complete'for k in x.value.keywords));keys={k.arg for k in first.value.keywords}
assert {'kind','source_SHA','run_id','actual_new_WM_updates','actual_new_PPO_updates','actual_new_Pi_updates','actual_new_critic_updates','actual_new_STD_updates','actual_Pi_Critic_teacher_updates','teacher_iteration','teacher_Adam_step','teacher_LR','WM_optimizer_count','teacher_actor_critic_STD_full17Adam_unchanged','finite_WM_loss_grad_params_optimizer','new_completed_controls','physics_callbacks','feedback_samples','first_complete'}<=keys
assert "receipt['actual_resource_admission_SHA']=TASK['actual_resource_admission_SHA']"in worker
assert 'runner.learn'not in worker and 'runner.alg.update'not in worker and 'wm.update()'in worker and 'p.requires_grad_(False)'in worker
node=(N/'control276/model2050_240_fullstate_slot_node.py').read_text('utf8');assert 'go["WM_ONLY"] and go["FROZEN_TEACHER"]'in node and '"--task",str(J/"TASK276.json")'in node and 'final.get("actual_new_WM_updates",0)>0'in node
ps=[p for p in N.rglob('*')if p.is_file()and '__pycache__'not in p.parts and p.suffix in('.py','.json','.txt','.md')]
for p in ps:
 if p.suffix=='.py':ast.parse(p.read_text('utf8'),filename=str(p))
report=R/'ROOT276_LIVE_WORKER_TaskGO_SOURCE_CPU_NEW_JOIN.json';put(report,dict(passed=True,epoch=time.time(),source_AST=sum(p.suffix=='.py'for p in ps),actual272_and274_saved_evidence_joined=True,selected275_INDEX_SHA=H(ix),actual272_SHA=H(p272),actual274_SHA=H(p274),actual_teacher_whole_CPU_SHA=H(teacher),worker_receipt_275_required_fields_joined=True,original_account_HMAC_rawfee_AST_proof=str(N/'SOURCE276_ORIGINAL_ACCOUNT_HMAC_SENDER_CONTROLS_AND_LIVE_WORKER_JOIN.json'),source_only_new_local_join=True,model_raw_SDK_GPU_remote_GO_optimizer=0,actual_276_task_frozen_not_started=True))
ps.append(report);index=N/'INDEX276_WM_ONLY_WARM_SOURCE_CALLERS_FROZEN.json';put(index,dict(kind='FROZEN_WM_ONLY_ONLINE_WARM276_ORIGINAL_FINITE_CALLERS',epoch=time.time(),files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in sorted(ps)]))
print(json.dumps(dict(passed=True,index_SHA=H(index),files=len(ps),run_id=run)))
