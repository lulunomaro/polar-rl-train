"""Independently compare the actual immutable nominal patch with original white paths."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports'
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 code=r'''
from pathlib import Path
import json,zipfile,ast,hashlib,time
D=Path('/home/egde/rl_candidates/MOD4_D6_FULL_CONTRACT_20261009');R=D/'reports';read=lambda p:json.loads(p.read_text())
new=read(R/'NOMINAL_SCOPE_PACKAGE_PUBLISHED.json')['package'];base=read(Path('/home/egde/rl_candidates/MOD4_D5_FULL_CONTRACT_20261008/reports/D5_FROZEN_BEHAVIOR_PACKAGES.json'))['flat']
trees=[]
for package in (base,new):
 assert hashlib.sha256(Path(package['path']).read_bytes()).hexdigest()==package['sha256']
 with zipfile.ZipFile(package['path']) as z:trees.append(ast.parse(z.read('runtime/isaac/mod4/mild_dr.py').decode()))
a,b=trees;ca=next(x for x in a.body if isinstance(x,ast.ClassDef) and x.name=='MildDR');cb=next(x for x in b.body if isinstance(x,ast.ClassDef) and x.name=='MildDR')
method=next(x for x in cb.body if isinstance(x,ast.FunctionDef) and x.name=='__call__');branch=next(x for x in method.body if isinstance(x,ast.If) and ast.unparse(x.test)=="self.profile == 'nominal'")
assert not any(isinstance(x,ast.Call) for x in ast.walk(branch));method.body.remove(branch)
assert ast.dump(ca,include_attributes=False)==ast.dump(cb,include_attributes=False)
v=dict(epoch=time.time(),CPU_AST_passed=True,white_profile_constructor_reset_audit_methods_AST_exact=True,nominal_reset_branch_no_setter_calls_or_RNG_calls=True,nominal_actual_SDK_pending=True,base_SHA=base['sha256'],new_SHA=new['sha256'],GPU_PPO_canonical_writes=0)
(R/'NOMINAL_PACKAGE_INDEPENDENT_CPU_REVIEW.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''
 _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=45);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');v=json.loads(raw)
 (R/'NOMINAL_PACKAGE_INDEPENDENT_CPU_REVIEW.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v))
finally:c.close()
