"""Launch/collect one read-only native gradient probe after authorized PPO closes."""
from pathlib import Path
import sys,json,hashlib,shlex,time
T=Path(__file__).resolve().parent;E=T/'evidence';sys.path.insert(0,str(T));from remote_run import connect,execute,P,REMOTE
assert (E/'training/SAFE_CLOSED.json').exists(),'PPO must release the GPU first'
final=json.loads((E/'training/FINAL.json').read_text());G=T/'tmp/gradient_audit';G.mkdir(parents=True,exist_ok=False);root=REMOTE+'/gradient_audit';p=json.loads(json.dumps(P));p.update(root=root,parent=final['checkpoint']['path'],root_parent=final['checkpoint']['path'],parent_sha256=final['checkpoint']['SHA']);p['training_round']['seconds']=0;p['gradient_audit_scope']='No optimizer updates; native gradient backward only; weights must remain identical'
(G/'PLAN.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf8');s=(T/'launch.py').read_text(encoding='utf8');s=s.replace("'-m','mod4v3_ppo_v1.continuous_stair_train'","str(T/'gradient_probe_entry.py')").replace("cwd=T/'support'","cwd=Path(plan['support'])")
(G/'launch.py').write_text(s,encoding='utf8')
c=connect()
try:
 sf=c.open_sftp();sf.mkdir(root)
 for source,name in [(G/'PLAN.json','PLAN.json'),(G/'launch.py','launch.py'),(T/'gradient_probe_entry.py','gradient_probe_entry.py')]:sf.put(str(source),root+'/'+name)
 code="from pathlib import Path;import hashlib;assert hashlib.sha256(Path("+repr(p['parent'])+").read_bytes()).hexdigest()=="+repr(p['parent_sha256'])+";print('Final frozen parent verified')";print(execute(c,P['python']+' -B -c '+shlex.quote(code)),flush=True)
 receipt=json.loads(execute(c,P['python']+' -B '+shlex.quote(root+'/launch.py')+' probe_gradient --kind probe --num-envs 2048'));(G/'LAUNCH.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8');print('ZERO_UPDATE_PROBE_LAUNCHED '+json.dumps(receipt),flush=True)
finally:c.close()
start=time.time();seen={}
while True:
 c=connect()
 try:
  sf=c.open_sftp()
  try:entries=sf.listdir_attr(root+'/probe_gradient')
  except FileNotFoundError:entries=[]
  for item in entries:
   if not item.filename.endswith(('.json','.py')) or seen.get(item.filename)==(item.st_mtime,item.st_size):continue
   sf.get(root+'/probe_gradient/'+item.filename,str(G/item.filename));seen[item.filename]=(item.st_mtime,item.st_size)
  sf.get(root+'/probe_gradient.log',str(G/'owner.log'))
 finally:c.close()
 if (G/'ERROR.json').exists():raise RuntimeError((G/'ERROR.json').read_text())
 if (G/'SAFE_CLOSED.json').exists():break
 if time.time()-start>900:raise TimeoutError('Gradient probe not closed; retain raw evidence')
 time.sleep(10)
d=json.loads((G/'ROUGH_PROBE.json').read_text());assert d['actual_optimizer_steps']==0 and d['parameters_unchanged']
__import__('shutil').copytree(G,E/'gradient_audit')
(E/'GRADIENT_AUDIT.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print('GRADIENT_AUDIT_COMPLETE '+json.dumps(d['mean']),flush=True)
