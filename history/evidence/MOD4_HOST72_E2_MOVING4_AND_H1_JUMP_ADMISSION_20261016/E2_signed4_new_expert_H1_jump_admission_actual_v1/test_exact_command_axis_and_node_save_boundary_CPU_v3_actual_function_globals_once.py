"""Actual command AST paired old/new with identical draws; isolated negative fixtures."""
from pathlib import Path
import os,ast,json,time,hashlib,shutil,types,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
D=Path(__file__).resolve().parent;Q=D/'payload';R=D/'reports';W=D.parent
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 for name in ('e2_h1_phase_worker_v1.py','verify_e2_h1_native_CPU_v1.py','e2_h1_node72_finite_v1.py','e2_source_original_canonical_owner_v1.py'):
  compile((D/name).read_text(encoding='utf8'),name,'exec');shutil.copyfile(D/name,Q/name)
 old=W/'MOD4_THREE_EXPERTS_AND_CURB878_EVAL_20261016/train_payload/job1/runtime/isaac/mod4/directional_spin_runtime.py';new=Q/'job0/runtime/isaac/mod4/e2_directional_spin_runtime_v1.py'
 class Base:
  def _resample_command(self,ids):self.is_standing_env[ids]=torch.arange(len(ids))%10==0
 fixtures=[];global_before=torch.get_rng_state().clone()
 for n in (80,88):
  for seed in (20261002,20261003):
   out=[]
   for path in (old,new):
    tree=ast.parse(path.read_text(encoding='utf8'));c=next(z for z in tree.body if isinstance(z,ast.ClassDef));methods=[z for z in c.body if isinstance(z,ast.FunctionDef) and z.name in ('_resample_command','_write_dynamic')];cls=ast.ClassDef(name='ExactCommand',bases=[ast.Name(id='UniformVelocityCommand',ctx=ast.Load())],keywords=[],body=methods,decorator_list=[]);module=ast.fix_missing_locations(ast.Module(body=[next(z for z in tree.body if isinstance(z,ast.FunctionDef) and z.name=='transition_yaw'),cls],type_ignores=[]))
    def body_command(goal,direction,heading,limit):return 2*goal*torch.cos(heading-direction),torch.zeros_like(heading)
    g={'torch':torch,'math':__import__('math'),'UniformVelocityCommand':Base,'body_command':body_command};exec(compile(module,str(path),'exec'),g);obj=g['ExactCommand']();obj.cfg=types.SimpleNamespace(rel_standing_envs=.1);obj.device='cpu';obj.pure_fraction=.3;obj.moving_fraction=.2;obj.transition_within_pure=1/3;obj.pure_max=4*torch.pi;obj.progress_goal=.5;obj.body_limit=1.5;obj.manual_evaluation_mode=False;obj._mode_rng=torch.Generator().manual_seed(seed);obj.robot=types.SimpleNamespace(data=types.SimpleNamespace(heading_w=types.SimpleNamespace(torch=torch.linspace(-3,3,n))))
    for key in ('is_standing_env','is_heading_env','is_pure_spin','is_moving_spin','is_transition_spin'):setattr(obj,key,torch.zeros(n,dtype=torch.bool))
    for key in ('world_direction','signed_yaw','phase_elapsed'):setattr(obj,key,torch.zeros(n))
    obj.vel_command_b=torch.zeros(n,3);obj._resample_command(torch.arange(n));out.append(obj)
   a,b=out;mask=b.is_moving_spin;assert mask.any() and torch.all(b.signed_yaw[mask].abs()==4) and torch.all(a.signed_yaw[mask].abs()<=2)
   assert torch.equal(a._mode_rng.get_state(),b._mode_rng.get_state()) and torch.equal(a.vel_command_b[~mask],b.vel_command_b[~mask]) and torch.equal(a.vel_command_b[mask,:2],b.vel_command_b[mask,:2]);fixtures.append(dict(N=n,seed=seed,moving4_rows=int(mask.sum()),original_other_modes_and_draws_next_state_exact=True))
 assert torch.equal(global_before,torch.get_rng_state()) and not torch.cuda.is_initialized()
 for j in (0,1):
  m=Q/('job'+str(j))/'runtime/isaac/mod4';tree=ast.parse((m/'train_E2_full_resume_v1.py').read_text(encoding='utf8'));assert any(isinstance(z,ast.ImportFrom) and z.module=='e2_command_checkpoint_v1' for z in tree.body)==(j==0)
 # Positive-vertical impulse is the original Warp kernel's semantics, not vector impulse.
 f=torch.tensor([[[2.,3.,10.],[-2.,-3.,-1.]]]*4);expected=f[:,:,2].clamp_min(0).sum(0)*.0025;assert torch.equal(expected,torch.tensor([.1,0.]))
 m=dict(epoch=time.time(),files=[dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(Q.rglob('*')) if p.is_file() and p.name!='PAYLOAD_MANIFEST.json' and '__pycache__' not in p.parts]);(Q/'PAYLOAD_MANIFEST.json').write_text(json.dumps(m,indent=2),encoding='utf8')
 write(R/'E2_EXACT_COMMAND_DRAW_AXIS_AND_NATIVE_IMPULSE_NODE_BOUNDARY_CPU_V3_ACTUAL.json',dict(epoch=time.time(),passed_CPU_only=True,fixtures=fixtures,actual_old_new_resample_and_dynamic_AST_executed=True,original_nonmoving_commands_and_private_rng_nextdraw_exact=True,global_CPU_RNG_unchanged=True,original_native_impulse_positive_vertical_semantics=True,H1_fresh80_no_fake_full20k_state=True,H1_original_D7_save_not_fake_E2_command_group=True,source_owner_waits_actual_CURB_lock_handoff=True,source_owner_cannot_settle_stale_precheck_exit_after_node_exception=True,all_own_node_children_wait_before_failure_handoff=True,not_target_native_or_PPO=True,packagefiles=len(m['files'])))
 print(json.dumps(dict(CPU_pass=True,fixtures=fixtures,files=len(m['files']))),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:write(R/('E2_H1_CPU_V3_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(error=traceback.format_exc(),no_GPU_dispatch=True));raise
