"""Append-only math/sensor units + SDK STATIC public oracle. Zero time steps."""
from pathlib import Path
import datetime,hashlib,importlib,io,json,sys,time,traceback,unittest
R=Path(__file__).resolve().parent
SOURCES=['export_public_nominal.py','nominal_model.py','contact_proxy.py','test_contact_proxy.py','static_qa.py','run_checks.py','PUBLIC_NOMINAL_CONSTANTS.json','probe_nominal.py']
PROTECTED=[R.parent/'MODEL_AUDIT/mod4v1_usd_source_aligned.xml',R.parent/'FSM_DETECTOR_V1/fsm_detector.py',R.parent/'FSM_DETECTOR_V1/INDEX.json',R.parent/'FSM_DETECTOR_V1/README.md',R.parent/'SPR_AUDIT/portable_core_v1/ct_core.c',R.parent/'sensor_core.py',R.parent/'physics_bridge.py']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    n=1
    while (R/'attempts'/f'{n:03d}').exists():n+=1
    out=R/'attempts'/f'{n:03d}';(out/'sources').mkdir(parents=True);pins={str(p):sha(p) for p in PROTECTED};source=[]
    for name in SOURCES:
        raw=(R/name).read_bytes();(out/'sources'/name).write_bytes(raw);source.append({'name':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
    started=time.perf_counter();log=io.StringIO();result={'attempt':n,'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_files':source,'new_robot_episodes':0,'physical_steps':0,'runtime_contacts_or_DR_read':False,'actual_hardware_IO':False,'Git_or_SSH':False}
    sys.path.insert(0,str(R))
    try:
        tests=importlib.import_module('test_contact_proxy');suite=unittest.defaultTestLoader.loadTestsFromModule(tests);r=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
        result['synthetic_units']={'tests':r.testsRun,'failures':len(r.failures),'errors':len(r.errors),'passed':r.wasSuccessful()}
    except Exception:log.write(traceback.format_exc());result['synthetic_units']={'passed':False,'import_error':True}
    (out/'unittest.log').write_text(log.getvalue(),encoding='utf-8')
    try:
        from static_qa import run_static_qa
        qa=run_static_qa();(out/'STATIC_QA.json').write_text(json.dumps(qa,indent=2,allow_nan=False)+'\n',encoding='utf-8');result['static_QA']={'passed':True,'file':'STATIC_QA.json','peaks':qa['peaks'],'static_forwards':qa['static_forwards'],'physics_steps':qa['physics_steps']}
    except Exception:
        (out/'STATIC_QA_ERROR.txt').write_text(traceback.format_exc(),encoding='utf-8');result['static_QA']={'passed':False,'original_error':'STATIC_QA_ERROR.txt'}
    unchanged=all(sha(p)==v for p,v in pins.items());result['protected_files_unchanged']=unchanged;result['protected_hashes']=pins;result['all_passed']=result['synthetic_units']['passed'] and result['static_QA']['passed'] and unchanged;result['wall_s']=time.perf_counter()-started
    (out/'RESULT.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8');print(log.getvalue());print(json.dumps(result,indent=2))
    return 0 if result['all_passed'] else 1
if __name__=='__main__':raise SystemExit(main())
