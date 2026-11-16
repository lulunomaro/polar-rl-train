"""Reconstruct labels from actual saved MOD4 states; no teacher/student optimization."""
from pathlib import Path
import sys,json,hashlib,time
import numpy as np,torch,mujoco as mj
T=Path(__file__).resolve().parent;R=T.parents[2];S=R/'sources/local/MOD4V3_FIXED200_DAGGER_SEMANTIC_10M_20261116';X=R/'sources/local/MOD4V3_FIXED200_PREWALL_DIAG_DAGGER_20261117';sys.path.insert(0,str(X))
from common import setup,PPO_TO_NATIVE
sys.path.insert(0,str(T/'support'));from mod4v3_ppo_v1.history_common import H

def put(f,d):f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def netforce(t):
 force=np.zeros((2,3))
 for j in range(t.d.ncon):
  c=t.d.contact[j];f=np.zeros(6);mj.mj_contactForce(t.m,t.d,j,f);world=np.asarray(c.frame).reshape(3,3).T@f[:3]
  for i,b in enumerate(t.wheels):
   if t.m.geom_bodyid[c.geom1]==b:force[i]-=world
   if t.m.geom_bodyid[c.geom2]==b:force[i]+=world
 return np.linalg.norm(force,axis=1)
def one_interval(t,action):
 a=torch.from_numpy(np.asarray(action[PPO_TO_NATIVE],dtype=np.float32)).reshape(1,6);hist=[]
 for j in range(8):
  torque=t.env._torque(a).numpy().reshape(-1)
  if j%4==0:t.d.ctrl[t.env.act_ids[:4]]=torque[:4]
  t.d.ctrl[t.env.act_ids[4:]]=torque[4:];mj.mj_step(t.m,t.d)
  if j%2==1:hist.append(netforce(t))
 return np.asarray(hist[-3:]).max(0)
def history(obs,prefix):
 allobs=np.concatenate((prefix,obs));n=len(prefix);return np.stack([allobs[np.maximum(0,np.arange(n+i-H+1,n+i+1))]for i in range(len(obs))]).astype(np.float32)

