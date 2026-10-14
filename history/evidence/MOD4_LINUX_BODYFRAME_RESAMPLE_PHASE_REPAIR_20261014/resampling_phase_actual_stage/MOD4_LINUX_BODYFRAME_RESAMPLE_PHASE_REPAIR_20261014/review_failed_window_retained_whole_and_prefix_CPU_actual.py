"""Accept only the complete retained checkpoint, not the interrupted scope or final health."""
from pathlib import Path
import json,hashlib,time,sys,os,re
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch,numpy as np
D=Path(__file__).resolve().parent;W=D.parent;S=W/'MOD4_LINUX_WAVE50_BODYFRAME_SECOND_PREPARE_20261014';B=W/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014';R=D/'reports';sys.path.insert(0,str(S/'payload_v1'))
from birth_bodyframe_state_v1 import KEY,validate
from birth_bodyframe_full_checkpoint_v5 import bindings_from_checkpoint
from bodyframe_original_CPU_guard import logical_fullsave,same
from left_sameidentity_typed13_receipts import REQUIRED_BOOLEAN_SCHEMA,validate_set
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 out=R/'SECOND_BODY_FAILURE_RETAINED_WHOLE_STATE_AND_COMPLETED_PREFIX_CPU_VERIFIED.json';assert not out.exists()
 collection=S/'reports/SECOND_BODY_FAILED_WINDOW_ALL_INPUTS_TWOHOST_ACTUAL_1791991561073533600.json';data=json.loads(collection.read_bytes());assert data['all_two_host_byteSHA_exact'] and data['original_false_preserved'];a=data['actual'];rows=data['collected'];assert a['parent_failed_not_PASS'] and a['actual_parent_guardian_child_out'] and a['canonical_idle'] and all(x['actual_free'] for x in a['locks'])
 for row in rows:assert Path(row['local_path']).stat().st_size==row['bytes'] and H(row['local_path'])==row['sha256']
 byremote={x['path']:Path(x['local_path']) for x in rows};p=byremote[a['latest_complete']['checkpoint']];assert H(p)=='1a370588db7706006a303e8d4ccd2efbb966201b826d3719ae42692a5339fd1a' and p.stat().st_size==19894311
 src=json.loads((B/'reports/BODYFRAME_OWN_FINAL_FULLTRACE_LOCAL_CPU_VERIFIED.json').read_bytes())['own_checkpoint'];old=torch.load(src['path'],map_location='cpu',weights_only=False);ck=torch.load(p,map_location='cpu',weights_only=False);info=logical_fullsave({k:v for k,v in ck.items() if k not in (KEY,'E1_WAVE50_BODYFRAME_OWN_GPU_SOURCE')});validate(ck[KEY],bindings_from_checkpoint(ck))
 assert same(ck['LINUX20K_LEFT_JOINT_EXPLORATION_INITIALIZATION'],old['LINUX20K_LEFT_JOINT_EXPLORATION_INITIALIZATION']) and torch.equal(ck[KEY]['bound_episode'],ck['E1_terrain_state']['episode'])
 delta=[float(ck['optimizer_state_dict']['state'][i]['step'])-float(old['optimizer_state_dict']['state'][i]['step']) for i in range(17)];assert len(set(delta))==1 and delta[0]>0 and delta[0]%20==0;updates=int(delta[0]/20);assert updates==46
 changed=[k for k,x in ck['actor_state_dict'].items() if not torch.equal(x,old['actor_state_dict'][k])];assert len(changed)==9
 run=p.parent;proof=json.loads((run/'BIRTH_BODYFRAME_RESUME_STARTUP_VERIFIED.json').read_bytes());typed=validate_set([run/n for n in REQUIRED_BOOLEAN_SCHEMA],proof['pid'],src['sha256']);assert proof['passed'] and proof['actual_GPU_fullrestore_passed'] and proof['predecessor_bodyframe_state_present'] and not proof['first_declared_new_entry_and_BODYdirection'] and proof['no_initializer_repeat_or_new_RNG'] and proof['source_episode_plus_one']
 mark=ck['E1_WAVE50_BODYFRAME_OWN_GPU_SOURCE'];assert mark['actual_GPU_fullrestore'] and mark['own_pid']==proof['pid'] and mark['startup_receipt_SHA']==H(run/'BIRTH_BODYFRAME_RESUME_STARTUP_VERIFIED.json')
 controls=updates*24;assert controls==1104 and ck[KEY]['completed_controls']-old[KEY]['completed_controls']==controls
 # Full completed raw prefix remains useful even though the next control failed after its four physical substeps.
 st=old[KEY];mask=st['wave_mask'].numpy();sign=st['world_toward_sign'].numpy();rank=st['rank_in_side'].numpy();births=st['births'].numpy().copy()+1;count=np.zeros(20000,dtype=np.int64);hist=np.zeros((2,2,3),dtype=np.int64);total=0;last=None;lastdone=None;at_saved=None;trace=[];term=trunc=0
 files=sorted(run.glob('retention_prefix_*.npz'),key=lambda p:int(re.fullmatch(r'retention_prefix_(\d+)_(\d+)\.npz',p.name)[1]))
 for q in files:
  m=re.fullmatch(r'retention_prefix_(\d+)_(\d+)\.npz',q.name);assert int(m[1])==total
  with np.load(q,allow_pickle=False) as z:
   x=z['rows'];assert x.shape[1:]==(20000,16) and len(x)==int(m[2])-int(m[1]) and np.isfinite(x).all();done=(x[:,:,14]!=0)|(x[:,:,15]!=0)
   if last is not None:assert np.array_equal(x[0,~lastdone,:3],last[~lastdone,3:6])
   assert np.array_equal(x[1:,:,:3][~done[:-1]],x[:-1,:,3:6][~done[:-1]])
   for row in x:
    wave=row[:,10]==4;moving=wave&mask&(row[:,7]!=0);flip=mask&(((rank+births)%2)==1);co=np.where(flip,-1.,1.)
    assert np.max(abs(row[wave,8:10]))<=1e-6 and np.max(abs(row[wave,7]))<=.300001 and (row[moving,7]*sign[moving]*co[moving]>=-1e-7).all()
    ix=mask&wave;side=(sign[ix]>0).astype(int);orientation=flip[ix].astype(int);mode=np.where(row[ix,7]==0,2,np.where(row[ix,7]<0,0,1));hist+=np.bincount(side*6+orientation*3+mode,minlength=12).reshape(2,2,3)
    ended=(row[:,14]!=0)|(row[:,15]!=0);births[ended]+=1;count[ended]+=1;total+=1
    if total==controls:at_saved=(births.copy(),count.copy(),hist.copy())
   term+=int((x[:,:,14]!=0).sum());trunc+=int((x[:,:,15]!=0).sum());last=x[-1].copy();lastdone=done[-1].copy()
  trace.append(dict(path=str(q),bytes=q.stat().st_size,sha256=H(q),controls=len(x)))
 assert total==1200 and at_saved is not None
 assert np.array_equal(at_saved[0],ck[KEY]['births'].numpy()) and np.array_equal(at_saved[1],ck['E1_terrain_state']['episode'].numpy()-old['E1_terrain_state']['episode'].numpy()-1) and np.array_equal(at_saved[2],ck[KEY]['completed_control_histogram'].numpy()-old[KEY]['completed_control_histogram'].numpy())
 health=json.loads((run/'CLOCK_TRAINING_HEALTH.json').read_bytes());assert health['control_steps']==1200 and health['actual_physics_callbacks']==4804
 worker=(p.parent.parent.parent/'worker_stdout.log').read_text(encoding='utf8',errors='replace');assert 'self.command_manager.compute(dt=self.step_dt)' in worker and 'self._retention_resampling' not in worker and 'self.apply_commands(ids)' in worker and 'mapped_command' in worker
 assert 'GPU collision stack overflow' not in worker and 'Contacts have been dropped' not in worker
 segment=a['unique_completed_segment'];elapsed=segment['ended_epoch']-segment['started_epoch'];assert segment['accounted_through_epoch']==segment['ended_epoch'] and segment['source_SHA']==src['sha256'] and abs(elapsed-1129.3144571781158)<1e-6
 assert not torch.cuda.is_initialized();remaining=int(3600-elapsed);assert remaining==2470
 value=dict(epoch=time.time(),passed_retained_checkpoint_only=True,original_scope_PARENT_FAIL_preserved=True,original_worker_EXIT0_with_Traceback_not_success=True,source_checkpoint=dict(local_path=str(p),remote_path=a['latest_complete']['checkpoint'],sha256=H(p),bytes=p.stat().st_size),whole_core=info,owned_BODY_validated=True,updates_saved=updates,saved_controls=controls,saved_envsteps=controls*20000,saved_callbacks=controls*4,actor_changed=changed,all17_Adam_delta=delta[0],typed13=typed,actual_body14_restore_and_source_episode_plus_one=True,initializer_not_repeated=True,complete_saved_prefix_episodes_and_hist_exact=True,all_completed_raw_controls=total,completed_raw_prefix_finite_and_continuity_exact=True,completed_raw_ordinary=term,completed_raw_truncation=trunc,trace=trace,original_last_health_failed_callbacks4804_vs1200times4_preserved=True,failed_partial_extra_physics_callbacks=4,not_complete_failedcontrol_or_formal_FINAL=True,root_command_proxy_not_contact_or_fullroute_certificate=True,original_unique_parent_cost_seconds=elapsed,original_cost_charged_once_no_refund=True,original_canonical_idle_and_two_locks_free=True,actual_parent_guardian_child_out=True,remaining_original_second_window_seconds=remaining,first300_plus_second3600_original_plan_not_extended=True,no_GPU_SSH_PPO_budgetwrite=True,qualification_NOT_claimed=True)
 out.write_text(json.dumps(value,indent=2),encoding='utf8');print(json.dumps(dict(report=str(out),retained_checkpoint_passed=True,original_scope_failed=True,updates_saved=updates,envsteps_saved=controls*20000,raw_controls=total,extra_partial_callbacks=4,remainder_seconds=remaining)))
if __name__=='__main__':main()
