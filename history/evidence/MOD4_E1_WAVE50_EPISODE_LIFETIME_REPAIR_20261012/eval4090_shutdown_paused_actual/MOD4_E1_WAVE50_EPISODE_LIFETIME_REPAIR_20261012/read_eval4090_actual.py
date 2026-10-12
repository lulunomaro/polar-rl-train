from pathlib import Path
import os,json,time,traceback
import stage_lifetime_target_CPU_once as io
ROOT='/home/egde/rl_candidates/MOD4_WAVE50_EVAL4090_FROZEN_20261012'
def main():
 n,w=io.connect_linux_only()
 try:
  v=io.run(n,r'''from pathlib import Path
import json,time,subprocess,hashlib
D=Path(ROOT_TOKEN);R=D/'reports';j=lambda p:json.loads(p.read_bytes());out={p.name:j(p) for p in R.glob('*.json')};results={p.parent.name:j(p) for p in (D/'jobs').glob('*/result.json')};logs=[]
for p in (D/'jobs').glob('*/probe.log'):
 b=p.read_bytes();logs.append(dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),tail=b[-3000:].decode('utf8','replace')))
print(json.dumps(dict(epoch=time.time(),root=str(D),reports=out,results=results,logs=logs,GPU=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,memory.used,memory.total','--format=csv,noheader,nounits']).decode(),GPU_processes=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name,used_memory','--format=csv,noheader,nounits']).decode(),no_GPU_or_training_write_by_reader=True)))
'''.replace('ROOT_TOKEN',repr(ROOT)))
  p=io.save('EVAL4090_ACTUAL_'+str(time.time_ns())+'.json',v);print(json.dumps(dict(report=str(p),current=v['reports'].get('EVAL_CURRENT.json'),attention=v['reports'].get('EVAL_ATTENTION.json'),completed=list(v['results']),GPU=v['GPU'],processes=v['GPU_processes'],last_log=v['logs'][-1]['tail'][-1800:] if v['logs'] else None)))
 finally:n.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
 try:main()
 except BaseException:io.save('EVAL4090_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU=True));raise
