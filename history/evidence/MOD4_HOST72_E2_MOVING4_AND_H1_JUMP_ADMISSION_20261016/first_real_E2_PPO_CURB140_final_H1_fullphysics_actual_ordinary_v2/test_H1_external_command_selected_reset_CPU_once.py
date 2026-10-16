"""Actual old and new resample AST; explicit operator request stays zero through reset."""
from pathlib import Path
import ast,types,json,time,os,hashlib
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch,math
D=Path(__file__).resolve().parent;R=D/'reports';P=D/'h1_calibration_payload_v1';old=D/'payload/job1/runtime/isaac/mod4/directional_spin_runtime.py'
class Base:
 def _resample_command(self,ids):self.is_standing_env[ids]=False
def body_command(goal,direction,heading,limit):return 2*goal*torch.cos(heading-direction),torch.zeros_like(heading)
def main():
 tree=ast.parse(old.read_text(encoding='utf8'));oc=next(z for z in tree.body if isinstance(z,ast.ClassDef));oc=ast.ClassDef(name='OriginalCommand',bases=[ast.Name(id='UniformVelocityCommand',ctx=ast.Load())],keywords=[],body=[z for z in oc.body if isinstance(z,ast.FunctionDef) and z.name in ('_resample_command','_write_dynamic')],decorator_list=[]);hc=next(z for z in ast.parse((D/'h1_external_operator_command_v1.py').read_text(encoding='utf8')).body if isinstance(z,ast.ClassDef));g=dict(torch=torch,math=math,UniformVelocityCommand=Base,body_command=body_command);exec(compile(ast.fix_missing_locations(ast.Module(body=[next(z for z in tree.body if isinstance(z,ast.FunctionDef) and z.name=='transition_yaw'),oc],type_ignores=[])),str(old),'exec'),g);g['DirectionalSpinCommand']=g['OriginalCommand'];exec(compile(ast.fix_missing_locations(ast.Module(body=[hc],type_ignores=[])),'actual_H1_external_class','exec'),g)
 fixtures=[];before=torch.get_rng_state().clone()
 for n in (80,88):
  for seed in (20261002,20261003):
   objs=[]
   for name in ('OriginalCommand','H1ExternalOperatorCommand'):
    o=g[name]();o.cfg=types.SimpleNamespace(rel_standing_envs=.1);o.device='cpu';o.pure_fraction=.3;o.moving_fraction=.2;o.transition_within_pure=1/3;o.pure_max=4*torch.pi;o.progress_goal=.5;o.body_limit=1.5;o.manual_evaluation_mode=False;o._mode_rng=torch.Generator().manual_seed(seed);o.robot=types.SimpleNamespace(data=types.SimpleNamespace(heading_w=types.SimpleNamespace(torch=torch.linspace(-3,3,n))))
    for k in ('is_standing_env','is_heading_env','is_pure_spin','is_moving_spin','is_transition_spin'):setattr(o,k,torch.zeros(n,dtype=torch.bool))
    for k in ('world_direction','signed_yaw','phase_elapsed'):setattr(o,k,torch.zeros(n))
    o.vel_command_b=torch.zeros(n,3);o._resample_command(torch.arange(n));objs.append(o)
   a,b=objs;assert torch.equal(a._mode_rng.get_state(),b._mode_rng.get_state()) and not b.vel_command_b.any();saved=b.vel_command_b.clone();ids=torch.tensor([1,4,7]);a._resample_command(ids);b._resample_command(ids);assert torch.equal(a._mode_rng.get_state(),b._mode_rng.get_state()) and torch.equal(saved,b.vel_command_b);assert not (b.is_pure_spin|b.is_moving_spin|b.is_transition_spin).any();fixtures.append(dict(N=n,seed=seed,original_private_nextdraw_exact=True,all_request_twist_zero_through_selected_reset=True))
 assert torch.equal(before,torch.get_rng_state()) and not torch.cuda.is_initialized()
 with (R/'H1_EXTERNAL_REQUEST_SELECTED_RESET_ACTUAL_AST_CPU_PASSED.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed_CPU_only=True,fixtures=fixtures,not_actual_SDK_or_airborne_credit=True,old_native_raw_and_command_generation_retained=True,new_calibration_scope_only=True),f,indent=2)
 print(json.dumps(dict(H1_selected_reset_CPU_passed=True,fixtures=4)),flush=True)
if __name__=='__main__':main()
