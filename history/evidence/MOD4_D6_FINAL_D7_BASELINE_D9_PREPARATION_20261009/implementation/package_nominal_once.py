"""New D7 nominal D0 lifecycle scope; frozen-only, no production or budget changes."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports'
assert not (R/'D9_NOMINAL_INTERFACE_PUBLISHED.json').exists()
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 code=r'''
from pathlib import Path
import json,zipfile,hashlib,time,ast,os
D=Path('/home/egde/rl_candidates/MOD4_D9_COMBINATION_PREPARE_20261009');R=D/'reports';R.mkdir(parents=True,exist_ok=True)
E=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007')
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not (R/'D9_NOMINAL_INTERFACE_PUBLISHED.json').exists()
base=E/'artifacts/d7-clock2500-solver32-chassisPD277-closedloop-frozen.zip';assert sha(base)=='8a964c1d0cfa291ea8faf72d978464daa8b2a8e90834554c435d528ffb222871'
with zipfile.ZipFile(base) as z:
 m=json.loads(z.read('SOURCE_MANIFEST.json'));payload={n:z.read(n) for n in m['files']}
assert all(hashlib.sha256(payload[n]).hexdigest()==h for n,h in m['files'].items())
key='runtime/isaac/mod4/mild_dr.py';original=payload[key].decode();t=original
a='from autonomy_policy import DR_PROFILES';assert t.count(a)==1
t=t.replace(a,a+"\nDR_PROFILES=dict(DR_PROFILES,nominal=dict(mass=[1.,1.],motor=[1.,1.],friction=[.9,.9]))")
a="        nominal = torch.rand(len(ids), device=env.device, generator=self.generator) < .2";assert t.count(a)==1
branch="        if self.profile=='nominal':\n            self.factor[ids]=1.;self.nominal[ids]=True;self.reset_count[ids]+=1\n            return\n"
t=t.replace(a,branch+a);a="    if profile in ('', 'nominal'):";assert t.count(a)==1;t=t.replace(a,"    if profile == '':")
ta,tb=ast.parse(original),ast.parse(t)
ca=next(x for x in ta.body if isinstance(x,ast.ClassDef) and x.name=='MildDR');cb=next(x for x in tb.body if isinstance(x,ast.ClassDef) and x.name=='MildDR')
method=next(x for x in cb.body if isinstance(x,ast.FunctionDef) and x.name=='__call__')
nom=next(x for x in method.body if isinstance(x,ast.If) and ast.unparse(x.test)=="self.profile == 'nominal'")
assert not any(isinstance(x,ast.Call) for x in ast.walk(nom));method.body.remove(nom)
assert ast.dump(ca,include_attributes=False)==ast.dump(cb,include_attributes=False)
payload[key]=t.encode()
for name in ('frozen_history_flat.py','frozen_history_spin.py','frozen_history_world.py'):
 k='runtime/isaac/mod4/'+name;s=payload[k].decode();lines=s.splitlines(keepends=True)
 ids=[i for i,l in enumerate(lines) if l.startswith('    chassis_pd_initial_assignments=')];assert len(ids)==1
 lines.insert(ids[0]+1,"    nominal_d0_rng_initial={k:v.get_state().clone() for k,v in vars(env._mild_dr).items() if isinstance(v,torch.Generator)}\n")
 s=''.join(lines);a="    result['D7_closed_loop_chassis_COM_explicit_PD_engineering_pressure']=True";assert s.count(a)==1
 extra="    nominal_d0_rng_exact=all(torch.equal(v,vars(env._mild_dr)[k].get_state()) for k,v in nominal_d0_rng_initial.items())\n    assert env._mild_dr.profile!='nominal' or nominal_d0_rng_exact\n    result['nominal_D0_private_RNG_unchanged']=nominal_d0_rng_exact\n    result['nominal_D0_parameter_reset_does_not_write_or_draw']=env._mild_dr.profile=='nominal'\n"
 s=s.replace(a,extra+a);tree=ast.parse(s)
 imports=[x for x in tree.body if isinstance(x,ast.ImportFrom) and x.module=='chassis_pd_training_env'];assert len(imports)==1 and imports[0].names[0].name=='ChassisPDMod4Env'
 payload[k]=s.encode()
changed=[n for n in payload if hashlib.sha256(payload[n]).hexdigest()!=m['files'][n]]
assert set(changed)=={key,*['runtime/isaac/mod4/'+n for n in ('frozen_history_flat.py','frozen_history_spin.py','frozen_history_world.py')]}
manifest=dict(m,files={n:hashlib.sha256(b).hexdigest() for n,b in payload.items()},base_D7_archive_SHA=sha(base),nominal_D0_explicit_manager_no_setter_or_draw=True,white_MildDR_class_AST_exact=True,D1_D7_retained=True,production_runtime_changed=False)
dest=E/'artifacts/d9-d7-nominal-d0-lifecycle-reviewed-frozen.zip';assert not dest.exists()
with zipfile.ZipFile(str(dest)+'.partial','w',zipfile.ZIP_DEFLATED) as z:
 for n,b in payload.items():z.writestr(n,b)
 z.writestr('SOURCE_MANIFEST.json',json.dumps(manifest,indent=2))
os.replace(str(dest)+'.partial',dest);package=dict(path=str(dest),sha256=sha(dest),bytes=dest.stat().st_size)
template=read(E/'eval_queue/clk2500-closure-episode-d3-98-d7-com-pd-anchor-flat.json')
job='clk2500-closure-episode-d3-100-d9-nominal-sdk';p=E/'eval_queue'/(job+'.json');assert not p.exists()
row=dict(template,job_id=job,published_epoch=time.time(),profile='nominal',num_envs=10,steps=300,role='D9 D0 nominal lifecycle interface with D1-D7 on; no learning, not skill graduation',artifacts=dict(template['artifacts'],runtime=package))
assert row['no_learning'] and not row['canonical_write_authority']
t=Path(str(p)+'.partial');t.write_text(json.dumps(row,indent=2));t.replace(p)
v=dict(epoch=time.time(),package=package,job=row,white_paths_AST_exact=True,nominal_branch_has_no_setter_or_RNG_calls=True,D1_D7_unchanged=True,changed_files=changed,actual_SDK_scope_pending=True,production_GPU_PPO_canonical_transactions=0)
(R/'D9_NOMINAL_INTERFACE_PUBLISHED.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''
 _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');v=json.loads(raw)
 (R/'D9_NOMINAL_INTERFACE_PUBLISHED.json').write_text(json.dumps(v,indent=2),encoding='utf8')
 print(json.dumps(dict(package=v['package'],job=v['job']['job_id'],SDK_pending=True,production_mutations=0)))
finally:c.close()
