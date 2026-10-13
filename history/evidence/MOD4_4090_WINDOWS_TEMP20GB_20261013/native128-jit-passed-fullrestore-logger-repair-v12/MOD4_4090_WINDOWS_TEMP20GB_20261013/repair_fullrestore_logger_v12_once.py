from pathlib import Path
import json,time,sys,traceback
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent/'MOD4_4090_WINDOWS_REPAIR_20261013'))
from windows4090_native_transport import connect,powershell,upload
R='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013';OLD=R+'/temporary_scope128_memory20GB_COM_jit_v11_20261013';NEW=R+'/temporary_scope128_memory20GB_logger_ready_v12_20261013'
def main():
 receipt=D/'reports/LOGGER_V12_CPU_DISPATCH_ACTUAL.json';assert not receipt.exists()
 code="""from pathlib import Path;import json,hashlib,time,psutil,msvcrt,shutil,ast
r=Path('"""+R+"""');old=Path('"""+OLD+"""');new=Path('"""+NEW+"""')
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=H(p))
x=json.loads((old/'attempts/temporary2048_fullrestore_v1/EXIT_RECEIPT.json').read_bytes());e=json.loads((old/'attempts/temporary2048_fullrestore_v1/output/ORIGINAL_ERROR.json').read_bytes());assert x['worker_exitcode']==1 and x['no_PPO'] and "'Logger' object has no attribute 'writer'" in e['error'] and x['own_child_and_descendants_actual_absent']
for row in (x['parent'],x['child']):
 try:p=psutil.Process(row['pid']);assert p.create_time()!=row['created']
 except psutil.NoSuchProcess:pass
with (r/'WINDOWS4090_GPU_EXCLUSIVE.lock').open('r+b') as f:f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1);f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
native=old/'attempts/temporary2048_native_v1/EXIT_RECEIPT.json';nx=json.loads(native.read_bytes());assert nx['passed'] and nx['worker_exitcode']==0 and nx['no_PPO']
nc=old/'attempts/temporary2048_native_v1/output/PROBE_COMPLETE.json';n=json.loads(nc.read_bytes());assert n['passed'] and n['actual_callbacks']==576
assert not new.exists();new.mkdir();shutil.copytree(old/'runtime2048',new/'runtime2048');shutil.copytree(old/'payload',new/'payload');(new/'reports').mkdir();(new/'attempts').mkdir()
p=new/'payload/temporary_training_runtime.py';before=ref(p);s=p.read_text(encoding='utf8');anchor="    if args.mode == 'fullrestore':";assert s.count(anchor)==1
s=s.replace(anchor,anchor+"\\n        runner.logger.init_logging_writer()\\n        assert hasattr(runner.logger,'writer')")
anchor="        return\\n    assert args.mode == 'train'";assert s.count(anchor)==1
s=s.replace(anchor,"        runner.logger.stop_logging_writer()\\n        if runner.logger.writer is not None and runner.logger.logger_type == 'tensorboard':\\n            runner.logger.writer.flush()\\n            runner.logger.writer.close()\\n"+anchor)
p.write_text(s,encoding='utf8');compile(s,str(p),'exec')
q=new/'payload/temporary_parent.py';ps=q.read_text(encoding='utf8');assert "('native', 'fullrestore', 'train')" in ps;ps=ps.replace("('native', 'fullrestore', 'train')","('fullrestore', 'train')");q.write_text(ps,encoding='utf8');compile(ps,str(q),'exec')
import torch;assert not torch.cuda.is_initialized()
from rsl_rl.utils.logger import Logger
assert hasattr(Logger,'init_logging_writer')
mf=json.loads((old/'TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json').read_bytes());mf.update(scope_root=str(new),epoch=time.time(),new_fullrestore_logger_initialization_only=dict(old=before,new=ref(p),public_RSL_init_logging_writer_before_noPPO_save=True,normal_PPO_learn_initialization_unchanged=True,old_partial_save_not_complete_source=True),reused_native128_actual=dict(EXIT=ref(native),complete=ref(nc),original_false_save_error_retained=ref(old/'attempts/temporary2048_fullrestore_v1/output/ORIGINAL_ERROR.json')))
cpu=json.loads(Path(mf['target_CPU_receipt']['path']).read_bytes());cpu.update(scope=str(new),epoch=time.time(),logger_API_CPU_import_passed=True);cp=new/'reports/TARGET_TEMP128_LOGGER_CPU_ACTUAL.json';cp.write_text(json.dumps(cpu,indent=2),encoding='utf8');mf['target_CPU_receipt']=ref(cp)
mf['sourcefreeze_files']=[ref(p) for base in (new/'runtime2048',new/'payload',r/'sdk_exact/source',r/'sdk_exact/apps') for p in sorted(base.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and '.egg-info' not in str(p)]
f=new/'TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json';f.write_text(json.dumps(mf,indent=2),encoding='utf8');l=new/'TEMPORARY_SEQUENCE_TASK_LEASE_GRANTED.json';l.write_text(json.dumps(dict(epoch=time.time(),case_id='temporary128_memory20GB_logger_ready_sequence_v12',approved_GPU_scope=True,mode='fullrestore',scope_root=str(new),environment_root=str(r),shared_gpu_lock=str(r/'WINDOWS4090_GPU_EXCLUSIVE.lock'),manifest_sha256=H(f),human20GB_temporary_branch_authorized=True),indent=2),encoding='utf8')
proof=dict(epoch=time.time(),passed_CPU_only=True,old_error=e,old_EXIT=x,native_actual_reused=mf['reused_native128_actual'],logger_fix=mf['new_fullrestore_logger_initialization_only'],new_manifest=ref(f),old_sources_partialsave_false_retained=True,no_PPO_claimed=True)
(new/'reports/LOGGER_API_CPU_ACTUAL.json').write_text(json.dumps(proof,indent=2),encoding='utf8');print(json.dumps(proof))
"""
 f=D/'logger_v12_cpu.py';assert not f.exists();f.write_text(code,encoding='utf8');compile(code,str(f),'exec');upload(f,R+'/'+f.name,60)
 actual=json.loads(powershell(connect(),"[Console]::OutputEncoding=[Text.Encoding]::UTF8;& '"+R+"/env/python.exe' '"+R+'/'+f.name+"'",90))
 ps="& '"+NEW+"/payload/register_windows4090_demand_task_audited_v6_once.ps1' -LeasePath '"+NEW+"/TEMPORARY_SEQUENCE_TASK_LEASE_GRANTED.json' -ManifestPath '"+NEW+"/TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json' -AttemptPath '"+NEW+"/attempts/temporary2048_fullrestore_v1' -PythonPath '"+R+"/env/python.exe' -RuntimePath '"+NEW+"/runtime2048' -StageMode fullrestore -TrainSeconds 3600 -StartApprovedLease"
 powershell(connect(),ps,35);receipt.write_text(json.dumps(dict(epoch=time.time(),actual=actual,new_fullrestore_requested_once=True,passedSDK10_native128_exact_reused=True,old_scope_not_replayed_or_hotpatched=True),indent=2),encoding='utf8');print(str(receipt))
if __name__=='__main__':
 try:main()
 except BaseException:
  (D/'reports'/('LOGGER_V12_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),inspect_before_any_continuation=True),indent=2),encoding='utf8');raise
