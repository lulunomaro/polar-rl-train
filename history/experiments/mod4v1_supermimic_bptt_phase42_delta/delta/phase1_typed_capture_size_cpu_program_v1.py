"""NEW functional synthetic-volume measurement; not another old-suite qualification.
Complete B4/C2 fixtures reused once each, CPU only, no native/model/task-data access.
"""
from pathlib import Path,PurePosixPath
import os,sys,argparse,json,hashlib,importlib.util,traceback,time,random
os.environ['CUDA_VISIBLE_DEVICES']='';sys.dont_write_bytecode=True
p=argparse.ArgumentParser();p.add_argument('--root',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args();root=a.root.resolve();assert __debug__ and not a.output.exists();H=lambda b:hashlib.sha256(b).hexdigest();inp=json.loads((root/'INPUT.json').read_bytes());before={}
assert inp['purpose']=='NEW_TYPED_CAPTURE_SYNTHETIC_MATERIALIZED_VOLUME_NOT_QUALIFICATION'
for row in inp['files']:
 rel=PurePosixPath(row['relative']);assert not rel.is_absolute()and '..'not in rel.parts and rel.suffix.lower()in('.py','.json','.md','.txt','.patch');path=root/Path(*rel.parts);raw=path.read_bytes();assert(len(raw),H(raw))==(row['bytes'],row['SHA256']);before[str(path)]=H(raw)
sys.path[:0]=[str(root/'b4'),str(root/'codec'),str(root/'producer')]
import torch
torch.set_num_threads(1)
import typed_capture_codec as codec
import passive_capture as passive
import field_snapshot as field
import dependency_contract as dependency

def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);assert Path(m.__file__).resolve()==path.resolve();return m
sensor=load('sensor_mild_math',root/'original/sensor_mild_math.py');delay=load('feedback_delay_mild',root/'original/feedback_delay_mild.py')
contract=load('phase1_capture_contract',root/'producer/phase1_capture_contract.py');observer=load('phase1_capture_observer',root/'producer/phase1_capture_observer.py')
tap=load('phase1_sealed_actuation_tap_v2',root/'actuation/actuation_tap_v2.py');queue=load('action_delay_physics_queue',root/'original/action_delay_physics_queue.py')
b4=load('b4_real_sensor_cpu_fixture_for_volume',root/'b4_fixture/cpu_fixture.py');c2=load('typed_c2_cpu_fixture_for_volume',root/'c2_fixture/typed_c2_cpu_fixture.py');size=load('typed_size_cpu_fixture',root/'size/size_fixture.py')
source_paths={label:root/Path(*PurePosixPath(relative).parts)for label,relative in inp['size_input_paths'].items()};assert len(source_paths)==9
# These indices are fixture-owned CPU setup, not extra observer operations.
existing_cpu_codec=codec.CaptureCodec(torch.Tensor,witness_index=torch.arange(8,dtype=torch.int64),witness_env_ids=list(range(8)),n=80)
py=random.getstate();rng=torch.get_rng_state().clone();started=time.time();result=None;error=None;prior_profile=sys.getprofile()
try:
 result=size.run_size_fixture(torch_module=torch,codec_module=codec,passive_module=passive,codec=existing_cpu_codec,source_paths=source_paths,b4_run=b4.run_fixture,b4_args=(torch,sensor.SensorCorruption,delay.FeedbackDelay),b4_kwargs=dict(codec_module=codec,passive_module=passive,field_module=field,dependency_module=dependency),c2_run=c2.run_fixture,c2_args=(torch,queue.PhysicsActionQueue,tap,codec,observer,field))
 assert result['status']=='SIZE_PROFILE_COMPLETE'and result['old_fixture_calls']=={'b4':1,'c2':1}and not result['native_size_guarantee']and result['stage2_GO']is False
except BaseException as e:error=dict(type=type(e).__name__,message=str(e),traceback=traceback.format_exc(limit=14))
unchanged={path:H(Path(path).read_bytes())for path in before}==before;rngsame=py==random.getstate()and torch.equal(rng,torch.get_rng_state());forbidden=[n for n in sys.modules if n.split('.')[0]in{'isaacsim','isaaclab','omni','warp','pxr'}];profile_restored=sys.getprofile()is prior_profile
passed=error is None and unchanged and rngsame and not forbidden and not torch.cuda.is_initialized()and profile_restored
v=dict(kind='ACTUAL_PARENT_TYPED_CAPTURE_SYNTHETIC_MATERIALIZED_SIZE_CPU_V1',epoch=time.time(),status='PASS'if passed else'FAILED',wall_seconds=time.time()-started,torch_version=str(torch.__version__),torch_threads=torch.get_num_threads(),device='cpu',source_files_verified=len(before),all_uploaded_source_bytes_unchanged=unchanged,global_Python_and_Torch_CPU_RNG_unchanged=rngsame,profile_restored=profile_restored,CUDA_initialized=torch.cuda.is_initialized(),forbidden_native_modules=forbidden,measurement=result,error=error,actual_SDK_GPU_model_raw_task_data_C_lock_or_parent_operations=0,additional_independent_old_suite_qualification_claim=False,source_fixtures_reuse_purpose='MATERIALIZED_VOLUME_ONCE_EACH_NOT_STATUS_OR_GIT',actual_native_case_group_bytes=None,native_size_guarantee=False,Gate1='UNKNOWN',stage2_GO=False)
with a.output.open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
print(json.dumps(v,indent=2,allow_nan=False));raise SystemExit(0 if passed else 1)
