"""Reuse unchanged ground/contact/raw/signed route contracts with new35mm protocol."""
from pathlib import Path
import ast,hashlib,json,sys,time,traceback
import numpy as np
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';read=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sys.path.insert(0,str(W/'MOD4_E1_G1_ACTUAL_REVIEW_20261010'));import review_actual_schema_checked as common
old=W/'MOD4_E1_G2_20MM_SCOPE_PREPARE_20261010/review20mm_allowlist_actual.py'
base=next(n for n in ast.parse(common.oldterrain.read_text(encoding='utf8')).body if isinstance(n,ast.FunctionDef) and n.name=='terrain')
class Protocol(ast.NodeTransformer):
 def visit_Constant(self,n):
  if n.value=='approved_E1_gentle_route_behavior_v1':n.value='approved_E1_G3_derived35mm_complete_wave_route_behavior_v1'
  return n
hashfile=sha;recipe_manager=common.recipe_manager
exec(compile(ast.fix_missing_locations(ast.Module(body=[Protocol().visit(base)],type_ignores=[])),str(common.oldterrain),'exec'))
node=next(n for n in ast.parse(old.read_text(encoding='utf8')).body if isinstance(n,ast.FunctionDef) and n.name=='audit')
exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),str(old),'exec'))
def main():
 v=read(sorted(R.glob('G3_125_COLLECTED_*.json'))[-1]);prepared=read(R/'PREPARED.json');rows={}
 for jid,row in v['cases'].items():
  p,m,r=row['probe'],row['manifest'],row['result'];assert r['phase']=='complete' and not r['exit_code'] and not r['errors'] and not r['error_files'] and not r['new_learning'] and row['raw_SHA_exact']
  assert r['checkpoint']['sha256']==m['artifacts']['checkpoint']['sha256']==p['checkpoint_sha256']==prepared['selected_source']['sha256'] and r['checkpoint']['finite_tensors']==96
  assert r['runtime_archive_sha256']==m['artifacts']['runtime']['sha256']==prepared['package']['sha256'] and m['no_learning'] and not m['canonical_write_authority']
  g=p['geometry_recipe']['G3_geometry_change'];assert g['peak_to_trough_m']==.035 and g['other_four_families_unchanged'] and g['proportions_unchanged'] and g['not_RM70mm']
  assert p['route_scope']['family']=='CAD_derived35mm_wave' and np.max(p['route_scope']['actual_sampled_ground'])<=.035001
  a=audit(p,R/'cases'/jid)
  previous=read(W/'MOD4_E1_G2_LEARNING_PREPARE_20261010/reports/cases/clk2500-closure-episode-d3-123-e1-g2-observation-terrain-flat/probe.json')
  assert p['seed']==previous['seed']==20260928 and p['profile']==previous['profile']=='white_v3'
  for k in ('sensor_recipe','feedback_recipe','action_recipe','spring_recipe','gas_recipe','chassis_PD_recipe','body_names'):assert p[k]==previous[k],k
  assert p['initial']['assignments']==previous['initial']['assignments'] and p['initial']['parameters']==previous['initial']['parameters'] and p['initial']['q']==previous['initial']['q']
  rows[jid]=dict(checkpoint_sha256=p['checkpoint_sha256'],review=a,actual_new_geometry=True,old_D1_D7_initial_parameters_recipes_assignments_exact=True)
 value=dict(epoch=time.time(),trial_id='E1-G3-35MM-ACTUAL-REVIEW-01',review=rows,summary={jid:dict(groups=x['review']['groups'],ordinary=x['review']['base_review']['ordinary'],closure_mm=x['review']['base_review']['closure_mm']) for jid,x in rows.items()},pending=v['pending'],review_complete=len(rows)==1 and not v['pending'],no_new_learning_or_native_fullPPO_admission=True,no_RM70mm_or_all_E1_graduation=True,no_permanent_anti_forgetting_proof=True,reused_raw_route_contract_sources={str(old):sha(old),str(common.oldterrain):sha(common.oldterrain)},no_clock_replay_or_GPU_PPO_canonical_write=True,new_budget_seconds=0)
 out=R/('G3_125_REVIEW_'+str(int(value['epoch']))+'.json');assert not out.exists();out.write_text(json.dumps(value,indent=2),encoding='utf8');print(json.dumps(dict(report=str(out),summary=value['summary'],pending=value['pending'],review_complete=value['review_complete']),ensure_ascii=True))
if __name__=='__main__':
 try:main()
 except Exception:
  out=R/('G3_125_REVIEW_ERROR_'+str(int(time.time()))+'.json');assert not out.exists();out.write_text(json.dumps(dict(epoch=time.time(),trial_id='E1-G3-35MM-CPU-READER-01',error=traceback.format_exc(),original_source_and_error_retained=True,no_production_change=True),indent=2),encoding='utf8');raise
