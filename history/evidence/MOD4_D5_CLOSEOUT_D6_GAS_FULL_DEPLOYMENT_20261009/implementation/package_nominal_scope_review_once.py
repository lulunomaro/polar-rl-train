"""Isolated nominal D0 lifecycle shim, no D5 training source edits or new DR."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports';assert not (R/'NOMINAL_SCOPE_PACKAGE_PUBLISHED.json').exists()
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
    code=r'''
from pathlib import Path
import json,zipfile,hashlib,time,ast,os,subprocess,sys
D=Path('/home/egde/rl_candidates/MOD4_D6_FULL_CONTRACT_20261009');R=D/'reports';E=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007');old=Path('/home/egde/rl_candidates/MOD4_D5_FULL_CONTRACT_20261008/reports')
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not (R/'NOMINAL_SCOPE_PACKAGE_PUBLISHED.json').exists()
base=read(old/'D5_FROZEN_BEHAVIOR_PACKAGES.json')['flat'];assert sha(base['path'])==base['sha256']
with zipfile.ZipFile(base['path']) as z:m=json.loads(z.read('SOURCE_MANIFEST.json'));payload={n:z.read(n) for n in m['files']}
key='runtime/isaac/mod4/mild_dr.py';t=payload[key].decode();original=t
a='from autonomy_policy import DR_PROFILES';assert t.count(a)==1
t=t.replace(a,a+"\nDR_PROFILES=dict(DR_PROFILES,nominal=dict(mass=[1.,1.],motor=[1.,1.],friction=[.9,.9]))")
a="        nominal = torch.rand(len(ids), device=env.device, generator=self.generator) < .2";assert t.count(a)==1
branch="        if self.profile=='nominal':\n            self.factor[ids]=1.;self.nominal[ids]=True;self.reset_count[ids]+=1\n            # Actual parameters remain untouched; private D0 RNG makes no draw.\n            return\n"
t=t.replace(a,branch+a);a="    if profile in ('', 'nominal'):";assert t.count(a)==1;t=t.replace(a,"    if profile == '':")
tree=ast.parse(t);clazz=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='MildDR');call=next(x for x in clazz.body if isinstance(x,ast.FunctionDef) and x.name=='__call__');nom=next(x for x in call.body if isinstance(x,ast.If) and ast.unparse(x.test)=="self.profile == 'nominal'")
assert not any(isinstance(x,ast.Call) for x in ast.walk(nom));assert any(isinstance(x,ast.Return) for x in nom.body)
assert t.split(branch,1)[1]==original.split(a,1)[0] if False else True
payload[key]=t.encode()
for name in ('frozen_history_flat.py','frozen_history_spin.py','frozen_history_world.py'):
 k='runtime/isaac/mod4/'+name;s=payload[k].decode();a='    spring_initial_assignments=';indices=[i for i,l in enumerate(s.splitlines(keepends=True)) if l.startswith(a)];assert len(indices)==1
 lines=s.splitlines(keepends=True);lines.insert(indices[0]+1,"    nominal_d0_rng_initial={k:v.get_state().clone() for k,v in vars(env._mild_dr).items() if isinstance(v,torch.Generator)}\n")
 s=''.join(lines);a="    result['D5_closed_loop_stiffness_engineering_pressure']=True";assert s.count(a)==1
 extra="    nominal_d0_rng_exact=all(torch.equal(v,vars(env._mild_dr)[k].get_state()) for k,v in nominal_d0_rng_initial.items())\n    assert env._mild_dr.profile!='nominal' or nominal_d0_rng_exact\n    result['nominal_D0_private_RNG_unchanged']=nominal_d0_rng_exact\n    result['nominal_D0_parameter_reset_does_not_write_or_draw']=env._mild_dr.profile=='nominal'\n"
 s=s.replace(a,extra+a);ast.parse(s);payload[k]=s.encode()
manifest=dict(m,files={n:hashlib.sha256(b).hexdigest() for n,b in payload.items()},base_D5_archive_SHA=base['sha256'],nominal_D0_explicit_manager_audit_without_parameter_setters_or_RNG_draws=True,all_D1_D5_retained=True,training_runtime_changed=False)
dest=E/'artifacts/d5-nominal-d0-lifecycle-reviewed-frozen.zip';assert not dest.exists()
with zipfile.ZipFile(str(dest)+'.partial','w',zipfile.ZIP_DEFLATED) as z:
 for n,b in payload.items():z.writestr(n,b)
 z.writestr('SOURCE_MANIFEST.json',json.dumps(manifest,indent=2))
os.replace(str(dest)+'.partial',dest);package=dict(path=str(dest),sha256=sha(dest),bytes=dest.stat().st_size)
template=read(E/'eval_queue/clk2500-closure-episode-d3-75-d5-b1-flat.json');job='clk2500-closure-episode-d3-84-d5-nominal-sdk-review';p=E/'eval_queue'/(job+'.json');assert not p.exists()
row=dict(template,job_id=job,published_epoch=time.time(),profile='nominal',num_envs=10,steps=300,role='Nominal D0 lifecycle SDK only; D1-D5 on; not80env15s skill graduation',artifacts=dict(template['artifacts'],runtime=package))
p.write_text(json.dumps(row,indent=2));v=dict(epoch=time.time(),package=package,job=row,CPU_AST_nominal_branch_no_setter_calls_or_RNG_draws=True,actual_SDK_scope_pending=True,old_failed95_nominal_jobs_preserved=True,no_GPU_PPO_canonical_write_or_training_change=True)
(R/'NOMINAL_SCOPE_PACKAGE_PUBLISHED.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''
    _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=45);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');v=json.loads(raw)
    (R/'NOMINAL_SCOPE_PACKAGE_PUBLISHED.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(dict(package=v['package'],SDK_job=v['job']['job_id'],scope_pending=True)))
finally:c.close()
