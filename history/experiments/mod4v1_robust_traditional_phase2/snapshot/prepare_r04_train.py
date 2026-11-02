"""FreezeR03supported-uprighttraincandidate; addproducertracehash +worldyawgrade.
No physicalcalls here. New trainseeds201..208; no heldoutcandidate selection.
"""
from pathlib import Path
import json,ast,hashlib
R=Path(__file__).resolve().parent;p=R/'run_ground_case_v5.py';assert not p.exists();s=(R/'run_ground_case_v4.py').read_text(encoding='utf-8');s=s.replace("w=np.array([r['ground_truth']['gyro_true'][2]for r in score_rows])", "w=np.array([(r['ground_truth']['gyro_true'][1]*math.sin(r['ground_truth']['roll_true'])+r['ground_truth']['gyro_true'][2]*math.cos(r['ground_truth']['roll_true']))/max(math.cos(r['ground_truth']['pitch_true']),.15)for r in score_rows])")
s=s.replace(";dump(out/'result.json',result)\n  with(out/'trace.jsonl').open('x',encoding='utf-8')as f:\n   for row in rows:f.write(json.dumps(row,separators=(',',':'),allow_nan=False)+'\\n')", ";result['yaw_score_frame']='EulerheadingratefrombodygyroandtrueRPY, notbodygyro_zalone';result['cohort']=cfg.get('cohort','train');trace_hash=hashlib.sha256();trace_bytes=0\n  with(out/'trace.jsonl').open('xb')as f:\n   for row in rows:\n    raw=(json.dumps(row,separators=(',',':'),allow_nan=False)+'\\n').encode('utf-8');f.write(raw);trace_hash.update(raw);trace_bytes+=len(raw)\n  result['trace_artifact']={'path':str(out/'trace.jsonl'),'bytes':trace_bytes,'SHA':trace_hash.hexdigest(),'producer_streamed_once':True};dump(out/'result.json',result)")
ast.parse(s);p.write_text(s,encoding='utf-8',newline='\n');files=[]
for name in('run_ground_case_v5.py','sensor_core_v4.py','ground_controller_v4.py','physics_bridge_v3.py','physics_bridge.py','nominal_gain_v1.json'):
 raw=(R/name).read_bytes();files.append(dict(name=name,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
with(R/'R04_FROZEN_TRAIN_SOURCE.json').open('x')as f:json.dump({'kind':'TRAIN_ONLY_CURRENTCANDIDATE_NOT_FINALHOLDOUT','trainseeds':list(range(201,209)),'holdoutseeds_reserved':list(range(10000,10064)),'files':files,'upright_arming_prior':True,'model_SHA':'0e9ca6854285dc73465a198656fdedd992ffbf205c4ea9ed9d3ce88b905bf324'},f,indent=2)
print('R04trainrunnerASTpass; sourcefrozen')
