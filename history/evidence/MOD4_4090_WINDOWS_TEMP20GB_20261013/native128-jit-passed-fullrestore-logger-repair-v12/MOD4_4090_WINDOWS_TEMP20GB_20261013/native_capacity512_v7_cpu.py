from pathlib import Path;import json,hashlib,shutil,time,psutil,msvcrt,ast,sys,os
r=Path('C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013');old=Path('C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013/temporary_scope2048_memory20GB_fixture_restore_v6_20261013');new=Path('C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013/temporary_scope512_memory20GB_native_capacity_v7_20261013')
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=H(p))
parent=json.loads((old/'SEQUENCE_ONCE_CONSUMED.json').read_bytes())['parent'];native=json.loads((old/'attempts/temporary2048_native_v1/DISPATCH_RECEIPT.json').read_bytes());error=json.loads((old/'SEQUENCE_ORIGINAL_ERROR.json').read_bytes());log=(old/'attempts/temporary2048_native_v1/worker_stdout.log').read_bytes()
assert b'foundLostAggregatePairsCapacity' in log and b'17891328' in log and '1455' in error['error']
for x in (parent,native['child']):
 try:p=psutil.Process(x['pid']);assert p.create_time()!=x['created']
 except psutil.NoSuchProcess:pass
active=[]
for p in psutil.process_iter(['pid','name','cmdline']):
 try:
  argv=' '.join(p.info['cmdline'] or [])
  if str(old).replace('/','\\').lower() in argv.replace('/','\\').lower():active.append(p.info)
 except psutil.Error:pass
assert not active,active
with (r/'WINDOWS4090_GPU_EXCLUSIVE.lock').open('r+b') as f:f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1);f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
sdk_path=old/'attempts/temporary2048_sdk_v1/output/PROBE_COMPLETE.json';sdk=json.loads(sdk_path.read_bytes());sdkexit=json.loads((old/'attempts/temporary2048_sdk_v1/EXIT_RECEIPT.json').read_bytes());assert sdk['passed'] and sdkexit['passed'] and sdk['actual_controls']==300 and sdk['actual_callbacks']==1200
assert not new.exists();new.mkdir();shutil.copytree(old/'runtime2048',new/'runtime2048');shutil.copytree(old/'payload',new/'payload');(new/'reports').mkdir();(new/'attempts').mkdir()
changed=[]
class N512(ast.NodeTransformer):
 def visit_Constant(self,n):
  if type(n.value) is int and n.value==2048:n.value=512
  if isinstance(n.value,str):n.value=n.value.replace('windows4090_temporary2048_memory20GB_selected_source_v1','windows4090_temporary512_memory20GB_selected_source_v7')
  return n
for name in ('temporary_worker.py','temporary_state_binding.py','temporary_training_runtime.py','temporary_probe_contract_base.py','windows4090_substep_readback_v6.py','left_head_offset_aware_migration_v3.py','temporary_parent.py'):
 p=new/'payload'/name;before=ref(p);tree=N512().visit(ast.parse(p.read_text(encoding='utf8')));p.write_text(ast.unparse(ast.fix_missing_locations(tree))+'\n',encoding='utf8');changed.append(dict(old=before,new=ref(p)))
