from pathlib import Path
import ast,json,time,hashlib
D=Path(__file__).resolve().parent;P=D/'payload';R=D/'reports';B=D.parent/'MOD4_E1_WAVE50_ROUTE_SECOND_BOUNDED_20261012/immutable449_source/isaac/mod4'
rows=[]
for name in ('train_wave50_lifetime_resume_ppo.py','train_wave50_lifetime_fresh_preflight_ppo.py'):
 p=P/'isaac/mod4'/name;s=p.read_text();original=D/(name+'.PRE_RESOURCE_REVIEWED.txt');assert not original.exists();original.write_bytes(p.read_bytes())
 anchor='app = launcher.app';assert s.count(anchor)==1;s=s.replace(anchor,anchor+'\n_OWN_PPO_LEARN_STARTED=False')
 # Same observer points already used in source449; no normallearn/save behavior changed.
 prior=(B/'train_wave50_route_startup_resource_reviewed_ppo.py').read_text()
 a=prior.index('_OWN_PPO_LEARN_STARTED=True');context=prior[a-100:a+100]
 before='    learn(runner, num_learning_iterations=target_iterations - start_iter, log_dir=log_dir)'
 # Actual function call from the frozen source is matched structurally below.
 tree=ast.parse(s);call=next(n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='_bounded_learn') if any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='_bounded_learn' for n in ast.walk(tree)) else None
 if call is None:
  call=next(n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='learn')
 line=call.lineno-1;lines=s.splitlines(True);indent=lines[line][:len(lines[line])-len(lines[line].lstrip())];lines.insert(line,indent+'global _OWN_PPO_LEARN_STARTED\n'+indent+'_OWN_PPO_LEARN_STARTED=True\n');s=''.join(lines)
 anchor='        print(traceback.format_exc(), flush=True)';assert s.count(anchor)==1
 s=s.replace(anchor,anchor+"\n        if not _OWN_PPO_LEARN_STARTED:\n            with crash.open('rb') as f:os.fsync(f.fileno())\n            os._exit(1)")
 ast.parse(s);p.write_text(s,encoding='utf8',newline='\n');rows.append(dict(file=name,original_prepared_SHA=hashlib.sha256(original.read_bytes()).hexdigest(),resource_reviewed_SHA=hashlib.sha256(p.read_bytes()).hexdigest()))
v=dict(epoch=time.time(),passed=True,only_prepared_never_deployed_workers_changed=True,prePPO_resource_failure_fsync_and_nonzero_exit_same_as449=True,normallearn_save_unchanged=True,original_prepared_source_retained=True,rows=rows)
p=R/'PREPARED_WORKER_RESOURCE_EXIT_REVIEW.json';assert not p.exists();p.write_bytes(json.dumps(v,indent=2).encode());print(json.dumps(v))
