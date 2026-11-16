from pathlib import Path
import json,hashlib,numpy as np
T=Path(__file__).resolve().parent;plan=json.loads((T/'PLAN.json').read_text());src=Path(plan['settle_cruise_repair']['source_dataset']);data=dict(np.load(src));old=data['sampling_weight'].copy();manifest=json.loads((src.parent/'MANIFEST.json').read_text());names=manifest['semantic_names'];targets=plan['quick_verification']['semantic_mass'];weights=np.zeros_like(old);stats={}
for i,name in enumerate(names):
 mask=data['semantic_id']==i;weights[mask]=old[mask]*(targets[name]/old[mask].sum());stats[name]=dict(manifest['semantic_sampling'][name],mass=float(weights[mask].sum()),expected_samples_per192=float(weights[mask].sum()*192),source_mass={str(int(s)):float(weights[mask&(data['source_id']==s)].sum())for s in np.unique(data['source_id'][mask])},previous_mass=float(old[mask].sum()))
assert np.all(weights>0)and abs(weights.sum()-1)<1e-10;data['sampling_weight']=weights;dst=T/'skill_dataset/qualified_mod4_skills.npz';assert not dst.exists();np.savez_compressed(dst,**data);verify=np.load(dst)
for key in data:
 if key!='sampling_weight':assert np.array_equal(verify[key],np.load(src)[key]),key
manifest.update(sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),semantic_sampling=stats,reweighted_from=str(src),source_dataset_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),observations_actions_episodes_and_source_membership_unchanged=True,new_teacher_episodes=0,optimizer_steps=0)
(T/'skill_dataset/MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8');plan['skill_supervision']['manifest_sha256']=manifest['sha256'];(T/'PLAN.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print('REWEIGHTED_SAME_DATA',manifest['frames'],'frames',json.dumps({n:round(x['mass'],4)for n,x in stats.items()}))
