"""Complete new slope raw, exact inherited data tolerances; all valid prefixes kept."""
from slope_io import *
import ast,numpy as np,traceback
sys.path.insert(0,str(D.parent/'MOD4_E1_G1_ACTUAL_REVIEW_20261010'))
import review_actual_schema_checked as common
recipe_manager=common.recipe_manager
hashfile=lambda p:H(p.read_bytes())
node=next(n for n in ast.parse(common.oldterrain.read_text(encoding='utf8')).body if isinstance(n,ast.FunctionDef) and n.name=='terrain')
class ProtocolOnly(ast.NodeTransformer):
 def visit_Constant(self,n):
  if n.value=='approved_E1_gentle_route_behavior_v1':n.value='approved_E1_SLOPE_derived8deg_mirrored_fullroute_behavior_v1'
  return n
exec(compile(ast.fix_missing_locations(ast.Module(body=[ProtocolOnly().visit(node)],type_ignores=[])),str(common.oldterrain),'exec'))

def main():
 collection=sorted(R.glob('SLOPE136_COLLECTED_[0-9]*.json'))[-1];v=json.loads(collection.read_bytes());reviews={}
 for jid,row in v['cases'].items():
  p,m,r=row['probe'],row['manifest'],row['result'];assert r['phase']=='complete' and not r['exit_code'] and not r['errors'] and not r['error_files'] and not r['new_learning']
  assert r['checkpoint']['sha256']==p['checkpoint_sha256']==m['artifacts']['checkpoint']['sha256']=='24b18846fcff1e0b8da7fd478314fca9cd2ed2b97461ca34f65ef5b7c7ff2411'
  assert r['runtime_archive_sha256']==m['artifacts']['runtime']['sha256']=='050ef42a3909b13292f0caf29c3a82a05c030d38a35a16312bdc6790c2a5b0c9'
  assert row['raw_SHA_exact'] and r['checkpoint']['finite_tensors']==102
  s=p['route_scope'];assert s['angle_deg']==8. and s['ramp_length_m']==2. and s['required_after_support_m']==.2 and s['no_vertical_riser'] and s['not_actual_RM_geometry']
  g=p['geometry_recipe']['SLOPE_geometry_change'];assert g['other_four_families_unchanged'] and g['proportions_unchanged']
  base=terrain(p,R/'cases'/jid);centers=np.array(s['tile_centers']);o=np.array(s['orientation']);assert (o==1).sum()==(o==-1).sum()==40
  starts=np.array(s['requested_starts']);assert np.allclose(np.array(p['initial']['root'])[:,:2],starts.astype(np.float32),atol=1e-6,rtol=0)
  sampled=np.array(s['actual_sampled_ground']);x=np.array(s['actual_sampled_canonical_x_m']);assert np.max(abs(sampled-(np.clip((x+1)/2,0,1)*2*np.tan(np.deg2rad(8)))[None,:]))<=1e-6
  names=p['body_names'];wi=[names.index(n) for n in ('left_wheel','right_wheel')];rows=[]
  with np.load(R/'cases'/jid/p['full_route_raw']['name']) as a:
   pos=a['COM_link_pos'];ep=a['episode'];failed=a['terminated'];force=a['physical_wheel_force_N'].reshape(1500,4,80,2,3);supported=np.maximum(force[...,2],0).sum(1)*.0025/.01>1.
   assert np.max(abs(np.linalg.norm(a['normal'],axis=-1)-1))<=.01 and a['normal'][...,2].min()>.01
   for i in range(80):
    u=(pos[:,i,wi,0]-centers[i,0])*o[i];failure=int(np.where(failed[:,i],np.arange(1500),1500).min());segments=[]
    for episode in np.unique(ep[:,i]):
     ids=np.flatnonzero((ep[:,i]==episode)&(np.arange(1500)<failure))
     if not len(ids):continue
     w=u[ids]
     if i%3==0:before=np.flatnonzero(w.max(1)<-1.2);after=np.flatnonzero(w.min(1)>1.2)
     elif i%3==1:before=np.flatnonzero(w.min(1)>1.2);after=np.flatnonzero(w.max(1)<-1.2)
     else:before=after=np.array([],dtype=int)
     complete=bool(len(before) and len(after) and before.min()<after.max());bc=[k for k in before if supported[ids[k],i].all()];ac=[k for k in after if supported[ids[k],i].all()]
     confirmed=bool(complete and bc and ac and min(bc)<max(ac))
     segments.append(dict(episode=int(episode),first_control=int(ids[0]),last_control=int(ids[-1]),canonical_wheel_x_range_m=[float(w.min()),float(w.max())],full_route_complete=complete,original1N_contact_confirmed=confirmed))
    rows.append(dict(env=i,group=('ascending','descending','stand')[i%3],orientation=int(o[i]),first_ordinary_failure_control=failure,complete=any(x['full_route_complete'] for x in segments),contact_confirmed=any(x['original1N_contact_confirmed'] for x in segments),segments=segments))
  summary={g:dict(environments=sum(x['group']==g for x in rows),complete_envs=sum(x['group']==g and x['complete'] for x in rows),contact_confirmed_envs=sum(x['group']==g and x['contact_confirmed'] for x in rows)) for g in ('ascending','descending','stand')}
  reviews[jid]=dict(base_review=base,groups=summary,rows=rows,all_valid_prefixes_retained=True,standing_not_required_to_cross=True)
 result=dict(epoch=time.time(),trial_id='E1-SLOPE8-136-FULL-RAW-ACTUAL-REVIEW-01',collection=str(collection),review=reviews,pending=v['pending'],review_complete=len(reviews)==1 and not v['pending'],frozen_complete135_scoped5deg_source=True,different8deg_geometry_not_same5deg_initialization=True,all_new_SDK_native_fullstate_PPO_pending=True,no_MoE_gate_or_RM_graduation=True,no_GPU_PPO_budget_write=True)
 p=save('SLOPE136_ACTUAL_REVIEW_'+str(time.time_ns())+'.json',result);print(json.dumps(dict(report=str(p),review_complete=result['review_complete'],summary={k:v['groups'] for k,v in reviews.items()},pending=result['pending'])))

if __name__=='__main__':
 try:main()
 except BaseException:save('SLOPE136_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),reader_only=True,original_results_preserved=True));raise
