"""Read original own412 full trace: entry-side commands and actual episode prefixes."""
from entry_second_io import *
CODE=r'''from pathlib import Path
import json,numpy as np,torch,hashlib,time
torch.set_num_threads(1);v=json.loads(INPUT_TOKEN);cp=Path(v['checkpoint']['path']);module=Path(ROOT_TOKEN)/'isaac/mod4'
def h(p):
 a=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):a.update(b)
 return a.hexdigest()
assert h(cp)==v['checkpoint']['sha256'];ck=torch.load(cp,map_location='cpu',weights_only=False);s=ck['E1_terrain_state'];xy=s['spawn_xy'].numpy();profile=json.loads((module/'g4_cad_profile.json').read_bytes());assert h(module/'g4_cad_profile.json')==s['G4_profile_sha256']
half=profile['span_m']*.5;ids=None;hist=None;start=None;direction=None;firstcmd=None;flip=None;length=None;distance=None;turnmax=None;episodes=[];total=0;rootside_cross=0;indices=[]
for item in v['traces']:
 p=Path(item['path']);assert h(p)==item['sha256'] and p.stat().st_size==item['bytes'];indices.append(item)
 with np.load(p) as z:
  a=z['rows'];assert a.shape[1:]==(20000,16) and np.isfinite(a).all()
  if ids is None:
   ids=np.flatnonzero(a[0,:,10]==4);assert len(ids)==2820 and np.array_equal(xy,a[0,:,:2])
   centers=(np.floor(xy[ids]/9.+20)-20+.5)*9.;side=np.sign(xy[ids,0]-centers[:,0]);assert np.isin(side,[-1,1]).all();direction=-side;hist=np.zeros((2,3),dtype=np.int64);length=np.zeros(len(ids),dtype=int);firstcmd=np.zeros(len(ids));flip=np.zeros(len(ids),dtype=bool);distance=np.zeros(len(ids));turnmax=np.zeros(len(ids));start=xy[ids].copy()
  y=a[:,ids,:]
  for row in y:
   c=row[:,7];family=row[:,10]==4;assert np.max(abs(row[family,8:10]))<=1e-6 and np.max(abs(c[family]))<=.300001
   for i,which in enumerate((-1,1)):
    take=(side==which)&family;vx=direction[take]*c[take];hist[i]+=np.array([(vx>0).sum(),(vx<0).sum(),(vx==0).sum()])
   first=(length==0);start[first]=row[first,:2];firstcmd[first]=np.sign(c[first]);flip|=(firstcmd!=0)&(c!=0)&(np.sign(c)!=firstcmd)
   step=row[:,3:5]-row[:,:2];length+=1;distance+=direction*step[:,0];turnmax=np.maximum(turnmax,abs(row[:,6]));root_before=row[:,0]-centers[:,0];root_after=row[:,3]-centers[:,0];rootside_cross+=int(((root_before*root_after)<0).sum())
   ended=(row[:,14]!=0)|(row[:,15]!=0)
   for k in np.flatnonzero(ended):episodes.append(dict(env=int(ids[k]),initial_entry_side=int(side[k]),valid_controls=int(length[k]),physical_seconds=float(length[k]*.01),first_command_sign=float(firstcmd[k]),signed_command_changed_in_prefix=bool(flip[k]),same_control_prereset_before_toward_root_displacement_m=float(distance[k]),max_abs_heading_rad=float(turnmax[k]),ordinary=bool(row[k,14]),declared_truncation=bool(row[k,15])))
   length[ended]=0;flip[ended]=False;distance[ended]=0;turnmax[ended]=0
  total+=len(a)
assert total==v['controls'] and not torch.cuda.is_initialized();allprefix=len(episodes);flips=sum(x['signed_command_changed_in_prefix'] for x in episodes)
out=dict(epoch=time.time(),passed=True,own_checkpoint_SHA=v['checkpoint']['sha256'],all_full_trace_actual_indices=indices,controls=total,entry_map_SHA=s['entry_map_sha256'],Wave_initial2820_cohort=True,entry_origin_assignment_and_saved_first_spawn_exact=True,two_entry_sides_toward_away_standing_controls=hist.tolist(),histogram_columns=['toward_from_fixed_entry_side','away_from_fixed_entry_side','standing'],completed_prefix_count=allprefix,completed_prefix_signed_command_change_count=flips,completed_valid_prefixes=episodes,unfinished_valid_prefix_counts=[int(length.min()),int(length.max())],root_center_crossing_control_count=rootside_cross,original2m_route_from_spawn_m=2.,original_full_frozen_route_nominal_m=profile['span_m']+.4+.2,route_cannot_certify_whole_test=True,beforephysics_commands_samecontrol_prereset_before_root_only=True,not_contact_fullroute_or_causal_proof=True,no_reset_direction_command_reward_DR_or_route_modified=True,no_RNG_draw_restore_GPU_PPO_or_budget_write=True)
print(json.dumps(out))
'''
def main():
 own=json.loads(max(R.glob('ENTRY_SECOND_OWN_FORMAL_CPU_ACTUAL_[0-9]*.json'),key=lambda p:int(p.stem.rsplit('_',1)[1])).read_bytes());trace=json.loads(max(R.glob('ENTRY_SECOND_FULL_TRAINING_TRACE_ACTUAL_[0-9]*.json'),key=lambda p:int(p.stem.rsplit('_',1)[1])).read_bytes());assert own['closeout_ready'] and trace['passed']
 n,w=io.connect_both()
 try:
  value=dict(checkpoint=own['own_checkpoint'],controls=trace['actual_controls'],traces=trace['full_saved_trace_indices']);v=run(n,CODE.replace('INPUT_TOKEN',repr(json.dumps(value))).replace('ROOT_TOKEN',repr(ROOT)));p=save('OWN412_ENTRY_COMMAND_EXPOSURE_ACTUAL_'+str(time.time_ns())+'.json',v)
  print(json.dumps(dict(report=str(p),passed=True,two_sides_toward_away_standing=v['two_entry_sides_toward_away_standing_controls'],completed_prefixes=v['completed_prefix_count'],signed_command_changed_prefixes=v['completed_prefix_signed_command_change_count'])))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('OWN412_ENTRY_COMMAND_TRACE_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),read_only_no_GPU_or_experiment_replay=True));raise
