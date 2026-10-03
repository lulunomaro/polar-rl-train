import ast,copy
from pathlib import Path
D=Path(__file__).resolve().parent
tree=ast.parse((D/'supervise_targeted_mature5.py').read_text())
fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='validate_evidence')
sha='63662952ea6be6ca6c259a0563fe2495cefc0ebadf9eb729c69ec1e92aba9075'
ctx={'SOURCE_SHA':sha};exec(compile(ast.Module(body=[fn],type_ignores=[]),'<evidence_guard>','exec'),ctx)
source={'path':'formal','sha256':sha}
e={'stage':'completed','preselected_last_paired_mature':True,'no_checkpoint_search':True,'source':source,'physical_smoke_pass':True,'actual_material_parameters_pass':True,'initial_root_q_with_newer_source_exact':True,'PPO_performed':False,'frozen_ledger_exact':True}
r={'checkpoint':'formal','num_envs':20000,'seconds':1.2,'explicit_yaw_groups_rad_s':[0,0,-5.,5.],'mild_initial_parameters':{'profile':'white_v2','actual_parameters_pass':True},'mild_final_parameters':{'profile':'white_v2','actual_parameters_pass':True},'nonfinite':False,'terminations':0,'max_tilt_deg':12.4}
ctx['validate_evidence'](e,r,source)
cases=[('e','physical_smoke_pass',False),('e','PPO_performed',True),('e','initial_root_q_with_newer_source_exact',False),('e','frozen_ledger_exact',False),('r','num_envs',128),('r','max_tilt_deg',15.),('r','checkpoint','wrong'),('r','terminations',1)]
for side,key,value in cases:
 a,b=copy.deepcopy(e),copy.deepcopy(r);(a if side=='e' else b)[key]=value
 try:ctx['validate_evidence'](a,b,source)
 except AssertionError:pass
 else:raise AssertionError((side,key))
print('Nine pure evidence checks passed: accepted actual fullscale source and rejected unsafe/wrong-source/PPO/nonpaired evidence.')
