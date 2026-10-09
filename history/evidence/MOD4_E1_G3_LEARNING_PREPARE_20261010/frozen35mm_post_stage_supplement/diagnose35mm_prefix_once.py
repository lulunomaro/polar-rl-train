"""Preserve35mm partial routes, distinguish full section exit from after-support coverage."""
from pathlib import Path
import hashlib,json,time
import numpy as np
D=Path(__file__).resolve().parent;R=D/'reports';read=lambda p:json.loads(p.read_bytes());H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (R/'G3_126_PREFIX_DIAGNOSIS.json').exists()
v=read(sorted(R.glob('G3_126_REVIEW_*.json'))[-1]);assert v['review_complete'] and not v['pending'];jid,x=next(iter(v['review'].items()));x=x['review'];p=read(R/'cases'/jid/'probe.json');half=p['route_scope']['wave_x_halfspan_m'];centers=np.array(p['route_scope']['tile_centers']);rows=[]
with np.load(R/'cases'/jid/p['full_route_raw']['name']) as a:
 for r in x['full_route_rows']:
  if r['group']=='stand':continue
  i=r['env'];d=1 if r['group']=='forward' else -1;local=d*(a['COM_link_pos'][:,i][:,x['actual_wheel_indices'],0]-centers[i,0]);whole=np.max(np.min(local,axis=1));last=float(np.min(local[-1]));after=half+.2
  rows.append(dict(env=i,group=r['group'],complete_episodes=r['complete_episodes'],first_ordinary_failure_control=r['first_ordinary_failure_control'],best_both_wheel_after_wave_margin_m=float(whole-half),best_both_wheel_after_support_margin_m=float(whole-after),last_both_wheel_after_wave_margin_m=last-half,both_wheels_exited_wave=bool(whole>half),full_after_support=bool(r['complete_episodes']),original_prefix=r['segments']))
groups={g:dict(environments=sum(r['group']==g for r in rows),whole_wave_exit=sum(r['group']==g and r['both_wheels_exited_wave'] for r in rows),full_after_support=sum(r['group']==g and r['full_after_support'] for r in rows),incomplete=[r for r in rows if r['group']==g and not r['full_after_support']]) for g in ('forward','reverse')}
out=dict(epoch=time.time(),trial_id='E1-G3-35MM-126-PREFIX-DIAGNOSIS-06',source_sha256=p['checkpoint_sha256'],protocol=p['protocol'],independent_review_path=str(sorted(R.glob('G3_126_REVIEW_*.json'))[-1].resolve()),raw_sha256=H(R/'cases'/jid/p['full_route_raw']['name']),groups=groups,old_ground_contact_and_data_contracts_passed=True,ordinary=x['base_review']['ordinary'],closure_mm=x['base_review']['closure_mm'],new_geometry_learning_scope_admitted_only=True,full_35mm_course_passed=False,no_permanent_anti_forgetting_proof=True,selected32058_old_skills_from_complete123_reused=True,selected32103_for_more_learning=False,next_action='Prepare truly new35mm full geometry/resume CPU/SDK/native and two discarded PPO preflights, then one300s short observation from32058. Retain all partial routes and match candidate old skills before morePPO.',all_old_scope_clock_DR_tests_reused_without_replay=True,new_budget_seconds=0)
assert out['ordinary']==0; (R/'G3_126_PREFIX_DIAGNOSIS.json').write_bytes(json.dumps(out,indent=2).encode());print(json.dumps(dict(groups={g:{k:v for k,v in z.items() if k!='incomplete'} for g,z in groups.items()},ordinary=out['ordinary'],new_scope_short_observation_preparation_admitted=True,full35mm_pass=False)))
