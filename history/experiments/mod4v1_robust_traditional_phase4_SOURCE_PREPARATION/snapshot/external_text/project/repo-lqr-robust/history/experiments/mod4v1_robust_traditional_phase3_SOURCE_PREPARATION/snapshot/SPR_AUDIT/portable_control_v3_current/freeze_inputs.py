"""Freeze inspected source/data only. No controller/physics module import here."""
from pathlib import Path
import json,hashlib,ast
HERE=Path(__file__).resolve().parent;WORK=HERE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def item(p,role):return {'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'role':role}
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(n,v):(HERE/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def fl(x):
 s=format(float(x),'.10g');return s+('f' if '.' in s or 'e' in s else '.0f')
def main():
 out=HERE/'SOURCE_FREEZE.json';assert not out.exists(),'Preserve prior freeze'
 paths=['sensor_core_v4.py','ground_controller_v4.py','NORMAL_P25_HOLDOUT_V1/CONTROLLER_PACK.json','NORMAL_P25_HOLDOUT_V1/PROTOCOL.json',
        'NORMAL_P25_HOLDOUT_V1/sensor_core_v4.py','NORMAL_P25_HOLDOUT_V1/ground_controller_v4.py','reports/STATE14_SCHEMA_ERRATUM.md',
        'spin_center_torque_v2.py','spin_center_controller_v1.py','spin_base_v1.py','SPIN_H2_K20_V1/PROTOCOL.json','robot_geometry_constants_v1.py','nominal_gain_v1.json']
 sources=[item(WORK/p,'inspected frozen math/profile/schema; H2 profile deferred') for p in paths]
 sources.append(item(WORK.parent/'traditional_control_20261101/control_core.py','read as text only: original peak/stall/no-load/signed-DC clip'))
 for n in ['sensor_core_v4.py','ground_controller_v4.py']:assert sha(WORK/n)==sha(WORK/'NORMAL_P25_HOLDOUT_V1'/n)
 for folder in ['NORMAL_P25_HOLDOUT_V1','SPIN_H2_K20_V1']:
  for record in load(WORK/folder/'PROTOCOL.json')['source']:
   p=WORK/record['name'];assert p.stat().st_size==record['bytes'] and sha(p)==record['SHA']
 old={}
 base=HERE.parent
 packages=['portable_core_v1','portable_core_v2_kinematics','portable_mpc_qp_v1','ODOM2D_DIAGNOSTIC','C_MPC8_NUMERIC_V1','portable_mpc_qp_v2_fast','ARM_OBJECT_BUILD_V1']
 for package in packages:
  root=base/package
  for r in load(root/'INDEX.json')['files']:
   p=root/r['path'];assert sha(p)==r['sha256'];old[str(p)]=item(p,'old sealed artifact unchanged')
  for name in ['INDEX.json','VALIDATION.json','MANIFEST.json']:
   p=root/name;old[str(p)]=item(p,'old sealed metadata unchanged')
 for r in load(base/'deliverable_manifest.json')['files']:
  p=base/r['path'];assert sha(p)==r['sha256'];old[str(p)]=item(p,'original SPR audit deliverable')
 old[str(base/'deliverable_manifest.json')]=item(base/'deliverable_manifest.json','original SPR manifest')
 trains=[]
 for name in ['r04_spin_gyro_202','r11_k20_201']:
  directory=WORK/'results'/name;result=load(directory/'result.json');artifact=result['trace_artifact'];trace=directory/'trace.jsonl'
  assert trace.stat().st_size==artifact['bytes'] and sha(trace)==artifact['SHA']
  for n in ['result.json','SOURCE_MANIFEST.json','trace.jsonl']:trains.append(item(directory/n,'fixed TRAIN raw packet reference; no physics replay or parameter choice'))
 pack=load(WORK/'NORMAL_P25_HOLDOUT_V1/CONTROLLER_PACK.json');assert pack['kind']=='ACTUAL_DERIVED_P25_K_NOT_NOMINAL_K'
 assert pack['motor_row_order']==['Lhip','Lcrank','Lwheel','Rhip','Rcrank','Rwheel']
 # Literal-only parse of geometry constants, not import/exec of any producer.
 tree=ast.parse((WORK/'robot_geometry_constants_v1.py').read_text(encoding='utf-8'));constants={}
 for node in tree.body:
  if isinstance(node,ast.Assign):
   for target in node.targets:
    if isinstance(target,ast.Name):constants[target.id]=ast.literal_eval(node.value)
 pins=[constants['PINS'][side][pin][axis] for side in ['left','right'] for pin in ['O','K','P','A','B','C','D','W'] for axis in [0,1]]
 (HERE/'pc3_geometry_data.h').write_text('/* Numerical fixture data, not measured calibration. */\n#ifndef PC3_GEOMETRY_DATA_H\n#define PC3_GEOMETRY_DATA_H\nstatic const float pc3_export_pins32[]={'+','.join(fl(x) for x in pins)+'};\n#define PC3_EXPORT_TRACK '+fl(constants['TRACK'])+'\n#define PC3_EXPORT_GEOMETRIC_RADIUS '+fl(load(WORK/'nominal_gain_v1.json')['wheel_chart_radius_m'])+'\n#endif\n',encoding='utf-8')
 lines=['/* Frozen actual P25 K, row order hip/crank/wheel per side. */','#ifndef PC3_P25_DATA_H','#define PC3_P25_DATA_H']
 for key,name in [('K_6x14','pc3_export_K'),('tau_eq6','pc3_export_tau'),('eq14','pc3_export_eq')]:
  v=pack[key];values=[x for row in v for x in row] if key=='K_6x14' else v
  lines.append('static const float '+name+'[]={'+','.join(fl(x) for x in values)+'};')
 lines.append('#endif');(HERE/'pc3_p25_data.h').write_text('\n'.join(lines)+'\n',encoding='utf-8')
 freeze={'scope':'current V4 estimator + actual P25 normal math stages1+2; H2 common-torque feedback deferred','sources':sources,'old_sealed_snapshot':list(old.values()),'fixed_train_inputs':trains,
         'normal_sensor_config':load(WORK/'NORMAL_P25_HOLDOUT_V1/PROTOCOL.json')['sensor'],'normal_controller_config':pack['controller'],
         'controller_defaults_from_source':{'dt':.01,'accel':1.5,'yaw_accel':6.,'jerk':8.,'heading_leash':.6,'yaw_acceleration_ff':.08,'leg_kp':120.,'leg_kd':4.,'roll_kp':0.,'roll_kd':0.,'model_prediction_fraction':0.},
         'original_envelope':{'peak_row6':[40.,40.,5.775909774436091]*2,'stall_row6':[53.3333333333333,53.3333333333333,28.18532894736838]*2,'no_load_row6':[16.755160819145562,16.755160819145562,55.3557]*2},
         'no_physics_or_parent_module_import':True,'no_holdout_case_read_or_selection':True}
 dump('SOURCE_FREEZE.json',freeze)
 print(json.dumps({'frozen_sources':len(sources),'old_artifacts_snapshotted':len(old),'TRAIN_reference_files':len(trains),'P25_K_rows':6,'P25_K_columns':14,'physics_steps':0}))
if __name__=='__main__':main()
