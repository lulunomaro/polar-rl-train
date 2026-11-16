"""Record independent sources/reports; keep tensor/video originals indexed."""
from pathlib import Path
import json,hashlib,sys,argparse,subprocess,datetime
T=Path(__file__).resolve().parent;R=T.parents[2]
def main():
 p=argparse.ArgumentParser();p.add_argument('--stage',required=True);p.add_argument('--note',default='HISTORY_AND_PLAN.md');a=p.parse_args();files=[];rows=[]
 for f in sorted(T.rglob('*')):
  if not f.is_file()or '__pycache__'in f.parts or f.name.startswith(('ARTIFACT_INDEX','ARCHIVE_FILES')):continue
  text=f.suffix.lower()in ['.py','.md','.json','.yaml','.xml','.log','.jsonl','.txt']and f.stat().st_size<5000000
  rows.append(dict(path=str(f),bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest(),git_text=text))
  if text:files.append(f.relative_to(R).as_posix())
 idx=T/('ARTIFACT_INDEX_'+a.stage+'.json');idx.write_text(json.dumps(dict(date=datetime.datetime.now().astimezone().isoformat(),artifacts=rows,large_originals_retained=True),indent=2)+'\n');files.append(idx.relative_to(R).as_posix());files.append('AGENTS.md')
 sys.path.insert(0,str(R/'archive_tools'));import record_experiment as rec
 orig=rec.git
 def git(*args):
  if args[:2]==('add','--'):
   for i in range(0,len(args[2:]),25):orig('add','-f','--sparse','--',*args[2:][i:i+25])
   return ''
  return orig(*args)
 rec.git=git
 sys.argv=['record_experiment','--id','mod4v3-history-fixed200-'+a.stage,'--title','MOD4v3 history fixed200 '+a.stage,'--kind','training','--note-file',str(T/a.note),'--validation','See real preflight/launch evidence; no default promotion; 7200s maximum','--files',*files]
 rec.main()
 tag='trial-'+datetime.datetime.now().strftime('%Y%m%d')+'-mod4v3-history-fixed200-'+a.stage
 net=['git','-C',str(R),'-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true']
 subprocess.run(net+['push','--atomic','origin','HEAD','refs/tags/'+tag],check=True)
 print(subprocess.check_output(net+['ls-remote','origin','refs/heads/main','refs/tags/'+tag,'refs/tags/'+tag+'^{}'],text=True))
if __name__=='__main__':main()
