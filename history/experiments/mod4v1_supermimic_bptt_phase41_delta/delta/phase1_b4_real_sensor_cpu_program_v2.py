"""Run one reviewed complete B4 fixture on real original Torch CPU classes.
Fake environment only; never calls native install/preflight or any SDK.
"""
from pathlib import Path,PurePosixPath
import os,sys,argparse,json,hashlib,importlib.util,traceback,random,time
os.environ['CUDA_VISIBLE_DEVICES']='';sys.dont_write_bytecode=True
p=argparse.ArgumentParser();p.add_argument('--root',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args();root=a.root.resolve();assert __debug__ and not a.output.exists();H=lambda b:hashlib.sha256(b).hexdigest();inp=json.loads((root/'INPUT.json').read_bytes());before={}
for row in inp['files']:
 rel=PurePosixPath(row['relative']);assert not rel.is_absolute()and '..'not in rel.parts and rel.suffix.lower()in('.py','.json','.md','.txt','.patch');path=root/Path(*rel.parts);raw=path.read_bytes();assert(len(raw),H(raw))==(row['bytes'],row['SHA256']);before[str(path)]=H(raw)
assert len(before)==41 and inp['purpose']=='NEW_B4_REAL_SENSOR_DELAY_SOFTWARE_CPU_V2_NOT_NATIVE'
sys.path[:0]=[str(root/'b4'),str(root/'codec')]
import torch
torch.set_num_threads(1)
import typed_capture_codec as codec
import passive_capture as passive
import field_snapshot as field
import dependency_contract as dependency

def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
sensor=load('sensor_mild_math',root/'original/sensor_mild_math.py');delay=load('feedback_delay_mild',root/'original/feedback_delay_mild.py');fixture=load('b4_real_sensor_cpu_fixture',root/'fixture/cpu_fixture.py')
py_rng=random.getstate();rng=torch.get_rng_state().clone();started=time.time();result=None;error=None
try:
 result=fixture.run_fixture(torch,sensor.SensorCorruption,delay.FeedbackDelay,codec_module=codec,passive_module=passive,field_module=field,dependency_module=dependency)
 assert result['status']=='PASS'and result['checks']['main64']['controls']==64 and result['checks']['main64']['normal_channel_records']==640 and result['checks']['main64']['metadata_errors']==0
 assert result['private_generators_queue_cache_parity']and result['source_seals_unchanged']and result['Torch_CPU_and_Python_global_RNG_unchanged']and not result['native_binding_preflight_executed']and result['stage2_GO']is False
except BaseException as e:error=dict(type=type(e).__name__,message=str(e),traceback=traceback.format_exc(limit=14))
unchanged={path:H(Path(path).read_bytes())for path in before}==before;rng_same=random.getstate()==py_rng and torch.equal(rng,torch.get_rng_state());forbidden=[x for x in('isaaclab','omni','isaacsim')if x in sys.modules];passed=error is None and unchanged and rng_same and not forbidden
receipt=dict(kind='ACTUAL_PARENT_B4_REAL_ORIGINAL_SENSOR_DELAY_TYPED_TAP_CPU_V2',epoch=time.time(),status='PASS'if passed else'FAILED',wall_seconds=time.time()-started,torch_version=torch.__version__,torch_num_threads=1,source_files_verified=len(before),all_uploaded_source_bytes_unchanged=unchanged,global_Python_and_Torch_CPU_RNG_unchanged=rng_same,fixture_result=result,error=error,forbidden_SDK_modules=forbidden,native_install_or_binding_preflight_executed=False,actual_SDK_GPU_model_raw_C_or_resource_operations=0,native_policy_BPTT_updates=0,Gate1='UNKNOWN',stage2_GO=False)
with a.output.open('x',encoding='utf8')as f:json.dump(receipt,f,indent=2)
print(json.dumps(receipt,indent=2));raise SystemExit(0 if passed else 1)
