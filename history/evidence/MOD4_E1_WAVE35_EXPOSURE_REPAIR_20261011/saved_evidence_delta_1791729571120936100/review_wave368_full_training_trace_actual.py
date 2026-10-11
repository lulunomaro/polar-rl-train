"""Read all saved Wave controls, preserving episode prefixes and source artifacts."""
from wave_io import *

def main():
    own=json.loads(sorted(R.glob('WAVE_OWN_FORMAL_CPU_ACTUAL_[0-9]*.json'))[-1].read_bytes())
    assert own['passed'] and own['closeout_ready'] and own['actual_source_count']==368
    compact=dict(checkpoint=own['own_checkpoint'],source_SHA=own['source_SHA'],controls=own['health']['control_steps'])
    code=r'''from pathlib import Path
import json,hashlib,numpy as np,torch,time
torch.set_num_threads(1);v=json.loads(COMPACT_TOKEN);ckpath=Path(v['checkpoint']['path']);run=ckpath.parent
def h(p):
 a=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1048576),b''):a.update(block)
 return a.hexdigest()
assert h(ckpath)==v['checkpoint']['sha256'];m=json.loads((run/'run_manifest.json').read_bytes());assert h(Path(m['init_checkpoint']))==v['source_SHA']
a=json.loads((run/'RETENTION_COMMAND_ACTUAL.json').read_bytes());assert a['actual_controls']==v['controls']==2352
indices=[];total=0;ids=None;hist=np.zeros(3,dtype=np.int64);displacement=None;command_integral=None;segment_steps=None;max_segment=0
family_counts=None;speed_max=0.;root_step_max=0.;ended_prefixes=0;head_absmax=0.;standing=0
for name in a['trace_files']:
 p=run/name;assert p.is_relative_to(run)
 with np.load(p) as z:
  assert z['columns'].tolist()==['before_x','before_y','before_z','pre_reset_x','pre_reset_y','pre_reset_z','heading_before','BODY_vx','BODY_vy','signed_yaw','family','eligible','linear','moving','terminated','truncated']
  x=z['rows'];assert x.ndim==3 and x.shape[1:]==(20000,16) and np.isfinite(x).all()
  if ids is None:
   family=x[0,:,10].astype(int);assert set(family.tolist())==set(range(5));ids=np.flatnonzero(family==4);assert len(ids)==2820
   family_counts=np.bincount(family,minlength=5).tolist();displacement=np.zeros(len(ids));command_integral=np.zeros(len(ids));segment_steps=np.zeros(len(ids),dtype=np.int64)
  assert np.array_equal(x[:,:,10],np.broadcast_to(family,x[:,:,10].shape))
  y=x[:,ids,:];c=y[:,:,7];assert np.max(abs(y[:,:,8:10]))<=1e-6 and np.max(abs(c))<=.300001
  hist+=np.array([(c<0).sum(),(c>0).sum(),(c==0).sum()]);standing+=int((c==0).sum());speed_max=max(speed_max,float(abs(c).max()))
  command_integral+=abs(c).sum(0)*.01;delta=y[:,:,3:6]-y[:,:,:3]
  displacement+=delta[:,:,0].sum(0);root_step_max=max(root_step_max,float(np.linalg.norm(delta,axis=-1).max()));head_absmax=max(head_absmax,float(abs(y[:,:,6]).max()))
  for row in y:
   segment_steps+=1;max_segment=max(max_segment,int(segment_steps.max()));end=(row[:,14]!=0)|(row[:,15]!=0);ended_prefixes+=int(end.sum());segment_steps[end]=0
  total+=len(x)
 indices.append(dict(path=str(p),bytes=p.stat().st_size,sha256=h(p),original_retained=True,large_index_only=True))
assert total==v['controls'];assert all(hist>0);assert hist.sum()==total*2820;assert not torch.cuda.is_initialized()
print(json.dumps(dict(epoch=time.time(),passed=True,own_checkpoint_SHA=v['checkpoint']['sha256'],source_SHA=v['source_SHA'],full_saved_trace_indices=indices,
 actual_controls=total,simulated_control_seconds_per_environment=total*.01,actual_family_enum_counts=family_counts,Wave_actual_enum=4,Wave_environments=2820,
 Wave_beforephysics_negative_positive_standing_control_counts=hist.tolist(),signed_gentle_and_standing_observed=True,maximum_abs_BODY_vx=speed_max,vy_and_yaw_zero=True,
 per_environment_nominal_abs_command_integral_m_range=[float(command_integral.min()),float(command_integral.max())],
 same_control_prereset_minus_before_root_x_sum_range_m=[float(displacement.min()),float(displacement.max())],maximum_prereset_minus_before_root_step_norm_m=root_step_max,
 maximum_abs_heading_rad=head_absmax,observed_episode_ended_prefixes=ended_prefixes,longest_recorded_contiguous_episode_prefix_seconds=max_segment*.01,
 last_valid_unfinished_prefix_control_range=[int(segment_steps.min()),int(segment_steps.max())],
 trace_is_beforephysics_saved_command_histogram_is_afterupdate_not_forced_samephase=True,reset_teleport_excluded_by_prereset_minus_before=True,
 root_proxy_not_two_wheel_contact_or_fullroute_certificate=True,no_causal_learning_or_qualified_Wave_claim=True,CPU_only_no_RNG_draw_restore_GPU_or_budget_write=True)))
'''.replace('COMPACT_TOKEN',repr(json.dumps(compact)))
    n,w=io.connect_both()
    try:
        v=run(n,code);p=save('WAVE368_FULL_TRAINING_TRACE_ACTUAL_'+str(time.time_ns())+'.json',v)
        print(json.dumps(dict(report=str(p),controls=v['actual_controls'],simulated_seconds=v['simulated_control_seconds_per_environment'],Wave_histogram=v['Wave_beforephysics_negative_positive_standing_control_counts'],longest_prefix=v['longest_recorded_contiguous_episode_prefix_seconds'],passed=True)))
    finally:io.cleanup(n,w)

if __name__=='__main__':
    try:main()
    except BaseException:save('WAVE368_TRACE_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_PPO_replay=True));raise
