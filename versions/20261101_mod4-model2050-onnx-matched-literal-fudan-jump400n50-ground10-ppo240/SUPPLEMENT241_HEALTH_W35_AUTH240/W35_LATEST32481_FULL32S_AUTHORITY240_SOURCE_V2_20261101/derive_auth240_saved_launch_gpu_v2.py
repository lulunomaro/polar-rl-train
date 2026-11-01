"""Independent V2 fixes only actual240 missing-GPU-in-GO reader assumption."""
from pathlib import Path
import ast,hashlib,json,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
V1=T/'W35_LATEST32481_FULL32S_AUTHORITY240_SOURCE_V1_20261101'
A=T/'MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101/reports'
def read(p):return json.loads(Path(p).read_bytes())
def ref(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def main():
 assert read(R/'DERIVE_AUTH240_V2_PURPOSE_FROZEN.json')['executions']==1
 assert ref(V1/'INDEX_AUTH240_V1_REJECTED_CPU_FROZEN.json')['SHA']=='cb5de27e6c3ce707e20972b310ec6c0332210eaa84931005fbee73ebd15bb683'
 launch=read(A/'ROOT240_ORIGINAL_SOLO_OWNER_LAUNCH_ACTUAL.json');public=read(A/'ROOT240_ACTUAL_TASK_MANIFEST_READY_AND_PUBLIC_SCHEDULE.json');binding=read(A/'KNOWN_ACTIVE240_AUTHORITY_BINDING_FOR_FUTURE_SERIAL_READONLY.json')
 gpu=launch['specs']['jump_72']['GPU_UUID'];assert gpu==public['schedule']['experts']['jump_72']['GPU_UUID']=='GPU-16828f91-2b45-b646-8dc0-9481138e2842'
 assert launch['run_id']==public['run_id']==binding['run_id'] and 'GPU_UUID' not in binding['go']['jump_72']
 put(R/'DERIVE_AUTH240_V2_ONCE_CONSUMED.json',dict(epoch=time.time(),source_only=True))
 files=['contract_latest32.py','evaluate_latest32481_full32s_ROOT_ONLY_once.py','target_latest32_parent_ROOT_ONLY.py','guard_latest32.py','rm70_intervals227.py','positional_rows227.py','decode227_positional.py','make_latest32_Task_SOURCE_ONLY.py','run_ROOT_latest32481_full32s_once.py']
 for name in files:
  s=(V1/name).read_text(encoding='utf8')
  if name=='contract_latest32.py':
   a="KNOWN_ROLE='jump_72'";assert s.count(a)==1;s=s.replace(a,a+'\nKNOWN_ACTIVE_GPU_UUID='+repr(gpu))
   a="active_GPU_UUID=binding['go'][KNOWN_ROLE]['GPU_UUID']";assert s.count(a)==1;s=s.replace(a,'active_GPU_UUID=KNOWN_ACTIVE_GPU_UUID')
  ast.parse(s)
  with (N/name).open('x',encoding='utf8',newline='\n') as f:f.write(s)
 s=(V1/'check_auth240_new_JSON_AST_once.py').read_text(encoding='utf8')
 s=s.replace('CPU_AUTH240_PURPOSE_FROZEN.json','CPU_AUTH240_V2_PURPOSE_FROZEN.json').replace('CPU_AUTH240_ONCE_CONSUMED.json','CPU_AUTH240_V2_ONCE_CONSUMED.json').replace('CPU_AUTH240_ORIGINAL_ERROR.json','CPU_AUTH240_V2_ORIGINAL_ERROR.json')
 s=s.replace("'derive_authority240_source.py'","'derive_auth240_saved_launch_gpu_v2.py'").replace("'check_auth240_new_JSON_AST_once.py'","'check_auth240_new_JSON_AST_v2_once.py'")
 a="assert launch['owner']==binding['owner']==c.EXPECTED_OWNER and state['current']['go']==binding['go']==c.EXPECTED_GO";assert s.count(a)==1
 s=s.replace(a,a+"\n public,pr=c.metadata(a/'ROOT240_ACTUAL_TASK_MANIFEST_READY_AND_PUBLIC_SCHEDULE.json')\n assert c.KNOWN_ACTIVE_GPU_UUID==launch['specs']['jump_72']['GPU_UUID']==public['schedule']['experts']['jump_72']['GPU_UUID'] and 'GPU_UUID' not in c.EXPECTED_GO['jump_72']")
 s=s.replace('actual_saved_metadata_refs=[lr,sr,br]','actual_saved_metadata_refs=[lr,sr,br,pr]')
 s=s.replace('whole_READY_CPU_SHA_not_model_CPU_SHA=True,','whole_READY_CPU_SHA_not_model_CPU_SHA=True,active_GPU_from_saved_launch_and_public_schedule_not_GO=True,')
 ast.parse(s)
 with (N/'check_auth240_new_JSON_AST_v2_once.py').open('x',encoding='utf8',newline='\n') as f:f.write(s)
 put(R/'V1_GPU_GO_READER_FALSE_AND_V2_SAVED_SPEC_FIX.json',dict(epoch=time.time(),V1_rejected_INDEX=ref(V1/'INDEX_AUTH240_V1_REJECTED_CPU_FROZEN.json'),
  V1_original_CPU_error=ref(V1/'reports/CPU_AUTH240_ORIGINAL_ERROR.json'),actual_launch=ref(A/'ROOT240_ORIGINAL_SOLO_OWNER_LAUNCH_ACTUAL.json'),
  actual_public_schedule=ref(A/'ROOT240_ACTUAL_TASK_MANIFEST_READY_AND_PUBLIC_SCHEDULE.json'),GPU_UUID=gpu,
  original_actual_GO_unchanged=True,GPU_not_added_to_GO=True,worker_geometry_reward_commands_clocks_unchanged=True,
  target_metadata_SDK_GPU_model_raw_SSH_GO_Git=0))
if __name__=='__main__':
 try:main()
 except BaseException:put(R/'DERIVE_AUTH240_V2_ORIGINAL_ERROR.json',dict(error=traceback.format_exc()));raise
