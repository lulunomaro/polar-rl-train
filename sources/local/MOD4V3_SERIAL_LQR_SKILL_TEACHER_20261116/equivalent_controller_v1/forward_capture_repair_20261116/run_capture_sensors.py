from pathlib import Path
import json,subprocess,sys,os,concurrent.futures
P=Path(__file__).resolve().parent
profile=json.loads((P/'BASELINE_PROFILE.json').read_text())
probes=[('capture_sensors_r10',{'capture_loaded_hold':True,'capture_physics_sensors':True}),('capture_sensors_coherent_r10',{'capture_loaded_hold':True,'capture_physics_sensors':True,'capture_coherent_handoff':True})]
cases=[dict(profile,**options,name=f'{label}_{mm:+04d}mm',start_x=mm/1000.)for label,options in probes for mm in [0,-60]]
def one(case):
 p=subprocess.run([sys.executable,'-X','utf8','-u','-B',str(P/'run_case.py'),json.dumps(case)],capture_output=True,text=True,env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'})
 (P/(case['name']+'.log')).write_text(p.stdout+'\n'+p.stderr,encoding='utf8')
 r=json.loads((P/case['name']/'RESULT.json').read_text())if (P/case['name']/'RESULT.json').exists()else {}
 print(case['name'],p.returncode,r.get('pass_teacher_stair'),r.get('max_continuous_top_hold_s'),r.get('pitch_peak_deg'),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:list(pool.map(one,cases))
