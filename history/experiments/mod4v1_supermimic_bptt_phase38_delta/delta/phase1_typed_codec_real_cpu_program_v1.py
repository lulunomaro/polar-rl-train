"""NEW standalone original-codec real TorchCPU synthetic contract, never SDK."""
from pathlib import Path
import hashlib,importlib.util,json,os,sys,time,traceback
os.environ['CUDA_VISIBLE_DEVICES']='';sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;H=lambda b:hashlib.sha256(b).hexdigest();pins=json.loads((D/'INPUT_PINS.json').read_bytes());v=dict(kind='ACTUAL_TYPED_CODEC_TORCH_CPU_SYNTHETIC_CONTRACT_V1',epoch=time.time(),actual_SDK_model_raw_C_lock_parent_or_GPU_operations=0,native_BPTT_or_skill_evidence=False,Gate1='UNKNOWN',stage2_GO=False)
try:
 modules={}
 for name in('typed_capture_codec','cpu_fixture'):
  p=D/(name+'.py');b=p.read_bytes();assert(len(b),H(b))==(pins[name]['bytes'],pins[name]['SHA256']);spec=importlib.util.spec_from_file_location('_actual_'+name+'_v1',p);m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m);modules[name]=m
 import torch
 v['Torch_version']=torch.__version__;v['receipt']=modules['cpu_fixture'].run_fixture(torch,modules['typed_capture_codec']);assert v['receipt']['result']=='PASS';v['status']='PASS'
except BaseException as e:
 v.update(status='FAIL',error_type=type(e).__name__,error=str(e),traceback=traceback.format_exc())
with(D/'RESULT.json').open('x',encoding='utf8')as f:json.dump(v,f,indent=2)
print(json.dumps(v,indent=2));assert v['status']=='PASS',v.get('error')
