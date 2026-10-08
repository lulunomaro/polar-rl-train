"""Publish new isolated stiffness-pressure SDK off/on; no learning or host takeover."""
from pathlib import Path
import sys,json,shlex,time
D=Path(__file__).resolve().parent;R=D/'reports'
assert not (R/'SPRING_PRESSURE_SDK_PUBLISHED.json').exists()
assert json.loads((R/'D5_NOMINAL_ACTUAL_SDK_REVIEW.json').read_text(encoding='utf8'))['nominal_parameter_readback_scope_accepted']
assert json.loads((R/'SPRING_PRESSURE_ADAPTER_CPU_PASSED.json').read_text(encoding='utf8'))['passed']
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect();root='/home/egde/rl_candidates/MOD4_D5_SPRING_LAW_PREPARE_20261008'
try:
    with c.open_sftp() as f:
        for n in ('D5_NOMINAL_ACTUAL_SDK_REVIEW.json','SPRING_PRESSURE_ADAPTER_CPU_PASSED.json'):
            raw=(R/n).read_bytes()
            with f.open(root+'/reports/'+n,'wb') as out:out.write(raw)
            assert f.open(root+'/reports/'+n).read()==raw
    code=r"""
from pathlib import Path
import json,zipfile,hashlib,os,time
D=Path('/home/egde/rl_candidates/MOD4_D5_SPRING_LAW_PREPARE_20261008');R=D/'reports';E=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007')
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (R/'SPRING_PRESSURE_SDK_PUBLISHED.json').exists()
a=read(E/'reports/PLAN_APPROVAL.json');assert a['approved'] and 'S2' in a['allowed_stages'] and a['approved_plan_sha256']=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
assert read(R/'D5_NOMINAL_ACTUAL_SDK_REVIEW.json')['nominal_parameter_readback_scope_accepted']
for receipt in ('SPRING_PRESSURE_CPU_PASSED.json','SPRING_PRESSURE_ADAPTER_CPU_PASSED.json'):
 v=read(R/receipt);assert v['passed'] and v['CPU_only'] and not v['CUDA_initialized']
 for n,h in v['source_sha256'].items():assert sha(D/n)==h
base=E/'artifacts/d5-nominal-spring-si-sdk-frozen.zip';assert sha(base)=='9c4d18bffd50da978981154dfd87c8404f85985866fe09b8c509019f5b5166fc'
with zipfile.ZipFile(base) as z:
 m=json.loads(z.read('SOURCE_MANIFEST.json'));payload={n:z.read(n) for n in m['files']}
assert all(hashlib.sha256(payload[n]).hexdigest()==h for n,h in m['files'].items())
for n in ('spring_pressure_component.py','spring_pressure_sdk_adapter.py'):payload['runtime/isaac/mod4/'+n]=(D/n).read_bytes()
name='runtime/isaac/mod4/frozen_history_flat.py';text=payload[name].decode()
def change(old,new):
 global text
 assert text.count(old)==1,old
 text=text.replace(old,new)
change('        from spring_nominal_sdk_readback import NominalSpringReadback\n        self._spring_nominal_sdk=NominalSpringReadback(self)',
'''        from spring_pressure_sdk_adapter import SpringPressureSDK,PressureSpringReadback
        profile=os.environ['RM_SPRING_PRESSURE_PROFILE']
        assert profile in ('off','stiffness_independent_episode_090_110_v1')
        self._spring_pressure=SpringPressureSDK(self,profile!='off',int(self.cfg.seed))
        self._spring_nominal_sdk=PressureSpringReadback(self)''')
marker='            self._platform_sensor_sdk.append(self.sensor_sdk_audit())'
change(marker,'''            if len(self._platform_sensor_sdk)==150:
                import tempfile
                from spring_pressure_component import SpringPressure
                pressure=self._spring_pressure;saved=pressure.state_dict()
                actor=self.observation_manager.compute_group('policy').clone()
                q=self.scene['robot'].data.joint_pos.torch.clone()
                with tempfile.TemporaryDirectory() as td:
                    path=Path(td)/'spring_pressure.pt';torch.save(saved,path)
                    loaded=torch.load(path,map_location='cpu',weights_only=False);pressure.load_state_dict(loaded)
                now=pressure.state_dict()
                assert torch.equal(now['factor'],saved['factor']) and torch.equal(now['episode'],saved['episode'])
                assert all(torch.equal(x,y) for x,y in zip(now['rng'],saved['rng']))
                assert torch.equal(actor,self.observation_manager.compute_group('policy')) and torch.equal(q,self.scene['robot'].data.joint_pos.torch)
                left=SpringPressure(self.num_envs,self.device,1,pressure.component.enabled);right=SpringPressure(self.num_envs,self.device,2,pressure.component.enabled)
                left.load_state_dict(saved);right.load_state_dict(loaded)
                ids=torch.tensor([1,4,7],device=self.device);left.reset(ids);right.reset(ids)
                assert torch.equal(left.factor,right.factor) and all(torch.equal(x.get_state(),y.get_state()) for x,y in zip(left.rng,right.rng))
                pressure.roundtrip=dict(actual_device=str(self.device),CUDA_state_factor_two_RNG_disk_exact=True,next_selected_draw_exact=True,actor_same_tick_exact=True,joint_state_exact=True,physical_resume_not_claimed=True)
'''+marker)
change("    result['D5_nominal_only_no_randomization_or_PPO']=True",'''    result['D5_pressure_spring_actual_SDK']=result.pop('D5_nominal_spring_actual_SDK')
    result['D5_pressure_adapter_actual_SDK']=env._spring_pressure.audit()
    result['D5_pressure_SDK_no_PPO_or_hardware_calibration']=True
    result['D5_nominal_spring_only_field_superseded_by_actual_stiffness_pressure']=True''')
compile(text,name,'exec');payload[name]=text.encode()
assert hashlib.sha256(payload['assets/robot.usd']).hexdigest()=='694e9d5414401972d9186c44baef25aa785e1e07409ce9acf1ef553b9279dd87'
checkpoint=E/'artifacts/d4-own-8cb04bd8ad8379eb58bd5ce3347766965761400d0dce93fe29a3d5bdc3708053.pt'
assert sha(checkpoint)=='8cb04bd8ad8379eb58bd5ce3347766965761400d0dce93fe29a3d5bdc3708053'
source=dict(path=str(checkpoint),sha256=sha(checkpoint),bytes=checkpoint.stat().st_size)
jobs=[]
for label,profile in [('00-off','off'),('01-on','stiffness_independent_episode_090_110_v1')]:
 p=dict(payload);env=json.loads(p['runtime/isaac/mod4/env.json']);env['RM_SPRING_PRESSURE_PROFILE']=profile
 p['runtime/isaac/mod4/env.json']=json.dumps(env,indent=2).encode()
 manifest=dict(m,files={n:hashlib.sha256(v).hexdigest() for n,v in p.items()},nominal_spring_read_only_SDK=False,no_spring_randomization_or_nominal_parameter_change=False,
    D5_SDK_stiffness_pressure_only=True,D5_stiffness_profile=profile,nominal_preload_damping_armature_limits_unchanged=True,base_immutable_SHA=sha(base),
    SDK_approximate_effort_not_PhysX_drive_or_constraint_or_hardware_force=True,no_PPO_or_hardware_calibration=True)
 dest=E/'artifacts'/('d5-stiffness-pressure-sdk-'+label+'-frozen.zip');assert not dest.exists()
 with zipfile.ZipFile(str(dest)+'.partial','w',zipfile.ZIP_DEFLATED) as z:
  for n,b in p.items():z.writestr(n,b)
  z.writestr('SOURCE_MANIFEST.json',json.dumps(manifest,indent=2))
 os.replace(str(dest)+'.partial',dest)
 runtime=dict(path=str(dest),sha256=sha(dest),bytes=dest.stat().st_size)
 job='clk2500-closure-episode-d3-66-d5-stiffness-sdk-'+label;target=E/'eval_queue'/(job+'.json');assert not target.exists()
 row=dict(job_id=job,stage='S0E',immutable=True,plan_id=a['plan_id'],plan_sha256=a['approved_plan_sha256'],published_epoch=time.time(),kind='flat',profile='white_v3',sensor_profile='noise_bias_mild_v1',feedback_delay_profile='control_0_10ms_v1',action_delay_profile='physical_target_0_2500_5000us_v1',seed=20261002,num_envs=10,steps=300,max_wall_seconds=1800,architecture_variant='A0',role='D5 actual independent episode stiffness-only .9–1.1 engineering-pressure SDK off/on; not force-stroke hardware calibration or learning',physics_dt_s=.0025,control_dt_s=.01,solver_position=32,solver_velocity=4,artifacts=dict(runtime=runtime,checkpoint=source),no_learning=True,canonical_write_authority=False,GPU_concurrency=1,platform_scope_not_yet_accepted=True)
 tmp=target.with_suffix('.partial');tmp.write_text(json.dumps(row,indent=2));os.replace(tmp,target);jobs.append(row)
value=dict(epoch=time.time(),jobs=jobs,actual_SDK_pending=True,D5_learning_executor_deployed=False,source=source,nominal_preload_damping_limits_armature_unchanged=True,current243_runtime_worker_and_canonical_unchanged=True,no_GPU_on4090_or_PPO_or_budget_mutation=True)
(R/'SPRING_PRESSURE_SDK_PUBLISHED.json').write_text(json.dumps(value,indent=2));print(json.dumps(value))
"""
    compile(code,'new isolated pressureSDK publication','exec')
    _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=40)
    raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
    v=json.loads(raw);(R/'SPRING_PRESSURE_SDK_PUBLISHED.json').write_text(json.dumps(v,indent=2),encoding='utf8')
    print(json.dumps(dict(epoch=v['epoch'],jobs=[r['job_id'] for r in v['jobs']],packages=[r['artifacts']['runtime'] for r in v['jobs']],D5_learning=False)))
finally:c.close()
