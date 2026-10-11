"""CPU inspection of actual saved origins, first trace, and collision bank. No restore."""
from second50_io import *
CODE = r'''
from pathlib import Path
import torch,numpy as np,json,hashlib,time
torch.set_num_threads(1)
v=json.loads(INPUT_TOKEN);p=Path(v['checkpoint']['path']);module=Path(ROOT_TOKEN)/'isaac/mod4'
def h(p):
 a=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):a.update(b)
 return a.hexdigest()
assert h(p)==v['checkpoint']['sha256']
ck=torch.load(p,map_location='cpu',weights_only=False);s=ck['E1_terrain_state'];xy=s['spawn_xy'].numpy()
trace=Path(v['trace']['path']);assert h(trace)==v['trace']['sha256']
with np.load(trace) as z:row=z['rows'][0].copy();columns=z['columns'].tolist()
bank=module/'MOD4_RESET_COLLISION_BANK.npz';assert h(bank)==s['reset_bank_sha256']
with np.load(bank) as z:
 pick=int(np.argmin(abs(z['root_height']-.25)));points=z['points_root'][pick];q=z['q'][pick]
manifest=json.loads((p.parent/'run_manifest.json').read_bytes())
assert xy.shape==(20000,2) and np.array_equal(xy,row[:,:2])
profile=json.loads((module/'g4_cad_profile.json').read_bytes())
assert h(module/'g4_cad_profile.json')==s['G4_profile_sha256']
ids=np.flatnonzero(row[:,10]==4);rc=np.floor(xy[ids]/9.+20).astype(int);center=(rc-20+.5)*9.;off=xy[ids]-center
assert len(ids)==2820 and np.all((rc>=0)&(rc<40))
assert set(rc[:,1])==set(range(34,40)) and (off>=-4.5).all() and (off<4.5).all()
half=profile['span_m']*.5;extent=np.max(abs(points[:,:2]),axis=0)
before=(off[:,0]+extent[0]<-half);after=(off[:,0]-extent[0]>half);inside=abs(off[:,0])<=half
hist={}
for side,mask in [('left',off[:,0]<0),('right',off[:,0]>=0)]:
 c=row[ids[mask],7];hist[side]={'environments':int(mask.sum()),'negative':int((c<0).sum()),'positive':int((c>0).sum()),'standing':int((c==0).sum())}
assert not torch.cuda.is_initialized()
out=dict(epoch=time.time(),passed=True,source386_own_checkpoint=dict(path=str(p),bytes=p.stat().st_size,sha256=h(p)),
 actual_saved_terrain_identity={k:x for k,x in s.items() if not torch.is_tensor(x)},
 actual_first_trace=dict(v['trace'],columns=columns,first_reset_spawn_xy_exact=True),
 reset_bank=dict(path=str(bank),bytes=bank.stat().st_size,sha256=h(bank),selected_pose_index=pick,complete_sampled_collision_points=len(points),extent_xy=extent.tolist()),
 actual_Wave_initial_cohort=len(ids),actual_current_root_cell_rows=sorted(set(rc[:,0].tolist())),actual_current_root_cell_columns=sorted(set(rc[:,1].tolist())),
 actual_grid_pitch_m=9.,grid_verified_by_saved_bounds_family_and_original_source=False,
 initial_root_offset_x_range_m=[float(off[:,0].min()),float(off[:,0].max())],initial_root_offset_y_range_m=[float(off[:,1].min()),float(off[:,1].max())],
 root_centers_inside_ten_wave_span=int(inside.sum()),full_axis_aligned_sampled_footprint_before_wave=int(before.sum()),full_axis_aligned_sampled_footprint_after_wave=int(after.sum()),
 first_control_side_command_histogram=hist,
 ten_wave_span_m=profile['span_m'],profile_path=str(module/'g4_cad_profile.json'),profile_sha256=h(module/'g4_cad_profile.json'),
 original_route_boundary_from_spawn_m=2.,whole_test_route_nominal_distance_m=profile['span_m']+.4+.2,
 entry_repair_cannot_claim_whole_test_route_inside_original2m_training_truncation=True,
 current_root_cell_not_permanent_family=True,root_and_footprint_CPU_proxy_not_physical_contact_or_causal_proof=True,
 CPU_only_no_RNG_draw_no_restore_no_GPU_or_budget_write=True)
print(json.dumps(out))
'''
def main():
 own=json.loads(max(R.glob('SECOND50_OWN_FORMAL_CPU_ACTUAL_[0-9]*.json'),key=lambda p:int(p.stem.rsplit('_',1)[1])).read_bytes())
 trace=json.loads(max(R.glob('SECOND50_FULL_TRAINING_TRACE_ACTUAL_[0-9]*.json'),key=lambda p:int(p.stem.rsplit('_',1)[1])).read_bytes())
 n,w=io.connect_both()
 try:
  out=run(n,CODE.replace('INPUT_TOKEN',repr(json.dumps(dict(checkpoint=own['own_checkpoint'],trace=trace['full_saved_trace_indices'][0])))).replace('ROOT_TOKEN',repr(ROOT)))
  p=save('SECOND50_SAVED_ENTRY_IDENTITY_CPU_ACTUAL_'+str(time.time_ns())+'.json',out)
  print(json.dumps(dict(report=str(p),passed=out['passed'],histogram=out['first_control_side_command_histogram'],inside=out['root_centers_inside_ten_wave_span'],before=out['full_axis_aligned_sampled_footprint_before_wave'],after=out['full_axis_aligned_sampled_footprint_after_wave'],extent=out['reset_bank']['extent_xy'])))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('SAVED_ENTRY_CPU_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_training_replay=True));raise
