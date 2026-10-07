"""Two new frozen SDK jobs on the existing3060 worker; production PPO continues."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports';assert (R/'ADAPTER_CPU_PASSED.json').exists()
assert not (R/'D3_SDK_IMMUTABLE_PUBLISHED.json').exists()
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 code=r"""
from pathlib import Path
import json,hashlib,zipfile,time,os
E=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007');D=Path('/home/egde/rl_candidates/MOD4_D3_ACTOR_DELAY_SDK_PREPARE_20261008');R=D/'reports'
OLD=Path('/home/egde/rl_candidates/MOD4_E0_DT2500_ENV20K_CONTINUATION_20261007')
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (R/'D3_SDK_IMMUTABLE_PUBLISHED.json').exists()
a=read(E/'reports/PLAN_APPROVAL.json');assert a['approved'] and 'S2' in a['allowed_stages'] and a['approved_plan_sha256']=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
assert read(R/'ADAPTER_CPU_PASSED.json')['CPU']['passed']
old=read(OLD/'reports/ASYNC_CLOCK2500_PACKAGE_AND_JOBS.json');pack=old['package'];assert sha(Path(pack['path']))==pack['sha256']
f=read(R/'SOURCE_FREEZE.json')['sha256'];assert len(f)==221
payload={}
for name,h in f.items():
 assert sha(D/name)==h,name;payload['runtime/'+name]=(D/name).read_bytes()
with zipfile.ZipFile(pack['path']) as z:
 oldmanifest=json.loads(z.read('SOURCE_MANIFEST.json'))
 for name,h in oldmanifest['files'].items():
  if name.startswith('assets/') or name.startswith('runtime/isaac/mod4/frozen_history_'):
   raw=z.read(name);assert hashlib.sha256(raw).hexdigest()==h;payload[name]=raw
