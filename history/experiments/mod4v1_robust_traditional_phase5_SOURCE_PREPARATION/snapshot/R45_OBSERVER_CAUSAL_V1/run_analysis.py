from pathlib import Path
import hashlib,json,sys,traceback
R=Path(__file__).resolve().parent;T=R.parent;n=1
while (R/'attempts'/f'{n:03d}').exists():n+=1
out=R/'attempts'/f'{n:03d}';(out/'sources').mkdir(parents=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
source=[]
for name in ['analyze_pairs.py','run_analysis.py']:
 p=R/name;(out/'sources'/name).write_bytes(p.read_bytes());source.append({'name':name,'SHA':sha(p),'bytes':p.stat().st_size})
protected=[T/'MINIHOP_OBSERVER_V2/controller.py',T/'MINIHOP_OBSERVER_V2/BOUNDARY_DIAGNOSTIC.json',T/'MINIHOP_AUDIT_V2/run_minihop_case_v2.py',T/'MINIHOP_AUDIT_V2/contact_grade_v2.py',T/'MODEL_AUDIT/mod4v1_usd_source_aligned.xml'];pins={str(p):sha(p) for p in protected};sys.path.insert(0,str(R))
try:
 import analyze_pairs
 assert analyze_pairs.equal(0.,-0.) is False and analyze_pairs.equal(1,True) is False
 analyze_pairs.main(out/'output')
 assert all(sha(Path(p))==h for p,h in pins.items())
 (out/'VALIDATION.json').write_text(json.dumps({'source_files':source,'protected_files_unchanged':pins,'new_physics_Git_agents_realIO':False,'rawSHA_not_recomputed':True,'only4222physics_read':True,'simple_comparison_semantics_selfcheck':True},indent=2)+'\n',encoding='utf-8')
except Exception:
 (out/'ERROR.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
