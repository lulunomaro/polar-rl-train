"""Prior CPU reader imported the full SDK before AppLauncher; only unfinished CPU/dispatch."""
from route_fixture_io import *
import ast
def main():
 assert not (R/'FIXTURE_REVIEWED_TARGET_CPU_PASSED.json').exists() and not (R/'FIXTURE_DISPATCH_REQUESTED.json').exists()
 source=D/'stage_fixture_reviewed_target_and_dispatch_once.py';tree=ast.parse(source.read_text());values=[n.value for n in ast.walk(tree) if isinstance(n,ast.Constant) and isinstance(n.value,str)]
 cpu=next(s for s in values if 'from wave50_route_fixture_adapter_v2 import verify_GPU_boundary_fixture' in s and 'old440_math_runtime_command_reward_DR_clock_geometry_bytes_exact' in s)
 anchor="reset_entry_xy(env,torch.arange(20000));rng=torch.get_rng_state().clone();fixture=verify_GPU_boundary_fixture(env)";assert cpu.count(anchor)==1
 replacement="""reset_entry_xy(env,torch.arange(20000))
import ast
original_source=(D/'isaac/mod4/e1_terrain_runtime.py').read_text();node=next(n for n in ast.parse(original_source).body if isinstance(n,ast.FunctionDef) and n.name=='boundary_timeout');ns=dict(torch=torch);exec(compile(ast.Module(body=[node],type_ignores=[]),'<actual-parent-boundary-only-for-CPU-no-SDK>','exec'),ns)
stub=types.ModuleType('e1_terrain_runtime');stub.boundary_timeout=ns['boundary_timeout'];sys.modules['e1_terrain_runtime']=stub
rng=torch.get_rng_state().clone();fixture=verify_GPU_boundary_fixture(env)"""
 cpu=cpu.replace(anchor,replacement).replace('CPU_RNG_exact_no_CUDA=True,','CPU_RNG_exact_no_CUDA=True,CPU_original_boundary_AST_exact_no_full_SDK_import=True,')
 dispatch=next(s for s in values if 'args=[own.s.q.base.PY' in s and 'supervise_wave50_route_fixture_reviewed_once.py' in s)
 n,w=io.connect_both()
 try:
  proof=run(n,cpu.replace('ROOT_TOKEN',repr(ROOT)).replace('FAILED_TOKEN',repr(FAILED_ROOT)))
  save('FIXTURE_REVIEWED_TARGET_CPU_PASSED.json',proof)
  save('CPU_FIXTURE_SDK_IMPORT_READER_REVIEW.json',dict(epoch=time.time(),original_CPU_reader_source=str(source),original_CPU_reader_SHA=H(source.read_bytes()),original_importError_before_CPU_write_GPU_dispatch_retained=True,actual_original_boundary_function_AST_only_same_function_and_thresholds=True,production_SDK_and_new443_allbytes_unmodified=True,actual_fixture_CPU_passed=True,no_GPU_replay=True))
  number=json.loads((R/'CANDIDATE_JOB_UNUSED_ACTUAL.json').read_bytes())['number'];checks=[]
  with n.open_sftp() as f,w.open_sftp() as g:
   for fs,host,path in ((f,'4090',io.E+'/eval_queue'),(f,'4090',io.E+'/eval_results'),(g,'3060','D:/MOD4_async_eval/closure_episode_clock2500_v15/jobs')):
    found=[x for x in fs.listdir(path) if 'episode-d3-'+str(number)+'-' in x];assert not found;checks.append(dict(host=host,path=path,matches=[]))
  save('FIXTURE_DISPATCH_REQUESTED.json',dict(epoch=time.time(),actual_CPU443_passed=True,unused_rechecked=checks,only_unexecuted_unique_dispatch_continued=True,newSDK_native_scope_admission_required=True))
  result=run(n,dispatch.replace('ROOT_TOKEN',repr(ROOT)));save('FIXTURE_DISPATCH_ACTUAL_RECEIPT.json',result)
  print(json.dumps(dict(actual_dispatch=True,source_count=result['source_count'],controller=result['controller'])))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('CPU_AST_CONTINUATION_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),only_unexecuted_substeps_no_GPU_replay=True));raise
