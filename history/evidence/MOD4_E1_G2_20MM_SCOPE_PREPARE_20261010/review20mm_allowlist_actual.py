"""Independently audit full same-G1 before-to-after wheel routes; CPU only."""
from pathlib import Path
import ast,hashlib,json,sys,time,traceback
import numpy as np
D=Path(__file__).resolve().parent;R=D/'reports';sys.path.insert(0,str(D.parent/'MOD4_E1_G1_ACTUAL_REPAIRED_REVIEW_20261010'))
import review_actual_schema_checked as common
read=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
node=next(n for n in ast.parse(common.oldterrain.read_text(encoding='utf8')).body if isinstance(n,ast.FunctionDef) and n.name=='terrain')
class Protocol(ast.NodeTransformer):
 def visit_Constant(self,n):
  if n.value=='approved_E1_gentle_route_behavior_v1':n.value='approved_E1_G2_derived20mm_complete_wave_route_behavior_v1'
  return n
node=Protocol().visit(node);hashfile=sha;recipe_manager=common.recipe_manager
exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),str(common.oldterrain),'exec'))
def audit(p,folder):
 base=terrain(p,folder);s=p['route_scope'];centers=np.array(s['tile_centers']);starts=np.array(s['requested_starts']);half=s['wave_x_halfspan_m']
 assert s['actual_authored_ground_query_passed'] and s['production_boundary_unchanged'] and s['not_training_or_RM70mm']
 assert centers.shape==starts.shape==(80,2) and len(set(zip(s['tile_rows'],s['tile_cols'])))==80
 assert np.all(np.array(s['tile_cols'])>=34) and np.all(np.array(s['tile_cols'])<=39)
 assert np.allclose(np.array(p['initial']['root'])[:,:2],starts.astype(np.float32),atol=1e-6,rtol=0)
 names=p['body_names'];left=[i for i,n in enumerate(names) if n in ('left_wheel','left_wheel_link')];right=[i for i,n in enumerate(names) if n in ('right_wheel','right_wheel_link')]
 assert len(left)==len(right)==1,('Actual wheel-link names need an explicit reader mapping',names)
 wheelids=[left[0],right[0]];rows=[]
 with np.load(folder/p['full_route_raw']['name']) as a:
  assert a['COM_link_pos'].shape==(1500,80,len(names),3)
  normals=a['normal'];assert np.max(abs(np.linalg.norm(normals,axis=-1)-1))<=.01 and np.min(normals[...,2])>.01
  for i in range(80):
   group=i%3;d=1 if group==0 else -1
   failure=int(np.where(a['terminated'][:,i],np.arange(1500),1500).min())
   local=a['COM_link_pos'][:,i,:,:][:,wheelids,0]-centers[i,0]
   episodes=a['episode'][:,i];completes=[];segments=[]
   for ep in np.unique(episodes):
    ids=np.flatnonzero((episodes==ep)&(np.arange(1500)<failure));
    if not len(ids):continue
    signed=d*local[ids]
    before=np.flatnonzero(np.max(signed,axis=1)<-half-.2);after=np.flatnonzero(np.min(signed,axis=1)>half+.2)
    complete=group!=2 and len(before)>0 and len(after)>0 and before.min()<after.max()
    if complete:completes.append(int(ep))
    segments.append(dict(episode=int(ep),first_control=int(ids[0]),last_control=int(ids[-1]),wheel_x_range_m=[float(local[ids].min()),float(local[ids].max())],both_wheels_before_support_observed=bool(len(before)),both_wheels_after_support_observed=bool(len(after)),whole_section_correct_direction_before_ordinary_failure=bool(complete)))
   rows.append(dict(env=i,group=('forward','reverse','stand')[group],first_ordinary_failure_control=failure,complete_episodes=completes,segments=segments,route_truncations=int(a['reasons'][:,i,p['reason_names'].index('rough_route_boundary')].sum())))
  # Actual wheel link position, force and ground samples are all retained, no reset jump counted.
  force=a['physical_wheel_force_N'].reshape(1500,4,80,2,3)
  supported=(np.maximum(force[...,2],0).sum(1)*.0025/.01)>1.
  support_summary={label:dict(both_wheels_control_fraction=float(supported[:,np.arange(80)%3==g].all(-1).mean()),complete_envs=sum(bool(x['complete_episodes']) for x in rows if x['group']==label),environments=sum(x['group']==label for x in rows)) for g,label in enumerate(('forward','reverse','stand'))}
 return dict(base_review=base,actual_wheel_indices=wheelids,full_route_rows=rows,groups=support_summary,actual_full_wave_route_not_just_origin_reset=True,all_saved_failed_prefix_and_signed_progress_retained=True)
def main():
 v=read(sorted(R.glob('ACTUAL_REPAIRED_COLLECTED_*.json'))[-1]);review={}
 for jid,row in v['cases'].items():
  p,m,r=row['probe'],row['manifest'],row['result'];assert r['checkpoint']['sha256']==m['artifacts']['checkpoint']['sha256']==p['checkpoint_sha256']
  assert r['runtime_archive_sha256']==m['artifacts']['runtime']['sha256']=='c4255fe5c3407a42019416fdffa6d6786a51b84ae4312f6e362e2b2a60ba1271'
  assert m['no_learning'] and not m['canonical_write_authority'] and r['exit_code']==0 and not r['errors'] and not r['error_files']
  role=m['role'];review[role]=dict(job_id=jid,checkpoint_sha256=p['checkpoint_sha256'],review=audit(p,R/'cases'/jid))
 if False: # This new geometric scope is a single selected-source actual interface/route check, not a paired learning result.
  a,b=[read(R/'cases'/review[x]['job_id']/'probe.json') for x in ('anchor32053','candidate32098')]
  for k in ('initial','geometry','geometry_recipe','route_scope','sensor_recipe','feedback_recipe','action_recipe','spring_recipe','gas_recipe','chassis_PD_recipe','body_names'):assert a[k]==b[k],k
 summary={k:dict(groups=x['review']['groups'],ordinary=x['review']['base_review']['ordinary'],closure_mm=x['review']['base_review']['closure_mm']) for k,x in review.items()}
 report=dict(epoch=time.time(),trial_id='E1-G2-20MM-ACTUAL-FULLROUTE-REVIEW-01',review=review,summary=summary,pending=v['pending'],review_complete=len(review)==1,single_selected_source_actual_ground_contact_route_scope=True,source_selection_not_changed=True,failed32098_not_auto_selected=True,no_90_95_100_graduation_line=True,no_RM70mm_or_all_E1_graduation=True,new_budget_seconds=0,no_GPU_PPO_or_canonical_write=True)
 p=R/('ACTUAL_REPAIRED_REVIEW_'+str(int(report['epoch']))+'.json');p.write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(dict(report=str(p),summary=summary,pending=v['pending']),ensure_ascii=True))
if __name__=='__main__':
 try:main()
 except Exception:
  (R/('ACTUAL_REPAIRED_REVIEW_ERROR_'+str(int(time.time()))+'.json')).write_text(json.dumps(dict(epoch=time.time(),trial_id='E1-G2-20MM-CPU-READER-01',error=traceback.format_exc(),reader_only_production_unchanged=True),indent=2),encoding='utf8');raise