def main():
 start=time.perf_counter();old=np.load(S/'skill_dataset/qualified_mod4_skills.npz');new=np.load(X/'evidence/qualified_prewall_pool.npz');om=json.loads((S/'skill_dataset/MANIFEST.json').read_text());nm=json.loads((X/'evidence/NEW_POOL_MANIFEST.json').read_text());records=[];arrays={k:[]for k in ['obs','actions','history','targets','episode','offset','semantic_id','origin']};counter=0
 for origin,entries,bank in [(0,om['episodes'],old),(1,nm['episode_index'],new)]:
  for e in entries:
   eid=int(e.get('episode',counter-23 if origin else counter));ids=np.flatnonzero(bank['episode']==eid)
   if origin:ids=ids[bank['prewall_mask'][ids]]
   path=Path(e['path']if origin else (e['trajectory']if 'trajectory'in e else str(Path(e['result']).parent/'observation_action_pairs.npz')));raw=np.load(path);nominal=not path.name=='correction.npz';obs=raw['obs'];act=raw['actions'];mm=int(e['start_offset_mm']);prefix=np.empty((0,35),np.float32)
   handoff=None
   if not nominal:
    handoff=json.loads((path.parent/'HANDOFF.json').read_text());cap=np.load(path.parent.parent/'student_capture/capture.npz');take=int(handoff['frame']);prefix=cap['obs'][:take]
   dest=T/'preflight/label_reconstruction'/f'episode_{counter:03d}';dest.mkdir(parents=True,exist_ok=False);t=setup(dest,mm)
   try:
    fullstates=raw['integration_state']if not nominal else None
    labels=[];contact_hist=netforce(t);max_qerr=0.;max_qd_error=0.;max_obs_qd_error=0.
    if nominal:
     trace=np.load(path.parent/'trace.npz');vel=np.concatenate((np.zeros((1,t.m.nv)),trace['qvel'][:-1]));t.d.qpos[:]=raw['pre_qpos'][0];t.d.qvel[:]=0;t.d.ctrl[:]=0;mj.mj_forward(t.m,t.d)
    else:
     if take:
      mj.mj_setState(t.m,t.d,cap['integration_state'][take-1],mj.mjtState.mjSTATE_INTEGRATION);mj.mj_forward(t.m,t.d);contact_hist=one_interval(t,cap['actions'][take-1])
    for k in range(len(obs)):
     if fullstates is not None:mj.mj_setState(t.m,t.d,fullstates[k],mj.mjtState.mjSTATE_INTEGRATION)
     else:
      t.d.qpos[:]=raw['pre_qpos'][k];t.d.qvel[:]=vel[k]
     mj.mj_forward(t.m,t.d)
     if k==0:contact_hist=np.maximum(contact_hist,netforce(t))
     bodyvel=t.d.xmat[t.env.base_id].reshape(3,3).T@t.d.qvel[:3];labels.append(np.r_[bodyvel,(contact_hist>5.).astype(np.float32)])
     max_obs_qd_error=max(max_obs_qd_error,float(np.abs(t.d.qvel[t.va][PPO_TO_NATIVE]*.1-obs[k,16:22]).max()))
     contact_hist=one_interval(t,act[k]);targetq=trace['qpos'][k]if nominal else raw['qpos'][k];max_qerr=max(max_qerr,float(np.abs(t.d.qpos-targetq).max()))
     targetv=trace['qvel'][k]if nominal else raw['qvel'][k];max_qd_error=max(max_qd_error,float(np.abs(t.d.qvel-targetv).max()))
    local=np.flatnonzero(bank['episode']==eid);selected=ids-local[0];assert np.array_equal(obs[selected],bank['obs'][ids]);assert np.array_equal(act[selected],bank['actions'][ids]);assert max_obs_qd_error<2e-6,(counter,max_obs_qd_error)
    hist=history(obs,prefix);labels=np.asarray(labels,np.float32);assert np.isfinite(labels).all()
    for key,value in [('obs',obs[selected]),('actions',act[selected]),('history',hist[selected]),('targets',labels[selected]),('episode',np.full(len(ids),counter)),('offset',np.full(len(ids),mm)),('semantic_id',np.full(len(ids),9)if origin else old['semantic_id'][ids]),('origin',np.full(len(ids),origin))]:arrays[key].append(value)
    records.append(dict(episode=counter,source=str(path),frames=len(ids),full_history_frames=len(obs)+len(prefix),offset_mm=mm,origin=origin,max_replayed_qpos_error=max_qerr,max_replayed_qvel_error=max_qd_error,pre_obs_joint_velocity_error=max_obs_qd_error));print('EPISODE',counter,len(ids),'qerr',max_qerr,flush=True)
   finally:
    if hasattr(t.env,'close'):t.env.close()
   counter+=1
 data={k:np.concatenate(v)for k,v in arrays.items()};assert len(data['obs'])==8391+1838;assert data['history'].shape==(10229,H,35)
 # Explicit semantic fractions, replacing undersampled key transition buckets.
 names=om['semantic_names']+['prewall_recovery'];fractions=np.array([.08,.13,.03,.20,.14,.08,.08,.04,.02,.20]);assert abs(fractions.sum()-1)<1e-6
 weights=np.zeros(len(data['obs']),np.float64)
 for j,p in enumerate(fractions):mask=data['semantic_id']==j;assert mask.any();weights[mask]=p/mask.sum()
 data['sampling_weight']=weights.astype(np.float32);np.savez_compressed(T/'skill_dataset/history_skills.npz',**data)
 manifest=dict(frames=len(weights),original_frames=8391,qualified_prewall_frames=1838,episodes=records,semantic_names=names,semantic_fractions=fractions.tolist(),sha256=hashlib.sha256((T/'skill_dataset/history_skills.npz').read_bytes()).hexdigest(),history_includes_current=True,history_first_frame_repeated=True,DAgger_student_prefix_context_only=True,critic_velocity_slice=[28,31],critic_contact_slice=[69,71],velocity_scale=1.,contact_threshold_N=5.,contact_sampling='MuJoCo reconstructed per-body net force norm;5ms samples,last3;Isaac online labels use actual critic sensor history',PPO_updates=0,wall_seconds=time.perf_counter()-start)
 put(T/'skill_dataset/MANIFEST.json',manifest);print('DATASET_COMPLETE',len(weights),flush=True)
if __name__=='__main__':main()
