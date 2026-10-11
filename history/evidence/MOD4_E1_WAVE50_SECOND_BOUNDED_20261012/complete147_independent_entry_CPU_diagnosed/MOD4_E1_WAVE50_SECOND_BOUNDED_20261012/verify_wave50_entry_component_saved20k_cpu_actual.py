"""Execute new CPU component against actual own saved20k origins/native assignments."""
from second50_io import *
CODE=r'''
from pathlib import Path
import torch,numpy as np,json,hashlib,time,types
torch.set_num_threads(1);v=json.loads(INPUT_TOKEN)
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=Path(v['checkpoint']['path']);assert h(p)==v['checkpoint']['sha256'];ck=torch.load(p,map_location='cpu',weights_only=False)
module=Path(ROOT_TOKEN)/'isaac/mod4';native=Path(OLD_TOKEN)/'WAVE50_NATIVE20K.json';a=json.loads(native.read_bytes())
assign=a['actual_generated_family_assignments'];assert isinstance(assign,list) and len(assign)==1600
assert hashlib.sha256(json.dumps(assign,sort_keys=True,separators=(',',':')).encode()).hexdigest()==ck['E1_retained_flat_command_state']['assignment_sha256']
assert ck['E1_terrain_state']['G4_height_peak_to_trough_m']==.05 and a['E1_terrain_identity']=={k:x for k,x in ck['E1_terrain_state'].items() if k not in ('spawn_xy','reset_expected_q','episode')}
orig=ck['E1_terrain_state']['spawn_xy'].numpy();assert np.array_equal(np.array(a['reset_root_before_physics'])[:,:2],orig)
profile=json.loads((module/'g4_cad_profile.json').read_bytes());assert h(module/'g4_cad_profile.json')==ck['E1_terrain_state']['G4_profile_sha256']
bank=module/'MOD4_RESET_COLLISION_BANK.npz';assert h(bank)==ck['E1_terrain_state']['reset_bank_sha256']
with np.load(bank) as z:pick=int(np.argmin(abs(z['root_height']-.25)));points=z['points_root'][pick].copy()
component=types.ModuleType('wave50_entry_v1_math');exec(compile(SOURCE_TOKEN,'wave50_entry_v1_math.py','exec'),component.__dict__)
cache=component.OriginBoundEntryCache();xy,report=cache.get(orig,assign,points,profile['span_m']);same,same_report=cache.get(orig,assign,points,profile['span_m'])
assert np.array_equal(same,xy) and same_report['cache_builds']==1
shifted=orig.copy();shifted[0,1]+=.001;new,new_report=cache.get(shifted,assign,points,profile['span_m']);assert new_report['cache_builds']==2 and new_report['actual_input_identity_sha256']!=same_report['actual_input_identity_sha256'] and new[0,1]==shifted[0,1]
assert report['Wave_environments']==2820 and report['other_environments_unchanged']==17180 and report['changed_environments']==2820
rejected=[]
bad=points.copy();bad[0,0]=.4
for name,args in [('wrong_footprint',(orig,assign,bad,profile['span_m'])),('duplicate_assignment',(orig,assign+[assign[0]],points,profile['span_m'])),('wrong_span',(orig,assign,points,7.))]:
 try:component.entry_map(*args)
 except ValueError:rejected.append(name)
 else:raise AssertionError('Strict rejection missing: '+name)
assert len(rejected)==3 and not torch.cuda.is_initialized()
print(json.dumps(dict(epoch=time.time(),passed=True,stage='CPU_component_only_not_target_GPU_or_learning_admission',
 source386_own_checkpoint=v['checkpoint'],original_native_actual=dict(path=str(native),bytes=native.stat().st_size,sha256=h(native)),
 exact_actual_assignment_sha256=ck['E1_retained_flat_command_state']['assignment_sha256'],full1600_actual_assignments_matched=True,
 native_initial20k_origin_own_saved_spawn_exact=True,reset_bank=dict(path=str(bank),bytes=bank.stat().st_size,sha256=h(bank),selected_pose_index=pick,points=len(points)),
 component_sha256=hashlib.sha256(SOURCE_TOKEN.encode()).hexdigest(),map=report,actual_origin_mutation_invalidates_cache=True,
 same_input_cache_exact=True,strict_rejections=rejected,CPU_only_no_cuda_no_rng_draw_no_restore_no_canonical_write=True,
 no_SDK_native_fullstate_PPO_fresh_formal_dispatch=True,no_qualified50_or70mm_claim=True)))
'''
def main():
 source=D/'wave50_entry_cpu_component/wave50_entry_v1_math.py';own=json.loads(max(R.glob('SECOND50_OWN_FORMAL_CPU_ACTUAL_[0-9]*.json'),key=lambda p:int(p.stem.rsplit('_',1)[1])).read_bytes())
 n,w=io.connect_both()
 try:
  v=run(n,CODE.replace('INPUT_TOKEN',repr(json.dumps(dict(checkpoint=own['own_checkpoint'])))).replace('ROOT_TOKEN',repr(ROOT)).replace('OLD_TOKEN',repr(OLD)).replace('SOURCE_TOKEN',repr(source.read_text(encoding='utf8'))))
  p=save('WAVE50_ENTRY_V1_SAVED20K_CPU_COMPONENT_ACTUAL_'+str(time.time_ns())+'.json',v);print(json.dumps(dict(report=str(p),passed=v['passed'],map_SHA=v['map']['map_sha256'],changed=v['map']['changed_environments'],no_GPU=True)))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('ENTRY_COMPONENT_CPU_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_training_replay=True));raise
