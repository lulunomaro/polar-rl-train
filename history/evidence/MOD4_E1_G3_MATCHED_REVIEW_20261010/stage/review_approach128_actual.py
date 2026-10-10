"""New paired frozen approach scope with unchanged full raw/contact/route contracts."""
from pathlib import Path
import ast,hashlib,json,sys,time,traceback
import numpy as np
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';read=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sys.path.insert(0,str(W/'MOD4_E1_G1_ACTUAL_REVIEW_20261010'));import review_actual_schema_checked as common
old=W/'MOD4_E1_G2_20MM_SCOPE_PREPARE_20261010/review20mm_allowlist_actual.py';hashfile=sha;recipe_manager=common.recipe_manager
node=next(n for n in ast.parse(common.oldterrain.read_text(encoding='utf8')).body if isinstance(n,ast.FunctionDef) and n.name=='terrain')
class Protocol(ast.NodeTransformer):
 def visit_Constant(self,n):
  if n.value=='approved_E1_gentle_route_behavior_v1':n.value='approved_E1_G3_derived35mm_paired_approach040_behavior_v2'
  return n
exec(compile(ast.fix_missing_locations(ast.Module(body=[Protocol().visit(node)],type_ignores=[])),str(common.oldterrain),'exec'))
node=next(n for n in ast.parse(old.read_text(encoding='utf8')).body if isinstance(n,ast.FunctionDef) and n.name=='audit');exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),str(old),'exec'))
def main():
 v=read(sorted(R.glob('G3_128_COLLECTED_*.json'))[-1]);prepared=read(R/'PAIRED_APPROACH_PREPARED.json');rows={};probes={}
 for jid,row in v['cases'].items():
  p,m,r=row['probe'],row['manifest'],row['result'];assert r['phase']=='complete' and not r['exit_code'] and not r['errors'] and not r['error_files'] and not r['new_learning'] and row['raw_SHA_exact']
  assert r['checkpoint']['sha256']==m['artifacts']['checkpoint']['sha256']==p['checkpoint_sha256'] and r['checkpoint']['finite_tensors']==96
  assert r['runtime_archive_sha256']==m['artifacts']['runtime']['sha256']==prepared['package']['sha256'] and m['no_learning'] and not m['canonical_write_authority']
  assert p['steps']==m['steps']==r['steps']==1500 and p['route_scope']['flat_support_margin_m']==.4
  g=p['geometry_recipe']['G3_geometry_change'];assert g['peak_to_trough_m']==.035 and g['other_four_families_unchanged'] and g['proportions_unchanged'] and g['not_RM70mm']
  a=audit(p,R/'cases'/jid);rows[m['role']]=dict(job_id=jid,checkpoint_SHA=p['checkpoint_sha256'],review=a);probes[m['role']]=p
 pair=False
 if set(probes)=={'source32058','candidate32063'}:
  a,b=[probes[k] for k in ('source32058','candidate32063')]
  for k in ('initial','geometry','geometry_recipe','route_scope','sensor_recipe','feedback_recipe','action_recipe','spring_recipe','gas_recipe','chassis_PD_recipe','body_names'):assert a[k]==b[k],k
  pair=True
 out=dict(epoch=time.time(),trial_id='E1-G3-128-PAIRED-APPROACH-ACTUAL-REVIEW-01',review=rows,summary={role:dict(groups=x['review']['groups'],ordinary=x['review']['base_review']['ordinary'],closure_mm=x['review']['base_review']['closure_mm']) for role,x in rows.items()},pending=v['pending'],review_complete=pair and not v['pending'],paired_initial_root30q_parameters_recipes_assignments_exact=pair,old15s_065_original_failures_preserved=True,no_original15s_pass_relabeling=True,retention127_reused_without_replay=True,no_PPO_or_next50mm_admission=True,new_budget_seconds=0)
 p=R/('G3_128_REVIEW_'+str(int(out['epoch']))+'.json');assert not p.exists();p.write_bytes(json.dumps(out,indent=2).encode());print(json.dumps(dict(report=str(p),summary=out['summary'],pending=out['pending'],review_complete=out['review_complete'])))
if __name__=='__main__':
 try:main()
 except Exception:
  p=R/('G3_128_REVIEW_ERROR_'+str(int(time.time()))+'.json');p.write_bytes(json.dumps(dict(epoch=time.time(),trial_id='E1-G3-128-CPU-READER-01',error=traceback.format_exc(),no_production_mutation=True),indent=2).encode());raise
