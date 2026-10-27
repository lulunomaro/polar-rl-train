"""Bounded metadata mocks; no target, model, actor, SDK or physical control."""
from pathlib import Path
import ast,hashlib,inspect,json,sys,types
import psutil
P=Path(__file__).resolve().parent
source=(P/'native87_closed_source_CPU_v1.py').read_text('utf8')
tree=ast.parse(source);old=ast.parse((P/'ORIGINAL_V3_BYTES.txt').read_text('utf8'))
def node(t,n):return next(x for x in t.body if isinstance(x,(ast.FunctionDef,ast.ClassDef)) and x.name==n)
checks=[]
def check(v,label):
 assert v,label
 checks.append(label)
for name in ('_argv','expected_exec_identity','validate_proof_data'):
 check(ast.dump(node(tree,name))==ast.dump(node(old,name)),name+'_AST_exact_V3')
constants=[x for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('PY210','EXE210','WRAPPER72','LOADER72','LIBRARY72','PYTHON72') for t in x.targets)]
nodes=constants+[node(tree,'expected_exec_identity'),node(tree,'ExecIdentityError'),node(tree,'wait_exact_exec_identity')]
ns={'json':json};exec(compile(ast.Module(body=nodes,type_ignores=[]),'<source-functions>','exec'),ns)
class Clock:
 def __init__(self):self.t=0
 def monotonic(self):return self.t
 def sleep(self,d):self.t+=d
class Child:
 pid=42
 def poll(self):return None
spec={'key':'recovery','python':ns['WRAPPER72'],'execution_backend':'target72'}
args=[spec['python'],'-u','-B','/ownroot/target_CPU.py']
expected=ns['expected_exec_identity'](spec,args,'/ownroot')
class Gone(Exception):pass
class Denied(Exception):pass
calls=[]
class FreshProcess:
 def __init__(self,pid):self.which=len(calls);calls.append(pid)
 def create_time(self):return 123.
 def cmdline(self):return ['/bin/bash','wrapper'] if self.which==0 else expected['argv']
 def cwd(self):return expected['root']
 def exe(self):return '/usr/bin/bash' if self.which==0 else expected['exe']
saved=sys.modules['psutil']
try:
 sys.modules['psutil']=types.SimpleNamespace(Process=FreshProcess,NoSuchProcess=Gone,AccessDenied=Denied)
 ns['time']=Clock()
 row=ns['wait_exact_exec_identity'](Child(),'/ownroot',spec,args)
 check(len(calls)==3 and row['exe']==expected['exe'],'fresh_instance_after_exec_then_two_exact_snapshots')
 class Wrong(FreshProcess):
  def exe(self):return '/usr/bin/bash'
 sys.modules['psutil'].Process=Wrong;ns['time']=Clock()
 try:ns['wait_exact_exec_identity'](Child(),'/ownroot',spec,args,timeout_s=.1)
 except ns['ExecIdentityError'] as exc:
  d=exc.details
  check(d['lastrow']['exe']=='/usr/bin/bash' and d['expected']==expected and 'exe' in d['mismatch'],'timeout_retains_actual_expected_and_diff')
 else:raise AssertionError('wrong exe accepted')
finally:sys.modules['psutil']=saved
load=node(tree,'load');guard=next(x for x in load.body if isinstance(x,ast.Try) and any(isinstance(c,ast.Call) and isinstance(c.func,ast.Name) and c.func.id=='wait_exact_exec_identity' for st in x.body for c in ast.walk(st)))
final=ast.unparse(ast.Module(body=guard.finalbody,type_ignores=[]))
check('p.wait()' in final and 'WAITED_RELATIVE' in final,'wait_and_waited_receipt_are_inside_finally')
exe_source=inspect.getsource(psutil.Process.exe)
check('cached after first call' in exe_source and 'self._exe' in exe_source,'local_psutil_documents_and_implements_exe_cache')
(P/'LOCAL_PSUTIL_EXE_SOURCE.txt').write_text(exe_source,encoding='utf8')
result=dict(passed=True,checks=checks,count=len(checks),not_synthetic=False,
 evidence_kind='source_and_synthetic_metadata_only',actual_remote_identity_capture=False,
 actual_target_CPU_execution=False,actual_model_load=False,
 psutil_version=psutil.__version__,exe_source_SHA=hashlib.sha256(exe_source.encode()).hexdigest())
with (P/'CPU.json').open('x',encoding='utf8') as f:json.dump(result,f,indent=2)
print(json.dumps(result))
