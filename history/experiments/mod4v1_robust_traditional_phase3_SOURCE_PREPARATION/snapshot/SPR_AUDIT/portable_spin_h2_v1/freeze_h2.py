"""Freeze H2 lineage and export NOMINAL immutable tables; no module execution."""
from pathlib import Path
import json,hashlib,ast
HERE=Path(__file__).resolve().parent;WORK=HERE.parents[1];IO=HERE.parent/'HOST_CLOSED_LOOP_IO_V1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(n,v):(HERE/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def f(x):
 s=format(float(x),'.10g');return s+('f' if '.' in s or 'e' in s else '.0f')
def main():
 assert not (HERE/'SOURCE_FREEZE.json').exists();old={}
 for r in load(IO/'DEPENDENCY_FREEZE.json')['read_only_files']:
  p=Path(r['path']);assert sha(p)==r['sha256'];old[str(p)]={'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}
 for r in load(IO/'INDEX.json')['files']:
  p=IO/r['path'];assert sha(p)==r['sha256'];old[str(p)]={'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}
 for n in ['INDEX.json','VALIDATION.json','MANIFEST.json','index_validation_01.log']:
  p=IO/n;old[str(p)]={'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}
 protocol=load(WORK/'SPIN_H2_K20_V1/PROTOCOL.json');sources=[]
 for r in protocol['source']:
  p=WORK/r['name'];assert p.stat().st_size==r['bytes'] and sha(p)==r['SHA'];sources.append({'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'role':'frozen H2 lineage; physics files hash only, never imported'})
 for n in ['SPIN_H2_K20_V1/PROTOCOL.json','reports/STATE14_SCHEMA_ERRATUM.md']:
  p=WORK/n;sources.append({'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)})
 train=[];directory=WORK/'results/r11_k20_201';r=load(directory/'result.json')['trace_artifact'];assert (directory/'trace.jsonl').stat().st_size==r['bytes'] and sha(directory/'trace.jsonl')==r['SHA']
 for n in ['result.json','SOURCE_MANIFEST.json','trace.jsonl']:
  p=directory/n;train.append({'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)})
 gain=load(WORK/'nominal_gain_v1.json')['gain'];p25=load(WORK/'NORMAL_P25_HOLDOUT_V1/CONTROLLER_PACK.json')['K_6x14']
 assert len(gain['K'])==6 and all(len(x)==14 for x in gain['K']);difference=max(abs(gain['K'][i][j]-p25[i][j]) for i in range(6) for j in range(14));assert difference>1
 lines=['/* Frozen nominal K, NOT P25. LH LC LW RH RC RW rows. */','#ifndef SH2_NOMINAL_DATA_H','#define SH2_NOMINAL_DATA_H']
 for name,values in [('K',[x for row in gain['K'] for x in row]),('eq',gain['q']+[0.]*7),('tau',gain['tau'])]:lines.append('static const float sh2_nom_'+name+'[]={'+','.join(f(x) for x in values)+'};')
 lines+=['#define SH2_LEAD_S '+f(protocol['controller']['center_lead_s']),'#define SH2_CENTER_KP 20.0f','#define SH2_CENTER_CAP 1.8f','#endif'];(HERE/'sh2_nominal_data.h').write_text('\n'.join(lines)+'\n',encoding='utf-8')
 constants={}
 for node in ast.parse((WORK/'robot_geometry_constants_v1.py').read_text(encoding='utf-8')).body:
  if isinstance(node,ast.Assign):
   for target in node.targets:
    if isinstance(target,ast.Name):constants[target.id]=ast.literal_eval(node.value)
 pins=[constants['PINS'][s][k][a] for s in ['left','right'] for k in ['O','K','P','A','B','C','D','W'] for a in [0,1]]
 (HERE/'sh2_geometry_fixture.h').write_text('/* Fixture only, no measured hardware calibration. */\n#ifndef SH2_GEOMETRY_FIXTURE_H\n#define SH2_GEOMETRY_FIXTURE_H\nstatic const float sh2_fixture_pins32[]={'+','.join(f(x) for x in pins)+'};\n#define SH2_TRACK .4376f\n#define SH2_RADIUS_CHART .06369999796152115f\n#endif\n',encoding='utf-8')
 dump('SOURCE_FREEZE.json',{'old_files':list(old.values()),'sources':sources,'TRAIN':train,'nominal_K_vs_P25_max_abs_difference':difference,'H2_controller':protocol['controller'],'H2_sensor':protocol['sensor'],
 'base_defaults':{'position_leash':.2,'heading_leash':.6,'leg_kp':120.,'leg_kd':4.,'yaw_acceleration_ff':.08,'jerk':8.,'accel':1.5,'yaw_accel':6.,'velocity_center_cap':0.},
 'dispatch':'DEFERRED; no P25 controller/dispatcher/profile25 reuse','archive':'postR16/PH3_pending_no_PH2_expansion','no_new_physics':True})
 print(json.dumps({'old_files_snapshotted':len(old),'H2_sources':len(sources),'TRAIN_files':len(train),'nominal_K_vs_P25_max_abs_difference':difference,'dispatch':'deferred','physics_steps':0}))
if __name__=='__main__':main()
