"""Read own saved full training trace on CPU; no replay, restore or RNG draws."""
from direction_io import *
import traceback

def main():
    p=sorted(R.glob('EXPOSURE_MATCHED_OWN_FORMAL_CPU_ACTUAL_[0-9]*.json'))[-1]
    own=json.loads(p.read_bytes())
    assert own['passed'] and own['closeout_ready'] and own['actual_source_count']==424
    n,w=io.connect_both()
    try:
        code=r'''from pathlib import Path
import json,hashlib,numpy as np,torch
torch.set_num_threads(1)
own=json.loads(OWN_JSON_TOKEN);ckpath=Path(own['own_checkpoint']['path']);run=ckpath.parent
j=lambda p:json.loads(p.read_bytes())
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert h(ckpath)==own['own_checkpoint']['sha256']
m=j(run/'run_manifest.json');src=Path(m['init_checkpoint']);assert h(src)==own['source_SHA']
ck=torch.load(ckpath,map_location='cpu',weights_only=False);pre=torch.load(src,map_location='cpu',weights_only=False)
s=ck['E1_CURB_entry_direction_state'];ss=pre['E1_CURB_entry_direction_state']
for name in ('curb_mask','entry_sign','reset_xy'):assert torch.equal(s[name],ss[name]),name
mask=s['curb_mask'].numpy();sign=s['entry_sign'].numpy();xy=s['reset_xy'].numpy()
assert mask.sum()==2820
centers=(np.floor(xy/9.)+.5)*9.
a=j(run/'RETENTION_COMMAND_ACTUAL.json');health=j(run/'CLOCK_TRAINING_HEALTH.json')
controls=own['health']['control_steps'];assert controls==health['control_steps']==a['actual_controls']==1104
hist=np.zeros((2,3),dtype=np.int64);indices=[];total=0;first=None
groups=[]
for label,side in [('left_positive',sign>0),('right_negative',sign<0)]:
 ids=np.flatnonzero(mask&side)
 groups.append(dict(entry=label,ids=ids,moving=0,standing=0,command_integral=np.zeros(len(ids)),root_min=np.inf,root_max=-np.inf,
  root_cross_controls=0,root_cross_envs=np.zeros(len(ids),bool),signed_displacement=np.zeros(len(ids)),speed_max=0.))
for name in a['trace_files']:
 p=run/name;assert p.is_relative_to(run)
 with np.load(p) as z:
  assert z['columns'].tolist()==['before_x','before_y','before_z','pre_reset_x','pre_reset_y','pre_reset_z','heading_before','BODY_vx','BODY_vy','signed_yaw','family','eligible','linear','moving','terminated','truncated']
  x=z['rows'];assert x.ndim==3 and x.shape[1:]==(20000,16) and np.isfinite(x).all()
  if first is None:first=x[0,:,7].copy()
  total+=len(x)
  for side,g in enumerate(groups):
   ids=g['ids'];c=x[:,ids,7]
   assert np.max(abs(x[:,ids,8:10]))<=1e-6 and np.min(c*sign[ids])>=-1e-6 and np.max(abs(c))<=.300001
   hist[side]+=np.array([(c<0).sum(),(c>0).sum(),(c==0).sum()])
   g['moving']+=int((c!=0).sum());g['standing']+=int((c==0).sum())
   g['command_integral']+=abs(c).sum(0)*.01;g['speed_max']=max(g['speed_max'],float(abs(c).max()))
   before=x[:,ids,0]-centers[ids,0];after=x[:,ids,3]-centers[ids,0]
   valid=x[:,ids,14]==0;cross=(before*after<0)&valid
   g['root_cross_controls']+=int(cross.sum());g['root_cross_envs']|=cross.any(0)
   g['root_min']=min(g['root_min'],float(after.min()));g['root_max']=max(g['root_max'],float(after.max()))
   g['signed_displacement']+=((x[:,ids,3]-x[:,ids,0])*sign[ids]).sum(0)
 indices.append(dict(path=str(p),bytes=p.stat().st_size,sha256=h(p),original_retained=True,large_index_only=True))
assert total==controls
def modes(x):return np.array([(x<0).sum(),(x>0).sum(),(x==0).sum()])
endpoint=np.zeros((2,3),dtype=np.int64)
for side,g in enumerate(groups):
 ids=g['ids'];endpoint[side]=modes(ck['E1_retained_flat_command_state']['BODY_command'].numpy()[ids,0])-modes(first[ids])
baseline=ss['control_histogram'].numpy();stored=s['control_histogram'].numpy()
assert np.array_equal(stored,baseline+hist+endpoint),dict(inherited=baseline.tolist(),trace_before=hist.tolist(),stored_after=stored.tolist(),endpoint=endpoint.tolist())
result=[]
for g in groups:
 ids=g['ids'];result.append(dict(entry=g['entry'],environments=len(ids),moving_controls=g['moving'],standing_controls=g['standing'],
  maximum_command_abs_m_s=g['speed_max'],nominal_integral_absolute_command_m_range=[float(g['command_integral'].min()),float(g['command_integral'].max())],
  fixed_reset_root_x_offset_abs_m_range=[float(abs(xy[ids,0]-centers[ids,0]).min()),float(abs(xy[ids,0]-centers[ids,0]).max())],
  actual_prereset_root_x_range_m=[g['root_min'],g['root_max']],same_control_signed_root_displacement_sum_range_m=[float(g['signed_displacement'].min()),float(g['signed_displacement'].max())],
  root_center_side_change_control_count=g['root_cross_controls'],root_center_side_change_environment_count=int(g['root_cross_envs'].sum()),
  root_proxy_not_both_wheel_contact_or_fullroute=True))
assert not torch.cuda.is_initialized()
print(json.dumps(dict(epoch=__import__('time').time(),passed=True,own_checkpoint_SHA=own['own_checkpoint']['sha256'],selected_source_SHA=own['source_SHA'],
 complete_saved_trace_indices=indices,complete_saved_trace_controls=controls,simulated_control_seconds_per_environment=controls*.01,
 own_callbacks_exact=own['health']['actual_physics_callbacks']==own['health']['expected_physics_callbacks']==controls*4,
 inherited_source_direction_histogram=baseline.tolist(),actual_before_physics_histogram=hist.tolist(),saved_after_update_histogram=stored.tolist(),endpoint_delta=endpoint.tolist(),
 cumulative_histogram_and_endpoint_phase_exact=True,both_signed_directions_and_standing_verified=True,entry_groups=result,
 CPU_only_no_RNG_draw_restore_GPU_queue_or_budget_write=True,no_causal_or_contact_or_route_success_claim=True)))
'''.replace('OWN_JSON_TOKEN',repr(json.dumps(own)))
        v=run(n,code)
        q=save('EXPOSURE424_COMPLETE_TRAINING_TRACE_ACTUAL_'+str(time.time_ns())+'.json',v)
        print(json.dumps(dict(report=str(q),passed=v['passed'],controls=v['complete_saved_trace_controls'],simulated_seconds=v['simulated_control_seconds_per_environment'],entry_groups=v['entry_groups'])))
    finally:io.cleanup(n,w)

if __name__=='__main__':
    try:main()
    except BaseException:
        save('EXPOSURE424_TRACE_READER_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),read_only_no_physics_or_PPO_replay=True))
        raise
