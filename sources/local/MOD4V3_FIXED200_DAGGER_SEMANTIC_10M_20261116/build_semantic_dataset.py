"""Build event-semantic dataset from frozen nominal teacher and admitted DAgger."""
from pathlib import Path
import json,hashlib,numpy as np
T=Path(__file__).resolve().parent;R=T.parents[2];F=R/'sources/local/MOD4V3_SERIAL_TEACHER_FIXED200_40M_20261116';plan=json.loads((T/'PLAN.json').read_text());targets=plan['quick_verification']['semantic_mass'];names=list(targets);xs=[];ys=[];labels=[];sources=[];episodes=[];meta=[]
def admit(obs,actions,groups,source,entry):
 assert len(obs)==len(actions)==len(groups)and (groups>=0).all()
 eid=len(meta);xs.append(obs.astype(np.float32));ys.append(actions.astype(np.float32));labels.extend(groups);sources.extend([source]*len(obs));episodes.extend([eid]*len(obs));meta.append(dict(entry,episode=eid,qualified=True,source='nominal_teacher'if source==0 else'qualified_dagger',frames=len(obs)))
a=np.load(F/'skill_dataset/qualified_mod4_skills.npz');old=json.loads((F/'skill_dataset/MANIFEST.json').read_text())
for eid,mm in enumerate([-60,-30,0,30,60]):
 ids=np.flatnonzero(a['episode']==eid);z=np.load(F/'teacher_collection'/f'start_{mm:+04d}mm/trace.npz');cols=list(z['columns']);f=z['trace'];ph=z['phases'][:,0];idx=np.arange(len(ids));contact=int(np.flatnonzero((f[:,cols.index('edge_l')]>0)|(f[:,cols.index('edge_r')]>0)|(f[:,cols.index('guide_force')]>5))[0]);first=int(np.flatnonzero(ph=='lift')[0]);last=int(np.flatnonzero(ph!='idle')[-1]);g=np.full(len(ids),-1,np.int64)
 for key,mask in [('settle',(idx<contact)&(a['obs'][ids,0]==0)),('cruise',(idx<contact)&(a['obs'][ids,0]>0)),('contact_pre_lift',(idx>=contact)&(idx<first)),('post',idx>last)]+[(p,ph==p)for p in ['lift','swing','plant','capture']]:g[mask]=names.index(key)
 admit(a['obs'][ids],a['actions'][ids],g,0,dict(start_offset_mm=mm,original_episode=eid,result=str(F/'teacher_collection'/f'start_{mm:+04d}mm/RESULT.json'),first_contact_frame=contact,first_lift_frame=first))
for row in json.loads((T/'dagger/ADMISSION_SUMMARY.json').read_text())['rows']:
 if not row['qualified']:continue
 path=Path(row['trajectory']);z=np.load(path);x=z['obs'];ph=z['phases'];f=z['features'];idx=np.arange(len(x));active=np.flatnonzero(ph!='idle');assert len(active);lifts=np.flatnonzero(ph=='lift');assert len(lifts);first=int(lifts[0]);last=int(active[-1]);contacts=np.flatnonzero((f[:,11]>0)|(f[:,12]>0)|(f[:,15]>5));assert len(contacts);contact=int(contacts[0]);g=np.full(len(x),-1,np.int64)
 for key,mask in [('approach_correction',idx<contact),('contact_pre_lift',(idx>=contact)&(idx<first)),('post',idx>last)]+[(p,ph==p)for p in ['lift','swing','plant','capture']]:g[mask]=names.index(key)
 assert np.allclose(x[:,3],z['root_height_cmd']*5.,atol=2e-6)
 admit(x,z['actions'],g,1,dict(start_offset_mm=row['start_offset_mm'],source_model=row['model'],takeover_node=row['node'],admission=str(path.parent/'ADMISSION.json'),trajectory=str(path),final_hold_s=row['final_continuous_top_hold_s'],first_contact_frame=contact,first_lift_frame=first))
x=np.concatenate(xs);y=np.concatenate(ys);semantic=np.asarray(labels,np.int64);source=np.asarray(sources,np.int64);episode=np.asarray(episodes,np.int64);weights=np.zeros(len(x),np.float64);groups={}
for i,name in enumerate(names):
 mask=semantic==i;assert mask.any(),f'Empty required semantic group {name}'
 present=np.unique(source[mask]);source_mass={}
 for origin in present:
  origin_mask=mask&(source==origin);eids=np.unique(episode[origin_mask]);mass=targets[name]/len(present);source_mass[str(origin)]=mass
  for eid in eids:
   select=origin_mask&(episode==eid);weights[select]=mass/len(eids)/select.sum()
 groups[name]=dict(frames=int(mask.sum()),mass=float(weights[mask].sum()),expected_samples_per192=float(weights[mask].sum()*192),nominal_frames=int((mask&(source==0)).sum()),dagger_frames=int((mask&(source==1)).sum()),source_mass=source_mass)
assert np.isclose(weights.sum(),1.)and np.all(weights>0)and np.isfinite(x).all()and np.isfinite(y).all()and np.abs(y).max()<=6.
path=T/'skill_dataset/qualified_mod4_skills.npz';assert not path.exists();np.savez_compressed(path,obs=x,actions=y,episode=episode,semantic_id=semantic,source_id=source,sampling_weight=weights)
manifest=dict(sha256=hashlib.sha256(path.read_bytes()).hexdigest(),frames=len(x),episodes=meta,semantic_names=names,semantic_sampling=groups,nominal_teacher_episodes=5,qualified_dagger_episodes=len(meta)-5,rejected_dagger_episodes=json.loads((T/'dagger/ADMISSION_SUMMARY.json').read_text())['rejected'],actor_observations=35,critic_observations=78,actions=6,mode=[0,1,0,0,0,1,0],preaction_observations=True,teacher_phase_is_postaction=True,height_command='target_leg_length_command +0.0625; previous published command is used in preaction observation',teacher_actor_inference_calls=0,student_prefix_actions_excluded=True,optimizer_steps=0,action_order=old['action_order'],teacher_profile_sha256=old['teacher_profile_sha256'],dagger_admission='Native teacher physical stable-top standard; final hold>=0.4s; no historical student-speed veto; student evaluation unchanged')
(T/'skill_dataset/MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8');plan['skill_supervision']['manifest_sha256']=manifest['sha256'];plan['budget_total_training_seconds']=600;plan['source_attempt']='New10min experiment; prior40min startup failures remain in prior directory';plan['quick_verification']['dagger_admission_protocol']='NATIVE_TEACHER_RECOVERY_STABLE_TOP_V2';(T/'PLAN.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('DATASET',len(x),'frames',len(meta)-5,'qualified DAgger episodes')
print('SAMPLING',json.dumps(groups,ensure_ascii=False))
