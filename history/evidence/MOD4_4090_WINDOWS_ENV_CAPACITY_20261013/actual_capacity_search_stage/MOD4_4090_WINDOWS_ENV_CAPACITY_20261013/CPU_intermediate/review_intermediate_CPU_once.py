"""Actualown128 snapshot expansion proofs only; no launch or latestfinal claim."""
from pathlib import Path
import copy,hashlib,json,os,shutil,time,traceback
import torch
import expanded_source_projection as e
W=Path('C:/Users/lulu/Desktop/claude/mjcf');D=Path(__file__).resolve().parent
INPUT=W/'MOD4_4090_WINDOWS_TEMP20GB_20261013/OWN_PPO_CPU_INPUTS_1791894571823537900'
def ref(p):return dict(path=str(p),bytes=Path(p).stat().st_size,sha256=e.H(p))
def fresh(p,value):
 with Path(p).open('xb') as f:f.write(json.dumps(value,indent=2).encode());f.flush();os.fsync(f.fileno())
def main():
 assert not torch.cuda.is_initialized()
 collection=json.loads((INPUT/'ACTUAL_COLLECTION.json').read_bytes());row=next(x for x in collection['files'] if Path(x['local_actual_path']).name=='OWN_PPO_SAVED.pt');p=Path(row['local_actual_path'])
 assert e.H(p)==row['sha256']=='f1d3ddf129c81cfc83735d230058abce6b81702cd9a479776d7e31d826636db3'
 inputs=D/'retained_input';assert not inputs.exists();inputs.mkdir();retained=inputs/'OWN128_PPO_SAVED_SOURCE_RETAINED.pt';shutil.copy2(p,retained);assert e.H(retained)==row['sha256']
 shutil.copy2(INPUT/'ACTUAL_COLLECTION.json',inputs/'ACTUAL_COLLECTION_ORIGINAL.json')
 source=torch.load(retained,map_location='cpu',weights_only=False);fields=e.inventory(source,128)
 assert len(fields)==99
 assert fields==json.loads(schema.read_bytes())['fields']
 e.validate_parent128(source);rng=torch.get_rng_state().clone();reports=[];negatives=[]
 for n in (640,768):
  out,proof=e.materialize(retained,expected_source_sha=row['sha256'],target_n=n,output_dir=D/('candidate'+str(n)))
  child=torch.load(out,map_location='cpu',weights_only=False);mapping=e.repeat_index(n)
  for path in fields:
   a=e.at(source,path['tokens']);b=e.at(child,path['tokens']);assert e.same(b,a.index_select(path['axis'],mapping)) and a.data_ptr()!=b.data_ptr()
  for k in ('actor_state_dict','critic_state_dict','optimizer_state_dict','sensor_global_rng_state','sensor_command_DR_rng_state','sensor_physical_DR_rng_state','WINDOWS4090_LEFT_HEAD_REPAIR_ACTUAL','WINDOWS4090_TEMPORARY_BACKEND_BINDING'):
   assert e.same(child[k],source[k]),k
  # Test caller-visible binding against CPU copies, not an actualGPU birth.
  states={k:copy.deepcopy(child[k]) for k in e.STATES};bound,changes=e.bind_runtime_metadata_once(child,target_n=n,actual_states=states,approved_code_changes={})
  assert not changes and e.require_same_runtime_metadata(bound,target_n=n,actual_states=states)
  for label,mutate in (
   ('duplicate_child_slot',lambda c:c['WINDOWS4090_EXPANDED_ENV_BRANCH']['child_slot_ids'].__setitem__(1,0)),
   ('wrong_parent_slot',lambda c:c['WINDOWS4090_EXPANDED_ENV_BRANCH']['parent_slot_ids'].__setitem__(0,127)),
   ('wrong_assignment',lambda c:c['E1_terrain_state'].__setitem__('entry_assignment_sha256','0'*64)),
   ('wrong_perenv_shape',lambda c:c['sensor_DR_state'].__setitem__('bias',torch.zeros((n+1,4)))),
   ('changed_actor_hidden128',lambda c:c['actor_state_dict'].__setitem__('mlp.2.weight',torch.zeros((n,256)))),
   ('initializer_repeated',lambda c:c['WINDOWS4090_EXPANDED_ENV_BRANCH'].__setitem__('left_initializer_repeated',True)),
   ('wrong_map',lambda c:c['E1_terrain_state'].__setitem__('entry_map_sha256','0'*64))):
   bad=copy.deepcopy(child);mutate(bad)
   try:e.validate_expanded(bad,target_n=n)
   except (AssertionError,KeyError):negatives.append(dict(N=n,case=label,rejected=True))
   else:raise AssertionError(('negative accepted',n,label))
   del bad
  changedstates=copy.deepcopy(states);changedstates['E1_WAVE50_route_lifecycle_state']['parent_boundary_source_sha256']='0'*64
  try:e.require_same_runtime_metadata(bound,target_n=n,actual_states=changedstates)
  except AssertionError:negatives.append(dict(N=n,case='sameN_runtime_metadata_rebind',rejected=True))
  else:raise AssertionError('same metadata changed')
  physical=copy.deepcopy(states);physical['E1_terrain_state']['command_vx_range']=[-.9,.9]
  try:e.bind_runtime_metadata_once(child,target_n=n,actual_states=physical,approved_code_changes={})
  except AssertionError:negatives.append(dict(N=n,case='first_binding_physical_command_change',rejected=True))
  else:raise AssertionError('physicalcommand wrongly migrated')
  reports.append(dict(num_envs=n,actual_CPU_candidate=ref(out),CPU_proof=ref(out.parent/'CPU_EXPANSION_ACTUAL.json'),family_counts=child['WINDOWS4090_TEMPORARY_BRANCH']['family_counts'],unique_child_slot_count=len(set(child['WINDOWS4090_EXPANDED_ENV_BRANCH']['child_slot_ids'])),unique_20k_ancestor_count=len(set(child['WINDOWS4090_TEMPORARY_BRANCH']['source_original_ids'])),repeat_copies_per_parent=n//128,actorcriticAdam_histograms_privateRNG_exact=True,all99_independentstorage_exact=True,CPU_disk_roundtrip_exact=True,finite_floating_count=e.floating_count(child),CPU_synthetic_binding_test_not_actual_runtime_pass=True,max256updates_float32_retention_RAM_bytes=256*24*n*16*4,one_update_controls24=True,one_update_envsteps=24*n))
  del child,bound,states,changedstates,physical
 try:e.expand_tree(source,source_sha=e.DONOR_SHA,target_n=256)
 except AssertionError:negatives.append(dict(case='old20k_donor_SHA_instead_of_repaired128',rejected=True))
 else:raise AssertionError('oldsource permitted')
 bad=copy.deepcopy(source);bad.pop('WINDOWS4090_LEFT_HEAD_REPAIR_ACTUAL')
 try:e.expand_tree(bad,source_sha=row['sha256'],target_n=256)
 except (AssertionError,KeyError):negatives.append(dict(case='missing_actual_left_repair_receipt',rejected=True))
 else:raise AssertionError('missingrepair accepted')
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized() and e.H(p)==e.H(retained)==row['sha256']
 report=dict(epoch=time.time(),passed_CPU_projection_and_disk_only=True,source_original=ref(p),retained_immutable_source=ref(retained),actual_original_collection=ref(INPUT/'ACTUAL_COLLECTION.json'),source_is_actual_121_update_complete_own128_final=True,latest_STOP_fullsave_source_used_after_actual_boundary=True,component=ref(D/'expanded_source_projection.py'),schema=ref(schema),candidates=reports,strict_negative_cases=negatives,source_unchanged=True,no_CPU_RNG_draw_no_CUDA_no_network_no_GPU=True,no_left_initializer_called=True,
  integration=['Root must use actual fullsave-stop/PIDcreation/parentcost/exited/OSlockfree boundary; these CPU candidates are from retained2-update snapshot for math only.','Use component expand_tree or materialize with actual latest own128 SHA; never d05c20k state splice or91d localactor.','Provide fixed PERENV128_SCHEMA_V1.json beside module. All99 fields expand along declared axis0, all hidden128 neural/Adam tensors remain unchanged.','New source_original_ids intentionally repeat original20k ancestry; only child_slot_ids must be unique0..N-1 and parent_slot_ids exactly arangeN%128.','Current13 state countfields and computed spawn/map/origin/inputSHA change explicitly; no spawnXY/currentcommands/DR/geometry/LR/reward modifications. Original1600assignmentSHA remains exact.','Keep historical128 backend andleft repair receipts exactly; do not claim their API offsets were actually verified fornewN. Separate ownnewNoffset/defaultq verification must precede learning.','At actual birth use bind_runtime_metadata_once only for approved codehash changes; physical values/map hashes must already exact. Same expanded resumes require_same_runtime_metadata with no rebinding.','After new12 CPUCUDA fullstate disk roundtrip, source parent-slot episode+1, actualnative scope physical/resource pass, saveownnewNfullstate; preserve newexpandedbranch in each ownsave. Never rerunleft initializer.','Copies begin with correlated parent perenvstate; future vectorlength changes draw consumption while saved private/global RNG bytes are retained. This is declared newN scope, not PhysXexactresume or fresh independent resampling.','Capacity/throughput optimality needs root actual20GB-bound native/probe/PPO measurements; checkpointbytes and traceformula do not prove peakRAM or GPUcapacity.'])
 path=D/'EXPANDED_OWN_FINAL128_TO640_768_CPU_ACTUAL_REVIEW.json';fresh(path,report)
 print(json.dumps(dict(report=str(path),sha256=e.H(path),candidates=[x['actual_CPU_candidate'] for x in reports],strict_negative_cases=len(negatives),CPU_pass_only=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  fresh(D/('EXPANSION_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_no_network=True,no_original_source_modified=True));raise
