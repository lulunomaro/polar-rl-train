"""New D4 target-delay SDK off/on jobs through the existing3060 single-GPU worker."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports'
assert (R/'D4_ADAPTER_CPU_PASSED.json').exists() and (R/'D3_BLOCK2_EXISTING_MATCHED_REVIEW.json').exists()
assert not (R/'D4_ACTION_SDK_PUBLISHED.json').exists()
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect();root='/home/egde/rl_candidates/MOD4_D4_ACTION_QUEUE_COMPONENT_PREPARE_20261008'
try:
    with c.open_sftp() as f:f.put(str(R/'D3_BLOCK2_EXISTING_MATCHED_REVIEW.json'),root+'/reports/D3_BLOCK2_EXISTING_MATCHED_REVIEW.json')
    code=r"""
from pathlib import Path
import json,time,hashlib,zipfile,os
D=Path('/home/egde/rl_candidates/MOD4_D4_ACTION_QUEUE_COMPONENT_PREPARE_20261008');R=D/'reports';E=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007')
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (R/'D4_ACTION_SDK_PUBLISHED.json').exists()
approval=read(E/'reports/PLAN_APPROVAL.json');assert approval['approved'] and 'S2' in approval['allowed_stages'] and approval['approved_plan_sha256']=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
cpu=read(R/'D4_COMPONENT_CPU_PASSED.json');adapter=read(R/'D4_ADAPTER_CPU_PASSED.json');assert cpu['passed'] and adapter['passed'] and not adapter['actual_SDK']
for name,h in adapter['source_sha256'].items():assert sha(D/name)==h
review=read(R/'D3_BLOCK2_EXISTING_MATCHED_REVIEW.json');assert review['decision']['block2_complete_learning_source_valid']
source=read(E/'eval_queue/clk2500-closure-episode-d3-20-b2-flat.json')['artifacts']['checkpoint']
assert source['sha256']==review['block2']['checkpoint']['sha256']=='ded074be755d5320a4050f69753163800a409d6eaf077fb3b990b686d9547a61' and sha(Path(source['path']))==source['sha256']
base=E/'artifacts/d3-clock2500-solver32-closure234-frozen.zip';assert sha(base)=='56f6ac8fe847b27e4a59e679b6dba99912652efe6b077d255f85754963fd359d'
with zipfile.ZipFile(base) as z:
    original=json.loads(z.read('SOURCE_MANIFEST.json'));payload={}
    for n,h in original['files'].items():
        raw=z.read(n);assert hashlib.sha256(raw).hexdigest()==h;payload[n]=raw
for n in ['action_delay_physics_queue.py','action_delay_sdk_adapter.py']:
    payload['runtime/isaac/mod4/'+n]=(D/n).read_bytes()
name='runtime/isaac/mod4/frozen_history_flat.py';derived=payload[name].decode()
def change(old,new):
    global derived
    assert derived.count(old)==1,old;derived=derived.replace(old,new)
