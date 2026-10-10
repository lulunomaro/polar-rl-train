"""Preserve first staged source; repair its CPU validation adapter before GPU admission."""
from pathlib import Path
import ast,json,time,hashlib
D=Path(__file__).resolve().parent;P=D/'reviewed_payload';C=P/'isaac/mod4';R=D/'reports';C.mkdir(parents=True,exist_ok=True)
base=(D/'inherited_source/supervise_e1_command_retention_episode_reviewed_once.py').read_text();tree=ast.parse(base)
fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='fullsave');text=ast.get_source_segment(base,fn)
old="validator=validate if ck['E1_terrain_state']['profile']=='mod4_G3_CAD_derived_35mm_v1' else (previous_G2_validate if ck['E1_terrain_state']['profile']=='mod4_G2_CAD_derived_20mm_v1' else old_validate)"
assert text.count(old)==1
text=text.replace(old,"from curb20_current_state import validate as CURB_validate\n        validator=CURB_validate if ck['E1_terrain_state']['profile']=='mod4_CURB_derived20mm_strip150_mirrored_v1' else (validate if ck['E1_terrain_state']['profile']=='mod4_G3_CAD_derived_35mm_v1' else (previous_G2_validate if ck['E1_terrain_state']['profile']=='mod4_G2_CAD_derived_20mm_v1' else old_validate))")
prefix='''"""All original D0-D7 validators retained; explicitly validate new CURB terrain too."""
import supervise_e1_command_retention_episode_reviewed_once as inherited
s=inherited.s
validate_delay_state=inherited.validate_delay_state
PhysicsActionQueue=inherited.PhysicsActionQueue
validate_saved_pressure=inherited.validate_saved_pressure
validate_saved_damping=inherited.validate_saved_damping
validate_saved_chassis_pd=inherited.validate_saved_chassis_pd
'''
raw=prefix+text+'\n';compile(raw,'curb20_fullsave_cpu.py','exec');p=C/'curb20_fullsave_cpu.py';assert not p.exists();p.write_text(raw)
raw='''"""Reviewed admission wrapper; original378 source retained, no original main replay."""
import supervise_curb20_fullstate_once as prior
from curb20_fullsave_cpu import fullsave as complete_validation
def fullsave(path,count=20000):
 import torch
 info=complete_validation(path,count=count);ck=torch.load(path,map_location='cpu',weights_only=False)
 assert ck['independent_terrain_expert']=='E1_CURB' and ck['E1_CURB_initial_source_sha256']==prior.SOURCE_SHA
 return info
prior.fullsave=fullsave
old_phase=prior.phase
def phase(name,**kw):
 if name=='bounded_E1_G3_command_retention_learning':name='bounded_E1_CURB20_independent_learning'
 old_phase(name,**kw)
prior.phase=phase
if __name__=='__main__':
 import argparse,time,traceback
 p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2);a=p.parse_args()
 try:
  if a.guardian:prior.guardian(int(a.guardian[0]),int(a.guardian[1]))
  else:prior.main()
 except BaseException:
  prior.write('E1_REVIEWED_CONTROLLER_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),own_child_still_alive=bool(prior.s.LIVE and prior.s.LIVE.poll() is None),active_segment=prior.s.q.base.budget_state()['active_segment'],all_weights_retained=True,no_blind_resume=True));raise
'''
compile(raw,'supervise_curb20_fullstate_reviewed_once.py','exec');p=P/'supervise_curb20_fullstate_reviewed_once.py';assert not p.exists();p.write_text(raw)
report=dict(epoch=time.time(),trial_id='CURB-FULLSTATE-PREDEPLOY-VALIDATOR-REVIEW-01',
 source_review_discovered="First controller calls inherited fullsave(require_e1=False), whose strict else branch rejects any E1_terrain_state. Thus the new CURB own save would be rejected after learning; discovered before any GPU/PPO launch.",
 actual_rejection_executed=False,static_source_review=True,first378_source_retained=True,
 repair='Independent validator retains every original allDR check and adds explicit CURB profile validation with require_e1=True; independent controller binds it before launch, original loader and production sources unchanged.',
 no_GPU_or_budget_effect=True,workspace_rg_denied_error='Unrelated rmuc2026_work/unpack_verify_4zomhj13 access denied during broad readonly rg; targeted reads succeeded; no production implication',
 new_files={p.relative_to(P).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in P.rglob('*') if p.is_file()})
(R/'PREDEPLOY_VALIDATOR_SOURCE_REVIEW.json').write_text(json.dumps(report,indent=2));print(json.dumps(dict(reviewed=True,new_files=2,no_GPU_before_corrected_CPU_admission=True)))
