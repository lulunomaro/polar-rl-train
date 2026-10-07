"""New immutable2.5ms/32-4 scope; no training or canonical write authority."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports'
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 code=r"""
from pathlib import Path
import json,hashlib,zipfile,time,os,shutil
E=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007');F=Path('/home/egde/rl_candidates/MOD4_DT2500_SOLVER32_TRAINING_TEST_20261007');D=Path('/home/egde/rl_candidates/MOD4_E0_DT2500_ENV20K_CONTINUATION_20261007')
R=E/'reports';A=E/'artifacts';Q=E/'eval_queue'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (D/'reports/ASYNC_CLOCK2500_PACKAGE_AND_JOBS.json').exists()
a=json.loads((R/'PLAN_APPROVAL.json').read_text());assert a['approved'] and 'S0E' in a['allowed_stages'] and 'S2' in a['allowed_stages']
old=json.loads((R/'SENSOR_COMPLETE_ASYNC_PACKAGE_AND_JOBS.json').read_text());p=Path(old['package']['path']);assert sha(p)==old['package']['sha256']
payload={};aliases={};f=json.loads((F/'reports/SOURCE_FREEZE.json').read_text())['sha256'];assert len(f)==211
for n,h in f.items():
 assert sha(F/n)==h,n;payload['runtime/'+n]=(F/n).read_bytes()
with zipfile.ZipFile(p) as z:
 oldman=json.loads(z.read('SOURCE_MANIFEST.json'))
 for n,h in oldman['files'].items():
  if n.startswith('assets/'):
   raw=z.read(n);assert hashlib.sha256(raw).hexdigest()==h;payload[n]=raw
 for kind in ('flat','spin','world'):
  n='runtime/isaac/mod4/frozen_history_'+kind+'.py';raw=z.read(n);assert hashlib.sha256(raw).hexdigest()==oldman['files'][n]
  original=(F/'isaac/mod4'/('sensor_'+kind+'_probe.py')).read_bytes()
  old_source='runtime/'+oldman['probe_alias_deltas'][n]['original_path']
  assert hashlib.sha256(original).hexdigest()==hashlib.sha256(z.read(old_source)).hexdigest(),kind
  derived=raw.decode()
  # Actual new clock and all articulation/closed-loop settings are read from live scene.
  marker="    result['sensor_actual_manager_audit']=env.sensor_sdk_audit()";assert derived.count(marker)==1
  extra='''
    from pxr import Usd,PhysxSchema,UsdPhysics
    stage=env.sim.stage;solver_rows=[];enabled_loops=0
    for ei in range(env.num_envs):
        for prim in Usd.PrimRange(stage.GetPrimAtPath('/World/envs/env_'+str(ei)+'/Robot')):
            if prim.HasAPI(PhysxSchema.PhysxArticulationAPI):
                api=PhysxSchema.PhysxArticulationAPI(prim)
                solver_rows.append((api.GetSolverPositionIterationCountAttr().Get(),api.GetSolverVelocityIterationCountAttr().Get()))
            if prim.IsA(UsdPhysics.Joint):
                joint=UsdPhysics.Joint(prim)
                if joint.GetExcludeFromArticulationAttr().Get() and joint.GetJointEnabledAttr().Get():enabled_loops+=1
    assert len(solver_rows)==env.num_envs and all(x==(32,4) for x in solver_rows)
    assert enabled_loops==6*env.num_envs
    assert abs(env.physics_dt-.0025)<1e-12 and abs(env.step_dt-.01)<1e-12
    assert env.cfg.sim.physics.solver_type==1
    result['clock2500_actual_solver']=dict(articulations=len(solver_rows),all_position32_velocity4=True,enabled_closed_loops=enabled_loops,physics_dt_s=env.physics_dt,control_dt_s=env.step_dt)
'''
  derived=derived.replace(marker,marker+extra);compile(derived,n,'exec');payload[n]=derived.encode()
  aliases[n]=dict(original_runtime_probe_sha256=hashlib.sha256(original).hexdigest(),original_old_scope_alias_sha256=hashlib.sha256(raw).hexdigest(),old_sensor_SDK_audit_exact_reused=True,only_extra_actual_clock_solver_loop_audit=True)
