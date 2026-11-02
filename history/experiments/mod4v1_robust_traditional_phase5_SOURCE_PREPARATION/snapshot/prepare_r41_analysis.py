from pathlib import Path
import ast,hashlib,json
R=Path(__file__).resolve().parent
old=R/'analyze_r40_worldleg_v1.py';raw=old.read_bytes();s=raw.decode('utf-8')
s=s.replace('batches/r40_world_leg4/BATCH_RESULT.json','batches/r41_world_capture4/BATCH_RESULT.json')
s=s.replace('R40_WORLDLEG_NEW_TRAIN_FACTS_AND_OBSERVER_DIAGNOSTIC','R41_SCHEDULED_WORLDLEG_NEW_TRAIN_FACTS')
s=s.replace('reports/R40_WORLDLEG_FACTS.json','reports/R41_WORLDLEG_FACTS.json')
ast.parse(s)
p=R/'analyze_r41_world_capture_v1.py'
with p.open('x',encoding='utf-8')as f:f.write(s)
with(R/'ROUGH_WORLD_LEG_V2/ANALYSIS_PREPARATION.json').open('x',encoding='utf-8')as f:json.dump(dict(old_analysis_SHA=hashlib.sha256(raw).hexdigest(),new_analysis_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),only_batch_result_kind_and_output_path_changed=True,physics_steps=0),f,indent=2)
print(p)
