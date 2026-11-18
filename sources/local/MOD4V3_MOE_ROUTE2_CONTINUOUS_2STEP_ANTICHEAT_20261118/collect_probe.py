from pathlib import Path
import argparse,json,hashlib,shlex,stat,sys
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T));from remote_run import connect,execute,P,REMOTE
p=argparse.ArgumentParser();p.add_argument('job');args=p.parse_args();target=T/'evidence'/args.job;target.mkdir(exist_ok=True)
c=connect()
try:
 sf=c.open_sftp();todo=[(REMOTE+'/'+args.job,target)];files=[]
 while todo:
  remote,local=todo.pop();local.mkdir(exist_ok=True)
  for item in sf.listdir_attr(remote):
   src=remote+'/'+item.filename;dst=local/item.filename
   if stat.S_ISDIR(item.st_mode):
    if item.filename in ['kit_isolation']:continue
    todo.append((src,dst))
   elif dst.suffix in ['.json','.npz']:
    pending=dst.with_name(dst.name+'.partial');sf.get(src,str(pending));pending.replace(dst);files.append((src,dst))
 log=REMOTE+'/'+args.job+'.log';sf.get(log,str(target/'stdout.log'));sf.close()
 manifest={f.relative_to(target).as_posix():hashlib.sha256(f.read_bytes()).hexdigest()for _,f in files}
 code="from pathlib import Path;import hashlib,json;r=Path("+repr(REMOTE+'/'+args.job)+");h="+repr(manifest)+";assert all(hashlib.sha256((r/k).read_bytes()).hexdigest()==v for k,v in h.items());print(json.dumps(dict(verified=True,files=len(h))))"
 verified=json.loads(execute(c,P['python']+' -B -c '+shlex.quote(code)));(target/'DOWNLOAD_VERIFICATION.json').write_text(json.dumps(dict(**verified,sha256=manifest),indent=2)+'\n',encoding='utf8');print(json.dumps(verified))
 if(target/'ROUTE2_NATIVE_PREFLIGHT.json').exists():
  d=json.loads((target/'ROUTE2_NATIVE_PREFLIGHT.json').read_text(encoding='utf8'));sd=d['startup_diagnostics'];sd={k:v for k,v in sd.items()if k!='rows'}
  print(json.dumps(dict(passed=d['passed'],success_replay=d.get('success_replay'),dense_reward_ledger=d.get('dense_reward_ledger'),startup=sd,PPO_updates=d['PPO_updates'],optimizer_updates=d['optimizer_updates']),ensure_ascii=False))
finally:c.close()
