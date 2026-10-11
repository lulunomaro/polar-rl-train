"""Read-only matched prefixes and full saved formal command exposure; no physics replay."""
from direction_io import *
import traceback
sys.path.insert(0,str(W/'MOD4_E1_CURB20_133_COMPLETE_REVIEW_20261011'))
from diagnose_curb133_prefix_actual import inspect

def main():
 cpath=sorted(R.glob('CURB140_COLLECTED_[0-9]*.json'))[-1];c=json.loads(cpath.read_bytes())
 reviewpath=sorted(R.glob('CURB140_SCHEMA_REVIEW_[0-9]*.json'))[-1];review=json.loads(reviewpath.read_bytes())
 assert review['review_complete'] and not c['pending'] and len(c['cases'])==4
 jid=next(k for k,v in c['cases'].items() if 'full_route_raw' in v['probe'])
 candidate=inspect(R/'cases'/jid,c['cases'][jid]['probe'])
 base=W/'MOD4_E1_CURB20_INDEPENDENT_PREPARE_20261011/reports/cases/clk2500-closure-episode-d3-132-e1-curb20-source364-mirrored-fullroute-flat'
 source=inspect(base,json.loads((base/'probe.json').read_bytes()))
 prior=json.loads((W/'MOD4_E1_CURB20_ENTRY_FULLSTATE_PREPARE_20261011/reports/ENTRY139_COMPLETE_PREFIX_ACTUAL_DIAGNOSIS.json').read_bytes())['candidate139']
 failed=[x for x in candidate['rows'] if not x['complete']]
 pairs={str(x['env']):dict(source132=next(y for y in source['rows'] if y['env']==x['env']),prior139=next(y for y in prior['rows'] if y['env']==x['env']),candidate140=x) for x in failed}
 n,w=io.connect_both()
 try:
  exposure=run(n,r'''from pathlib import Path
import json,hashlib,numpy as np,torch
run=Path(FORMAL_RUN_PATH_TOKEN);j=lambda p:json.loads(p.read_bytes());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ckpath=Path(CHECKPOINT_PATH_TOKEN);assert h(ckpath)==CHECKPOINT_HASH_TOKEN
ck=torch.load(ckpath,map_location='cpu',weights_only=False);s=ck['E1_CURB_entry_direction_state']
a=j(run/'RETENTION_COMMAND_ACTUAL.json');health=j(run/'CLOCK_TRAINING_HEALTH.json')
assert a['actual_controls']==health['control_steps']==168
parts=[];indices=[]
for name in a['trace_files']:
 p=run/name
 with np.load(p) as z:
  assert z['columns'].tolist()==['before_x','before_y','before_z','pre_reset_x','pre_reset_y','pre_reset_z','heading_before','BODY_vx','BODY_vy','signed_yaw','family','eligible','linear','moving','terminated','truncated']
  parts.append(z['rows'])
 indices.append(dict(path=str(p),bytes=p.stat().st_size,sha256=h(p)))
x=np.concatenate(parts);assert x.shape==(168,20000,16) and np.isfinite(x).all()
mask=s['curb_mask'].numpy();xy=s['reset_xy'].numpy();sign=s['entry_sign'].numpy();assert mask.sum()==2820
centers=(np.floor(xy/9.)+.5)*9.
hist=np.zeros((2,3),dtype=np.int64)
for side in (0,1):
 ids=np.flatnonzero(mask & ((sign<0)==bool(side)))
 commands=x[:,ids,7];assert np.max(abs(x[:,ids,8:10]))<=1e-6
 hist[side]=[(commands<0).sum(),(commands>0).sum(),(commands==0).sum()]
stored=s['control_histogram'].numpy()
def modes(values):return np.array([(values<0).sum(),(values>0).sum(),(values==0).sum()])
endpoint=np.zeros((2,3),dtype=np.int64)
for side in (0,1):
 ids=np.flatnonzero(mask & ((sign<0)==bool(side)))
 endpoint[side]=modes(ck['E1_retained_flat_command_state']['BODY_command'].numpy()[ids,0])-modes(x[0,ids,7])
assert np.array_equal(stored,hist+endpoint),dict(trace_before=hist.tolist(),stored_after=stored.tolist(),endpoint=endpoint.tolist())
displacement=x[:,mask,3:5]-x[:,mask,:2]
moving=x[:,mask,7]!=0
groups=[]
for label,side in [('left_positive',sign>0),('right_negative',sign<0)]:
 ids=np.flatnonzero(mask&side);off=x[:,ids,3]-centers[ids,0]
 root_before=x[:,ids,0]-centers[ids,0]
 groups.append(dict(entry=label,environments=len(ids),commanded_moving_controls=int((x[:,ids,7]!=0).sum()),standing_controls=int((x[:,ids,7]==0).sum()),
  commanded_speed_abs_range_m_s=[float(abs(x[:,ids,7]).min()),float(abs(x[:,ids,7]).max())],
  fixed_reset_root_x_offset_abs_m_range=[float(abs(xy[ids,0]-centers[ids,0]).min()),float(abs(xy[ids,0]-centers[ids,0]).max())],
  nominal_integral_absolute_command_m_range=[float(abs(x[:,ids,7]).sum(0).min()*.01),float(abs(x[:,ids,7]).sum(0).max()*.01)],
  actual_prereset_root_x_range_m=[float(off.min()),float(off.max())],
  actual_same_control_signed_displacement_m_range=[float(((x[:,ids,3]-x[:,ids,0])*sign[ids]).sum(0).min()),float(((x[:,ids,3]-x[:,ids,0])*sign[ids]).sum(0).max())],
  root_center_side_changes_control_count=int(((root_before*off<0)&(x[:,ids,14]==0)).sum()),
  root_proxy_only_not_both_wheel_passage_or_contact=True))
assert not torch.cuda.is_initialized()
print(json.dumps(dict(saved_full_trace_actual_SHA_indices=indices,actual_control_steps=168,simulated_control_seconds_per_environment=1.68,
 maximum_nominal_command_distance_at_unchanged_speed_bound_m=.3*1.68,actual_before_physics_direction_histogram=hist.tolist(),saved_after_update_direction_histogram=stored.tolist(),command_phase_endpoint_delta=endpoint.tolist(),histogram_phase_relation_exact=True,
 nonzero_CURB_signed_direction_and_standing_confirmed=True,entry_groups=groups,CPU_only_no_RNG_draw_or_restore_or_GPU=True,
 short_prefix_does_not_certify_route_contact_or_circle=True)))
'''.replace('FORMAL_RUN_PATH_TOKEN',repr(c['passed']['run'])).replace('CHECKPOINT_PATH_TOKEN',repr(c['passed']['checkpoint']['path'])).replace('CHECKPOINT_HASH_TOKEN',repr(c['passed']['checkpoint']['sha256'])))
 finally:io.cleanup(n,w)
 result=dict(epoch=time.time(),trial_id='CURB140-COMPLETE-PREFIX-AND-FORMAL-EXPOSURE-DIAGNOSIS-01',collection=str(cpath),collection_SHA=H(cpath.read_bytes()),review=str(reviewpath),review_SHA=H(reviewpath.read_bytes()),source132=source,candidate140=candidate,incomplete_pairs=pairs,incomplete_envs=[x['env'] for x in failed],source_ascending_complete=sum(x['complete'] for x in source['rows']),prior139_ascending_complete=sum(x['complete'] for x in prior['rows']),candidate140_ascending_complete=sum(x['complete'] for x in candidate['rows']),formal_actual_exposure=exposure,
  no_causal_command_or_optimizer_or_router_ablation_claim=True,no_shorter_approach_or_longer_evaluation_window=True,no_original_false_raw_cost_relabel=True,no_GPU_PPO_queue_or_budget_write=True,
  earlier_literal_wildcard_rg_path_reader_error_preserved='Windows rg literal path ending src_snapshot/curb20* was invalid; no source/result/PPO mutation occurred.')
 p=save('CURB140_COMPLETE_PREFIX_EXPOSURE_DIAGNOSIS.json',result)
 print(json.dumps(dict(report=str(p),incomplete_envs=result['incomplete_envs'],incomplete_first_segments=[x['segments'][0] for x in failed],exposure=exposure),ensure_ascii=True))

if __name__=='__main__':
 try:main()
 except BaseException:save('CURB140_EXPOSURE_READER_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),reader_only=True,no_GPU_or_PPO_replay=True));raise
