"""Append-only new projection shadow audit runner. No physics/Git/newagent."""
from pathlib import Path
import datetime,hashlib,importlib,io,json,sys,time,traceback,unittest
R=Path(__file__).resolve().parent;TASK=R.parent
SOURCES=['shadow_audit.py','test_shadow.py','run_audit.py']
PROTECTED=[TASK/'DYNAMIC_COM_MOTION_V1/com_motion.py',TASK/'DYNAMIC_COM_MOTION_V1/INDEX.json',TASK/'DYNAMIC_COM_MOTION_V1/README.md',TASK/'CONTACT_PROXY_NOMINAL_V1/contact_proxy.py',TASK/'CONTACT_PROXY_NOMINAL_V1/nominal_model.py',TASK/'CONTACT_PROXY_NOMINAL_V1/PUBLIC_NOMINAL_CONSTANTS.json',TASK/'CONTACT_PROXY_NOMINAL_V1/INDEX.json',TASK/'FSM_DETECTOR_V1/fsm_detector.py',TASK/'FSM_DETECTOR_V1/INDEX.json',TASK/'ARCHIVE_PHASE2_RECEIPT.json',TASK/'SPIN_H2_K20_V1/sensor_core_v4.py',TASK/'SENSOR_CAPTURE_CLOOP_V1/MANIFEST.json']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    n=1
    while (R/'attempts'/f'{n:03d}').exists():n+=1
    out=R/'attempts'/f'{n:03d}';(out/'sources').mkdir(parents=True);source=[]
    for name in SOURCES:
        raw=(R/name).read_bytes();(out/'sources'/name).write_bytes(raw);source.append({'name':name,'bytes':len(raw),'SHA':hashlib.sha256(raw).hexdigest()})
    pins={str(p):sha(p) for p in PROTECTED};sys.path.insert(0,str(R));sys.path.insert(1,str(TASK));log=io.StringIO();start=time.perf_counter();result={'attempt':n,'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_files':source,'new_physics_steps':0,'Git_SSH_hardware_newagents':False,'original_trace_or_episode_DR_receipt_reads':0}
    try:
        suite=unittest.defaultTestLoader.loadTestsFromModule(importlib.import_module('test_shadow'));u=unittest.TextTestRunner(stream=log,verbosity=2).run(suite);result['units']={'tests':u.testsRun,'failures':len(u.failures),'errors':len(u.errors),'passed':u.wasSuccessful()}
    except Exception:log.write(traceback.format_exc());result['units']={'passed':False,'import_error':True}
    (out/'unittest.log').write_text(log.getvalue(),encoding='utf-8')
    try:
        from shadow_audit import run
        summary=run(out/'audit');result['audit']={'completed':True,'total_rows':summary['total_rows'],'cases':[{'case':x['case'],'rows':x['rows'],'duplicates':x['duplicate_epochs'],'eligible':x['fresh_homogeneous_mean_derivative_rows'],'bounded':x['conditional']['bounded_under_declared_assumptions_rows'],'cue_counts':x['conditional']['cue_counts'],'radius':x['conditional']['radius_m_s2']} for x in summary['cases']]}
    except Exception:
        (out/'AUDIT_ERROR.txt').write_text(traceback.format_exc(),encoding='utf-8');result['audit']={'completed':False,'original_error':'AUDIT_ERROR.txt'}
    result['protected_sources_unchanged']=all(sha(Path(p))==v for p,v in pins.items());result['protected_hashes']=pins;result['all_passed']=result['units']['passed'] and result['audit']['completed'] and result['protected_sources_unchanged'];result['wall_s']=time.perf_counter()-start
    (out/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8');print(log.getvalue());print(json.dumps(result,ensure_ascii=False,indent=2));return 0 if result['all_passed'] else 1
if __name__=='__main__':raise SystemExit(main())
