"""Saved-trace kinematic audit of ten independent student rollouts. No optimizer."""
from common import *
import math

def feature(z,k,m,d):
 d.qpos[:]=z['qpos'][k];d.qvel[:]=0;mj.mj_forward(m,d)
 gids=[j for j in range(m.ngeom)if m.geom_bodyid[j]>0 and(m.geom_contype[j]or m.geom_conaffinity[j])]
 front=max(float(d.geom_xpos[j,0]+m.geom_rbound[j])for j in gids)
 tr=z['trace'][k];o=z['obs'][k];a=z['actions'][k]
 return dict(frame_k=int(k),pre_action_time_s=round(float(tr[0]-.02),6),post_action_time_s=round(float(tr[0]),6),root_xyz=tr[1:4].tolist(),forward_vx=float(tr[4]),pitch_deg=math.degrees(float(tr[6])),command=o[:4].tolist(),wheel_observation=o[20:22].tolist(),wheel_velocity_rad_s=(10*o[20:22]).tolist(),leg_actions=a[:4].tolist(),wheel_actions=a[4:].tolist(),all35_observation=o.tolist(),root_height_error_m=float(o[3]/5-tr[3]),conservative_front_x=front,definitely_clear_of_step=bool(front<1.2),robot_collision_bound_clearance_m=1.2-front)

def main():
 guard();rows=[]
 for tag in ['model_005m','model_010m']:
  for mm in [-60,-30,0,30,60]:
   src=P/f'evidence/checkpoint_evals/{tag}/single_step/start_{mm:+04d}mm';z=np.load(src/'rollout.npz');m=mj.MjModel.from_xml_path(str(src/'scene.xml'));d=mj.MjData(m)
   o=z['obs'];a=z['actions'];tr=z['trace'];start=int(np.flatnonzero(o[:,0]>.1)[0]);mask=(np.arange(len(tr))>=start)&(tr[:,1]<1.)&(o[:,3]>2.)
   def first(cond):
    ix=np.flatnonzero(mask&cond);return feature(z,int(ix[0]),m,d)if len(ix)else None
   wheel=first(np.all(a[:,4:]<-.1,axis=1))
   mild=first(o[:,3]/5-tr[:,3]>=.02)
   severe=first((o[:,3]/5-tr[:,3]>=.08)&np.all(a[:,[1,3]]>1.,axis=1))
   row=dict(model=tag,start_offset_mm=mm,source=str(src/'rollout.npz'),sha256=sha(src/'rollout.npz'),first_command=feature(z,start,m,d),first_both_negative_wheel_actions=wheel,first_height_error20mm=mild,first_severe_crouch80mm_with_rear_action_above1=severe,student_has_lift_fsm=False,heuristic_crouch_is_not_an_actual_FSM_transition=True,all_student_actions_teacher_free=True)
   rows.append(row);print(tag,mm,'drop20',mild['frame_k']if mild else None,'severe',severe['frame_k']if severe else None,'clear',severe['definitely_clear_of_step']if severe else None,flush=True)
 names=json.loads((S/'skill_dataset/MANIFEST.json').read_text(encoding='utf-8'))['semantic_names'];old=np.load(S/'skill_dataset/qualified_mod4_skills.npz');o=old['obs'];low=(abs(o[:,0]-.47)<1e-5)&(np.max(abs(o[:,20:22]),axis=1)<.2)
 put(T/'evidence/PREWALL_DIAGNOSIS.json',dict(rows=rows,criterion=dict(mild='root height >=20mm below constant command',severe='>=80mm below command AND both rear actions>1.0, while root_x<1m',geometry='Conservative sphere bounds, kinematics only; no inferred contact forces'),existing_low_wheel_frames=dict(criterion='cmd=.47,both |wheel obs|<.2',total=int(low.sum()),by_semantic={n:int((low&(old['semantic_id']==i)).sum())for i,n in enumerate(names)}),optimizer_updates=0,PPO_updates=0))
 guard()
if __name__=='__main__':main()
