"""Append-only synthetic-first RAW2K sensor-only functional audit,0physics."""
from pathlib import Path
import datetime,hashlib,importlib,io,json,sys,time,traceback,unittest
R=Path(__file__).resolve().parent;TASK=R.parent
SOURCES=['raw_functional.py','test_raw_functional.py','shadow_cases.py','run_checks.py','SCOPE_AND_FUNCTIONAL.md']
PROTECTED=[TASK/'INTEGRATED_COM_WINDOW_V1/window_math.py',TASK/'INTEGRATED_COM_WINDOW_V1/INDEX.json',TASK/'DYNAMIC_COM_MOTION_V1/com_motion.py',TASK/'DYNAMIC_COM_MOTION_V1/INDEX.json',TASK/'CONTACT_PROXY_NOMINAL_V1/nominal_model.py',TASK/'CONTACT_PROXY_NOMINAL_V1/PUBLIC_NOMINAL_CONSTANTS.json',TASK/'ROUGH_POSTURE_CAUSAL_V1/INDEX.json',TASK/'RAW2K_SHADOW_V1/SENSOR_ONLY_MANIFEST.json']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    n=1
    while (R/'attempts'/f'{n:03d}').exists():n+=1
    out=R/'attempts'/f'{n:03d}';(out/'sources').mkdir(parents=True);sources=[]
    for name in SOURCES:
        p=R/name;(out/'sources'/name).write_bytes(p.read_bytes());sources.append({'name':name,'bytes':p.stat().st_size,'SHA':sha(p)})
    pins={str(p):sha(p) for p in PROTECTED};start=time.perf_counter();sys.path.insert(0,str(R));sys.path.insert(1,str(TASK));log=io.StringIO();result={'attempt':n,'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_files':sources,'new_physics_Git_GPU_newagents_realIO':False,'original_trace_result_DR_GT_reads':0}
    try:
        suite=unittest.defaultTestLoader.loadTestsFromModule(importlib.import_module('test_raw_functional'));u=unittest.TextTestRunner(stream=log,verbosity=2).run(suite);result['units']={'tests':u.testsRun,'failures':len(u.failures),'errors':len(u.errors),'passed':u.wasSuccessful()}
    except Exception:log.write(traceback.format_exc());result['units']={'passed':False,'import_error':True}
    (out/'unittest.log').write_text(log.getvalue(),encoding='utf-8')
    if result['units']['passed']:
        try:
            from shadow_cases import run_shadow
            s=run_shadow(out/'shadow');result['shadow']={'completed':True,'frames':s['total_frames'],'samples':s['total_samples'],'unique_source_samples':s['unique_source_samples'],'joined_steady_samples':s['joined_steady_samples'],'cases':[{'id':c['id'],'duplicate':c['duplicate_source_frames_excluded'],'boot':c['boot_frames_excluded'],'mean_roundoff_max':c['max_authoritative_mean_vs_raw_recompute_roundoff'],'windows':{k:{'n':v['numeric_windows'],'delta':v['paired_raw_minus_mean_vector_difference_m_s2'],'radius':v['proposed_discrete_radius_m_s2']} for k,v in c['windows'].items()}} for c in s['cases']]}
        except Exception:
            (out/'SHADOW_ERROR.txt').write_text(traceback.format_exc(),encoding='utf-8');result['shadow']={'completed':False,'original_error':'SHADOW_ERROR.txt'}
    else:result['shadow']={'completed':False,'not_run_due_to_new_synthetic_failure':True}
    result['protected_sources_unchanged']=all(sha(Path(p))==v for p,v in pins.items());result['protected_hashes']=pins;result['all_passed']=result['units']['passed'] and result['shadow']['completed'] and result['protected_sources_unchanged'];result['wall_s']=time.perf_counter()-start
    (out/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8');print(log.getvalue());print(json.dumps(result,ensure_ascii=False,indent=2));return 0 if result['all_passed'] else 1
if __name__=='__main__':raise SystemExit(main())
