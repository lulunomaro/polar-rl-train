"""Exact scalar / tensor serialization fixture; no Warp, Kit, GPU or transport."""
from pathlib import Path
import ast,hashlib,json,math,time
import numpy as np,torch
D=Path(__file__).resolve().parent;P=D/'payload';R=D/'reports';out=R/'HARDWARE_SCALAR_V6_SYNTHETIC_CPU_FIXTURE_PASSED.json';assert not out.exists()
source=P/'retention_native_witness_v6.py';fn=next(n for n in ast.parse(source.read_text(encoding='utf8')).body if isinstance(n,ast.FunctionDef) and n.name=='scalar_or_tensor_json')
calls=[]
def original_js(value):
 calls.append(type(value).__name__)
 if isinstance(value,torch.Tensor):return value.detach().cpu().tolist()
 if hasattr(value,'torch'):return value.torch.detach().cpu().tolist()
 raise RuntimeError('Native scalar must never enter original tensor bridge')
scope=dict(np=np,math=math,js=original_js);exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),str(source),'exec'),scope)
convert=scope['scalar_or_tensor_json'];cases=[53.3333,np.float32(53.3333),np.float64(28.1853),np.int64(128),2**63+7,True]
rows=[]
for value in cases:
 result=convert(value);expected=value.item() if isinstance(value,np.generic) else value
 assert result==expected and json.loads(json.dumps(result))==expected
 rows.append(dict(input_type=type(value).__name__,output_type=type(result).__name__,exact_result=result))
assert calls==[]
t=torch.tensor([[16.7552,40.],[55.3557,5.7759]],dtype=torch.float32);value=convert(t);assert value==t.detach().cpu().tolist() and calls==['Tensor']
class Proxy:
 def __init__(self,t):self.torch=t
value=convert(Proxy(t));assert value==t.detach().cpu().tolist() and calls==['Tensor','Proxy']
negative=[]
for value in (float('nan'),float('inf'),np.float32(float('-inf'))):
 try:convert(value);raise RuntimeError('Nonfinite scalar incorrectly accepted')
 except AssertionError as error:negative.append(str(error))
assert len(negative)==3 and calls==['Tensor','Proxy']
report=dict(epoch=time.time(),passed_CPU_synthetic_only=True,source=str(source),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),fixtures=rows,original_tensor_and_proxy_array_bridge_output_exact=True,native_scalars_never_entered_tensor_bridge=True,exact_integer_uint64_scalar_roundtrip=True,js_calls=calls,nonfinite_scalar_negative_cases=negative,hardware_values_not_modified=True,no_GPU_no_SSH_no_Warp_no_Kit_no_PPO=True,actual_native_control_PASS_not_claimed=True)
out.write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report))
