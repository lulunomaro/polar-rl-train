"""Independent saved full trace CPU review after typed-schema closeout. No GPU or ledger mutation."""
from pathlib import Path
import json,os,time,shlex
from deploy_original_linux20k_formal_once import S as BASE,PY,D
from read_linux_resume_boundary_actual import connect_linux_only
S=BASE.replace('_v1','_runtime_assets_complete_v3')
def main():
    c=connect_linux_only()
    try:
        src=r'''
from pathlib import Path
import json,hashlib,numpy as np,torch,time,re,sys
R=Path(S);close=json.loads((R/'INDEPENDENT_POSTEXIT_TYPED_SCHEMA_ACTUAL.json').read_bytes());assert close['independent_postexit_pass']
p=Path(close['ownfullsave']['path']);ck=torch.load(p,map_location='cpu',weights_only=False);run=p.parent
sys.path.insert(0,str(R/'isaac/mod4'));from e1_terrain_training_health import learning_health_pass
health=json.loads((run/'CLOCK_TRAINING_HEALTH.json').read_bytes());assert learning_health_pass(health) and health['truncation_reason_coverage_exact'] and health['stop_reason'] is None
assert health['control_steps']==close['actual_saved_updates']*24
assert health['actual_physics_callbacks']==health['control_steps']*4
meta=json.loads((run/'RETENTION_COMMAND_ACTUAL.json').read_bytes());assert meta['actual_controls']==health['control_steps']
assert meta['pre_reset_roots_no_teleport'] and meta['complete_cycles_not_claimed_from_truncated_prefixes']
direction=ck['E1_WAVE50_episode_direction_state'];sign=direction['entry_sign'].numpy();mask=direction['wave_mask'].numpy();assert int(mask.sum())==2820
def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
assert sha(p)==close['ownfullsave']['sha256']
columns=['before_x','before_y','before_z','pre_reset_x','pre_reset_y','pre_reset_z','heading_before','BODY_vx','BODY_vy','signed_yaw','family','eligible','linear','moving','terminated','truncated']
indices=[];total=0;first_family=None;hist=np.zeros(3,dtype=np.int64);dynamic=0;term=trunc=both=ends=0
length=np.zeros(20000,dtype=np.int64);longest=0;last=None;last_done=None;root_max=0.;command_integral=np.zeros(20000);displacement=np.zeros(20000)
for name in meta['trace_files']:
 q=run/name;assert q.resolve().is_relative_to(run.resolve());match=re.fullmatch('retention_prefix_(\d+)_(\d+)\.npz',name);assert match and int(match[1])==total
 with np.load(q) as z:
  assert z['columns'].tolist()==columns;x=z['rows'];assert x.ndim==3 and x.shape[1:]==(20000,16) and np.isfinite(x).all()
  assert int(match[2])-int(match[1])==len(x)
  for j in (11,12,13,14,15):assert np.isin(x[:,:,j],[0.,1.]).all()
  assert np.isin(x[:,:,10],np.arange(-1,5)).all()
  if first_family is None:
   first_family=x[0,:,10].astype(int);assert set(first_family)==set(range(5));assert int((first_family==4).sum())==2820
  if last is not None:assert np.array_equal(x[0,~last_done,:3],last[~last_done,3:6])
  done=(x[:,:,14]!=0)|(x[:,:,15]!=0)
  assert np.array_equal(x[1:,:,:3][~done[:-1]],x[:-1,:,3:6][~done[:-1]])
  current_wave=x[:,:,10]==4;vx=x[:,:,7]
  assert np.max(abs(x[:,:,8:10][current_wave]))<=1e-6 and np.max(abs(vx[current_wave]))<=.300001
  assert np.min((vx*sign[None,:])[current_wave&mask[None,:]])>=-1e-7
  values=vx[current_wave];hist+=np.array([(values<0).sum(),(values>0).sum(),(values==0).sum()])
  dynamic+=int((x[:,:,10]!=first_family[None,:]).sum());term+=int((x[:,:,14]!=0).sum());trunc+=int((x[:,:,15]!=0).sum());both+=int(((x[:,:,14]!=0)&(x[:,:,15]!=0)).sum());ends+=int(done.sum())
  delta=x[:,:,3:6]-x[:,:,:3];root_max=max(root_max,float(np.linalg.norm(delta,axis=-1).max()));displacement+=delta[:,:,0].sum(0);command_integral+=abs(vx).sum(0)*.01
  # Failing ordinary frames remain saved but are excluded from valid pre-failure duration.
  for row in x:
   ordinary=row[:,14]!=0;length[~ordinary]+=1;longest=max(longest,int(length.max()));length[ordinary|(row[:,15]!=0)]=0
  last=x[-1].copy();last_done=done[-1].copy();total+=len(x)
 indices.append(dict(path=str(q),bytes=q.stat().st_size,sha256=sha(q),controls=int(match[2])-int(match[1]),original_retained=True))
assert total==health['control_steps'] and term==health['actual_task_reset_events'] and trunc==health['actual_truncation_reset_events']
assert ends==term+trunc-both and all(hist>0)
assert longest*.01<=40.001
assert not torch.cuda.is_initialized()
reasons=health['termination_events_by_reason'];timeout_route_overlap=reasons['time_out']+reasons['rough_route_boundary']-trunc;assert timeout_route_overlap>=0
report=dict(epoch=time.time(),passed=True,own_final_SHA=close['ownfullsave']['sha256'],actual_saved_updates=close['actual_saved_updates'],controls=total,envsteps=total*20000,callbacks=health['actual_physics_callbacks'],full_trace=indices,total_trace_bytes=sum(x['bytes'] for x in indices),initial_static_family_enum_counts=np.bincount(first_family,minlength=5).tolist(),dynamic_currentroot_family_changed_control_count=dynamic,currentroot_Wave_enum=4,Wave_negative_positive_standing_controls=hist.tolist(),ordinary_events=term,unique_truncations=trunc,timeout_route_overlap=timeout_route_overlap,ordinary_truncation_overlap=both,unique_episode_ends=ends,all_original_reasons_counts_not_summed_as_unique=True,reason_coverage_exact=health['termination_reason_coverage_exact'],truncation_coverage_exact=health['truncation_reason_coverage_exact'],health=health,max_valid_recorded_episode_prefix_seconds=longest*.01,whole_control_seconds_per_env=total*.01,root_command_integral_allenv_range_m=[float(command_integral.min()),float(command_integral.max())],actual_prereset_minus_before_root_x_allenv_sum_range_m=[float(displacement.min()),float(displacement.max())],maximum_samecontrol_prereset_before_root_step_norm_m=root_max,last_valid_unfinished_prefix_length_range=[int(length.min()),int(length.max())],all_complete_indices_and_control_continuity_exact=True,reset_teleport_excluded=True,ordinary_failure_frames_preserved_but_not_credited_validprogress=True,beforephysics_command_vs_afterupdate_histogram_not_forced_equal=True,root_command_proxy_not_two_wheel_contact_or_fullroute_certificate=True,no_qualified50_or_causal_fix_claim=True,no_RNG_GPU_signal_or_budget_action=True)
q=R/'FINAL_FULL_TRAINING_TRACE_CPU_ACTUAL.json';assert not q.exists();q.write_text(json.dumps(report,indent=2));print(json.dumps(report))
'''
        si,so,se=c.exec_command('CUDA_VISIBLE_DEVICES= '+shlex.quote(PY)+' -',timeout=180);si.write('S='+repr(S)+'\n'+src);si.flush();si.channel.shutdown_write();out=so.read();err=se.read();rc=so.channel.recv_exit_status()
        p=D/'reports'/('ORIGINAL_LINUX20K_FINAL_FULLTRACE_CPU_ACTUAL_'+str(time.time_ns())+'.json');p.write_bytes(json.dumps(dict(code=rc,stdout=out.decode(),stderr=err.decode()),indent=2).encode());assert rc==0,str(p);v=json.loads(out)
        print(json.dumps(dict(receipt=str(p),passed=v['passed'],updates=v['actual_saved_updates'],envsteps=v['envsteps'],trace_files=len(v['full_trace']),trace_bytes=v['total_trace_bytes'],ordinary=v['ordinary_events'],truncations=v['unique_truncations'],timeout_route_overlap=v['timeout_route_overlap'],max_valid_prefix_s=v['max_valid_recorded_episode_prefix_seconds'])))
    finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':main()
