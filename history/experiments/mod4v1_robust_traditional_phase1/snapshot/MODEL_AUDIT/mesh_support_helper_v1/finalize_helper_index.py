"""Read-only helper/source integrity index; no simulator imports/calls."""
from pathlib import Path
import ast,hashlib,json
HERE=Path(__file__).resolve().parent
MODEL=HERE.parent/'mod4v1_usd_source_aligned.xml'
KIN=Path(r'F:\RMPOLAR-RL\traditional_control_20261101\kinematics.py')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def meta(p):return {'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}
s=json.loads((HERE/'QUICK_TEST_SUMMARY.json').read_text(encoding='utf-8'))
assert sha(MODEL)==s['model_sha256'] and sha(KIN)==s['source_kinematics_sha256']
assert sha(HERE/'mesh_support.py')==s['helper_sha256']
for f in ['mesh_support.py','test_static_forward.py','finalize_helper_index.py']:ast.parse((HERE/f).read_text(encoding='utf-8'))
result={'mode':'STATIC_MJDATA_FORWARD_FK_ONLY','status':s['status'],'physics_steps':0,'time_advanced_s':0,'thresholds_added':False,'source_model':meta(MODEL),'source_kinematics':meta(KIN),'summary':s,'core_helper':meta(HERE/'mesh_support.py'),'no_parent_code_changes':True,'source_skill_selection':'Office/ACL catalog inspected; neither matches model/control/geometry task; existing filesystem/CLI used','artifacts':[meta(HERE/n) for n in ['mesh_support.py','test_static_forward.py','finalize_helper_index.py','README.md','QUICK_TEST_SUMMARY.json','STATIC_FORWARD_RESULTS.json','STATIC_FORWARD_TEST_001.log']]}
path=HERE/'HELPER_INDEX.json';assert not path.exists();path.write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
print(json.dumps({'index':meta(path),'helper':result['core_helper'],'status':result['status']},indent=2))
