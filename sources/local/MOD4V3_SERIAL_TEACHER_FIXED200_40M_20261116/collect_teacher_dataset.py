"""Collect current native teacher, with pre-action observations and actual clipped PPO actions."""
from pathlib import Path
import sys,json,hashlib,time
import numpy as np
T=Path(__file__).resolve().parent;R=T.parents[2];E=R/'sources/local/MOD4V3_SERIAL_LQR_SKILL_TEACHER_20261116/equivalent_controller_v1';S=E/'forward_capture_repair_20261116'
sys.path.insert(0,str(E));import run_teacher as rt
Native=rt.NativeTeacher;PERM=np.array([0,2,1,3,4,5]);instances=[]
class RecordingTeacher(Native):
 def __init__(self,*args,**kwargs):
  super().__init__(*args,**kwargs);self.observations=[];self.labels=[];self.public_heights=[];self.pre_states=[];self.previous=np.zeros(6,np.float32);instances.append(self)
 def step(self,axes):
  height=float(self.controller.target_leg_length_command)+.0625
  q=self.d.qpos[self.qa][PERM].copy();q[:4]-=self.default[PERM[:4]];q[4:]=0.
  qd=self.d.qvel[self.va][PERM];rotation=self.d.xmat[self.env.base_id].reshape(3,3)
  mode=np.array([0,1,0,0,0,1,0],np.float32)
  obs=np.r_[[axes[0]*self.controller.reference_governor.max_speed,0.,0.,height*5.],self.d.qvel[3:6]*.5,rotation.T@np.array([0.,0.,-1.]),q,qd*.1,self.previous,mode].astype(np.float32)
  assert obs.shape==(35,) and np.isfinite(obs).all()
  self.pre_states.append(self.d.qpos.copy());diag=super().step(axes);action=diag['action'][PERM].astype(np.float32)
  self.observations.append(obs);self.labels.append(action.copy());self.public_heights.append(height);self.previous=action.copy();return diag
rt.NativeTeacher=RecordingTeacher
root=T/'skill_dataset';root.mkdir(exist_ok=False);xs=[];ys=[];groups=[];eids=[];entries=[];started=time.time()
profile=json.loads((S/'CANDIDATE_PROFILE.json').read_text());index=json.loads((T/'teacher_snapshot/SOURCE_INDEX.json').read_text())
for row in index['files']:assert hashlib.sha256(Path(row['path']).read_bytes()).hexdigest()==row['sha256']
for eid,mm in enumerate([-60,-30,0,30,60]):
 case=dict(profile,start_x=mm/1000);out=T/'teacher_collection'/f'start_{mm:+04d}mm';out.mkdir(parents=True)
 result=rt.run(case,out);teacher=instances[-1];x=np.asarray(teacher.observations,np.float32);y=np.asarray(teacher.labels,np.float32);heights=np.asarray(teacher.public_heights)
 trace=np.load(out/'trace.npz');assert np.array_equal(y,trace['actions'])
 assert np.allclose(x[:,3],heights*5.)and abs(y).max()<=6.
 previous=S/f'final_clean_v2_{mm:+04d}mm/trace.npz';same=None
 if previous.exists():same=bool(np.array_equal(np.load(previous)['qpos'],trace['qpos']));assert same,'Collection changed teacher trajectory'
 qualified=bool(result['pass_teacher_stair']and result['max_continuous_top_hold_s']>=.4 and result['error']is None)
 meta=dict(episode=eid,start_offset_mm=mm,qualified=qualified,result=str(out/'RESULT.json'),frames=len(x),same_states_as_approved_teacher=same,root_height_command_range_m=[float(heights.min()),float(heights.max())],actions_in_ppo_order=True,preaction_observations=True)
 entries.append(meta)
 np.savez_compressed(out/'observation_action_pairs.npz',obs=x,actions=y,root_height_cmd=heights,pre_qpos=np.asarray(teacher.pre_states))
 assert qualified,'Unqualified collection retained; do not admit to dataset'
 phase=trace['phases'][:,0];active=np.flatnonzero(phase!='idle');assert len(active)
 group=np.where(np.arange(len(x))<active[0],0,np.where(np.arange(len(x))<=active[-1],1,2))
 xs.append(x);ys.append(y);groups.extend(group);eids.extend([eid]*len(x));print('QUALIFIED_COLLECTION',mm,len(x),'unchanged',same,flush=True)
obs=np.concatenate(xs);actions=np.concatenate(ys);episode=np.asarray(eids,np.int64);phase=np.asarray(groups,np.int64);weights=np.zeros(len(obs),np.float32)
for e in np.unique(episode):
 for g in np.unique(phase[episode==e]):
  mask=(episode==e)&(phase==g);weights[mask]=1./mask.sum()
weights/=weights.sum();path=root/'qualified_mod4_skills.npz';np.savez_compressed(path,obs=obs,actions=actions,episode=episode,phase_group=phase,sampling_weight=weights)
manifest=dict(sha256=hashlib.sha256(path.read_bytes()).hexdigest(),frames=len(obs),episodes=entries,actor_observations=35,critic_observations=78,actions=6,action_order=['left_front1_joint','left_rear1_joint','right_front1_joint','right_rear1_joint','left_wheel_joint','right_wheel_joint'],mode=[0,1,0,0,0,1,0],height_command='target_leg_length_command + wheel_radius;root relative support plane;not leg length alone',teacher_profile_sha256=index['profile_sha256'],dataset_task='fixed200mm',failed_oblique_excluded=True,teacher_actor_inference_calls=0,optimizer_steps=0,collection_wall_seconds=time.time()-started)
(root/'MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for row in index['files']:assert hashlib.sha256(Path(row['path']).read_bytes()).hexdigest()==row['sha256']
print('DATASET_READY',len(obs),manifest['sha256'],flush=True)
