from pathlib import Path
import json
from evaluate_student200 import run
T=Path(__file__).resolve().parent;R=T.parents[2]
root=T/'evidence/local0';root.mkdir(exist_ok=True)
records={}
for name,model,smoothing in [('previous_final',R/'sources/local/MOD4V3_MOE_ROUTE2_HEIGHT_CURRICULUM_2H_20261117/weights/model_final.pt',0.),('v1_immediate',T/'weights/model_step000.pt',0.),('v1_smooth035',T/'weights/model_step000.pt',.35)]:
 records[name]=run(model,root/name,False,.2,[0],None,smoothing)
(root/'LANDING_COMPARISON.json').write_text(json.dumps(records,indent=2)+'\n')
print('LANDING_COMPARE',{k:dict(physical_events=v['physical_stable_events'],strict=v['passed'],row=v['rows'][0])for k,v in records.items()})
