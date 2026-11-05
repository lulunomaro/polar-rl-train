"""One actual CPU algorithm check of the new source-bound target layer, NOT Isaac/PhysX evidence."""
from pathlib import Path
from types import SimpleNamespace
import json,sys,math,traceback,os,hashlib
import torch
D=Path(__file__).resolve().parent;P=D/'candidates/HW300N60/package';out=D/'candidates/HW300N60/RUNTIME_TARGET_CPU_VALIDATION.json';assert not out.exists();sys.path.insert(0,str(P));import runtime_adapter_v2 as rt
checks={};errors=[];detail={}
def ck(n,v):
 checks[n]=bool(v)
 if not v:raise AssertionError(n)
try:
 denied=False
 try:rt.prepare_environment()
 except ValueError:denied=True
 ck('explicit_opt_in_required',denied)
 os.environ['RM_DIFF_MIN']='-1.0843';os.environ['RM_DIFF_MAX']='.85';prep=rt.prepare_environment(opt_in=True);bounds=prep['mechanical_delta_by_side_rad'];lo,hi=bounds['left'];ck('stale_operating_window_replaced',abs(float(os.environ['RM_DIFF_MIN'])-lo)<1e-12 and abs(float(os.environ['RM_DIFF_MAX'])-hi)<1e-12 and hi<.85)
 class Base:
  def __init__(self,cfg,env):self.action_dim=4;self._joint_ids=[0,1,2,3];self._asset=SimpleNamespace(data=SimpleNamespace(joint_pos=env.clone()));self.calls=dict(base=0,delay=0,legacy=0);self.cfg=cfg
  def process_actions(self,a):self.calls['base']+=1;self.processed_actions=a.clone()*self.cfg.scale
  def apply_actions(self):return 'original_apply'
  def reset(self,*a):return 'original_reset'
 class Delay:
  def process_actions(self,a):self.calls['delay']+=1;super().process_actions(a)
 class Legacy(Delay,Base):
  def __init__(self,cfg,env):Base.__init__(self,cfg,env)
  def process_actions(self,a):self.calls['legacy']+=1;super().process_actions(a);self.processed_actions.clamp_(-.5,.5)
 task=SimpleNamespace(DelayedJointPositionAction=Legacy,_DelayMixin=Delay,mdp_actions=SimpleNamespace(JointPositionAction=Base),LEG_ORDER=rt.LEG_ORDER,torch=torch)
 V2=rt.make_mechanical_action_class(task);cfg=SimpleNamespace(joint_names=rt.LEG_ORDER,preserve_order=True,scale=.5)
 current=torch.tensor([[2*math.pi+.3,2*math.pi+.2,2*math.pi+.3,2*math.pi+.2],[3.1,3.,3.1,3.],[0.,0.,0.,0.]],dtype=torch.float64)
 targets=torch.tensor([[.3,.2,.3,.2],[-3.,3.,-3.,3.],[hi+.3,0.,lo-.3,0.]],dtype=torch.float64);actions=targets/cfg.scale;original=actions.clone();obj=V2(cfg,current);obj.process_actions(actions);pa=obj.processed_actions
 ck('source_scale_and_delay_executed_once',obj.calls==dict(base=1,delay=1,legacy=0))
 ck('original_apply_reset_inherited',V2.apply_actions is Legacy.apply_actions and V2.reset is Legacy.reset)
 ck('input_tensor_not_mutated',torch.equal(actions,original))
 ck('common_turn_preserved',torch.max(torch.abs(pa[0]-current[0])).item()<1e-12)
 want=2*math.pi-6.;ck('relative_target_cross_pi_unwrapped_before_projection',abs((pa[1,0]-pa[1,1]).item()-want)<1e-12 and abs((pa[1,2]-pa[1,3]).item()-want)<1e-12)
 ck('real_upper_lower_projected',abs((pa[2,0]-pa[2,1]).item()-hi)<1e-12 and abs((pa[2,2]-pa[2,3]).item()-lo)<1e-12)
 ck('all_target_relative_coordinates_mechanically_bounded',bool(((pa[:,0]-pa[:,1])>=lo-1e-12).all()and((pa[:,0]-pa[:,1])<=hi+1e-12).all()and((pa[:,2]-pa[:,3])>=lo-1e-12).all()and((pa[:,2]-pa[:,3])<=hi+1e-12).all()))
 detail=dict(preimport=prep,current=current.tolist(),post_scale_targets=targets.tolist(),projected_targets=pa.tolist(),source_calls=obj.calls,relative_periodic_expected=want,bounds=bounds,torch_version=torch.__version__,adapter_SHA256=hashlib.sha256((P/'runtime_adapter_v2.py').read_bytes()).hexdigest())
except BaseException:errors.append(traceback.format_exc())
r=dict(kind='MOD4V2_TARGET_LAYER_CPU_ALGORITHM_VALIDATION_NOT_SDK',passed=not errors and all(checks.values()),checks=checks,details=detail,errors=errors,source_ABI_stub_not_native=True,Isaac_PhysX_GPU_or_training=False,native_feedback100Hz_verified=False);out.write_text(json.dumps(r,indent=2),encoding='utf8');print(json.dumps(dict(receipt=str(out),passed=r['passed'],failed=[k for k,v in checks.items()if not v],errors=errors),indent=2));sys.exit(0 if r['passed']else 1)
