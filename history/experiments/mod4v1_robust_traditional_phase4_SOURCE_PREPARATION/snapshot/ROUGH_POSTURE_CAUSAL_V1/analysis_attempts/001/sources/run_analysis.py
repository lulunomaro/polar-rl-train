from pathlib import Path
import hashlib,json,sys,traceback
R=Path(__file__).resolve().parent;TASK=R.parent;n=1
while (R/'analysis_attempts'/f'{n:03d}').exists():n+=1
out=R/'analysis_attempts'/f'{n:03d}';(out/'sources').mkdir(parents=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
source=[]
for name in ['causal_analysis.py','run_analysis.py']:
 p=R/name;(out/'sources'/name).write_bytes(p.read_bytes());source.append({'path':str(p),'SHA':sha(p)})
protected=[TASK/'CONTACT_PROXY_NOMINAL_V1/nominal_model.py',TASK/'CONTACT_PROXY_NOMINAL_V1/INDEX.json',TASK/'MODEL_AUDIT/mod4v1_usd_source_aligned.xml',TASK/'run_rm_grid_height_v1.py',TASK/'ground_controller_v4.py'];pins={str(p):sha(p) for p in protected};sys.path.insert(0,str(R))
try:
 import causal_analysis
 causal_analysis.main(out/'output')
 assert all(sha(Path(p))==h for p,h in pins.items())
 (out/'VALIDATION.json').write_text(json.dumps({'source':source,'protected_unchanged':pins,'physics_steps':0,'newGit_tests_GPU_agents_realIO':False,'geometry':'sparse analytic rigid chassis boxes, not force/contact reconstruction'},indent=2)+'\n',encoding='utf-8')
except Exception:
 (out/'ERROR.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
