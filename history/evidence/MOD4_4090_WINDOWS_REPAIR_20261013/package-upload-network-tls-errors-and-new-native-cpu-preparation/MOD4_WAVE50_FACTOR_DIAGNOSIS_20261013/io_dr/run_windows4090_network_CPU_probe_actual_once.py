from pathlib import Path
import sys,json,time,hashlib,traceback
W=Path('C:/Users/lulu/Desktop/claude/mjcf');F=W/'MOD4_WAVE50_FACTOR_DIAGNOSIS_20261013/io_dr';sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'))
from windows4090_native_transport import connect,powershell,upload
ROOT='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013';f=F/'windows4090_install_network_cpu_probe_v1.py';c=connect();p=F/('WINDOWS4090_PACKAGE_NETWORK_CPU_ACTUAL_'+str(time.time_ns())+'.json');r=dict(epoch=time.time(),source=dict(path=str(f),bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()),no_GPU_or_install_or_OS_network_mutation=True)
try:
 upload(str(f),ROOT+'/'+f.name,timeout=45)
 raw=powershell(c,r"""$OutputEncoding=[Console]::OutputEncoding=[Text.UTF8Encoding]::new();& 'D:\anaconda\python.exe' 'C:\Users\Win10\Documents\MOD4_WAVE50_WINDOWS_4090_20261013\windows4090_install_network_cpu_probe_v1.py'""",90)
 r['actual']=json.loads(raw);p.write_text(json.dumps(r,indent=2),encoding='utf8');print(json.dumps(dict(report=str(p),actual=r['actual']),ensure_ascii=True))
except BaseException:p.with_name(p.stem+'_ERROR.json').write_text(json.dumps(dict(error=traceback.format_exc(),no_GPU_or_OS_network_mutation=True),indent=2),encoding='utf8');raise
finally:c.close()
