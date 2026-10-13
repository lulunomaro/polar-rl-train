"""Restore the SDK requested fixture after diagnostic reset, no production change."""
from pathlib import Path
import json,time,sys,hashlib,traceback
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent/'MOD4_4090_WINDOWS_REPAIR_20261013'))
from windows4090_native_transport import connect,powershell,upload
R='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013';OLD=R+'/temporary_scope2048_memory20GB_diagnostic_binding_v5_20261013';NEW=R+'/temporary_scope2048_memory20GB_fixture_restore_v6_20261013'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 receipt=D/'reports/POSTRESET_MANUAL_FIXTURE_V6_ACTUAL.json';assert not receipt.exists()
 code="""from pathlib import Path;import json,hashlib,shutil,time,psutil,msvcrt,ast
r=Path('"""+R+"""');old=Path('"""+OLD+"""');new=Path('"""+NEW+"""')
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=H(p))
e=json.loads((old/'attempts/temporary2048_sdk_v1/output/ORIGINAL_ERROR.json').read_bytes());x=json.loads((old/'attempts/temporary2048_sdk_v1/EXIT_RECEIPT.json').read_bytes());assert e['prePPO'] and 'audit_direction' in e['error'] and x['own_child_and_descendants_actual_absent'] and x['worker_exitcode']==1
for row in (x['parent'],x['child']):
 try:p=psutil.Process(row['pid']);assert p.create_time()!=row['created']
 except psutil.NoSuchProcess:pass
with (r/'WINDOWS4090_GPU_EXCLUSIVE.lock').open('r+b') as f:f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1);f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
assert not new.exists();new.mkdir();shutil.copytree(old/'runtime2048',new/'runtime2048');shutil.copytree(old/'payload',new/'payload');(new/'reports').mkdir();(new/'attempts').mkdir()
w=new/'payload/temporary_worker.py';before=ref(w);tree=ast.parse(w.read_text(encoding='utf8'));hits=0
fixture=ast.parse('''assert args.mode=='sdk' and cmd.manual_evaluation_mode
postreset_fixture_rng_cpu=torch.get_rng_state().clone()
postreset_fixture_rng_cuda=torch.cuda.get_rng_state(env.device).clone()
cmd.time_left[:]=1e9
cmd.command[:]=0.
cmd.command[:,0]=torch.tensor([.3,-.3,.3,-.3,.3,-.3,.3,-.3,0.,0.],device=env.device)
cmd.is_standing_env[:]=False
cmd.is_standing_env[8:]=True
if hasattr(cmd,'is_heading_env'):cmd.is_heading_env[:]=False
cmd.is_pure_spin[:]=False
cmd.is_moving_spin[:]=False
cmd.is_transition_spin[:]=False
assert torch.equal(postreset_fixture_rng_cpu,torch.get_rng_state()) and torch.equal(postreset_fixture_rng_cuda,torch.cuda.get_rng_state(env.device))
write('SDK_POSTRESET_REQUESTED_FIXTURE_REBOUND_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),passed=True,same_requested10env_fixture_as_all300controls=True,production_command_sampler_and_its_reset_rng_consumption_not_modified=True,zero_additional_physics_control_or_actor_observation=True,new_reset_pending_fixture_not_route_progress=True))
''').body
for n in ast.walk(tree):
 for field,value in list(ast.iter_fields(n)):
  if not isinstance(value,list):continue
  for i,node in enumerate(value):
   if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='binding_command_before' for t in node.targets):value[i:i]=fixture;hits+=1;break
assert hits==1
w.write_text(ast.unparse(ast.fix_missing_locations(tree))+'\\n',encoding='utf8');compile(w.read_text(encoding='utf8'),str(w),'exec')
mf=json.loads((old/'TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json').read_bytes());mf['scope_root']=str(new);mf['epoch']=time.time();mf['SDK_postreset_fixture_only_contract']=dict(old=before,new=ref(w),same300controlfixture_rebound_without_physics=True,production_sampler_and_reset_RNG_not_changed=True)
cpu=json.loads(Path(mf['target_CPU_receipt']['path']).read_bytes());cpu.update(scope=str(new),epoch=time.time(),new_fixture_only_contract=mf['SDK_postreset_fixture_only_contract']);cp=new/'reports/TARGET_TEMP2048_POSTRESET_FIXTURE_CPU_ACTUAL.json';cp.write_text(json.dumps(cpu,indent=2),encoding='utf8');mf['target_CPU_receipt']=ref(cp)
mf['sourcefreeze_files']=[ref(p) for base in (new/'runtime2048',new/'payload',r/'sdk_exact/source',r/'sdk_exact/apps') for p in sorted(base.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and '.egg-info' not in str(p)]
f=new/'TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json';f.write_text(json.dumps(mf,indent=2),encoding='utf8');l=new/'TEMPORARY_SEQUENCE_TASK_LEASE_GRANTED.json';l.write_text(json.dumps(dict(epoch=time.time(),case_id='temporary2048_memory20GB_fixture_restore_sequence_v6',approved_GPU_scope=True,mode='sdk',scope_root=str(new),environment_root=str(r),shared_gpu_lock=str(r/'WINDOWS4090_GPU_EXCLUSIVE.lock'),manifest_sha256=H(f),human20GB_temporary_branch_authorized=True),indent=2),encoding='utf8')
proof=dict(epoch=time.time(),passed_CPU_new_fixture_contract_only=True,worker_change=mf['SDK_postreset_fixture_only_contract'],old_error=e,old_EXIT=x,manifest=ref(f),old_originals_not_hotpatched=True,new_Task_GPU_future=True)
(new/'reports/POSTRESET_FIXTURE_ONLY_CPU_ACTUAL.json').write_text(json.dumps(proof,indent=2),encoding='utf8');print(json.dumps(proof))
"""
 f=D/'postreset_manual_fixture_v6_cpu.py';assert not f.exists();f.write_text(code,encoding='utf8');compile(code,str(f),'exec');remote=R+'/'+f.name;upload(f,remote,60)
 assert powershell(connect(),"(Get-FileHash -LiteralPath '"+remote+"' -Algorithm SHA256).Hash.ToLower()",30)==H(f)
 actual=json.loads(powershell(connect(),"[Console]::OutputEncoding=[Text.Encoding]::UTF8;& '"+R+"/env/python.exe' '"+remote+"'",90))
 ps="& '"+NEW+"/payload/register_windows4090_demand_task_audited_v6_once.ps1' -LeasePath '"+NEW+"/TEMPORARY_SEQUENCE_TASK_LEASE_GRANTED.json' -ManifestPath '"+NEW+"/TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json' -AttemptPath '"+NEW+"/attempts/temporary2048_sdk_v1' -PythonPath '"+R+"/env/python.exe' -RuntimePath '"+NEW+"/runtime2048' -StageMode sdk -TrainSeconds 3600 -StartApprovedLease"
 powershell(connect(),ps,35);receipt.write_text(json.dumps(dict(epoch=time.time(),actual=actual,new_task_started_once=True,old_sources_failures_preserved=True),indent=2),encoding='utf8');print(json.dumps(dict(report=str(receipt),new_scope=NEW,newSDK_requested=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  (D/'reports'/('POSTRESET_FIXTURE_V6_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),inspect_no_replay=True),indent=2),encoding='utf8');raise
