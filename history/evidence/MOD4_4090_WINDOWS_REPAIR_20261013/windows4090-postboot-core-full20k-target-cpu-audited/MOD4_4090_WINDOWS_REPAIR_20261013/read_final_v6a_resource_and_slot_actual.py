from pathlib import Path
import base64,json,time,traceback
from windows4090_native_transport import connect,powershell
D=Path(__file__).resolve().parent
R='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013'
def main():
    code="""from pathlib import Path
import json,time,psutil,subprocess,msvcrt
r=Path('"""+R+"""');guard=r/'WINDOWS4090_GPU_EXCLUSIVE.lock';lock='not_created_yet'
if guard.exists():
 try:
  with guard.open('r+b') as f:
   f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1);lock='free_actual_native_OS_test'
 except PermissionError:lock='held_actual_native_OS_test'
gpu=subprocess.run(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits','-i','0'],capture_output=True,text=True,check=True).stdout.strip()
rows=[]
for p in psutil.process_iter(['pid','name','create_time','cmdline','memory_info']):
 try:
  name=(p.info['name'] or '').lower();args=p.info['cmdline'] or []
  if name.startswith(('python','kit')) or 'matlab' in name:rows.append(dict(pid=p.pid,name=name,created=p.info['create_time'],argv=args,RSS_bytes=p.info['memory_info'].rss))
 except (psutil.Error,TypeError):pass
print(json.dumps(dict(epoch=time.time(),actual_available_RAM_bytes=psutil.virtual_memory().available,actual_total_RAM_bytes=psutil.virtual_memory().total,GPU_free_bytes=int(gpu)*1024**2,shared_OSlock=lock,actual_processes=rows,no_process_signals_or_GPU_context_started=True)))
"""
    b=base64.b64encode(code.encode()).decode();s=connect()
    a=json.loads(powershell(s,"$OutputEncoding=[Console]::OutputEncoding=[Text.UTF8Encoding]::new();& '"+R+"/env/python.exe' -c \"import base64;exec(base64.b64decode('"+b+"'))\"",timeout=45))
    a['required_RAM_bytes']=50042386944;a['RAM_deficit_bytes']=max(0,a['required_RAM_bytes']-a['actual_available_RAM_bytes'])
    a['full20k_RAM_admitted']=a['RAM_deficit_bytes']==0
    out=D/'reports'/('V6A_FINAL_LIVE_RESOURCE_SLOT_ACTUAL_'+str(time.time_ns())+'.json')
    out.write_text(json.dumps(a,indent=2),encoding='utf8')
    print(json.dumps(dict(report=str(out),RAM=a['actual_available_RAM_bytes'],RAM_required=a['required_RAM_bytes'],deficit=a['RAM_deficit_bytes'],GPU_free=a['GPU_free_bytes'],OSlock=a['shared_OSlock'],our_task_GPU_started=False)))
if __name__=='__main__':main()
