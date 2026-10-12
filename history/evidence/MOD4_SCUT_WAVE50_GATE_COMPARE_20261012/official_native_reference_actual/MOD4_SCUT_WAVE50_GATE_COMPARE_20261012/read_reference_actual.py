"""Read this reference's actual progress, errors and results without replay."""
from scut_wave_io import *

def main():
    w=connect()
    try:
        v=execute(w,r'''from pathlib import Path
import json,time,hashlib,subprocess,base64
D=Path(ROOT_TOKEN);h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();reports={}
for p in D.glob('*.json'):
 if p.name!='FIXTURE.json':reports[p.name]=json.loads(p.read_bytes())
runs={}
for p in (D/'runs').glob('*'):
 if not p.is_dir():continue
 rows={}
 for q in p.glob('*.json'):rows[q.name]=json.loads(q.read_bytes())
 logs={q.name:dict(bytes=q.stat().st_size,sha256=h(q),tail=q.read_bytes()[-3500:].decode('utf8','replace')) for q in p.glob('*.log')}
 errors={q.name:q.read_text(encoding='utf8') for q in p.glob('*.error.txt')};runs[p.name]=dict(reports=rows,logs=logs,errors=errors)
ps="[pscustomobject]@{processes=@(Get-CimInstance Win32_Process|Where-Object {$_.Name -like 'python*' -and $_.CommandLine -like '*scut_wave50_gate_compare_20261012*'}|Select-Object ProcessId,ParentProcessId,CommandLine,@{n='creation_epoch';e={([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds()/1000}})}|ConvertTo-Json -Depth 5 -Compress"
r=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-EncodedCommand',base64.b64encode(ps.encode('utf-16le')).decode()],capture_output=True,text=True,encoding='utf8',errors='replace',creationflags=0x08000000);assert r.returncode==0
print(json.dumps(dict(epoch=time.time(),root=str(D),reports=reports,runs=runs,actual_processes=json.loads(r.stdout)['processes'],coordinator_log_tail=(D/'coordinator.log').read_bytes()[-2000:].decode('utf8','replace') if (D/'coordinator.log').exists() else None,no_GPU_worker_or_budget_mutation=True)))
'''.replace('ROOT_TOKEN',repr(REMOTE)))
        p=save('SCUT_REFERENCE_ACTUAL_'+str(time.time_ns())+'.json',v)
        print(json.dumps(dict(path=str(p),attention=v['reports'].get('REFERENCE_ATTENTION.json'),waiting=v['reports'].get('WAITING_FOR_OWNED_SLOT.json'),lock_acquired='SHARED_GPU_LOCK_ACTUAL_ACQUIRED.json' in v['reports'],allcomplete='REFERENCE_ALL_COMPLETE.json' in v['reports'],runs={n:dict(progress=x['reports'].get('PROGRESS.json'),result=x['reports'].get('RESULT.json'),errors=x['errors'],logs=x['logs']) for n,x in v['runs'].items()},actual_processes=v['actual_processes'])))
    finally:w.close()

if __name__=='__main__':
    try:main()
    except BaseException:save('SCUT_REFERENCE_ACTUAL_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),read_only=True));raise