p=new/'payload/temporary_parent.py';s=p.read_text(encoding='utf8');assert s.count("('sdk', 'native', 'fullrestore', 'train')")==1;s=s.replace("('sdk', 'native', 'fullrestore', 'train')","('native', 'fullrestore', 'train')")
s=s.replace('except psutil.Error:', 'except (psutil.Error,OSError):')
anchor='assert peakrss * 1.25 + 536870912 < 20000000000 and peakhard * 1.25 + 536870912 < 20000000000'
assert s.count(anchor)==1
s=s.replace(anchor,'assert peakrss * 1.25 + 536870912 < 20000000000 and peakhard + 512*256*24*16*4 + 1073741824 + 33554432 < 18000000000')
p.write_text(s,encoding='utf8');compile(s,str(p),'exec')
# IndependentN-agnostic actor/Adam schema before same512 restoration.
p=new/'payload/temporary_state_binding.py';s=p.read_text(encoding='utf8');anchor="assert len(perenv_inventory(ck)) == 99 and floating_count(ck) == 107";assert s.count(anchor)==1
s=s.replace(anchor,anchor+"\n a=ck['actor_state_dict'];assert list(a)==['distribution.std_param','mlp.0.weight','mlp.0.bias','mlp.2.weight','mlp.2.bias','mlp.4.weight','mlp.4.bias','mlp.6.weight','mlp.6.bias']\n assert a['distribution.std_param'].shape==(6,) and a['mlp.0.weight'].shape==(256,35) and a['mlp.6.weight'].shape==(6,64) and a['mlp.6.bias'].shape==(6,) and ck['critic_state_dict']['mlp.0.weight'].shape==(256,38)\n assert ck['optimizer_state_dict']['param_groups'][0]['params']==list(range(17))\n for pid,shape in ((0,(6,)),(7,(6,64)),(8,(6,))):\n  for key in ('exp_avg','exp_avg_sq'):assert ck['optimizer_state_dict']['state'][pid][key].shape==shape")
# Indent the inserted validatorblock to its enclosing function's4space AST layout.
lines=s.splitlines();start=next(i for i,z in enumerate(lines) if z.startswith(' a=ck'));end=start
while end<len(lines) and (lines[end].startswith(' ') and not lines[end].startswith('    ')):end+=1
# New source fragment hasone/twoleading spaces; add3 to every inserted line.
for i in range(start,start+5):lines[i]='   '+lines[i]
s='\n'.join(lines)+'\n';compile(s,str(p),'exec');p.write_text(s,encoding='utf8')
sys.path.insert(0,str(new/'payload'));import torch;assert not torch.cuda.is_initialized()
import original_full20k_binding as oldbinding
from selected_source_projection import project_tree
mf=json.loads((old/'TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json').read_bytes());ck=oldbinding.validate(torch.load(mf['source']['path'],map_location='cpu',weights_only=False),mf['source']['sha256']);rng=torch.get_rng_state().clone();ids=torch.linspace(0,19999,512).round().long();changes=[];small=project_tree(ck,ids,changes=changes);assert len(changes)==99 and oldbinding.floating_count(small)==107 and torch.equal(rng,torch.get_rng_state())
for key in ('actor_state_dict','critic_state_dict','optimizer_state_dict','sensor_global_rng_state','sensor_command_DR_rng_state','sensor_physical_DR_rng_state'):assert oldbinding.same(small[key],ck[key])
fixture=new/'reports/SELECTED512_CPU_SCHEMA_FIXTURE_NOT_GPU_SOURCE.pt';torch.save(small,fixture);assert oldbinding.same(small,torch.load(fixture,map_location='cpu',weights_only=False))
cpu=dict(epoch=time.time(),passed=True,no_GPU_or_PPO=True,actual_target_environment_root=str(r),scope=str(new),num_envs=512,source=mf['source'],floating107=True,projected_fields99=True,all_nonperenv_actorcritic_Adam_globalnamed_privateRNG_exact=True,CPU_fixture=ref(fixture),actual_family_GPU_selection_pending=True,old_native2048_failure_preserved=True,SDK10_actual_reused=ref(sdk_path),SDK_allocator_actual4M_aggregate_stricter_than_new8M_increased_only=True,original_scalar_physical_tolerances_unmodified=True)
cp=new/'reports/TARGET_TEMP512_CPU_PASSED_ACTUAL.json';cp.write_text(json.dumps(cpu,indent=2),encoding='utf8')
mf.update(scope_root=str(new),epoch=time.time(),num_envs=512,target_CPU_receipt=ref(cp),SDK10_actual_reused_receipt=ref(sdk_path),native_capacity_failure_repair=dict(original2048_requestedAggregateCapacity=17891328,old4Moverflow_failed=True,newN512=True,newAggregatePairsCapacity=8388608,not_actualcapacitypass_until_new_native=True),concrete_future_training_trace_upper_bound_bytes=512*256*24*16*4,original_physical_RAM_25percent_headroom_retained=True,new_commit_guard_explicit_trace_plus1GiB_plus32MiB_below18GB=True)
mf['temporary_small_batch_capacities']['gpu_found_lost_aggregate_pairs_capacity']=8388608;mf['admitted_Windows20k_GPU_buffer_capacities']['gpu_found_lost_aggregate_pairs_capacity']=8388608
mf['substep_readback_V6']['source_sha256']=H(new/'payload/windows4090_substep_readback_v6.py')
mf['sourcefreeze_files']=[ref(p) for base in (new/'runtime2048',new/'payload',r/'sdk_exact/source',r/'sdk_exact/apps') for p in sorted(base.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and '.egg-info' not in str(p)]
f=new/'TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json';f.write_text(json.dumps(mf,indent=2),encoding='utf8');l=new/'TEMPORARY_SEQUENCE_TASK_LEASE_GRANTED.json';l.write_text(json.dumps(dict(epoch=time.time(),case_id='temporary512_memory20GB_native_capacity_sequence_v7',approved_GPU_scope=True,mode='native',scope_root=str(new),environment_root=str(r),shared_gpu_lock=str(r/'WINDOWS4090_GPU_EXCLUSIVE.lock'),manifest_sha256=H(f),human20GB_temporary_branch_authorized=True),indent=2),encoding='utf8')
proof=dict(epoch=time.time(),passed_CPU_only=True,targetCPU=cpu,old_native_log=ref(old/'attempts/temporary2048_native_v1/worker_stdout.log'),old_parent_error=error,old_NATIVE_noPPO_initfailure=True,actual_old_PID_andOSlock_free=True,source_changes=changed,new_manifest=ref(f),original_20kguards_not_changed=True)
(new/'reports/NATIVE_CAPACITY512_TARGET_CPU_ACTUAL.json').write_text(json.dumps(proof,indent=2),encoding='utf8');print(json.dumps(proof))
