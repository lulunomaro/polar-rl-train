"""Append-only new COM math/static/sensor-field diagnostic; 0 physics steps."""
from pathlib import Path
import datetime,hashlib,importlib,io,json,sys,time,traceback,unittest
R=Path(__file__).resolve().parent;TASK=R.parent
SOURCES=['com_motion.py','test_com_motion.py','static_qa.py','sensor_derivative_diagnostic.py','run_checks.py']
PROTECTED=[TASK/'CONTACT_PROXY_NOMINAL_V1/contact_proxy.py',TASK/'CONTACT_PROXY_NOMINAL_V1/nominal_model.py',TASK/'CONTACT_PROXY_NOMINAL_V1/PUBLIC_NOMINAL_CONSTANTS.json',TASK/'CONTACT_PROXY_NOMINAL_V1/INDEX.json',TASK/'FSM_DETECTOR_V1/fsm_detector.py',TASK/'FSM_DETECTOR_V1/INDEX.json',TASK/'ARCHIVE_PHASE2_RECEIPT.json',TASK/'MODEL_AUDIT/mod4v1_usd_source_aligned.xml']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    n=1
    while (R/'attempts'/f'{n:03d}').exists():n+=1
    out=R/'attempts'/f'{n:03d}';(out/'sources').mkdir(parents=True);sources=[];pins={str(p):sha(p) for p in PROTECTED}
    for name in SOURCES:
        raw=(R/name).read_bytes();(out/'sources'/name).write_bytes(raw);sources.append({'name':name,'bytes':len(raw),'SHA':hashlib.sha256(raw).hexdigest()})
    sys.path.insert(0,str(TASK));sys.path.insert(0,str(R));start=time.perf_counter();log=io.StringIO();result={'attempt':n,'source_files':sources,'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'new_robot_episodes':0,'physical_steps':0,'Git_hardware_SSH':False}
    try:
        suite=unittest.defaultTestLoader.loadTestsFromModule(importlib.import_module('test_com_motion'));u=unittest.TextTestRunner(stream=log,verbosity=2).run(suite);result['synthetic_units']={'tests':u.testsRun,'failures':len(u.failures),'errors':len(u.errors),'passed':u.wasSuccessful()}
    except Exception:log.write(traceback.format_exc());result['synthetic_units']={'passed':False,'import_error':True}
    (out/'unittest.log').write_text(log.getvalue(),encoding='utf-8')
    for key,module,fn in [('static_QA','static_qa','run_static'),('sensor_diagnostic','sensor_derivative_diagnostic','run_diagnostic')]:
        try:
            data=getattr(importlib.import_module(module),fn)();(out/(key+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8');result[key]={'completed':True,'file':key+'.json','status':data.get('status',data.get('verdict'))}
            if key=='static_QA':result[key].update(peaks=data['peaks'],static_forwards=data['static_forwards'],physics_steps=data['physics_steps'])
        except Exception:
            (out/(key+'_ERROR.txt')).write_text(traceback.format_exc(),encoding='utf-8');result[key]={'completed':False,'original_error':key+'_ERROR.txt'}
    result['protected_sources_unchanged']=all(sha(Path(p))==v for p,v in pins.items());result['protected_hashes']=pins;result['all_passed']=result['synthetic_units']['passed'] and result['static_QA']['completed'] and result['sensor_diagnostic']['completed'] and result['protected_sources_unchanged'];result['wall_s']=time.perf_counter()-start
    (out/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8');print(log.getvalue());print(json.dumps(result,ensure_ascii=False,indent=2));return 0 if result['all_passed'] else 1
if __name__=='__main__':raise SystemExit(main())