assert hashlib.sha256(payload['assets/robot.usd']).hexdigest()=='694e9d5414401972d9186c44baef25aa785e1e07409ce9acf1ef553b9279dd87'
manifest=dict(files={n:hashlib.sha256(v).hexdigest() for n,v in payload.items()},original_runtime_source_count=211,source_freeze_sha256=sha(F/'reports/SOURCE_FREEZE.json'),probe_alias_deltas=aliases,clock=dict(physics_dt_s=.0025,control_dt_s=.01,decimation=4,force_bin_s=.005,force_history=3,solver_position=32,solver_velocity=4),sensor_profile='noise_bias_mild_v1',actor_feedback_only=True,clean_critic=True,allowed_windows_adapter=['RM_MOD4_USD'],asset_originals_unchanged=True,scope_not_yet_platform_accepted=True)
pack=A/'clock2500-solver32-sensor211-frozen.zip';assert not pack.exists()
with zipfile.ZipFile(str(pack)+'.partial','w',compression=zipfile.ZIP_DEFLATED) as z:
 for n,v in payload.items():z.writestr(n,v)
 z.writestr('SOURCE_MANIFEST.json',json.dumps(manifest,indent=2))
os.replace(str(pack)+'.partial',pack);runtime=dict(path=str(pack),bytes=pack.stat().st_size,sha256=sha(pack))
rows=[]
for role,source in [('anchor24827',json.loads((F/'reports/SELECTED_VALIDATED_SOURCE.json').read_text())['checkpoint']),('candidate25211',json.loads((F/'reports/solver32_formal45_PASSED.json').read_text())['checkpoint'])]:
 src=Path(source['path']);assert sha(src)==source['sha256'];target=A/('clock2500-'+role+'-'+source['sha256']+'.pt');assert not target.exists()
 shutil.copyfile(src,str(target)+'.partial');assert sha(Path(str(target)+'.partial'))==source['sha256'];os.replace(str(target)+'.partial',target)
 cp=dict(path=str(target),bytes=target.stat().st_size,sha256=source['sha256'])
 if role=='anchor24827':rows.append(('00-sdk','flat',10,300,role,cp))
 for kind in ('flat','spin','world'):rows.append((('10-anchor-' if role=='anchor24827' else '20-candidate-')+kind,kind,80 if kind=='flat' else 88,1500,role,cp))
jobs=[]
for label,kind,count,steps,role,cp in rows:
 job='clk2500-solver32-'+label;target=Q/(job+'.json');assert not target.exists()
 item=dict(job_id=job,stage='S0E',immutable=True,plan_id=a['plan_id'],plan_sha256=a['approved_plan_sha256'],published_epoch=time.time(),kind=kind,profile='white_v3',sensor_profile='noise_bias_mild_v1',seed=20261002,num_envs=count,steps=steps,max_wall_seconds=1800,architecture_variant='A0',role=role,physics_dt_s=.0025,control_dt_s=.01,solver_position=32,solver_velocity=4,protocol='New clock scope: actual SDK/reset/solver/closed-loop readback then matched full initial root/q/parameters and signed skill metrics. Pending acceptance; no GPU bitexact claim.',artifacts=dict(runtime=runtime,checkpoint=cp),no_learning=True,canonical_write_authority=False,GPU_concurrency=1,platform_scope_not_yet_accepted=True)
 temp=target.with_suffix('.json.partial');temp.write_text(json.dumps(item,indent=2));os.replace(temp,target);jobs.append(item)
v=dict(epoch=time.time(),package=runtime,source_manifest=manifest,jobs=jobs,total_jobs=len(jobs),no_training_or_canonical_write=True,old1ms_scope_not_reused_as_platform_proof=True,scope_pending=True)
(D/'reports/ASYNC_CLOCK2500_PACKAGE_AND_JOBS.json').write_text(json.dumps(v,indent=2));(R/'ASYNC_CLOCK2500_PACKAGE_AND_JOBS.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
"""
 _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=90);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode()
 v=json.loads(raw);(R/'ASYNC_CLOCK2500_PACKAGE_AND_JOBS.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps({'package':v['package'],'jobs':[x['job_id'] for x in v['jobs']],'scope_pending':True}))
finally:c.close()
