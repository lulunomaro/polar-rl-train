"""NEW CPU-only typed-C2 coupling. Complete modules, no SDK or native entry."""
from pathlib import Path
import hashlib,importlib.util,json,os,random,sys,time,traceback
HERE=Path(__file__).resolve().parent;os.environ['CUDA_VISIBLE_DEVICES']='';sys.path.insert(0,str(HERE));H=lambda b:hashlib.sha256(b).hexdigest();pins=json.loads((HERE/'PINS.json').read_bytes());source={}
for name,pin in pins.items():
 b=(HERE/name).read_bytes();assert(len(b),H(b))==(pin['bytes'],pin['SHA256']);source[name]=b
import torch
torch.set_num_threads(1)
def load(name,filename):
 path=HERE/filename;spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);assert Path(m.__file__).resolve()==path;return m
codec=load('typed_capture_codec','typed_capture_codec.py');field=load('field_snapshot','field_snapshot.py');contract=load('phase1_capture_contract','phase1_capture_contract.py');observer=load('phase1_capture_observer','phase1_capture_observer.py');tap=load('phase1_sealed_actuation_tap_v2','actuation_tap_v2.py');queue=load('action_delay_physics_queue','action_delay_physics_queue.py');fixture=load('typed_c2_cpu_fixture','typed_c2_cpu_fixture.py')
assert not torch.cuda.is_initialized()and not any(n.split('.')[0]in{'isaacsim','isaaclab','omni','warp','pxr'}for n in sys.modules)
py=random.getstate();rng=torch.get_rng_state().clone();start=time.perf_counter();result=None;error=None
try:
 result=fixture.run_fixture(torch,queue.PhysicsActionQueue,tap,codec,observer,field)
except BaseException:
 error=traceback.format_exc()
unchanged=all((HERE/n).read_bytes()==b for n,b in source.items());rngsame=random.getstate()==py and torch.equal(torch.get_rng_state(),rng);forbidden=[n for n in sys.modules if n.split('.')[0]in{'isaacsim','isaaclab','omni','warp','pxr'}]
v=dict(kind='ACTUAL_REAL_TORCH_CPU_TYPED_C2_COUPLING_V2',epoch=time.time(),status='PASS'if error is None and unchanged and rngsame and not forbidden and not torch.cuda.is_initialized()else'FAILED',wall_seconds=time.perf_counter()-start,torch_version=str(torch.__version__),torch_threads=torch.get_num_threads(),device='cpu',fixture_result=result,error=error,all_uploaded_source_bytes_unchanged=unchanged,global_python_and_torch_CPU_rng_unchanged=rngsame,CUDA_initialized=torch.cuda.is_initialized(),forbidden_native_modules=forbidden,synthetic_env_asset_term=True,real_original_queue_and_C2=True,SDK_or_model_raw_C_lock_or_parent_operations=0,actual_native_BPTT_updates=0,Gate1='UNKNOWN',stage2_GO=False)
print(json.dumps(v,allow_nan=False));sys.exit(0 if v['status']=='PASS'else 1)
