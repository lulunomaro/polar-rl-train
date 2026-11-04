"""One unused N20000 admission: full learner continuation, fresh environment; non-PT source stage only."""
from pathlib import Path
import ast,json,time,sys,shlex,hashlib
D=Path(__file__).resolve().parent;T=D.parent/'mod4v1_experts_fulldr_rm70_20261101';R=D.parent/'mod4v1_supermimic_bptt_20261102';P=D/'native_payload_v5_n20000_admission2';N=D/'source_fudan_native_worker_v3_20k';prefix='FDN_N20000_W5_';H=lambda b:hashlib.sha256(b).hexdigest()
W4_CLOSED=D/'reports/FDN_N20000_W4_20261104_195548/CLOSED_RESULT.json'
w4=json.loads(W4_CLOSED.read_bytes());assert w4['closed'] is True
assert w4['root']=='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_E3_FUDAN_N20000_LEARNER_CONTINUE64_W4_20261104_195410_1793793250201118300'
w4meta=w4['metadata'];w4exit=w4meta['OWNER_EXIT_ACTUAL.json'];w4outer=w4meta['OUTER_OWNER_WAIT_ACTUAL.json']
assert w4outer['actual_wait_returncode']==0 and w4outer['original_owner_reaped'] is True
assert w4outer['controller_pid']==1614620 and w4outer['original_owner_pid']==w4meta['OWNER_PARENT_IDENTITY.json']['pid']==1614627
assert w4exit['run_id']==w4['root'].rsplit('/',1)[-1]
assert all(w4exit[k] is True for k in('all_own_children_waited','original_cost_settled','original_leases_released'))
assert all(w4meta[k] is None for k in('COHORT_FINAL.json','FDN_FINAL.json','FDN_PARENT_WAIT_QUALIFICATION.json','FDN_LATEST_COMPLETE_SAVE.json','FDN_FULL_LEARNER_CONTINUATION_INITIALIZED.json','FDN_FRESH_NEW_NOMINAL_RESET.json','FDN_NATIVE_UPDATE.json','FDN_NATIVE_ERROR.json','FDN_SAVE_ERROR.json','FDN_FINAL_METADATA_ERROR.json','FDN_APP_FAST_CLOSE_INTENT.json','FDN_APP_CLOSE_RETURNED.json','FDN_APP_CLOSE_ERROR.json','FDN_TASK_RESOURCE_BOUND_BEFORE_SDK_MODEL.json'))
q=json.loads((D/'FDN_W3_4096_CLOSED_FOR_N20000_SOURCE.json').read_bytes());assert q['actual_inner_and_outer_waits_qualified']and q['original_cost_settled_and_leases_released']and q['target_envs_requested_by_user']==20000;source=q['source'];assert source['source_training_execution_qualified']and source['counters']['updates']==64
assert N.is_dir() and not P.exists() and not(D/(prefix+'STAGE_ONCE.json')).exists();main=[]
for p in sorted(N.glob('*.py')):
 tree=ast.parse(p.read_text(encoding='utf8'))
 if any(isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef))and x.name=='main'for x in tree.body):main.append(p)
assert len(main)==1,main
P.mkdir();U=P/'uploads';W=U/'worker_sources';W.mkdir(parents=True)
def cp(src,dst):
 src=Path(src);assert src.suffix.lower()not in('.pt','.pth','.ckpt','.onnx','.safetensors');raw=src.read_bytes()
 if src.suffix=='.py':ast.parse(raw.decode('utf8'))
 if dst.exists():assert dst.read_bytes()==raw;return
 dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(raw)
