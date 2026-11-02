"""Append-only synthetic unit/header checks; preserve source bytes BEFORE each run."""
from pathlib import Path
import datetime,hashlib,importlib,io,json,shutil,subprocess,sys,time,traceback,unittest
ROOT=Path(__file__).resolve().parent
PROTECTED=[ROOT.parent/'SPR_AUDIT/portable_core_v1/ct_core.c',ROOT.parent/'SPR_AUDIT/portable_core_v1/ct_core.h',ROOT.parent/'SPR_AUDIT/portable_core_v1/INDEX.json',ROOT.parent/'sensor_core.py',ROOT.parent/'physics_bridge.py']
SOURCES=['fsm_detector.py','test_fsm_detector.py','fsm_detector_v1.h','header_smoke.c','run_host_checks.py']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    n=1
    while (ROOT/'attempts'/f'{n:03d}').exists():n+=1
    out=ROOT/'attempts'/f'{n:03d}';(out/'sources').mkdir(parents=True,exist_ok=False)
    pins={str(p):sha(p) for p in PROTECTED};sources=[]
    for name in SOURCES:
        p=ROOT/name;raw=p.read_bytes();(out/'sources'/name).write_bytes(raw);sources.append({'name':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
    started=time.perf_counter();result={'attempt':n,'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_files':sources,'synthetic_only':True,'physics_steps':0,'robot_episodes':0,'hardware_access':False,'Git_access':False,'SSH':False,'C_is_interface_only_no_C_FSM_runtime':True}
    stream=io.StringIO();counter=[0]
    try:
        sys.path.insert(0,str(ROOT));fd=importlib.import_module('fsm_detector');original=fd.DetectorFSM.step
        def counted(*args,**kwargs):counter[0]+=1;return original(*args,**kwargs)
        fd.DetectorFSM.step=counted
        tests=importlib.import_module('test_fsm_detector');suite=unittest.defaultTestLoader.loadTestsFromModule(tests);r=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
        result['python']={'tests':r.testsRun,'failures':len(r.failures),'errors':len(r.errors),'passed':r.wasSuccessful(),'modes_seen':sorted(tests.SEEN_MODES),'synthetic_FSM_step_calls':counter[0]}
    except Exception:
        stream.write(traceback.format_exc());result['python']={'passed':False,'import_or_runner_error':True}
    (out/'python_unittest.log').write_text(stream.getvalue(),encoding='utf-8')
    gcc=Path(r'C:\MinGW\bin\gcc.exe');command=[str(gcc),'-std=c99','-Wall','-Wextra','-Werror','-pedantic','-fsyntax-only','header_smoke.c']
    try:
        p=subprocess.run(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace',check=False)
        (out/'c_header_syntax.log').write_text(p.stdout,encoding='utf-8');result['C_header']={'command':command,'returncode':p.returncode,'passed':p.returncode==0,'linked_executable':False,'C_FSM_implementation_present':False}
    except Exception:
        (out/'c_header_syntax.log').write_text(traceback.format_exc(),encoding='utf-8');result['C_header']={'command':command,'passed':False,'tool_invocation_error':True}
    unchanged=all(sha(path)==digest for path,digest in pins.items());result['protected_files_unchanged']=unchanged;result['protected_hashes']=pins
    result['all_passed']=result['python']['passed'] and result['C_header']['passed'] and unchanged;result['wall_s']=time.perf_counter()-started
    (out/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(stream.getvalue());print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result['all_passed'] else 1
if __name__=='__main__':raise SystemExit(main())
