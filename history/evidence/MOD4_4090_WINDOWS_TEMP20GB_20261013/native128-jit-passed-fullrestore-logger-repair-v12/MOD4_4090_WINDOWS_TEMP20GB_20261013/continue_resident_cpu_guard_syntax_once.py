"""Only unexecuted v8 parent/manifest after preTask source-pattern assertion."""
from pathlib import Path
import json,time,sys,hashlib,traceback
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent/'MOD4_4090_WINDOWS_REPAIR_20261013'))
from windows4090_native_transport import connect,powershell,upload
R='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013';OLD=R+'/temporary_scope512_memory20GB_native_capacity_v7_20261013';NEW=R+'/temporary_scope512_memory20GB_resident_bound_v8_20261013'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 receipt=D/'reports/RESIDENT_CPU_GUARD_PATTERN_CONTINUED_ACTUAL.json';assert not receipt.exists()
 original=(D/'resident_memory_semantics_v8_cpu.py').read_text(encoding='utf8');anchor="p=new/'payload/temporary_parent.py';oldparent=ref(p);s=p.read_text(encoding='utf8')";assert original.count(anchor)==1
 suffix=original[original.index(anchor):]
 suffix=suffix.replace("needle='peakhard + 512 * 256 * 24 * 16 * 4 + 1073741824 + 33554432 < 18000000000'","needle='peakhard + 512*256*24*16*4 + 1073741824 + 33554432 < 18000000000'")
 code="""from pathlib import Path;import json,hashlib,psutil,msvcrt,time
r=Path('"""+R+"""');old=Path('"""+OLD+"""');new=Path('"""+NEW+"""')
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=H(p))
assert new.is_dir() and not (new/'TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json').exists() and not (new/'SEQUENCE_ONCE_CONSUMED.json').exists()
assert H(new/'payload/temporary_parent.py')==H(old/'payload/temporary_parent.py')
assert 'hard_resident_limit' in (new/'payload/temporary_memory_job.py').read_text(encoding='utf8')
before=ref(old/'payload/temporary_memory_job.py');x=json.loads((old/'attempts/temporary2048_native_v1/EXIT_RECEIPT.json').read_bytes());e=json.loads((old/'attempts/temporary2048_native_v1/output/ORIGINAL_ERROR.json').read_bytes());assert x['no_PPO'] and x['own_child_and_descendants_actual_absent']
with (r/'WINDOWS4090_GPU_EXCLUSIVE.lock').open('r+b') as f:f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1);f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
"""+suffix
 f=D/'resident_guard_exact_whitespace_continuation_cpu.py';assert not f.exists();f.write_text(code,encoding='utf8');compile(code,str(f),'exec');remote=R+'/'+f.name;upload(f,remote,60)
 actual=json.loads(powershell(connect(),"[Console]::OutputEncoding=[Text.Encoding]::UTF8;& '"+R+"/env/python.exe' '"+remote+"'",90))
 ps="& '"+NEW+"/payload/register_windows4090_demand_task_audited_v6_once.ps1' -LeasePath '"+NEW+"/TEMPORARY_SEQUENCE_TASK_LEASE_GRANTED.json' -ManifestPath '"+NEW+"/TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json' -AttemptPath '"+NEW+"/attempts/temporary2048_native_v1' -PythonPath '"+R+"/env/python.exe' -RuntimePath '"+NEW+"/runtime2048' -StageMode native -TrainSeconds 3600 -StartApprovedLease"
 powershell(connect(),ps,35);receipt.write_text(json.dumps(dict(epoch=time.time(),actual=actual,original_preCPU_pattern_error_preserved=True,only_unexecuted_CPU_steps_continued=True,new_native_task_started_once=True),indent=2),encoding='utf8');print(json.dumps(dict(report=str(receipt),new_scope=NEW,newN512_native_requested=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  (D/'reports'/('RESIDENT_PATTERN_CONTINUATION_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),inspect_no_replay=True),indent=2),encoding='utf8');raise