def put(p,v):assert not p.exists();p.write_text(json.dumps(v,indent=2,allow_nan=False),encoding='utf8')
for name in('three_slot_common_v1.py','single_writer72_authority_V85M_source.py'):cp(D.parent/'mod4v1_e3_continue_v2_20261104/payload'/name,P/name)
cp(D/'source_original_owner_v3_20k/fudan_original_owner_v1.py',P/'fudan_original_owner_v1.py');cp(D/'source_original_owner_v3_20k/fudan_worker_close_contract_v1.py',W/'fudan_worker_close_contract_v1.py');cp(D/'stage_fudan_nonpt_v3_20k.py',P/'stage_fudan_nonpt_v3_20k.py')
cp(D/'source_fudan_seq_ppo_v1/fudan_seq_ppo.py',W/'fudan_seq_ppo.py');cp(D/'source_task_runtime_v1/e3_fudan_task_runtime_v1.py',W/'e3_fudan_task_runtime_v1.py');cp(D/'CONTRACT_PARITY_AND_POSE_V2.json',U/'fudan_task_pose.json')
for p in sorted(N.glob('*.py')):
 if p.name.startswith('test_'):continue
 cp(p,W/('worker_fudan_sequence_ppo_native_v1.py' if p==main[0] else p.name))
for name in('app_close_semantics_v6.py','resume_runtime_contracts_v3.py','pose_cache_runtime_adapter_v4.py'):cp(R/'payload_a1_v6_small_source/source'/name,W/name)
run='MOD4V1_E3_FUDAN_N20000_LEARNER_CONTINUE64_W5_ADMISSION2_'+time.strftime('%Y%m%d_%H%M%S')+'_'+str(time.time_ns());root='/home/lc01/Zonglin Li/zonglin2/tasks/'+run
put(P/'SOURCE_PLAN.json',dict(kind='MOD4V1_E3_FUDAN_SEQUENCE_PPO_NATIVE_V1',run_id=run,base_root='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_E3_PPO_CONTINUE67EE_W2_SAVENAMESPACE_20261104_142648_1793773608384136500/roles/E3',asset_USD_SHA='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3',asset_contract_SHA='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755',learner_source=source))
files=[]
for p in P.rglob('*'):
 if p.is_file():raw=p.read_bytes();files.append(dict(path=p.relative_to(P).as_posix(),bytes=len(raw),sha256=H(raw)))
put(D/(prefix+'STAGE_ONCE.json'),dict(epoch=time.time(),root=root,run_id=run,payload=files,num_envs=20000,learner_source=source,new_window_updates_claim=0));sys.path.insert(0,str(T));from project_connector import connect72
c=connect72();s=c.open_sftp();report=dict(root=root,run_id=run,num_envs=20000,learner_source=source,source_PT_reads=0,SDK_GPU_GO_C_or_lock_operations=0)
def mkdir(p):
 try:s.stat(p)
 except FileNotFoundError:
  parent=p.rsplit('/',1)[0]
  if parent:mkdir(parent)
  s.mkdir(p)
try:
 try:s.stat(root);raise RuntimeError('Fresh unused N20000 root required')
 except FileNotFoundError:pass
 mkdir(root)
 for f in files:
  target=root+'/'+f['path'];mkdir(target.rsplit('/',1)[0]);raw=(P/f['path']).read_bytes();assert H(raw)==f['sha256']
  with s.open(target,'wx')as z:z.write(raw)
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B '+shlex.quote(root+'/stage_fudan_nonpt_v3_20k.py')+' '+shlex.quote(root),timeout=400);i.close();a=o.read().decode();b=e.read().decode();rc=o.channel.recv_exit_status();report.update(returncode=rc,stdout=a,stderr=b);assert rc==0,(rc,b)
 for name in('OWNER_PLAN.json','STAGE_COMPLETE.json'):
  with s.open(root+'/'+name,'rb')as z:raw=z.read()
  put(D/(prefix+name),json.loads(raw))
 command=shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote('import sys,json;sys.path.insert(0,'+repr(root)+');import fudan_original_owner_v1 as m;m.verify_sources(json.loads((m.B/"OWNER_PLAN.json").read_bytes()));print("Original N20000 owner source-only preflight passed; SDK/models/GO/C writes0")');i,o,e=c.exec_command(command,timeout=180);i.close();a=o.read().decode();b=e.read().decode();rc=o.channel.recv_exit_status();report.update(owner_source_preflight_rc=rc,owner_source_preflight_stdout=a,owner_source_preflight_stderr=b);assert rc==0,b
finally:s.close();c.close();put(D/(prefix+'STAGE_RESULT.json'),report);print(json.dumps(report,indent=2))
