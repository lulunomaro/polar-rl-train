"""Independent CPU math fixture on actual own412/native410 inputs, no GPU/runtime install."""
from entry_second_io import *
CPUROOT='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_DIRECTION_COMPONENT_CPU_20261012'
def latest(pattern):return max(R.glob(pattern),key=lambda p:int(p.stem.rsplit('_',1)[1]))
def main():
 assert not (R/'DIRECTION_COMPONENT_CPU_PASSED.json').exists()
 own=json.loads(latest('ENTRY_SECOND_OWN_FORMAL_CPU_ACTUAL_[0-9]*.json').read_bytes());trace=json.loads(latest('ENTRY_SECOND_FULL_TRAINING_TRACE_ACTUAL_[0-9]*.json').read_bytes());pair=json.loads(latest('ENTRY_SECOND_DIRECT148_PREFIX_ACTUAL_[0-9]*.json').read_bytes())
 assert own['closeout_ready'] and trace['passed'] and pair['passed'] and pair['pairs']['forward']['candidate_complete']==1
 p=D/'direction_cpu_component/wave50_episode_direction_math.py';raw=p.read_bytes();compile(raw,p.name,'exec')
 n,w=io.connect_both()
 try:
  with n.open_sftp() as f:io.put(f,CPUROOT+'/'+p.name,raw)
  v=run(n,r'''from pathlib import Path
import json,time,hashlib,sys,numpy as np,torch,copy
torch.set_num_threads(1);D=Path(CPUROOT_TOKEN);sys.path.insert(0,str(D));import wave50_episode_direction_math as component
actualroot=Path(ROOT_TOKEN);module=actualroot/'isaac/mod4';sys.path[:0]=[str(actualroot),str(module)];import supervise_wave50_entry_second_bounded_once as wrapper
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();info=json.loads(INPUT_TOKEN);cp=Path(info['checkpoint']['path']);assert h(cp)==info['checkpoint']['sha256'];ck=torch.load(cp,map_location='cpu',weights_only=False);s=ck['E1_terrain_state'];xy=s['spawn_xy'].numpy();t=Path(info['trace']['path']);assert h(t)==info['trace']['sha256']
with np.load(t) as z:row=z['rows'][0].copy()
assert np.array_equal(xy,row[:,:2]) and xy.shape==(20000,2)
native=Path('/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ENTRY_INITIALIZATION_REVIEWED_20261012/WAVE50_NATIVE20K.json');native_value=json.loads(native.read_bytes());assignments=native_value['actual_generated_family_assignments'];assert len(assignments)==1600
bank=module/'MOD4_RESET_COLLISION_BANK.npz';assert h(bank)==s['reset_bank_sha256']
with np.load(bank) as z:pick=int(np.argmin(abs(z['root_height']-.25)));points=z['points_root'][pick];extent=np.max(abs(points[:,:2]),axis=0)
profile=json.loads((module/'g4_cad_profile.json').read_bytes());assert h(module/'g4_cad_profile.json')==s['G4_profile_sha256'];half=profile['span_m']*.5
assert h(D/'wave50_episode_direction_math.py')==MATH_SHA_TOKEN
cpu_rng=torch.get_rng_state().clone();np_rng=np.random.get_state();cache=component.OriginBoundCPUCache();mask,sign=cache.current(xy,assignments,half,extent);original=row[:,7:10];out=component.apply(original,mask,sign)
assert int(mask.sum())==2820 and np.array_equal(mask,row[:,10]==4) and np.array_equal(out[~mask],original[~mask]) and np.array_equal(abs(out[mask,0]),abs(original[mask,0])) and np.array_equal(out[mask,0]==0,original[mask,0]==0)
assert (out[mask,0]*sign[mask]>=0).all() and np.array_equal(out[:,1:],original[:,1:])
ids=np.flatnonzero(mask);mutated=xy.copy();i=int(ids[0]);center=(np.floor(xy[i]/9.+20)-20+.5)*9.;mutated[i,0]=2*center[0]-xy[i,0];oldkey=cache.key;mask2,sign2=cache.current(mutated,assignments,half,extent);assert cache.key!=oldkey and sign2[i]==-sign[i] and np.array_equal(mask2,mask)
mask3,sign3=cache.current(xy,assignments,half,extent);assert np.array_equal(mask3,mask) and np.array_equal(sign3,sign)
rejected=[]
for name,xx,aa in [('duplicate_assignment',xy,assignments+[next(a for a in assignments if a['family']=='random_uniform_for_rm')]),('inside_wave_footprint',np.where(np.arange(20000)[:,None]==i,center[None,:],xy).astype('<f4'),assignments)]:
 try:component.bind(xx,aa,half,extent)
 except AssertionError:rejected.append(name)
 else:raise AssertionError('Invalid entry accepted:'+name)
fixture=D/'actual20k_direction_component_fixture.npz';np.savez_compressed(fixture,xy=xy,original=original,mask=mask,sign=sign,command=out)
with np.load(fixture) as z:assert np.array_equal(z['xy'],xy) and np.array_equal(z['command'],out) and np.array_equal(component.apply(z['original'],z['mask'],z['sign']),out)
source=Path(SOURCE35_TOKEN);source_info=wrapper.prior.inherited.fullsave(source);assert h(source)==SOURCE35_SHA_TOKEN and source_info['finite_tensors']==102
assert torch.equal(cpu_rng,torch.get_rng_state());now=np.random.get_state();assert np_rng[0]==now[0] and np.array_equal(np_rng[1],now[1]) and np_rng[2:]==now[2:] and not torch.cuda.is_initialized()
v=dict(epoch=time.time(),passed=True,CPU_component_only=True,CPU_root=str(D),actual_math_path=str(D/'wave50_episode_direction_math.py'),math_SHA=h(D/'wave50_episode_direction_math.py'),actual_inputs=dict(own412_checkpoint=info['checkpoint'],first_trace=info['trace'],native410=dict(path=str(native),bytes=native.stat().st_size,sha256=h(native)),complete1600_assignment_count=1600,entry_map_SHA=s['entry_map_sha256'],collision_bank_SHA=h(bank),complete_collision_points=len(points),complete_footprint_extent_xy=extent.tolist()),actual20k_Wave2820=int(mask.sum()),other17180_commands_exact=True,original_absolute_speed_standing_vy_yaw_exact=True,old_random_draw_inputs_preserved=True,no_CPU_RNG_draw=True,actual_origin_mutation_cache_refreshed=True,strict_rejections=rejected,fixture=dict(path=str(fixture),bytes=fixture.stat().st_size,sha256=h(fixture),large_original_index_only=True),two_entry_side_fixed_sign_counts=[int((sign>0).sum()),int((sign<0).sum())],approved_initial_source35=source_info,not_default_unqualified_ea9_or9bfe=True,no_live_position_heading_correction_teacher_truth_actor_gate=True,no_geometry_reset_reward_LR_DR_clock_hardware_or_route_change=True,no_target_fullstate_admission_or_SDK_native_CUDA_PPO_formal_claim=True,not_causal_failure_or_learning_proof=True,no_CUDA_initialized=True,no_GPU_or_budget_write=True)
q=D/'DIRECTION_COMPONENT_CPU_PASSED.json';assert not q.exists();q.write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('CPUROOT_TOKEN',repr(CPUROOT)).replace('ROOT_TOKEN',repr(ROOT)).replace('INPUT_TOKEN',repr(json.dumps(dict(checkpoint=own['own_checkpoint'],trace=trace['full_saved_trace_indices'][0])))).replace('MATH_SHA_TOKEN',repr(H(raw))).replace('SOURCE35_TOKEN',repr(old.SOURCE)).replace('SOURCE35_SHA_TOKEN',repr(old.SOURCE_SHA)))
  save('DIRECTION_COMPONENT_CPU_PASSED.json',v);print(json.dumps(dict(component_CPU_passed=True,actual_Wave2820=v['actual20k_Wave2820'],other17180_exact=True,no_new_GPU_or_learning=True)))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('DIRECTION_COMPONENT_CPU_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_budget_write=True));raise
