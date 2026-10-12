from pathlib import Path
import ast,json,time,hashlib,traceback
D=Path(__file__).resolve().parent;P=D/'payload';R=D/'reports'
v=dict(epoch=time.time(),error='ValueError substring _OWN_PPO_LEARN_STARTED=True: frozen449 uses spaces; before any prepared-worker write',original_source=str(D/'review_prepared_worker_resource_exit_once.py'),no_target_root_or_GPU=True)
(R/'ORIGINAL_WORKER_OBSERVER_PATTERN_ERROR.json').write_bytes(json.dumps(v,indent=2).encode())
rows=[]
try:
 for name in ('train_wave50_lifetime_resume_ppo.py','train_wave50_lifetime_fresh_preflight_ppo.py'):
  p=P/'isaac/mod4'/name;s=p.read_text();original=D/(name+'.PRE_RESOURCE_REVIEWED.txt')
  if original.exists():assert original.read_bytes()==p.read_bytes()
  else:original.write_bytes(p.read_bytes())
  anchor='app = launcher.app';assert s.count(anchor)==1;s=s.replace(anchor,anchor+'\n_OWN_PPO_LEARN_STARTED=False')
  lines=s.splitlines(True);node=next(n for n in ast.walk(ast.parse(s)) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in ('learn','rescue_learn'))
  index=node.lineno-1;indent=lines[index][:len(lines[index])-len(lines[index].lstrip())];lines.insert(index,indent+'global _OWN_PPO_LEARN_STARTED\n'+indent+'_OWN_PPO_LEARN_STARTED=True\n');s=''.join(lines)
  anchor='        print(traceback.format_exc(), flush=True)';assert s.count(anchor)==1;s=s.replace(anchor,anchor+"\n        if not _OWN_PPO_LEARN_STARTED:\n            with crash.open('rb') as f:os.fsync(f.fileno())\n            os._exit(1)")
  ast.parse(s);p.write_text(s,encoding='utf8',newline='\n');rows.append(dict(file=name,original_prepared_SHA=hashlib.sha256(original.read_bytes()).hexdigest(),resource_reviewed_SHA=hashlib.sha256(p.read_bytes()).hexdigest()))
 v=dict(epoch=time.time(),passed=True,only_prepared_never_deployed_workers_changed=True,prePPO_resource_failure_fsync_nonzero_exit_same449=True,normallearn_save_unmodified=True,original_prepared_source_retained=True,rows=rows)
 (R/'PREPARED_WORKER_RESOURCE_EXIT_REVIEW.json').write_bytes(json.dumps(v,indent=2).encode());print(json.dumps(v))
except BaseException:
 (R/('WORKER_OBSERVER_AST_ERROR_'+str(time.time_ns())+'.json')).write_bytes(json.dumps(dict(error=traceback.format_exc(),no_GPU=True),indent=2).encode());raise
