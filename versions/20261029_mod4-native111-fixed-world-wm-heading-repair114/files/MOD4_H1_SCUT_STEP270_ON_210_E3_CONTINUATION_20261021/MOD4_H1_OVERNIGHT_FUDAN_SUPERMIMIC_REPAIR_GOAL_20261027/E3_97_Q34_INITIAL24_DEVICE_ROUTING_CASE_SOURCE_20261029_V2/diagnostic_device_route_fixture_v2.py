"""Real CPU tensors + device-label spies. NO CUDA kernel/SDK/model invocation."""
import ast
def run_device_route_fixture(helper,t):
 checks=[]
 values=t.arange(12,dtype=t.float32).reshape(4,3);saved=values.clone()
 for index in (t.tensor([3,1],dtype=t.long),t.tensor([True,False,True,False],dtype=t.bool)):
  before=index.clone();out=helper.diagnostic_select(t,values,index)
  assert t.equal(out,values[index]) and t.equal(before,index) and t.equal(saved,values)
  checks.append('real_CPU_'+str(index.dtype)+'_index_dtype_values_unchanged')
 try:helper.diagnostic_select(t,values,t.tensor([0.,1.]))
 except AssertionError:checks.append('floating_tensor_index_rejected_not_silently_cast')
 else:raise AssertionError('Floating diagnostic indices accepted')
 routes=[]
 class Index:
  def __init__(self,device,dtype,data):self.device=device;self.dtype=dtype;self.data=data
  def to(self,*,device,dtype):routes.append(dict(source=self.device,target=device,dtype=str(dtype)));return Index(device,dtype,self.data)
 class Target:
  def __init__(self,device,dtype):self.device=device;self.dtype=dtype
  def __getitem__(self,index):
   assert index.device==self.device,'Synthetic reproducer: CUDA-index/CPU-target device mismatch'
   assert index.dtype in (t.long,t.bool),'Index dtype incorrectly taken from floating target'
   return dict(value=index.data,target=self.device,index_dtype=str(index.dtype))
 class TorchAPI:
  long=t.long;bool=t.bool
  @staticmethod
  def is_tensor(x):return isinstance(x,Index)
 for target_device,index_device in [('cpu','cuda:0'),('cuda:0','cpu'),('cuda:1','cuda:0'),('cpu','cpu')]:
  for dtype,data in ((t.long,[3,1]),(t.bool,[True,False,True,False])):
   value=Target(target_device,t.float32);index=Index(index_device,dtype,data)
   result=helper.diagnostic_select(TorchAPI,value,index)
   assert result['target']==target_device and result['index_dtype']==str(dtype) and result['value']==data
   assert index.device==index_device and index.dtype==dtype
   checks.append('label_spy_'+index_device+'->'+target_device+'_'+str(dtype))
 # Exact old value[index] fails the mixed-domain proxy; new source succeeds above.
 try:Target('cpu',t.float32)[Index('cuda:0',t.long,[0])]
 except AssertionError:checks.append('old_direct_CPU_target_CUDA_index_reproduced_with_label_spy')
 else:raise AssertionError('Old mixed-domain access not rejected')
 limits=t.tensor([[[-.0267046843609,.020639440248416612]]*2]*3)
 q=t.tensor([-.017186211422085762,-.017186211422085762]);ls=limits.clone();qs=q.clone()
 class QCopySpy:
  def __init__(self,v):self.v=v;self.device='cuda:0';self.dtype=v.dtype;self.targets=[]
  def to(self,*,device):self.targets.append(device);return self.v.to(device=device)
 qp=QCopySpy(q);mask=helper.diagnostic_outside_actual_limits(qp,limits)
 assert qp.targets==[limits.device] and not bool(mask.any()) and t.equal(limits,ls) and t.equal(q,qs)
 badq=q.clone();badq[0]=.1;mask=helper.diagnostic_outside_actual_limits(badq,limits)
 assert bool(mask[:,0].all()) and not bool(mask[:,1].any()) and t.equal(limits,ls)
 checks+=['diagnostic_comparison_q_copy_routes_to_limits_device_only','limits_and_original_q_dtype_data_unchanged','actual_outside_value_not_clamped_or_hidden']
 return dict(passed=True,checks=checks,route_calls=routes,scope='fresh REAL CPU tensors and symbolic device-label proxies, NOT a CUDA device/kernel test',actual_CUDA_execution_tested=False,no_torch_cuda_query_SDK_model_NPZ_raw_or_host=True,index_dtype_long_or_bool_preserved_target_float_not_used=True)

def validate_index_route_source(raw):
 tree=ast.parse(raw);functions={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
 target=ast.parse('value[index.to(device=value.device,dtype=index.dtype)]',mode='eval').body
 fn=functions['diagnostic_select'];ret=next(n for n in fn.body if isinstance(n,ast.Return))
 assert ast.dump(ret.value,include_attributes=False)==ast.dump(target,include_attributes=False)
 comp=functions['diagnostic_outside_actual_limits']
 expected=ast.parse('compare_q=q.to(device=limits.device)').body[0]
 assert ast.dump(comp.body[0],include_attributes=False)==ast.dump(expected,include_attributes=False)
 # All dynamic observer tensor selections must use the single typed router.
 bad=[]
 for n in ast.walk(tree):
  if not isinstance(n,ast.Subscript):continue
  sl=n.slice
  if isinstance(sl,ast.Name) and sl.id in ('selected','recipe'):
   bad.append(ast.unparse(n))
  if isinstance(sl,ast.Name) and sl.id=='ids' and isinstance(n.value,ast.Name) and n.value.id in ('pp','qq','v'):bad.append(ast.unparse(n))
 assert not bad,bad
 assert sum(isinstance(n,ast.Attribute) and n.attr=='get_dof_limits' for n in ast.walk(tree))==0
 assert sum(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='diagnostic_select' for n in ast.walk(tree))==19
 return dict(passed=True,diagnostic_select_calls19=True,index_target_device_index_original_dtype_exact_AST=True,q_copy_device_only_exact_AST=True,no_added_original_limit_or_SDK_query=True)
