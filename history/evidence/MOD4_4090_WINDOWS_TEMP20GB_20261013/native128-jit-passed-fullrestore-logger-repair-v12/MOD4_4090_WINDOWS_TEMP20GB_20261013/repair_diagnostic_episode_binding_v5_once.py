"""SDK manual fixture final-reset metadata refresh, no command/RNG/control change."""
from pathlib import Path
import json,time,sys,hashlib,traceback
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent/'MOD4_4090_WINDOWS_REPAIR_20261013'))
from windows4090_native_transport import connect,powershell,upload
R='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013';OLD=R+'/temporary_scope2048_memory20GB_reset_context_v4_20261013';NEW=R+'/temporary_scope2048_memory20GB_diagnostic_binding_v5_20261013'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 receipt=D/'reports/DIAGNOSTIC_EPISODE_BINDING_V5_ACTUAL.json';assert not receipt.exists()
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
for n in ast.walk(tree):
 if isinstance(n,ast.With) and any('torch.inference_mode()'==ast.unparse(i.context_expr) for i in n.items) and any(ast.unparse(z).startswith('env._reset_idx(selected)') for z in n.body):
  n.body.extend(ast.parse('''from temporary_training_runtime import private_rng_hashes
binding_command_before=cmd.command.clone()
binding_cpu_rng=torch.get_rng_state().clone()
binding_cuda_rng=torch.cuda.get_rng_state(env.device).clone()
binding_private_rng=private_rng_hashes(env)
cmd._bind_episode(torch.arange(env.num_envs,device=env.device))
assert torch.equal(cmd.command,binding_command_before) and torch.equal(binding_cpu_rng,torch.get_rng_state()) and torch.equal(binding_cuda_rng,torch.cuda.get_rng_state(env.device))
assert binding_private_rng==private_rng_hashes(env) and torch.equal(cmd.bound_episode,env._e1_episode)
write('SDK_SELECTED_RESET_EPISODE_METADATA_BINDING_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),passed=True,manual_evaluation_fixture_bound_to_actual_reset_episode=True,actual_command_exact_before_after=True,all_global_private_rng_hashes_before_after_exact=True,no_step_observation_noise_draw_or_live_actor_correction=True,only_physical_reset_episode_binding=True))
''').body);hits+=1
assert hits==1
w.write_text(ast.unparse(ast.fix_missing_locations(tree))+'\\n',encoding='utf8');compile(w.read_text(encoding='utf8'),str(w),'exec')
mf=json.loads((old/'TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json').read_bytes());mf['scope_root']=str(new);mf['epoch']=time.time();mf['SDK_manual_fixture_reset_metadata_binding_only']=dict(old=before,new=ref(w),no_control_loop_or_production_command_change=True,global_private_RNG_and_command_actual_negative_control_required=True)
cpu=json.loads(Path(mf['target_CPU_receipt']['path']).read_bytes());cpu.update(scope=str(new),epoch=time.time(),new_metadata_only_contract=mf['SDK_manual_fixture_reset_metadata_binding_only']);cp=new/'reports/TARGET_TEMP2048_DIAGNOSTIC_BINDING_CPU_ACTUAL.json';cp.write_text(json.dumps(cpu,indent=2),encoding='utf8');mf['target_CPU_receipt']=ref(cp)
mf['sourcefreeze_files']=[ref(p) for base in (new/'runtime2048',new/'payload',r/'sdk_exact/source',r/'sdk_exact/apps') for p in sorted(base.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and '.egg-info' not in str(p)]
f=new/'TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json';f.write_text(json.dumps(mf,indent=2),encoding='utf8');l=new/'TEMPORARY_SEQUENCE_TASK_LEASE_GRANTED.json';l.write_text(json.dumps(dict(epoch=time.time(),case_id='temporary2048_memory20GB_diagnostic_binding_sequence_v5',approved_GPU_scope=True,mode='sdk',scope_root=str(new),environment_root=str(r),shared_gpu_lock=str(r/'WINDOWS4090_GPU_EXCLUSIVE.lock'),manifest_sha256=H(f),human20GB_temporary_branch_authorized=True),indent=2),encoding='utf8')
proof=dict(epoch=time.time(),passed_CPU_new_fixture_contract_only=True,worker_change=mf['SDK_manual_fixture_reset_metadata_binding_only'],old_error=e,old_EXIT=x,manifest=ref(f),old_originals_not_hotpatched=True,new_Task_GPU_future=True)
(new/'reports/DIAGNOSTIC_BINDING_ONLY_CPU_ACTUAL.json').write_text(json.dumps(proof,indent=2),encoding='utf8');print(json.dumps(proof))
"""
 f=D/'diagnostic_episode_binding_v5_cpu.py';assert not f.exists();f.write_text(code,encoding='utf8');compile(code,str(f),'exec');remote=R+'/'+f.name;upload(f,remote,60)
 assert powershell(connect(),"(Get-FileHash -LiteralPath '"+remote+"' -Algorithm SHA256).Hash.ToLower()",30)==H(f)
 actual=json.loads(powershell(connect(),"[Console]::OutputEncoding=[Text.Encoding]::UTF8;& '"+R+"/env/python.exe' '"+remote+"'",90))
 ps="& '"+NEW+"/payload/register_windows4090_demand_task_audited_v6_once.ps1' -LeasePath '"+NEW+"/TEMPORARY_SEQUENCE_TASK_LEASE_GRANTED.json' -ManifestPath '"+NEW+"/TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json' -AttemptPath '"+NEW+"/attempts/temporary2048_sdk_v1' -PythonPath '"+R+"/env/python.exe' -RuntimePath '"+NEW+"/runtime2048' -StageMode sdk -TrainSeconds 3600 -StartApprovedLease"
 powershell(connect(),ps,35);receipt.write_text(json.dumps(dict(epoch=time.time(),actual=actual,new_task_started_once=True,old_sources_failures_preserved=True),indent=2),encoding='utf8');print(json.dumps(dict(report=str(receipt),new_scope=NEW,newSDK_requested=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  (D/'reports'/('DIAGNOSTIC_BINDING_V5_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),inspect_no_replay=True),indent=2),encoding='utf8');raise