name='runtime/isaac/mod4/frozen_history_flat.py';original=payload[name].decode();derived=original
marker='from sensor_a0_runtime import SensorMod4Env\nclass Mod4Env(SensorMod4Env):'
assert derived.count(marker)==1
derived=derived.replace(marker,'from feedback_delay_runtime import DelaySensorMod4Env\nclass Mod4Env(DelaySensorMod4Env):')
marker='            self._platform_sensor_sdk.append(self.sensor_sdk_audit())';assert derived.count(marker)==1
# Independent selected-row timestamp/cache check around the same actual reset as the inherited SDK.
prefix='''            if len(self._platform_sensor_sdk)==100:
                d=self._feedback_delay_mild
                old_delay=d.state_dict();old_other=torch.tensor([0,2,3,5,6,8,9],device=self.device)
'''
oldreset="            if len(self._platform_sensor_sdk)==100:\n                ids=torch.tensor([1,4,7],device=self.device);other=torch.tensor([0,2,3,5,6,8,9],device=self.device)"
assert derived.count(oldreset)==1
derived=derived.replace(oldreset,prefix+oldreset)
suffix='''            if len(self._platform_sensor_sdk)==100:
                d=self._feedback_delay_mild;ids=torch.tensor([1,4,7],device=self.device)
                assert torch.equal(d.episode[ids],old_delay['episode'][ids]+1)
                assert torch.equal(d.episode[old_other],old_delay['episode'][old_other])
                assert torch.equal(d.delay[old_other],old_delay['delay'][old_other])
                if d.enabled:
                    for key,queue in d.cache.items():
                        assert all(torch.equal(queue[k][old_other],v[old_other]) for k,v in old_delay['cache'][key].items())
                        assert bool((d.receipt(key,self.common_step_counter)['actual_age_us'][ids]==0).all())
                self._platform_delay_reset=dict(ids=[1,4,7],other_rows_exact=True,new_episode_warmup_age_us=0)
'''
derived=derived.replace(marker,suffix+marker)
marker='            else:action=policy(vec.get_observations())';assert derived.count(marker)==1
derived=derived.replace(marker,"            else:\n                sdk_obs=vec.get_observations().clone();sdk_obs['policy']=env.clean_policy()\n                action=policy(sdk_obs)")
marker="    result['sensor_actual_manager_audit']=env.sensor_sdk_audit()";assert derived.count(marker)==1
derived=derived.replace(marker,marker+"\n    result['feedback_delay_recipe']=env.feedback_delay_recipe()\n    result['feedback_delay_selected_reset']=getattr(env,'_platform_delay_reset',None)\n    result['SDK_fixed_clean_action_input']=True\n    result['final_root_state']=robot.data.root_state_w.cpu().tolist()\n    result['final_joint_pos']=robot.data.joint_pos.cpu().tolist()")
compile(derived,name,'exec');payload[name]=derived.encode()
assert hashlib.sha256(payload['assets/robot.usd']).hexdigest()=='694e9d5414401972d9186c44baef25aa785e1e07409ce9acf1ef553b9279dd87'
source=next(row['artifacts']['checkpoint'] for row in old['jobs'] if row['job_id']=='clk2500-solver32-20-candidate-flat')
assert source['sha256']=='4a4456efce65f238e8b02c7a65aa17236b5dcf97754604d54103359dede1c641' and sha(Path(source['path']))==source['sha256']
jobs=[];packages=[]
for label,profile in [('00-off','off'),('01-on','control_0_10ms_v1')]:
 pld=dict(payload);cfgname='runtime/isaac/mod4/env.json';cfg=json.loads(pld[cfgname]);cfg['RM_FEEDBACK_DELAY_PROFILE']=profile;pld[cfgname]=json.dumps(cfg,indent=2).encode()
 manifest=dict(files={n:hashlib.sha256(raw).hexdigest() for n,raw in pld.items()},original218_exact_in_candidate=True,source_count=221,
               delay_sdk_only=True,delay_profile=profile,training_executor_deployed=False,old_math_reused=True,source_freeze_sha256=sha(R/'SOURCE_FREEZE.json'),
               actual_training_clock_preserved=True,clock=oldmanifest['clock'],allowed_windows_adapter=['RM_MOD4_USD'],asset_originals_unchanged=True,
               prototype_delta_files=['feedback_delay_mild.py','feedback_delay_runtime.py','test_delay_actor_boundary_cpu.py',cfgname,name],
               unchanged_sensor_recipe_reports_D1D2_only=True,actual_delay_recipe_separate=True,
               fixed_clean_actor_actions_for_SDK_readback=True,scope_not_yet_platform_accepted=True)
 target=E/'artifacts'/('d3-delay-sdk-'+label+'-221-frozen.zip');assert not target.exists()
 with zipfile.ZipFile(str(target)+'.partial','w',zipfile.ZIP_DEFLATED) as z:
  for n,raw in pld.items():z.writestr(n,raw)
  z.writestr('SOURCE_MANIFEST.json',json.dumps(manifest,indent=2))
 os.replace(str(target)+'.partial',target);runtime=dict(path=str(target),bytes=target.stat().st_size,sha256=sha(target));packages.append(runtime)
 job='clk2500-solver32-70-d3-sdk-'+label;dest=E/'eval_queue'/(job+'.json');assert not dest.exists()
 row=dict(job_id=job,stage='S0E',immutable=True,plan_id=a['plan_id'],plan_sha256=a['approved_plan_sha256'],published_epoch=time.time(),kind='flat',
          profile='white_v3',sensor_profile='noise_bias_mild_v1',feedback_delay_profile=profile,seed=20261002,num_envs=10,steps=300,max_wall_seconds=1800,
          architecture_variant='A0',role='D3 feedback SDK off/on with original clean actor actions, not new trained expert',physics_dt_s=.0025,control_dt_s=.01,solver_position=32,solver_velocity=4,
          protocol='Actual actor manager/raw noise/queue age/reset/clean critic audit.300control3s; not15s skill regression or physics exact cross-process replay.',
          artifacts=dict(runtime=runtime,checkpoint=source),no_learning=True,canonical_write_authority=False,GPU_concurrency=1,platform_scope_not_yet_accepted=True)
 temp=dest.with_suffix('.json.partial');temp.write_text(json.dumps(row,indent=2));os.replace(temp,dest);jobs.append(row)
result=dict(epoch=time.time(),jobs=jobs,packages=packages,source=source,candidate_root=str(D),copied_training_entries_forbidden=True,
            SDK_pending=True,production_PPO_unchanged=True,old_worker_unchanged=True,single_GPU_lock_reused=True,no_canonical_write=True,new_budget_seconds=0)
(R/'D3_SDK_IMMUTABLE_PUBLISHED.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
"""
 _,out,err=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=45);raw,errors=out.read(),err.read();assert out.channel.recv_exit_status()==0,(raw+errors).decode()
 value=json.loads(raw);(R/'D3_SDK_IMMUTABLE_PUBLISHED.json').write_text(json.dumps(value,indent=2),encoding='utf8')
 print(json.dumps(dict(epoch=value['epoch'],job_ids=[row['job_id'] for row in value['jobs']],SDK_pending=True,production_training_unchanged=True)))
finally:c.close()
