"""Pin public upstream code for evidence, never import or execute it."""
from pathlib import Path
import concurrent.futures,hashlib,json,time,urllib.request,traceback
D=Path(__file__).resolve().parent;R=D/'reports';S=D/'scut_source';R.mkdir(exist_ok=True);H=lambda b:hashlib.sha256(b).hexdigest()
API='https://api.github.com/repos/scutrobotlab/wheeled-legged_RL'
def get(url):
 req=urllib.request.Request(url,headers={'User-Agent':'MOD4-source-audit','Accept':'application/vnd.github+json'})
 with urllib.request.urlopen(req,timeout=30) as r:return r.read()
def main():
 meta=json.loads(get(API));branch=meta['default_branch'];commit=json.loads(get(API+'/commits/'+branch))['sha']
 tree=json.loads(get(API+'/git/trees/'+commit+'?recursive=1'));assert not tree['truncated']
 paths=[x['path'] for x in tree['tree'] if x['type']=='blob' and (x['path'].endswith('.py') and x['path'].startswith(('source/','scripts/rsl_rl/')) or x['path']=='README.md' or x['path'].endswith(('params/env.yaml','params/agent.yaml')))]
 def fetch(p):
  url='https://raw.githubusercontent.com/scutrobotlab/wheeled-legged_RL/'+commit+'/'+p;b=get(url);out=S/p;out.parent.mkdir(parents=True,exist_ok=True)
  if out.exists():assert out.read_bytes()==b
  else:out.write_bytes(b)
  return dict(path=p,url=url,bytes=len(b),sha256=H(b),local=str(out.resolve()))
 rows=[];errors=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
  futures={pool.submit(fetch,p):p for p in paths}
  for f in concurrent.futures.as_completed(futures):
   try:rows.append(f.result())
   except Exception:errors.append(dict(path=futures[f],error=traceback.format_exc()))
 v=dict(epoch=time.time(),trial_id='SCUT-EXPERT-RETENTION-SOURCE-AUDIT-01',repository=meta['html_url'],default_branch=branch,commit=commit,previous_pin='b8ff79f3df855faf9dc92f4a282bd80c42649466',tree_sha256=H(json.dumps(tree,sort_keys=True).encode()),tree_count=len(tree['tree']),paths_considered=len(paths),files=sorted(rows,key=lambda x:x['path']),errors=errors,public_source_only=True,no_downloaded_code_executed=True,no_PPO_or_budget_mutation=True)
 p=R/('SCUT_SOURCE_AUDIT_'+str(int(v['epoch']))+'.json');p.write_bytes(json.dumps(v,indent=2).encode());print(json.dumps(dict(report=str(p),commit=commit,files=len(rows),errors=[e['path'] for e in errors])))
if __name__=='__main__':main()
