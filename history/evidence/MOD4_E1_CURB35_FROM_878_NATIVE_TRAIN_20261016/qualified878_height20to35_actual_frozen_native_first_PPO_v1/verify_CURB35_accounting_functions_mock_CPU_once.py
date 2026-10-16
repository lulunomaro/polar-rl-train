"""Run exact owner accounting AST against in-memory canonical; never touch real ledger."""
from pathlib import Path
import ast,copy,json,time,types
D=Path(__file__).resolve().parent;source=D/'curb35_owner.py';tree=ast.parse(source.read_text());owner=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='owner');funcs=[n for n in owner.body if isinstance(n,ast.FunctionDef) and n.name in ('budget_start','account')];assert len(funcs)==2
body='def fixture():\n active=False\n charged=0.\n rows=[]\n'+''.join('\n'.join(' '+line for line in ast.unparse(n).splitlines())+'\n' for n in funcs)+' return budget_start,account,lambda:(active,charged,rows)\n'
base=json.loads((D/'reports/FRESH_210_ORIGINAL_CANONICAL_RESOURCE_READONLY_ACTUAL.json').read_bytes())['canonical'];v=dict(active_segment=None,authorized_training_seconds=base['authorized_training_seconds'],charged_training_seconds=base['charged_training_seconds'],remaining_training_seconds=base['remaining_training_seconds'],budget_extensions=[{} for _ in range(7)],completed_segments=[])
class MemoryCanonical:
 def read_bytes(self):return json.dumps(v).encode()
class Clock:
 t=10.
 def time(self):return self.t
 def time_ns(self):return int(self.t*1e9)
clock=Clock()
def put(p,x):assert isinstance(p,MemoryCanonical);v.clear();v.update(copy.deepcopy(x))
env=dict(C=MemoryCanonical(),LIMIT=2700.,json=json,time=clock,os=types.SimpleNamespace(getpid=lambda:123),put=put,child=types.SimpleNamespace(returncode=0));exec(compile(body,'<actual owner functions in memory only>','exec'),env);start,account,status=env['fixture']();initial=v['charged_training_seconds'];start('precheck128');clock.t=15.;account();clock.t=20.;account(True);assert status()[1]==10
clock.t=310.;start('precheck20k_production');clock.t=320.;account();clock.t=334.;account(True);assert status()[1]==34 and len(v['completed_segments'])==2 and v['charged_training_seconds']-initial==34
before=copy.deepcopy(v);rejected=False
try:account()
except (TypeError,AssertionError):rejected=True
assert rejected and v==before
clock.t=400.;start('negative_foreign_owner');v['active_segment']['owner_parent_pid']=456;before=copy.deepcopy(v);rejected=False
try:account()
except AssertionError:rejected=True
assert rejected and v==before
out=dict(epoch=time.time(),actual_owner_AST_functions_tested=True,in_memory_only_no_actual_ledger_read_or_write=True,precheck10_and_production24_charged_once_total34=True,native_gap290_seconds_not_charged=True,repeated_settlement_and_foreign_owner_rejected=True,no_refund_cap_copy_or_extension=True,no_GPU_optimizer_network=True)
with (D/'reports/CURB35_ORIGINAL_LEDGER_OWNER_FUNCTIONS_CPU_MOCK_ACTUAL.json').open('x') as f:json.dump(out,f,indent=2)
print(json.dumps(out))
