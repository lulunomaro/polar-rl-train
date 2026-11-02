"""Extend exact H1 staticworker OUTSIDE original for24 AST only. No runtime imports."""
from pathlib import Path
import ast,hashlib,json
B=Path(__file__).resolve().parent;T=B.parent;O=T/'staged_sources/H1_NORMAL_MOD4V1_SOURCE_V1'
p=O/'worker_mod4v1_normal_h1.py';base=p.read_text(encoding='utf-8');s=''.join(' '+line if line.startswith(' ') else line for line in base.splitlines(keepends=True));assert ast.dump(ast.parse(s),include_attributes=False)==ast.dump(ast.parse(base),include_attributes=False)

def rep(old,new):
 global s
 assert s.count(old)==1,old;s=s.replace(old,new,1)
rep("   ns=None;created=[None]","   ns=None;created=[None];cache=None;forbidden={'alg_update':0,'optimizer_step':0,'runner_learn':0}")
rep("env=factory();created[0]=env;assert env.num_envs", "env=factory();created[0]=env;original_close=env.close\n     def closed(*aa,**kk):\n      result=original_close(*aa,**kk)\n      if not (O/'ENV_CLOSE_RETURNED.json').exists():put('ENV_CLOSE_RETURNED.json',dict(closed=True))\n      return result\n     env.close=closed;assert env.num_envs")
anchor="     runner.logger.writer=None;real=runner.env.unwrapped;ck="
pre="""     def forbid(name):
      def fail(*aa,**kk):forbidden[name]+=1;raise RuntimeError('H1NOUPDATE forbids '+name)
      return fail
     runner.alg.update=forbid('alg_update');runner.alg.optimizer.step=forbid('optimizer_step');runner.learn=forbid('runner_learn')
"""
rep(anchor,pre+anchor)
anchor="     required={'SENSOR_RESUME_STARTUP_VERIFIED.json'"
pre="""     def core_summary():
      def tree(v):
       rows=[]
       def walk(x,path):
        if torch.is_tensor(x):
         a=x.detach().cpu().contiguous();rows.append(dict(path=path,dtype=str(a.dtype),shape=list(a.shape),SHA=hashlib.sha256(a.numpy().tobytes()).hexdigest()))
        elif isinstance(x,dict):
         for k in sorted(x,key=str):walk(x[k],path+'/'+str(k))
        elif isinstance(x,(tuple,list)):
         for i,z in enumerate(x):walk(z,path+'/'+str(i))
        else:rows.append(dict(path=path,value=x))
       walk(v,'');return dict(tree_SHA=hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest(),leaves=rows)
      return dict(iteration=runner.current_learning_iteration,alg_LR=runner.alg.learning_rate,param_groups=runner.alg.optimizer.state_dict()['param_groups'],raw_STD6=runner.alg.actor.state_dict()['distribution.std_param'].detach().cpu().tolist(),actor=tree(runner.alg.actor.state_dict()),critic=tree(runner.alg.critic.state_dict()),optimizer=tree(runner.alg.optimizer.state_dict()))
     before_core=core_summary();before_audit=real._mild_dr.audit();assert before_audit['actual_parameters_pass']
     from actual_DR_memory_getter272 import RuntimeOrderBinding,ActualDRMemoryGetter
     robot=real.scene['robot']
     def names(key):
      ids=robot.actuators[key].joint_indices
      if isinstance(ids,slice):ids=list(range(len(robot.joint_names)))[ids]
      elif hasattr(ids,'tolist'):ids=ids.tolist()
      return tuple(robot.joint_names[i] for i in ids)
     bind=RuntimeOrderBinding(tuple(robot.body_names),tuple(robot.joint_names),names('legs'),names('wheels'),names('gas_springs'),int(real._mild_dr.materials.shape[1]));getter=ActualDRMemoryGetter(real,bind);getter.capture_initial()
     def small(v):
      a=v.detach();return dict(shape=list(a.shape),dtype=str(a.dtype),finite=bool(torch.isfinite(a).all()),min=float(a.min()),max=float(a.max()),first8=a.reshape(-1)[:8].cpu().tolist())
     put('H1_CORE_AND_DR_BEFORE.json',dict(core=before_core,actual_mild_DR_audit=before_audit,component_memory_NOT_independentbackend={k:small(v) for k,v in getter.cache.items()},source_read_purpose=task['source_read_purpose'],source_cache=cache.receipt(),forbidden_calls=forbidden))
"""
rep(anchor,pre+anchor)
anchor="     put('MOD4V1_NORMAL_H1_NATIVE24_192PHYSICS_48FEEDBACK_NOUPDATE.json',dict(passed=True,source_SHA=SOURCE,"
pre="""     after_core=core_summary();assert after_core==before_core and all(v==0 for v in forbidden.values())
     after_audit=real._mild_dr.audit();assert after_audit['actual_parameters_pass'];real._mod4v1_nominal_guard.assert_new_nominals_unchanged()
     counts=cache.receipt();assert counts['selected_source_physical_byte_reads']==counts['selected_source_SHA_calculations']==counts['selected_source_decodes']==1
     after_components=getter._read(torch.arange(real.num_envs,device=real.device))
     put('H1_CORE_AND_DR_AFTER.json',dict(core=after_core,core_before_after_exact=True,actual_mild_DR_audit=after_audit,component_memory_NOT_independentbackend={k:small(v) for k,v in after_components.items()},source_read_purpose=task['source_read_purpose'],source_cache=counts,forbidden_calls=forbidden,one_original_fresh_reset=real._mod4v1_nominal_guard.reset_calls,D6_scope='originalgasdamping only',birth_inertia_independent_qualification=False,canonical_access=False))
"""
rep(anchor,pre+anchor)
rep("put('MOD4V1_NORMAL_H1_NATIVE24_192PHYSICS_48FEEDBACK_NOUPDATE.json',dict(passed=True,source_SHA=SOURCE,","put('MOD4V1_NORMAL_H1_NATIVE24_192PHYSICS_48FEEDBACK_NOUPDATE.json',dict(passed=True,source_SHA=SOURCE,forbidden_calls=forbidden,source_read_purpose=task['source_read_purpose'],core_before_after_exact=True,actual_mild_DR_audit_after=after_audit,")
rep("   finally:\n    put('APP_CLOSING.json',dict(epoch=time.time()))","   finally:\n    if cache is not None:put('SOURCE_FINAL_READ_COUNTS.json',cache.receipt())\n    if created[0] is not None and not (O/'ENV_CLOSE_RETURNED.json').exists():created[0].close()\n    put('APP_CLOSING.json',dict(epoch=time.time()))")

