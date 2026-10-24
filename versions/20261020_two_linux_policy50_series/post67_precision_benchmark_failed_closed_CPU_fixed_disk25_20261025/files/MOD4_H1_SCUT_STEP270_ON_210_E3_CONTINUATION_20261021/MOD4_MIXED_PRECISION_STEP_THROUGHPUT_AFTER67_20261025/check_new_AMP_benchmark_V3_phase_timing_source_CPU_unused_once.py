from pathlib import Path
import ast,hashlib,importlib.util,json,time,traceback
import torch
M=Path(__file__).resolve().parent;T=M.parent;R=M/'reports'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
try:
 p=M/'mixed_precision_step_benchmark_runtime_v3.py';s=importlib.util.spec_from_file_location('bench_runtime_cpu',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 old=T/'H1_STEP270_REWARD_AIRBORNE_FEASIBLE_V5_RESOURCE_V67_20261025/payloads/h1/job0/runtime/isaac/mod4/owned_h1_public4_mean_overflow_ppo_v2.py';a=old.read_text('utf8');b=m.amp_ppo_source(a);ast.parse(b)
 # Exact inverse of only scale/unscale/step changes, preserving all PPO loss and STD expressions.
 needle=next(l for l in a.splitlines() if l.strip()=='nn.utils.clip_grad_norm_(self.actor.parameters(), self.max_grad_norm)');indent=needle[:len(needle)-len(needle.lstrip())]
 normalized=b.replace('self._benchmark_scaler.scale(loss).backward()','loss.backward()').replace(indent+'self._benchmark_scaler.unscale_(self.optimizer)\n','').replace('self._benchmark_scaler.step(self.optimizer)\n'+indent+'self._benchmark_scaler.update()','self.optimizer.step()')
 assert normalized==a
 clock=type('Clock',(),{'t':0.,'__call__':lambda self:self.t})()
 profiler=m.ExclusivePhaseTimers(clock);obj=type('Object',(),{})()
 def child():clock.t+=2.
 def parent():clock.t+=1.;obj.child();clock.t+=3.
 obj.child=child;obj.parent=parent;profiler.install(obj,'parent','parent');profiler.install(obj,'child','child');profiler.enabled=True;obj.parent();assert profiler.sums=={'child':2.,'parent':4.};assert profiler.counts=={'child':1,'parent':1};profiler.restore()
 rng=torch.get_rng_state().clone();net=torch.nn.Sequential(torch.nn.Linear(8,16),torch.nn.Tanh(),torch.nn.Linear(16,6));torch.set_rng_state(rng)
 x=torch.arange(32,dtype=torch.float32).reshape(4,8)/32;before=[v.clone() for v in net.parameters()];dtype=torch.bfloat16
 with torch.autocast('cpu',dtype=dtype):out=net(x)
 y=out.float();assert y.dtype==torch.float32 and torch.isfinite(y).all();loss=y.square().mean();loss.backward();assert all(p.dtype==torch.float32 and p.grad.dtype==torch.float32 and torch.isfinite(p.grad).all() for p in net.parameters())
 assert all(torch.equal(p,q) for p,q in zip(net.parameters(),before)) and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 put('AMP_BENCHMARK_V3_SCALER_ALLOWLIST_AND_CPU_SYNTHETIC_ACTUAL.json',dict(epoch=time.time(),passed=True,runtime_source=str(p),runtime_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),H1_actual_PPO_base_SHA=hashlib.sha256(a.encode()).hexdigest(),only_loss_scale_unscale_optimizer_scaler_step_changes_AST_exact=True,FP32_master_and_gradients_under_CPU_BF16_MLP=True,FP32_probability_output_boundary=True,no_optimizer_step_or_model_source_changed=True,CPU_synthetic_only_not_GPU_timing_or_numerical_acceptance=True,original3900_save3600_exit300_and_runtime8GiB_completeupdate_guard=True))
 print(json.dumps(dict(passed=True,base_PPO_AST_exact_except_AMP=True,CPU_BF16_test=True,no_CUDA=True)))
except BaseException:
 put('AMP_BENCHMARK_SOURCE_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc()));raise

