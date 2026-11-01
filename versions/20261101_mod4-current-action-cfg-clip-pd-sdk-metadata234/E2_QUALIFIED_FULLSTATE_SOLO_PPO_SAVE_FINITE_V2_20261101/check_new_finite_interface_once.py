"""New finite-only purpose; stdlib synthetic objects, no Torch/model runtime."""
from pathlib import Path
import ast,hashlib,json,math,time,traceback
N=Path(__file__).resolve().parent;R=N/'reports'
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def main():
 purpose=json.loads((R/'CPU_FINITE_V2_PURPOSE_FROZEN.json').read_bytes());assert purpose['executions']==1
 put(R/'CPU_FINITE_V2_ONCE_CONSUMED.json',dict(epoch=time.time(),old_fixtures=0))
 s=(N/'worker_e2_original_fullPPO.py').read_text(encoding='utf8');tree=ast.parse(s)
 function=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='validate_finite_tree')
 ns={};exec(compile(ast.Module(body=[function],type_ignores=[]),'<new_finite_function>','exec'),ns)
 class Tensor:
  def __init__(self,v):self.v=v
  def is_floating_point(self):return True
  def is_complex(self):return False
 class All:
  def __init__(self,v):self.v=v
  def all(self):return self.v
 class Torch:
  @staticmethod
  def is_tensor(v):return isinstance(v,Tensor)
  @staticmethod
  def isfinite(v):return All(all(math.isfinite(x) for x in v.v))
 f=ns['validate_finite_tree'];f(Torch,dict(state=[1,2.,complex(1,2),Tensor([0.,1.])],rng=(3,)))
 rejected=[]
 for value in [dict(x=float('nan')),dict(x=[float('inf')]),(complex(1,float('inf')),),dict(a=Tensor([1.,float('nan')]))]:
  try:f(Torch,value)
  except AssertionError:rejected.append(True)
  else:raise AssertionError('New finite rejection did not reject')
 assert s.index("validate_finite_tree(torch,state,'complete_save')")<s.index('torch.save(state,tmp);tmp.replace(path)')<s.index("put('latest_complete.json',row)")
 assert s.index("validate_finite_tree(torch,losses,'PPO_losses')")<s.index('updates[0]+=1')
 assert s.index("put('E2_SOURCE_SELECTED_FINAL_READ_COUNTS.json'")<s.index("ns['app'].close()")
 put(R/'CPU_FINITE_V2_NEW_INTERFACE_ACTUAL.json',dict(epoch=time.time(),passed=True,worker_AST=1,new_synthetic_finite_pass=1,new_nonfinite_rejections=len(rejected),
  complete_save_and_loss_order_verified=True,Torch_imports=0,model_reads=0,SDK_network_Git=0,old_fixture_replays=0))
if __name__=='__main__':
 try:main()
 except BaseException:put(R/'CPU_FINITE_V2_ORIGINAL_ERROR.json',dict(error=traceback.format_exc()));raise
