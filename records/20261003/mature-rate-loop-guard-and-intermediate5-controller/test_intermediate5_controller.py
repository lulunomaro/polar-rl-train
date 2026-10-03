"""Reject blocked escalation and verify full-state source/phase workflow on CPU."""
import ast,copy,importlib.util,types
from pathlib import Path
D=Path(__file__).resolve().parent/'intermediate5_controller'
def load(name):
 s=importlib.util.spec_from_file_location(name,D/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
p=load('autonomy_policy');r=load('rate_schedule')
assert r.validate_limit(5.)==5. and r.next_limit(4.)==5.
assert p.next_action(5.,'white_v2',2,True,10000,[],[6.])==('targeted_repair_hold',6.)
assert p.next_action(4.,'white_v2',2,True,10000,[],[5.,6.])==('targeted_repair_hold',5.)
assert p.next_action(4.,'white_v2',2,True,10000,[],[6.])==('rate_preflight',5.)
assert p.next_action(6.,'white_v1',2,True,10000,[],[6.])==('dr_trial','white_v2')
assert p.next_action(5.,'white_v2',1,False,10000,[],[6.])==('continue',None)
tree=ast.parse((D/'supervise_autonomy.py').read_text())
fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='intermediate5_bootstrap')
def workflow(baseline=True,preflight=True):
 calls=[];rate=types.SimpleNamespace(current_limit=lambda:4.)
 state={'profile':'white_v2','rate_rejected':[6.],'pending_intermediate5':{'id':'INTERMEDIATE5_FROM_MATURE4_20261003','phase':'prepared','source_sha256':'formal-sha'}}
 def pre(ck,target):
  calls.append(('preflight',ck,target));rate.current_limit=lambda:5. if preflight else 4.
 def train(ck,phase,duration):
  assert ck=='formal-checkpoint' and phase=='intermediate5_trial45' and duration==2700
  calls.append(('training',ck));return 'formal-trial'
 base=types.SimpleNamespace(checkpoint=lambda ck:{'sha256':'formal-sha','path':ck},atomic_json=lambda *args:None)
 context={'S':state,'base':base,'rate':rate,'fresh_label':lambda s:s,'persist':lambda:None,'current_decision':lambda ck:(baseline,baseline),'targeted_hold':lambda *args:calls.append(('hold',args)),'rate_preflight':pre,'training':train,'REPORTS':Path('/unused')}
 exec(compile(ast.Module(body=[fn],type_ignores=[]),'<isolated_bootstrap>','exec'),context)
 answer=context['intermediate5_bootstrap']('formal-checkpoint')
 return state,calls,answer,context
s,c,a,_=workflow(False);assert a is None and not any(x[0]=='training' for x in c) and 6. in s['rate_rejected']
s,c,a,_=workflow(True,False);assert a is None and not any(x[0]=='training' for x in c) and 6. in s['rate_rejected']
s,c,a,x=workflow();assert a=='formal-trial' and c==[('preflight','formal-checkpoint',5.),('training','formal-checkpoint')] and s['pending_intermediate5'] is None and s['rollback']['checkpoint']=='formal-checkpoint'
# Interrupted preflights cannot be silently replayed by --resume.
x['S']['pending_intermediate5']={'id':'INTERMEDIATE5_FROM_MATURE4_20261003','phase':'preflighting5','source_sha256':'formal-sha'}
try:x['intermediate5_bootstrap']('formal-checkpoint')
except AssertionError:pass
else:raise AssertionError('Repeated interrupted preflight was allowed')
print('Ten CPU gate/workflow checks passed: registered5, blocked6/5, DR separation, baseline/preflight rejection, exact formal warmstart, interrupted-phase refusal.')
