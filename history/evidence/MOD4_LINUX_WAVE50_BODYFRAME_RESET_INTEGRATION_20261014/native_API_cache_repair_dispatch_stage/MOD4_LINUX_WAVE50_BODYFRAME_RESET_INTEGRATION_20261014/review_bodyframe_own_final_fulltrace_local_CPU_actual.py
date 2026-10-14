"""Independent CPU-only closeout of the new own source, startup and all traces."""
from pathlib import Path
import os,sys,json,time,re,hashlib
os.environ['CUDA_VISIBLE_DEVICES']=''
import numpy as np
import torch
B=Path(__file__).resolve().parent
sys.path.insert(0,str(B/'payload_v1'))
from birth_bodyframe_state_v1 import KEY,validate
MARK='E1_WAVE50_BODYFRAME_OWN_GPU_SOURCE'

def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()

def main():
 inputs=max((B/'reports').glob('BODYFRAME_OWN_FINAL_ALL_INPUTS_TWOHOST_ACTUAL_*.json'),key=lambda p:p.stat().st_mtime_ns)
 d=json.loads(inputs.read_bytes());assert d['twohost_byte_SHA_all_exact']
 rows=d['local_collected_files'];a=d['actual'];assert a['canonical_active'] is None and all(v['held'] is False for v in a['two_fcntl_free'])
 byremote={v['path']:Path(v['local_path']) for v in rows}
 for v in rows:assert Path(v['local_path']).stat().st_size==v['bytes'] and sha(v['local_path'])==v['sha256']
 final=byremote[a['formal']['own_checkpoint']['path']];src=byremote[a['formal']['source']['path']]
 ck=torch.load(final,map_location='cpu',weights_only=False);old=torch.load(src,map_location='cpu',weights_only=False)
 validate(ck[KEY]);validate(old[KEY]);assert ck[MARK]['actual_GPU_fullrestore'] is True
 assert torch.equal(ck[KEY]['bound_episode'],ck['E1_terrain_state']['episode'])
 sys.path.insert(0,str(B.parent/'MOD4_LINUX_LEFT_SECOND_SAMEIDENTITY_CPU_PREPARE_20261014/payload_v1'))
 import second_target_CPU_pure_guard_v2 as guard
 info=guard.logical_fullsave({k:v for k,v in ck.items() if k not in (KEY,MARK)});assert info['floating_finite']==107 and info['perenv']==99 and info['tensors']==195
 assert guard.same(ck['LINUX20K_LEFT_JOINT_EXPLORATION_INITIALIZATION'],old['LINUX20K_LEFT_JOINT_EXPLORATION_INITIALIZATION'])
 changed=[k for k,v in ck['actor_state_dict'].items() if not torch.equal(v,old['actor_state_dict'][k])];assert len(changed)==9
 deltas=[float(ck['optimizer_state_dict']['state'][i]['step'])-float(old['optimizer_state_dict']['state'][i]['step']) for i in range(17)]
 assert len(set(deltas))==1 and deltas[0]>0 and deltas[0]%20==0
 updates=int(deltas[0]/20);assert updates==a['formal']['updates']
 run=final.parent
 health=json.loads((run/'CLOCK_TRAINING_HEALTH.json').read_bytes());controls=health['control_steps'];assert controls==updates*24 and health['actual_physics_callbacks']==controls*4 and health['stop_reason'] is None
 assert health['termination_reason_coverage_exact'] and health['truncation_reason_coverage_exact']
 assert health['integrity_task_reset_events']==health['unknown_task_reset_events']==0 and health['nonfinite_observed'] is False
 proof=json.loads((run/'BIRTH_BODYFRAME_RESUME_STARTUP_VERIFIED.json').read_bytes());assert proof['passed'] and proof['actual_GPU_fullrestore_passed'] and proof['CPU_fixture_only'] is False and proof['no_initializer_repeat_or_new_RNG']
 assert proof['source_sha256']==a['formal']['source']['sha256'] and proof['pid']==ck[MARK]['own_pid'] and sha(run/'BIRTH_BODYFRAME_RESUME_STARTUP_VERIFIED.json')==ck[MARK]['startup_receipt_SHA']
 from left_sameidentity_typed13_receipts import REQUIRED_BOOLEAN_SCHEMA,validate_set
 typed=validate_set([run/name for name in REQUIRED_BOOLEAN_SCHEMA],proof['pid'],proof['source_sha256'])
 meta=json.loads((run/'RETENTION_COMMAND_ACTUAL.json').read_bytes());assert meta['actual_controls']==controls and meta['pre_reset_roots_no_teleport']
 columns=['before_x','before_y','before_z','pre_reset_x','pre_reset_y','pre_reset_z','heading_before','BODY_vx','BODY_vy','signed_yaw','family','eligible','linear','moving','terminated','truncated']
 st=old[KEY];mask=st['wave_mask'].numpy();sign=st['world_toward_sign'].numpy();rank=st['rank_in_side'].numpy();births=st['births'].numpy().copy()+1
 count=np.zeros(20000,dtype=np.int64);hist=np.zeros((2,2,3),dtype=np.int64);total=0;term=trunc=both=0;last=None;lastdone=None;indices=[];dynamic=0;firstfamily=None;validlen=np.zeros(20000,dtype=np.int64);maxvalid=0
 for name in meta['trace_files']:
  q=run/name;m=re.fullmatch(r'retention_prefix_(\d+)_(\d+)\.npz',name);assert m and int(m[1])==total
  with np.load(q) as z:
   x=z['rows'];assert z['columns'].tolist()==columns and x.ndim==3 and x.shape[1:]==(20000,16) and np.isfinite(x).all() and len(x)==int(m[2])-int(m[1])
   done=(x[:,:,14]!=0)|(x[:,:,15]!=0)
   if last is not None:assert np.array_equal(x[0,~lastdone,:3],last[~lastdone,3:6])
   assert np.array_equal(x[1:,:,:3][~done[:-1]],x[:-1,:,3:6][~done[:-1]])
   if firstfamily is None:firstfamily=x[0,:,10].copy();assert int((firstfamily==4).sum())==2820
   for row in x:
    wave=row[:,10]==4;moving=wave&mask&(row[:,7]!=0);flip=mask&(((rank+births)%2)==1);co=np.where(flip,-1.,1.)
    assert np.max(abs(row[wave,8:10]))<=1e-6 and np.max(abs(row[wave,7]))<=.300001
    assert (row[moving,7]*sign[moving]*co[moving]>=-1e-7).all()
    ix=mask&wave;side=(sign[ix]>0).astype(int);orientation=flip[ix].astype(int);mode=np.where(row[ix,7]==0,2,np.where(row[ix,7]<0,0,1));hist+=np.bincount(side*6+orientation*3+mode,minlength=12).reshape(2,2,3)
    ordinary=row[:,14]!=0;ended=ordinary|(row[:,15]!=0);validlen[~ordinary]+=1;maxvalid=max(maxvalid,int(validlen.max()));validlen[ended]=0
    births[ended]+=1;count[ended]+=1
   term+=int((x[:,:,14]!=0).sum());trunc+=int((x[:,:,15]!=0).sum());both+=int(((x[:,:,14]!=0)&(x[:,:,15]!=0)).sum());dynamic+=int((x[:,:,10]!=firstfamily[None,:]).sum())
   last=x[-1].copy();lastdone=done[-1].copy();total+=len(x)
  indices.append(dict(path=str(q),bytes=q.stat().st_size,sha256=sha(q),controls=len(x)))
 assert total==controls and term==health['actual_task_reset_events'] and trunc==health['actual_truncation_reset_events']
 assert np.array_equal(births,ck[KEY]['births'].numpy()) and np.array_equal(count,ck['E1_terrain_state']['episode'].numpy()-old['E1_terrain_state']['episode'].numpy()-1)
 assert np.array_equal(hist,ck[KEY]['completed_control_histogram'].numpy()-old[KEY]['completed_control_histogram'].numpy())
 assert ck[KEY]['completed_controls']-old[KEY]['completed_controls']==controls and maxvalid*.01<=40.001
 segment=a['unique_completed_segment'];assert segment['ended_epoch']==segment['accounted_through_epoch'] and segment['source_SHA']==a['formal']['source']['sha256']
 assert not torch.cuda.is_initialized()
 result=dict(epoch=time.time(),passed=True,own_checkpoint=dict(path=str(final),sha256=sha(final),bytes=final.stat().st_size),whole_core=info,updates=updates,controls=controls,envsteps=controls*20000,callbacks=controls*4,actor_changed=changed,Adam_delta=deltas[0],typed13=typed,body14_actual_source_PID_and_GPU_restore=True,source_original_SHA=a['source_original_SHA'],all_twohost_input_SHA_exact=True,all_trace=indices,all_trace_controls_exact=True,all_birth_episode_counts_exact=True,pre_reset_BODY_WORLD_orientation_histogram_exact=hist.tolist(),currentrootfamily4_dynamic_changes=dynamic,ordinary=term,truncations=trunc,unique_ends=term+trunc-both,max_valid_recorded_prefix_seconds=maxvalid*.01,health=health,canonical_unique_parent_seconds=segment['ended_epoch']-segment['started_epoch'],canonical_remaining_snapshot=a['canonical_remaining'],actual_parent_guardian_child_out=True,two_locks_free=True,no_new_budget_write=True,qualified50=False,rootcommand_proxy_not_contact_or_fullroute_or_causal_certificate=True,original_fourcase_frozen_3060_behavior_next=True)
 out=B/'reports/BODYFRAME_OWN_FINAL_FULLTRACE_LOCAL_CPU_VERIFIED.json';assert not out.exists();out.write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps({k:result[k] for k in ('passed','own_checkpoint','updates','controls','envsteps','callbacks','ordinary','canonical_unique_parent_seconds')}))

if __name__=='__main__':main()