def loop(text):
 a=[n for n in ast.walk(ast.parse(text)) if isinstance(n,ast.For) and isinstance(n.iter,ast.Call) and isinstance(n.iter.func,ast.Name) and n.iter.func.id=='range' and len(n.iter.args)==1 and isinstance(n.iter.args[0],ast.Constant) and n.iter.args[0].value==24];assert len(a)==1;return ast.dump(a[0],include_attributes=False)
assert loop(s)==loop(base);compile(s,'evaluate_h1_71db_noupdate.py','exec')
f=B/'evaluate_h1_71db_native24_noupdate_v1.py'
with f.open('x',encoding='utf-8',newline='') as z:z.write(s)
with (B/'H1_NOUPDATE_FOR24_EXACT_AST_PROOF.json').open('x',encoding='utf-8') as z:json.dump(dict(kind='H1_ORIGINAL_NATIVE24_AST_UNCHANGED_OUTER_AUDIT_ONLY',staticworker_path=str(p),staticworker_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),derivedworker_path=str(f),derivedworker_SHA=hashlib.sha256(s.encode()).hexdigest(),for24_AST_SHA=hashlib.sha256(loop(s).encode()).hexdigest(),for24_AST_exact=True,PT_or_SDK_operations=0),z,indent=2)
print('H1 originalfor24 AST exact; independent core/MildDR audit and forbiddensentinels outside loop only.')
