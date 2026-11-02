"""Append-only synthetic mathematics THEN projection shadow;0physics/Git."""
from pathlib import Path
import datetime,hashlib,importlib,io,json,sys,time,traceback,unittest
R=Path(__file__).resolve().parent;TASK=R.parent
SOURCES=['window_math.py','test_window.py','shadow_windows.py','run_checks.py','THEORY_AND_BUDGET.md']
PROTECTED=[TASK/'DYNAMIC_COM_MOTION_V1/com_motion.py',TASK/'DYNAMIC_COM_MOTION_V1/INDEX.json',TASK/'CONTACT_PROXY_NOMINAL_V1/contact_proxy.py',TASK/'CONTACT_PROXY_NOMINAL_V1/nominal_model.py',TASK/'CONTACT_PROXY_NOMINAL_V1/PUBLIC_NOMINAL_CONSTANTS.json',TASK/'FSM_DETECTOR_V1/fsm_detector.py',TASK/'COM_SENSOR_CAPTURE_AUDIT_V1/shadow_audit.py',TASK/'COM_SENSOR_CAPTURE_AUDIT_V1/INDEX.json',TASK/'ARCHIVE_PHASE2_RECEIPT.json',TASK/'SENSOR_CAPTURE_CLOOP_V1/MANIFEST.json']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    n=1
    while (R/'attempts'/f'{n:03d}').exists():n+=1
    out=R/'attempts'/f'{n:03d}';(out/'sources').mkdir(parents=True);sources=[]
    for name in SOURCES:
        raw=(R/name).read_bytes();(out/'sources'/name).write_bytes(raw);sources.append({'name':name,'bytes':len(raw),'SHA':hashlib.sha256(raw).hexdigest()})
    pins={str(p):sha(p) for p in PROTECTED};start=time.perf_counter();sys.path.insert(0,str(R));sys.path.insert(1,str(TASK));log=io.StringIO();result={'attempt':n,'source_files':sources,'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'new_physics_steps':0,'Git_newagent_realIO':False,'original_trace_DR_GT_reads':0,'proof_budget_frozen_before_synthetic_execution':True}
    try:
        suite=unittest.defaultTestLoader.loadTestsFromModule(importlib.import_module('test_window'));u=unittest.TextTestRunner(stream=log,verbosity=2).run(suite);result['units']={'tests':u.testsRun,'failures':len(u.failures),'errors':len(u.errors),'passed':u.wasSuccessful()}
    except Exception:log.write(traceback.format_exc());result['units']={'passed':False,'import_error':True}
    (out/'unittest.log').write_text(log.getvalue(),encoding='utf-8')
    if result['units']['passed']:
        try:
            from shadow_windows import run_shadow
            s=run_shadow(out/'shadow');result['shadow']={'completed':True,'rows':s['projection_rows'],'cases':[{'case':x['case'],'duplicates':x['duplicate_sensor_epochs'],'windows':{k:{'n':v['numeric_conditional_windows'],'radius':v['proposed_radius_m_s2'],'conditional_interval_nonfreefall_only':v['conditional_interval_nonfreefall_diagnostic_only']} for k,v in x['windows'].items()}} for x in s['cases']]}
        except Exception:
            (out/'SHADOW_ERROR.txt').write_text(traceback.format_exc(),encoding='utf-8');result['shadow']={'completed':False,'original_error':'SHADOW_ERROR.txt'}
    else:result['shadow']={'completed':False,'not_run_due_to_synthetic_failure':True}
    result['protected_sources_unchanged']=all(sha(Path(p))==v for p,v in pins.items());result['protected_hashes']=pins;result['all_passed']=result['units']['passed'] and result['shadow']['completed'] and result['protected_sources_unchanged'];result['wall_s']=time.perf_counter()-start
    (out/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8');print(log.getvalue());print(json.dumps(result,ensure_ascii=False,indent=2));return 0 if result['all_passed'] else 1
if __name__=='__main__':raise SystemExit(main())
