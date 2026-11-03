"""Compile ONLY new C99 gate/bridge/synthetic smoke. Never build target/old code."""
from pathlib import Path
import hashlib,json,subprocess,re,sys
O=Path(__file__).resolve().parent;A=O/'attempts/host_01';A.mkdir(parents=True,exist_ok=False)
def sha(b):return hashlib.sha256(b).hexdigest()
def rec(p):
 b=p.read_bytes();return dict(path=p.relative_to(O).as_posix(),bytes=len(b),SHA=sha(b))
inputs=['new_code/mod4_port_gate.c','new_code/mod4_port_gate.h','new_code/mod4_port_bridge.c','new_code/mod4_port_bridge.h','host_smoke.c','METHOD.md','SOURCE.json','PATCH_PLAN.md','build_host_once.py'];snap=[]
for n in inputs:
 p=O/n;b=p.read_bytes();d=A/'sources'/n;d.parent.mkdir(parents=True,exist_ok=True);d.write_bytes(b);snap.append(rec(p))
count=len(re.findall(r'\bCHECK\s*\(', (O/'host_smoke.c').read_text(encoding='utf-8')))-1
assert count==40
G=r'C:\MinGW\bin\gcc.exe';flags=['-std=c99','-O2','-Wall','-Wextra','-Werror','-pedantic','-Wvla','-fno-fast-math','-ffp-contract=off','-msse2','-mfpmath=sse']
receipt=dict(kind='NEW_C99_GATE_ONLY_NO_TARGET_BUILD',inputs=snap,flags=flags,planned_checks=count,commands=[],success=False,missing_exit0_artifact=False,full_target_builds=0,old_QA=0,PHY=0,real_CAN_SPI=0)
def save(): (O/'HOST_BUILD_01.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
def run(argv,name,artifact=None):
 cp=subprocess.run([str(a)for a in argv],cwd=O,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);(A/(name+'.log')).write_bytes(cp.stdout)
 row=dict(argv=[str(a)for a in argv],exit=cp.returncode,log=rec(A/(name+'.log')))
 if artifact is not None:row['artifact']=rec(artifact)if artifact.exists()else None
 receipt['commands'].append(row);save();sys.stdout.buffer.write(cp.stdout);sys.stdout.flush()
 if cp.returncode:raise RuntimeError('ordinary compile/test failure retained: '+name)
 if artifact is not None and not artifact.exists():receipt['missing_exit0_artifact']=True;save();raise RuntimeError('STOP component: exit0 artifact absent; no retry/rename')
 return cp.stdout
try:
 run([G,'--version'],'compiler')
 objs=[]
 for n in ('new_code/mod4_port_gate.c','new_code/mod4_port_bridge.c','host_smoke.c'):
  obj=A/(Path(n).stem+'.o');run([G,*flags,'-I',O/'new_code','-c',O/n,'-o',obj],Path(n).stem,obj);objs.append(obj)
 exe=A/'mod4_port_host_smoke.exe';run([G,*flags,*objs,'-o',exe],'link',exe)
 raw=run([exe],'smoke');assert b'checks=40 failures=0'in raw
 receipt['success']=True;receipt['smoke_assertions']=40;receipt['smoke_failures']=0;save();print(json.dumps(dict(status='HOST_NEW_GATE_PASS',executable=rec(exe),checks=40,full_target_builds=0,real_CAN_SPI=0),indent=2))
except BaseException as e:
 receipt['error']=repr(e);save();raise
