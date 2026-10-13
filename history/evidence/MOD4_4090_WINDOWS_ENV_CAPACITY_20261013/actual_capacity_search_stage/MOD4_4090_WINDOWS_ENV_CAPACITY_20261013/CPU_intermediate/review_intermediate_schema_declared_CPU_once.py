from pathlib import Path
import torch,json,time,copy
import expanded_source_projection as e
D=Path(__file__).resolve().parent
p=D/'retained_input/OWN128_PPO_SAVED_SOURCE_RETAINED.pt'
sha='f1d3ddf129c81cfc83735d230058abce6b81702cd9a479776d7e31d826636db3'
assert e.H(p)==sha and not torch.cuda.is_initialized()
source=torch.load(p,map_location='cpu',weights_only=False);e.validate_parent128(source)
rng=torch.get_rng_state().clone();fields,_=e.schema();rows=[];negative=[]
for n in (640,768):
 out,proof=e.materialize(p,expected_source_sha=sha,target_n=n,output_dir=D/f'candidate{n}')
 child=torch.load(out,map_location='cpu',weights_only=False);mapping=e.repeat_index(n)
 for row in fields:
  a=e.at(source,row['tokens']);b=e.at(child,row['tokens']);assert e.same(b,a.index_select(0,mapping)) and b.data_ptr()!=a.data_ptr()
 for key in ('actor_state_dict','critic_state_dict','optimizer_state_dict','sensor_global_rng_state','sensor_command_DR_rng_state','sensor_physical_DR_rng_state','WINDOWS4090_LEFT_HEAD_REPAIR_ACTUAL','WINDOWS4090_TEMPORARY_BACKEND_BINDING'):assert e.same(child[key],source[key])
 states={k:copy.deepcopy(child[k]) for k in e.STATES};bound,changes=e.bind_runtime_metadata_once(child,target_n=n,actual_states=states,approved_code_changes={});assert not changes and e.require_same_runtime_metadata(bound,target_n=n,actual_states=states)
 for label,change in [('duplicate_child_slot',lambda c:c['WINDOWS4090_EXPANDED_ENV_BRANCH']['child_slot_ids'].__setitem__(1,0)),('wrong_parent_slot',lambda c:c['WINDOWS4090_EXPANDED_ENV_BRANCH']['parent_slot_ids'].__setitem__(0,127)),('wrong_assignment',lambda c:c['E1_terrain_state'].__setitem__('entry_assignment_sha256','0'*64)),('wrong_map',lambda c:c['E1_terrain_state'].__setitem__('entry_map_sha256','0'*64)),('wrong_perenv_shape',lambda c:c['sensor_DR_state'].__setitem__('bias',torch.zeros((n+1,4)))),('wrong_network_dimension',lambda c:c['actor_state_dict'].__setitem__('mlp.2.weight',torch.zeros((n,256)))),('repeated_initializer',lambda c:c['WINDOWS4090_EXPANDED_ENV_BRANCH'].__setitem__('left_initializer_repeated',True))]:
  bad=copy.deepcopy(child);change(bad)
  try:e.validate_expanded(bad,target_n=n)
  except (AssertionError,KeyError):negative.append(dict(N=n,label=label,rejected=True))
  else:raise AssertionError(label)
 rows.append(dict(n=n,candidate=str(out),sha256=e.H(out),all99_exact_independentstorage=True,fullactorcritic_Adam_privateRNG_exact=True,no_initializer_repeat=True,CPU_synthetic_binding_not_GPU_pass=True))
assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
report=dict(epoch=time.time(),passed=True,parent_actual121_update_final_SHA=sha,num_targets=[640,768],component_SHA=e.H(D/'expanded_source_projection.py'),fixed99_schema_SHA=e.H(D/'PERENV128_SCHEMA_V1.json'),candidates=rows,strict_negatives=negative,no_CPU_RNG_no_CUDA=True,old_component_false_preserved=True)
q=D/'EXPANDED_OWN_FINAL128_TO640_768_CPU_ACTUAL_REVIEW.json';assert not q.exists();q.write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(dict(report=str(q),CPU_only=True,strict_negatives=len(negative))))