change('class Mod4Env(DelaySensorMod4Env):\n', '''class Mod4Env(DelaySensorMod4Env):
    def __init__(self,*a,**kw):
        super().__init__(*a,**kw)
        from action_delay_sdk_adapter import PhysicalActionDelayAdapter
        profile=os.environ['RM_PHYSICS_ACTION_DELAY_PROFILE']
        assert profile in ('off','physical_target_0_2500_5000us_v1')
        self._physics_action_delay=PhysicalActionDelayAdapter(self,profile!='off',int(self.cfg.seed),collect=True)
    def feedback_delay_recipe(self):
        row=super().feedback_delay_recipe()
        if hasattr(self,'_physics_action_delay'):
            row['action_delay_us']=self._physics_action_delay.queue.recipe()['actual_transition_delay_us']
            row['action_delay_profile']=self._physics_action_delay.queue.recipe()['profile']
        return row
''')
marker='            self._platform_sensor_sdk.append(self.sensor_sdk_audit())'
change(marker,'''            if len(self._platform_sensor_sdk)==150:
                import tempfile
                adapter=self._physics_action_delay;saved=adapter.state_dict()
                actor=self.observation_manager.compute_group('policy').clone()
                with tempfile.TemporaryDirectory() as td:
                    savedfile=Path(td)/'action_queue.pt';torch.save(saved,savedfile)
                    loaded=torch.load(savedfile,map_location='cpu',weights_only=False);adapter.load_state_dict(loaded)
                now=adapter.state_dict()
                assert all(torch.equal(now['groups'][k][f],v) for k,g in saved['groups'].items() for f,v in g.items())
                assert all(torch.equal(now['rng'][k],v) for k,v in saved['rng'].items())
                assert torch.equal(actor,self.observation_manager.compute_group('policy'))
                self._platform_action_cuda_roundtrip=dict(queue_timestamps_targets_RNG_exact=True,actor_same_tick_exact=True,physical_state_unchanged=True)
'''+marker)
change('    for step in range(args.steps):','    callback_start=env._integrated_contact.tick\n    action_call_start=dict(env._physics_action_delay.calls)\n    for step in range(args.steps):')
marker="    result['sensor_platform_sdk']=dict(rows=getattr(env,'_platform_sensor_sdk',[]),selected_reset=getattr(env,'_platform_sensor_reset',None),diagnostic_reset_only_for_10env=True)"
change(marker,marker+'''
    result['actual_physics_callbacks']=env._integrated_contact.tick-callback_start
    result['expected_physics_callbacks']=args.steps*4
    assert result['actual_physics_callbacks']==result['expected_physics_callbacks']
    result['action_delay_actual_SDK']=env._physics_action_delay.audit()
    result['action_delay_callback_delta']={k:v-action_call_start[k] for k,v in env._physics_action_delay.calls.items()}
    assert all(v==args.steps*4 for v in result['action_delay_callback_delta'].values())
    result['action_delay_CUDA_disk_roundtrip']=getattr(env,'_platform_action_cuda_roundtrip',None)
    result['inherited_sensor_recipe_is_D1D2_only']=True
    result['sensor_recipe']['observation_delay_control_steps']=[0,1]
    result['sensor_recipe']['action_delay_control_steps']='Not the action queue timing unit; physical apply receipt is authoritative'
    result['sensor_recipe']['action_delay_us']=env._physics_action_delay.queue.recipe()['actual_transition_delay_us']
    result['SDK_actual_actor_closed_loop']=True
    result['D4_actual_SDK_not_training_or_15s_graduation']=True
    result['final_root_state']=robot.data.root_state_w.cpu().tolist()
    result['final_joint_pos']=robot.data.joint_pos.cpu().tolist()
''')
compile(derived,name,'exec');payload[name]=derived.encode()
assert hashlib.sha256(payload['assets/robot.usd']).hexdigest()=='694e9d5414401972d9186c44baef25aa785e1e07409ce9acf1ef553b9279dd87'
jobs=[];packages=[]
for label,profile in [('00-off','off'),('01-on','physical_target_0_2500_5000us_v1')]:
    pld=dict(payload);cfgname='runtime/isaac/mod4/env.json';cfg=json.loads(pld[cfgname])
    assert cfg['RM_PHYSICS_DT_S']=='0.0025' and cfg['RM_SOLVER_POS']=='32'
    cfg['RM_PHYSICS_ACTION_DELAY_PROFILE']=profile;pld[cfgname]=json.dumps(cfg,indent=2).encode()
    manifest=dict(original,files={n:hashlib.sha256(v).hexdigest() for n,v in pld.items()},D4_action_SDK_only=True,action_delay_profile=profile,action_delay_actual_us=[0,2500,5000] if profile!='off' else [0],D4_learning_executor_deployed=False,base_immutable_package_sha256=sha(base),allowed_windows_adapter=['RM_MOD4_USD'],asset_originals_unchanged=True,scope_not_yet_platform_accepted=True,delta_files=['runtime/isaac/mod4/action_delay_physics_queue.py','runtime/isaac/mod4/action_delay_sdk_adapter.py',name,cfgname],actual_initial_source='Full healthy and same3060 behavior-reviewed27575; no preflight strategy')
    dest=E/'artifacts'/('d4-action-physical-sdk-'+label+'-frozen.zip');assert not dest.exists()
    with zipfile.ZipFile(str(dest)+'.partial','w',zipfile.ZIP_DEFLATED) as z:
        for n,raw in pld.items():z.writestr(n,raw)
        z.writestr('SOURCE_MANIFEST.json',json.dumps(manifest,indent=2))
    os.replace(str(dest)+'.partial',dest);runtime=dict(path=str(dest),sha256=sha(dest),bytes=dest.stat().st_size);packages.append(runtime)
    job='clk2500-closure-episode-d3-30-d4-sdk-'+label;target=E/'eval_queue'/(job+'.json');assert not target.exists()
    row=dict(job_id=job,stage='S0E',immutable=True,plan_id=approval['plan_id'],plan_sha256=approval['approved_plan_sha256'],published_epoch=time.time(),kind='flat',profile='white_v3',sensor_profile='noise_bias_mild_v1',feedback_delay_profile='control_0_10ms_v1',action_delay_profile=profile,seed=20261002,num_envs=10,steps=300,max_wall_seconds=1800,architecture_variant='A0',role='D4 physical processed-target queue SDK off/on;300control3s, not trained D4 expert',physics_dt_s=.0025,control_dt_s=.01,solver_position=32,solver_velocity=4,protocol='Actual target issue/apply timestamp and Articulation target readback;coherent legs/wheels;selectedreset;full1200callbacks;CUDA queue disk restore;cleancritic and D3 feedback preserved',artifacts=dict(runtime=runtime,checkpoint=source),no_learning=True,canonical_write_authority=False,GPU_concurrency=1,platform_scope_not_yet_accepted=True)
    tmp=target.with_suffix('.partial');tmp.write_text(json.dumps(row,indent=2));os.replace(tmp,target);jobs.append(row)
v=dict(epoch=time.time(),jobs=jobs,packages=packages,source=source,CPU_contracts=28,actual_SDK_pending=True,D4_learning_executor_deployed=False,current234_production_changed=False,training_4090_not_paused=True,old_3060_worker_unchanged=True,single_GPU_lock_reused=True,PPO_or_budget_operations=0)
(R/'D4_ACTION_SDK_PUBLISHED.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
"""
    compile(code,'D4 SDK isolated publisher transport','exec')
    _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=40)
    raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
    v=json.loads(raw);(R/'D4_ACTION_SDK_PUBLISHED.json').write_text(json.dumps(v,indent=2),encoding='utf8')
    print(json.dumps(dict(epoch=v['epoch'],jobs=[x['job_id'] for x in v['jobs']],packages=v['packages'],actual_SDK_pending=True,current234_production_changed=False)))
finally:c.close()
