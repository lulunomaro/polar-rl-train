"""Compile the actual firmware core and compare the frozen policy golden vectors."""
import ctypes as C
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'firmware/application/mod4_rl'
BUILD = ROOT / 'build/portable'
Float6 = C.c_float * 6
Float3 = C.c_float * 3
class State(C.Structure):
    _fields_ = [('q',Float6),('qd',Float6),('gyro',Float3),('gravity',Float3)]
class Command(C.Structure):
    _fields_ = [('command',C.c_float*4)]
class Memory(C.Structure):
    _fields_ = [('previous_action',Float6),('target',Float6),('target_valid',C.c_int)]

def run(args):
    p = subprocess.run(list(map(str,args)),capture_output=True,text=True,encoding='utf-8',errors='replace')
    return dict(command=list(map(str,args)),returncode=p.returncode,stdout=p.stdout,stderr=p.stderr)

if __name__ == '__main__':
    BUILD.mkdir(parents=True,exist_ok=True)
    report = dict(started=time.strftime('%Y-%m-%dT%H:%M:%S%z'),attempt=sys.argv[1] if len(sys.argv)>1 else 'manual')
    common=['gcc','-std=c99','-O2','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-I',SRC]
    if sys.platform != 'win32': common += ['-fPIC']
    sources=[SRC/(n+'.c') for n in ('mod4_runtime','mod4_controller','dm_protocol','mod4_wire')]
    dll=BUILD/('mod4.dll' if sys.platform=='win32' else 'mod4.so')
    report['compile_dll']=run(common+['-shared','-o',dll]+sources+['-lm'])
    report['compile_tests']=run(common+[ROOT/'tests/test_controller.c','-o',BUILD/'test_controller.exe']+sources+['-lm'])
    if not report['compile_tests']['returncode']:
        report['controller_tests']=run([BUILD/'test_controller.exe'])
    if not report['compile_dll']['returncode']:
        lib=C.CDLL(str(dll))
        lib.mod4_build_observation.argtypes=[C.POINTER(State),C.POINTER(Command),C.POINTER(Memory),C.POINTER(C.c_float)]
        lib.mod4_forward.argtypes=[C.POINTER(C.c_float),C.POINTER(C.c_float)]
        lib.mod4_decode_targets.argtypes=[C.POINTER(C.c_float)]*3
        vectors=json.loads((ROOT/'tests/golden_vectors.json').read_text(encoding='utf-8'))['vectors']
        errors=dict(observation=0.0,action=0.0,target=0.0)
        rows=[]
        for index,v in enumerate(vectors):
            state=State(Float6(*v['joint_position_rad']),Float6(*v['joint_velocity_rad_s']),Float3(*v['gyro_b_rad_s']),Float3(*v['gravity_b']))
            command=Command((C.c_float*4)(*v['command'])); memory=Memory(); memory.previous_action[:]=v['previous_action']
            obs=(C.c_float*35)(); action=Float6(); target=Float6()
            assert lib.mod4_build_observation(C.byref(state),C.byref(command),C.byref(memory),obs)
            assert lib.mod4_forward(obs,action)
            assert lib.mod4_decode_targets(action,state.q,target)
            e={k:max(abs(float(a)-float(b)) for a,b in zip(actual,v[k])) for k,actual in [('observation',obs),('action',action),('target',target)]}
            for k in errors: errors[k]=max(errors[k],e[k])
            rows.append(dict(index=index,max_abs_errors=e))
        tolerances=dict(observation=2e-6,action=2e-4,target=2e-3)
        report['golden_policy']=dict(vectors=len(vectors),max_abs_errors=errors,tolerances=tolerances,passed=all(errors[k]<=tolerances[k] for k in errors),rows=rows)
    report['passed']=(report['compile_dll']['returncode']==0 and report['compile_tests']['returncode']==0 and report.get('controller_tests',{}).get('returncode',1)==0 and report.get('golden_policy',{}).get('passed',False))
    dest=ROOT/'reports'/('portable_'+report['attempt']+'.json')
    assert not dest.exists(), 'Use a new attempt ID; retain earlier actual failures.'
    dest.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='compile_dll'},indent=2))
    sys.exit(0 if report['passed'] else 1)
