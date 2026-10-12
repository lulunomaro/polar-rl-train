from route_second_io import *

def main():
    n,w=io.connect_both()
    try:
      v=run(n,r'''import subprocess,json,time
from pathlib import Path
cmds=[['nvidia-smi','--query-gpu=name,memory.total,memory.used,memory.free,utilization.gpu','--format=csv,noheader,nounits'],['nvidia-smi','--query-compute-apps=pid,process_name,used_gpu_memory','--format=csv,noheader,nounits']]
rows=[]
for c in cmds:
 r=subprocess.run(c,capture_output=True,text=True);rows.append(dict(command=c,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
p=Path('/proc/3340979');print(json.dumps(dict(epoch=time.time(),GPU=rows,meminfo=Path('/proc/meminfo').read_text(),child_status=(p/'status').read_text() if p.exists() else None,child_limits=(p/'limits').read_text() if p.exists() else None,no_GPU_process_signal_or_budget_write=True)))
''')
      save('FAILED_SECOND_GPU_MEMORY_ACTUAL_'+str(time.time_ns())+'.json',v);print(json.dumps(v))
    finally:io.cleanup(n,w)

if __name__=='__main__':
    try:main()
    except BaseException:save('FAILED_RESOURCE_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),observer_only_no_GPU_signal=True));raise
