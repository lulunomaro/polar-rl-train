"""BuildnewMOD4v1nominal14stateDAREonce; no mj_step/oldonce. Saveallsourceidentity."""
from pathlib import Path
import json,time,hashlib,platform,sys
import numpy as np,mujoco,scipy
from physics_bridge import RobustPlant,serialize_gain,MODEL_SHA,MODEL_FILE,MODEL_WHEEL_RADIUS,ROOT,OLD
out=ROOT/'nominal_gain_v1.json';assert not out.exists(),'Gainpurposealreadyconsumed; reuseexistingJSON';start=time.perf_counter();p=RobustPlant(False);g=p.full_lqr(-.2)
rows=[]
for f in [ROOT/'physics_bridge.py',ROOT/'MODEL_AUDIT'/MODEL_FILE,OLD/'control_core.py',OLD/'full_lqr.py',OLD/'kinematics.py',OLD/'reports/model_manifest.json']:
 raw=f.read_bytes();rows.append({'path':str(f),'bytes':len(raw),'SHA':hashlib.sha256(raw).hexdigest()})
result={'kind':'NEW_MOD4V1_NOMINAL_REDUCED14_DARE_SYNTHESIS_NOT_PHYSICAL_SKILL','model_SHA':MODEL_SHA,'model_file':MODEL_FILE,'mass_kg':float(p.m.body_mass.sum()),'robot_bodies':p.m.nbody-1,'dimensions':[p.m.nq,p.m.nv,p.m.nu],'neq':p.m.neq,'wheel_chart_radius_m':MODEL_WHEEL_RADIUS,'hardware_nominal_spec_radius_m':.0625,'wheel_radius_calibration':'Geometriccircumradiususedforinitialchartandnominalodometry; notmeasuredrollingradius','engine':mujoco.__version__,'numpy':np.__version__,'scipy':scipy.__version__,'python':sys.version,'host':platform.platform(),'wall_s':time.perf_counter()-start,'control_period_s':.01,'physics_period_s':.0005,'physics_steps':0,'gain':serialize_gain(g),'source_snapshot':rows,'cross_engine_semantic_flags_reference':'MODEL_AUDIT/USD_SOURCE_DERIVATION_RECEIPT.json','max_closedloop_eigenvalue_abs':float(np.max(np.abs(g['eigenvalues']))),'skill_qualification':False}
with out.open('x',encoding='utf-8')as f:json.dump(result,f,indent=2,allow_nan=False)
print(json.dumps({k:v for k,v in result.items()if k not in('gain','source_snapshot')},indent=2));print('GAIN_SAVED',out)
