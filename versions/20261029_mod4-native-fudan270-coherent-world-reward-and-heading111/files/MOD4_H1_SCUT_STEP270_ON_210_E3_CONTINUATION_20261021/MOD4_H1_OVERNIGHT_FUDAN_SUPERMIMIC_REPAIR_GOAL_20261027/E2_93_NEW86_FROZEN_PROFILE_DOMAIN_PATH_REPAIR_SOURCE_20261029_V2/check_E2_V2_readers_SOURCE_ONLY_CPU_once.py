"""Pure metadata receipt fixtures only; no saved model/remote/SDK/process query."""
from pathlib import Path
import ast,hashlib,json,types
B=Path(__file__).resolve().parent
def main():
 p=B/'E2_frozen_actual_receipts_readonly_CODE_v1.py';tree=ast.parse(p.read_bytes());code=next(ast.literal_eval(x.value) for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(n,ast.Name) and n.id=='CODE' for n in x.targets));remote=ast.parse(code)
 functions=[n for n in remote.body if isinstance(n,ast.FunctionDef) and n.name in ('native_valid','full_coverage','state')]
 class FakePath:
  def __init__(self,p):self.p=p
  def __truediv__(self,x):return FakePath(self.p+'/'+str(x))
  def read_text(self):
   if self.p=='/proc/stat':return 'btime 1000\n'
   assert self.p.endswith('/stat');a=['S']+['0']*18+['200'];return '7 (synthetic only) '+' '.join(a)
  def read_bytes(self):raise AssertionError('replacement cmdline must not be read')
 def forbidden_link(p):raise AssertionError('replacement exe/cwd must not be read')
 scope=dict(MODEL='b3ae94dfded75360d43dcebc1ac0e7a0c51f2c2f11a9b28e58bb9ae8566ea1e1',Path=FakePath,os=types.SimpleNamespace(sysconf=lambda _:100,readlink=forbidden_link))
 exec(compile(ast.Module(body=functions,type_ignores=[]),'<fresh metadata only>', 'exec'),scope)
 rr=dict(passed=True,source_SHA=scope['MODEL'],Adam_step=859300,stored_RSL_iteration=42822,actual_constructor_algorithm_optimizer_LR=.00022500000000000002)
 nn=dict(passed=True,source_SHA=scope['MODEL'],controls=24,physics_callbacks=192,feedback_samples=48,legs_queue_apply=192,wheels_queue_apply=192,trace_controls=list(range(1,25)),RewardManager_calls=24,RewardManager_dt_s=.02,original_Adam859300_unchanged=True)
 assert scope['native_valid'](rr,nn);checks=['native CUDA receipt positive']
 for k,value in [('controls',23),('physics_callbacks',191),('feedback_samples',47),('legs_queue_apply',191),('wheels_queue_apply',191),('trace_controls',[1,24]),('RewardManager_dt_s',.01)]:assert not scope['native_valid'](rr,dict(nn,**{k:value}));checks.append('native rejects '+k)
 for k,value in [('Adam_step',857460),('source_SHA','0'*64),('actual_constructor_algorithm_optimizer_LR',6.666666666666667e-5)]:assert not scope['native_valid'](dict(rr,**{k:value}),nn);checks.append('restore rejects '+k)
 result=dict(controls=900,requested_controls=900,warmup_controls=100,steady_controls=800,wall_time_limited=False,all17_Adam_steps=859300,actual_LR_unchanged=.00022500000000000002,core_actor_critic_STD_norm_optimizer_literal_unchanged=True);assert scope['full_coverage'](True,result);checks.append('full900 coverage positive')
 for k,value in [('controls',899),('steady_controls',799),('wall_time_limited',True),('all17_Adam_steps',859320),('actual_LR_unchanged',.0001)]:assert not scope['full_coverage'](True,dict(result,**{k:value}));checks.append('coverage rejects '+k)
 assert not scope['full_coverage'](False,result);checks.append('rc0 or result alone cannot pass')
 reused=scope['state'](dict(pid=7,creation=1001));assert reused['original_out'] and 'reused' in reused['reason'];checks.append('PID reuse refuses replacement argv/exe query')
 early=scope['state'](dict(pid=7,initial_spawn_already_exited=True,worker_self_identity_required=True));assert early['no_PID_query_without_creation'];checks.append('early no-identity exit needs no process query')
 assert "nominal=sup['creation']+1800" in code and "nominal-time.time()<=900" in code and "else 850" in code and "if mode=='first'" in code;checks.append('original sup1800/remaining900/first110/normal850 source bounds')
 core=(B/'run_E2_new86_readonly_secure_stdin_v1.py').read_text();assert "sup['creation']+1800-time.time()<=900" in core and "ch.settimeout(150 if mode=='first' else 900)" in core;checks.append('local and remote normal eligibility retained')
 parsed=[]
 for p in B.glob('*.py'):ast.parse(p.read_bytes());parsed.append(p.name)
 with (B/'reports/E2_V2_READER_PURE_METADATA_CPU_AND_AST_ACTUAL.json').open('x') as f:json.dump(dict(passed=True,checks=checks,count=len(checks),parsed_sources=parsed,remote_CODE_SHA=hashlib.sha256(code.encode()).hexdigest(),no_real_process_path_read_remote_model_SDK_GPU_or_network=True),f,indent=2)
 print(json.dumps(dict(passed=True,checks=len(checks),source_only=True)))
if __name__=='__main__':main()
