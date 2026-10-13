from pathlib import Path
import json,sys,time,traceback
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent/'MOD4_4090_WINDOWS_REPAIR_20261013'))
from windows4090_native_transport import connect,powershell,upload
R='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013';OLD=R+'/temporary_scope128_memory20GB_COM_repr_v10_20261013';NEW=R+'/temporary_scope128_memory20GB_COM_jit_v11_20261013'
def main():
 receipt=D/'reports/COM_JIT_V11_UNEXECUTED_CPU_CONTINUATION_ACTUAL.json';assert not receipt.exists()
 oldcode=(D/'COM_jit_v11_cpu.py').read_text(encoding='utf8');start=oldcode.index("p=new/'payload/windows4090_substep_readback_v6.py'")
 prefix="""from pathlib import Path;import json,hashlib,time,psutil,msvcrt
r=Path('"""+R+"""');old=Path('"""+OLD+"""');new=Path('"""+NEW+"""')
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=H(p))
assert new.is_dir() and not (new/'TEMPORARY_SEQUENCE_TASK_LEASE_GRANTED.json').exists() and not (new/'SEQUENCE_ONCE_CONSUMED.json').exists()
assert H(new/'payload/windows4090_substep_readback_v6.py')==H(old/'payload/windows4090_substep_readback_v6.py')
x=json.loads((old/'attempts/temporary2048_native_v1/EXIT_RECEIPT.json').read_bytes());e=json.loads((old/'attempts/temporary2048_native_v1/output/ORIGINAL_ERROR.json').read_bytes())
for row in (x['parent'],x['child']):
 try:p=psutil.Process(row['pid']);assert p.create_time()!=row['created']
 except psutil.NoSuchProcess:pass
with (r/'WINDOWS4090_GPU_EXCLUSIVE.lock').open('r+b') as f:f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1);f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
"""
 code=prefix+oldcode[start:].replace("s.index('    com_error=',start)","s.index('    com_error',start)")
 f=D/'COM_jit_v11_unexecuted_cpu.py';assert not f.exists();f.write_text(code,encoding='utf8');compile(code,str(f),'exec');upload(f,R+'/'+f.name,60)
 actual=json.loads(powershell(connect(),"[Console]::OutputEncoding=[Text.Encoding]::UTF8;& '"+R+"/env/python.exe' '"+R+'/'+f.name+"'",90))
 ps="& '"+NEW+"/payload/register_windows4090_demand_task_audited_v6_once.ps1' -LeasePath '"+NEW+"/TEMPORARY_SEQUENCE_TASK_LEASE_GRANTED.json' -ManifestPath '"+NEW+"/TEMPORARY_GPU_SEQUENCE_MANIFEST_GRANTED.json' -AttemptPath '"+NEW+"/attempts/temporary2048_native_v1' -PythonPath '"+R+"/env/python.exe' -RuntimePath '"+NEW+"/runtime2048' -StageMode native -TrainSeconds 3600 -StartApprovedLease"
 powershell(connect(),ps,35);receipt.write_text(json.dumps(dict(epoch=time.time(),actual=actual,only_unexecuted_CPU_continued=True,original_whitespace_anchor_error_retained=True,preSSH_Powershell_quote_error_no_remote_call=True,new_native_requested_once=True),indent=2),encoding='utf8');print(str(receipt))
if __name__=='__main__':
 try:main()
 except BaseException:
  (D/'reports'/('COM_JIT_V11_CONTINUATION_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),inspect_no_replay=True),indent=2),encoding='utf8');raise
