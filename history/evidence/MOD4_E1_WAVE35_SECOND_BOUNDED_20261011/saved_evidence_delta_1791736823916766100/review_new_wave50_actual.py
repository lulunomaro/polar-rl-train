"""Independent fullraw50mm query/contact/route original contracts, geometry difference disclosed."""
from second_io import *
import ast,numpy as np
sys.path.insert(0,str(W/'MOD4_E1_G1_ACTUAL_REVIEW_20261010'));import review_actual_schema_checked as common
sys.path.insert(0,str(W/'MOD4_E1_G3_MATCHED_REVIEW_20261010'));import review_approach128_actual as oldaudit
prepared=json.loads((R/'WAVE50_COMPONENT_FROZEN_PREPARED.json').read_bytes());hashfile=lambda p:H(p.read_bytes());recipe_manager=common.recipe_manager
node=next(n for n in ast.parse(common.oldterrain.read_text(encoding='utf8')).body if isinstance(n,ast.FunctionDef) and n.name=='terrain')
class NewProtocolOnly(ast.NodeTransformer):
 def visit_Constant(self,n):
  if n.value=='approved_E1_gentle_route_behavior_v1':n.value=prepared['protocol']
  return n
exec(compile(ast.fix_missing_locations(ast.Module(body=[NewProtocolOnly().visit(node)],type_ignores=[])),str(common.oldterrain)+'#new50-protocol-only','exec'))
node=next(n for n in ast.parse((W/'MOD4_E1_G2_20MM_SCOPE_PREPARE_20261010/review20mm_allowlist_actual.py').read_text(encoding='utf8')).body if isinstance(n,ast.FunctionDef) and n.name=='audit')
exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),'original-full-wave-contact-route-audit#unchanged','exec'))
def main():
 cpath=sorted(R.glob('WAVE50_ACTUAL_COLLECTED_[0-9]*.json'))[-1];c=json.loads(cpath.read_bytes());rows={}
 for jid,row in c['cases'].items():
  p,m,r=row['probe'],row['manifest'],row['result'];assert r['phase']=='complete' and not r['exit_code'] and not r['errors'] and not r['error_files'] and not r['new_learning']
  assert p['checkpoint_sha256']==r['checkpoint']['sha256']==m['artifacts']['checkpoint']['sha256']==prepared['source_checkpoint']['sha256']
  assert r['checkpoint']['finite_tensors']==102 and p['steps']==m['steps']==r['steps']==1500 and row['raw_SHA_exact']
  assert r['runtime_archive_sha256']==m['artifacts']['runtime']['sha256']==prepared['package']['sha256'] and m['no_learning'] and not m['canonical_write_authority']
  assert m['physics_dt_s']==.0025 and m['control_dt_s']==.01 and m['solver_position']==32 and m['solver_velocity']==4
  g=p['geometry_recipe']['G4_geometry_change'];assert g['peak_to_trough_m']==.05 and g['other_four_families_unchanged'] and g['proportions_unchanged'] and g['not_RM70mm']
  s=p['route_scope'];orig=np.asarray(s['actual_world_ray_origins']);assert orig.shape==(80,35,3) and np.array_equal(orig,orig.astype(np.float32).astype(np.float64))
  x=orig[:,:,0]-np.asarray(s['tile_centers'])[:,None,0];assert np.array_equal(x,np.asarray(s['actual_canonical_ray_x']))
  profile=prepared['profile'];knots=np.r_[np.asarray(profile['profile_x_m'])[:-1],profile['span_m']];expected=np.interp(x+profile['span_m']/2,knots,np.asarray(profile['normalized_height'])*.05,left=0.,right=0.)
  assert np.array_equal(expected,np.asarray(s['expected_actual_sampled_ground'])) and np.max(abs(expected-np.asarray(s['actual_sampled_ground'])))<=1e-6 and s['actual_query_ground_tolerance_m']==1e-6
  a=audit(p,R/'cases'/jid);assert s['flat_support_margin_m']==.4 and p['geometry']['all_faces_and_winding_retained']
  source=next(x['probe'] for x in json.loads(sorted(R.glob('WAVE143_COLLECTED_[0-9]*.json'))[-1].read_bytes())['cases'].values() if 'full_route_raw' in x['probe'])
  for k in ('feedback_recipe','action_recipe','spring_recipe','gas_recipe','chassis_PD_recipe','body_names'):assert p[k]==source[k],k
  assert p['initial']['parameters']==source['initial']['parameters'] and p['initial']['assignments']==source['initial']['assignments'] and p['initial']['q']==source['initial']['q']
  rows[jid]=dict(review=a,actual_world_float32_query_identity_exact=True,original_ground1e6_tolerance_passed=True,new50mm_geometry_not_same35mm_initialization_claim=True,unchanged_parameters_assignments_q30_and_DR_static_recipes_exact=True)
 out=save('WAVE50_ACTUAL_REVIEW_'+str(time.time_ns())+'.json',dict(epoch=time.time(),collection=str(cpath),review=rows,review_complete=len(rows)==1 and not c['pending'],pending=c['pending'],original_strictfalse_and_all_failed_valid_prefixes_preserved=True,no_learning_or_full_RM70mm_MoE_graduation=True,source_saved_terraincommand_still35mm=True,no_GPU_PPO_queue_budget_write=True))
 print(json.dumps(dict(report=str(out),review_complete=len(rows)==1 and not c['pending'],summary={k:dict(groups=v['review']['groups'],base=v['review']['base_review']) for k,v in rows.items()},pending=c['pending'])))
if __name__=='__main__':
 try:main()
 except BaseException:save('WAVE50_REVIEW_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),read_only=True,original_result_not_relabelled=True));raise
