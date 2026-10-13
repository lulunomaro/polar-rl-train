from pathlib import Path
import sys,json
from remote_session import execute
from deploy_linux_runtime_cpu_once import S
D=Path(__file__).resolve().parent
def main():
    text=r'''
from pathlib import Path
import json,os,time
R=Path(S);rows={};logs={};procs=[]
for p in [R/'DISPATCH_RECEIPT.json',R/'CURRENT_STAGE.json',R/'ORIGINAL_PARENT_ERROR.json',R/'SAVED_REVIEW_READY.json']:
 if p.is_file():rows[str(p.relative_to(R))]=json.loads(p.read_bytes())
for a in (R/'attempts').glob('*') if (R/'attempts').is_dir() else []:
 for p in [a/'GUARDIAN_CURRENT.json',a/'EXIT_RECEIPT.json',a/'INDEPENDENT_STAGE_PASSED.json']+list((a/'output').glob('ORIGINAL_ERROR.json'))+list((a/'output').glob('LINUX4090_LATEST_COMPLETE.json'))+list((a/'output').glob('PROBE_PROGRESS.json')):
  if p.is_file():rows[str(p.relative_to(R))]=json.loads(p.read_bytes())
 log=a/'worker_stdout.log'
 if log.is_file():
  with log.open('rb') as f:f.seek(max(0,log.stat().st_size-2200));logs[str(log.relative_to(R))]=f.read().decode(errors='replace')
log=R/'parent_stdout.log'
if log.is_file():logs['parent_stdout.log']=log.read_bytes()[-2200:].decode(errors='replace')
for p in Path('/proc').iterdir():
 if not p.name.isdigit():continue
 try:
  argv=(p/'cmdline').read_bytes().replace(b'\0',b' ').decode()
  if S not in argv:continue
  tail=(p/'stat').read_text().split(') ',1)[1].split();procs.append(dict(pid=int(p.name),argv=argv,start_ticks=int(tail[19]),state=tail[0]))
 except (OSError,UnicodeError):pass
print(json.dumps(dict(epoch=time.time(),rows=rows,logs=logs,processes=procs),ensure_ascii=False))
'''
    r,p=execute('S='+repr(S)+'\n'+text,'LINUX_FULLSCALE_ACTUAL_OBSERVATION')
    print(json.dumps(dict(report=str(p),processes=[dict(pid=x['pid'],state=x['state']) for x in r['processes']],current=r['rows'].get('CURRENT_STAGE.json'),errors={k:v for k,v in r['rows'].items() if 'ERROR' in k},latest={k:v for k,v in r['rows'].items() if 'LATEST' in k},log_tails=r['logs']),ensure_ascii=False))
if __name__=='__main__':main()
