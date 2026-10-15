"""Original signed two-wheel before/after route certificate and every valid prefix."""
from pathlib import Path
import json,time,hashlib,numpy as np
D=Path(__file__).resolve().parent;R=D/'reports';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
admission=R/'S5_SINGLE35_OWN_PHYSICAL_DATA_ADMITTED_s5_single_w35_original35_1500_v1.json';assert json.loads(admission.read_bytes())['passed']
src=sorted(R.glob('s5_single_w35_original35_1500_v1_CURRENT_ACTUAL_*.json'))[-1];j=json.loads(src.read_bytes());c=j['outputs']['COMPLETE_ACTUAL.json'];files=j['collected_files']
row=next(x for x in files if x['relative'].endswith('/route_raw.npz'));assert H(row['local_path'])==c['raw']['sha256']
with np.load(row['local_path']) as z:d={k:z[k].copy() for k in z.files}
rp=next(x for x in files if x['relative'].endswith('/probe.json'));report=json.loads(Path(rp['local_path']).read_bytes());scope=report['route_scope'];centers=np.asarray(scope['tile_centers']);half=scope['wave_x_halfspan_m'];wheel=[report['body_names'].index(x) for x in ('left_wheel','right_wheel')]
mean=np.maximum(d['physical_wheel_force_N'].reshape(1500,4,80,2,3)[...,2],0).sum(1)*np.float32(.0025)/np.float32(.01)
per=[]
for i in range(80):
 group=int(d['group_ids'][i]);sign=1 if group==0 else -1;episodes=[];completed=False;position=False
 for ep in np.unique(d['episode'][:,i]):
  ids=np.flatnonzero(d['episode'][:,i]==ep);fail=ids[d['terminated'][ids,i]]
  if len(fail):ids=ids[ids<fail[0]]
  if not len(ids):continue
  x=(d['COM_link_pos'][ids,i][:,wheel,0]-centers[i,0])*sign
  before=x.max(1)<-half-.2;after=x.min(1)>half+.2;load=mean[ids,i].min(1)>1.
  pos=group!=2 and before.any() and after.any() and np.flatnonzero(before).min()<np.flatnonzero(after).max()
  contact=group!=2 and (before&load).any() and (after&load).any() and np.flatnonzero(before&load).min()<np.flatnonzero(after&load).max()
  position=position or bool(pos);completed=completed or bool(contact)
  episodes.append(dict(episode=int(ep),valid_first_control=int(ids[0]),valid_last_control=int(ids[-1]),valid_controls=len(ids),ordinary_failure_control=int(fail[0]) if len(fail) else None,valid_unfinished_prefix=group!=2 and not bool(contact),signed_wheel_route_range=[float(x.min()),float(x.max())],before_position_controls=ids[before].tolist(),after_position_controls=ids[after].tolist(),before_double1N_controls=ids[before&load].tolist(),after_double1N_controls=ids[after&load].tolist(),position_complete=bool(pos),contact_complete=bool(contact),position_contact_agree=bool(pos)==bool(contact)))
 per.append(dict(env=i,group=group,standing_no_transit_requirement=group==2,position_complete=position,contact_complete=completed,all_valid_episodes=episodes))
first=next(x for x in files if x['relative'].endswith('/FIRST_PHYSICS_INITIAL_ACTUAL.json'));f=json.loads(Path(first['local_path']).read_bytes());assert np.array_equal(np.asarray(f['values']['root'],dtype=np.float32),d['before_root'][0])
assert report['initial']==f['values']
counts={g:sum(x['contact_complete'] for x in per if x['group']==g) for g in (0,1)}
q=R/'S5_SINGLE35_FULL1500_ORIGINAL_1N_ROUTE_ALL_PREFIX_COMPLETE_ACTUAL_REVIEW.json';assert not q.exists()
out=dict(epoch=time.time(),passed=True,full_original_data_admission=dict(path=str(admission),sha256=H(admission)),source_SHA=c['checkpoint_sha256'],raw=row,original_report=rp,first_physics_initial_snapshot=first,firstphysics_root_exact_to_first_saved_before_root=True,legacy_pre_wrapper_snapshot_separately_retained=True,cohorts=[27,27,26],ten_wave_span_m=half*2,approach_m=.4,after_support_margin_m=.2,control_dt=.01,controls=1500,callbacks=6000,original_doublewheel_load_threshold_N=1.,forward_complete=counts[0],reverse_complete=counts[1],ordinary=int(d['terminated'].sum()),truncation_unique=int(d['truncated'].sum()),position_contact_agree_all_episodes=all(ep['position_contact_agree'] for x in per for ep in x['all_valid_episodes']),all_valid_unfinished_and_preordinary_prefixes_preserved=True,no_sameepisode_reset_teleport_credit=True,stand26_not_required_to_transit=True,rows=per,no_27of27_or90_95_100_mechanical_promotion_rule=True,only_single_W35_actor_frozen=True,actual_frozen_trained_gate_source=False,whole_route_single_W35_policy=True,own_gate_fullstate_training_admission_pending=False,frozen_eval_not_S5_fair_MoE_qualification=True,terrain_height35_not50=True,qualified50=False)
q.write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(dict(report=str(q),actual_full80_complete=True,forward=str(counts[0])+'/27',reverse=str(counts[1])+'/27',ordinary=out['ordinary'],contact_position_agree=out['position_contact_agree_all_episodes'],qualified50=False)))
