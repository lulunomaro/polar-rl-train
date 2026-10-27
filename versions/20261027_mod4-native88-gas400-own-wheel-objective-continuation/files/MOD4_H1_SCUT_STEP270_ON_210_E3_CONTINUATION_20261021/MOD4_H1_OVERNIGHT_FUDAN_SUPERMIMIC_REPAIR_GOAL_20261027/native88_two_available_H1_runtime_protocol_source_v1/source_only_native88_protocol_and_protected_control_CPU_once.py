"""New contract, accounting and own-PID boundary tests; no SDK, model or remote."""
from pathlib import Path
import ast,copy,json,time,types
S=Path(__file__).resolve().parent;R=S/'reports';R.mkdir(exist_ok=True)
import native88_protocol_v1 as p
checks=[]
def check(name,fn):
 fn();checks.append(name)
def require(v,msg):
 if not v:raise ValueError(msg)
def reject(fn):
 try:fn()
 except (ValueError,KeyError,TypeError,AssertionError):return
 raise AssertionError('negative case admitted')
def spec(key):
 old=p.SOURCES[key]
 s=dict(key=key,native88_changed_plant=True,finite_method_test=True,native87_policy_only=False,new_native_architecture_fresh=False,closed_production_continuation=False,native_continuation=True,native_continuation_restore_required=True,source_SHA=old['SHA'],source_progress={k:old[k] for k in ('updates','world_updates','policy_updates')},bootstrap_source_SHA=p.BOOTSTRAP_SHA,source_Adamstep=832460,seed=old['seed'],native_seed=old['seed'],GPU_UUID=old['GPU_UUID'],execution_backend=old['execution_backend'],method_config=copy.deepcopy(p.METHOD),policy_hz=100,max_parent_seconds=3900,exit_headroom_seconds=300,owner_authority_generation=p.AUTHORITY_GENERATION,fresh_environment_resume_scope='native_models_only_fresh400N_environment_no_old_DR',changed_plant700_to_nominal400=True,independent_own_step_objective_admission_passed=True,candidate_pins={'synthetic_only.py':'a'*64})
 s.update({k:'b'*64 for k in p.PIN_FIELDS});s['reference_artifact_SHA']=p.REFERENCE_SHA
 if key=='h1':s['owner_control_dependency_binding_SHA']='c'*64
 return s
for key in p.SOURCES:
 s=spec(key);check('own native '+key,lambda:require(p.validate_spec(s),'role'))
 go=dict(p.native88_go_fields(s),source_SHA=s['source_SHA'],source_qualification_kind=p.KIND,max_parent_seconds=3900,exit_headroom_seconds=300,nominal_end_epoch=10000,save_deadline=9700)
 check('Task/GO typed native source '+key,lambda:require(p.validate_task_go(s,go,s['manifest_SHA']),'go'))
 bad=copy.deepcopy(s);bad['source_SHA']=p.BOOTSTRAP_SHA
 check('reject normal bootstrap as native '+key,lambda:reject(lambda:p.validate_spec(bad)))
 bad=copy.deepcopy(s);bad['independent_own_step_objective_admission_passed']=False
 check('reject gas-only objective bypass '+key,lambda:reject(lambda:p.validate_spec(bad)))
 bad=copy.deepcopy(s);bad['GPU_UUID']='GPU-16828f91-2b45-b646-8dc0-9481138e2842'
 check('reject preserved third GPU '+key,lambda:reject(lambda:p.validate_spec(bad)))
 bad=copy.deepcopy(s);bad['native87_policy_only']=True
 check('reject old fresh native branch '+key,lambda:reject(lambda:p.validate_spec(bad)))
 badgo=copy.deepcopy(go);badgo['source_progress']['policy_updates']+=1
 check('reject source/window progress mismatch '+key,lambda:reject(lambda:p.validate_task_go(s,badgo,s['manifest_SHA'])))
# Only a pure AST-extracted own PID helper is exercised on Windows. No fcntl stub.
resource=ast.parse((S/'native88_resource_guard_v1.py').read_bytes())
helper=next(n for n in resource.body if isinstance(n,ast.FunctionDef) and n.name=='recorded_own_out')
class Missing(Exception):pass
called=[]
class Proc:
 def __init__(self,pid):called.append(pid);self.pid=pid
 def create_time(self):
  if self.pid==2:raise Missing()
  return 20
 def cmdline(self):raise AssertionError('foreign cmdline access')
 def exe(self):raise AssertionError('foreign exe access')
scope=dict(require=require,psutil=types.SimpleNamespace(Process=Proc,NoSuchProcess=Missing))
exec(compile(ast.fix_missing_locations(ast.Module(body=[helper],type_ignores=[])),'pure_own_PID_AST','exec'),scope)
rows=[dict(role='own_old',execution_backend='target72',pid=1,creation=10),dict(role='own_missing',execution_backend='target72',pid=2,creation=10),dict(role='other_host_own',execution_backend='source210',pid=3,creation=10)]
result=scope['recorded_own_out'](rows,'target72')
check('only current-host own PID/create probes',lambda:require(called==[1,2] and len(result)==2,'host scope'))
rows[0]['creation']=20
check('reject still-live exact own process',lambda:reject(lambda:scope['recorded_own_out'](rows,'target72')))
check('no global process iteration in new active resource path',lambda:require(not any(isinstance(n,ast.Attribute) and n.attr=='process_iter' for n in ast.walk(resource)),'process_iter'))
# Original pure fee function runs against synthetic in-memory dictionaries only.
tree=ast.parse((S/'three_slot_common_v1.py').read_bytes())
fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='charge_values')
scope=dict(terminal=lambda r:bool(r.get('terminal_all_own_children_waited') and r.get('returncode') is not None))
exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),'original_fee_AST','exec'),scope)
c=dict(charged_training_seconds=0.,remaining_training_seconds=2268000.);a=dict(experts={},charged_expert_seconds=0.)
go={k:dict(learning_started_epoch=(10 if k=='h1' else 20),max_parent_seconds=3900) for k in ('h1','recovery')}
scope['charge_values'](c,a,go,{},30)
check('independent overlap charged actual intervals',lambda:require(a['charged_expert_seconds']==30 and c['remaining_training_seconds']==2267970.,'overlap'))
term={k:dict(terminal_all_own_children_waited=True,returncode=0,owner_received_terminal_epoch=(4010 if k=='h1' else 32)) for k in go}
scope['charge_values'](c,a,go,term,4020)
check('overcap not clamped/refunded or hidden',lambda:require(a['experts']['h1']['charged_seconds']==4000 and a['experts']['h1']['duration_bound_passed'] is False and a['experts']['recovery']['charged_seconds']==12 and a['charged_expert_seconds']==4012,'independent original fees'))
for path in S.glob('*.py'):ast.parse(path.read_bytes())
with (R/'SOURCE_PROTOCOL_OWN_PID_AND_ORIGINAL_FEE_CPU_ACTUAL.json').open('x',encoding='utf8') as f:
 json.dump(dict(epoch=time.time(),passed=True,checks=checks,count=len(checks),source_only_synthetic_metadata=True,no_models_SDK_remote_Go_or_budget_mutation=True,all_reports_errors_retained=True),f,indent=2)
print(json.dumps(dict(passed=True,checks=len(checks),no_actual_runtime_admission=True)))
