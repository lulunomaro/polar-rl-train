"""Publish one isolated nominal gas-drive SDK readback through the existing worker."""
from pathlib import Path
import json,sys,shlex,hashlib,time
D=Path(__file__).resolve().parent;R=D/'reports'
assert not (R/'SPRING_NOMINAL_SDK_PUBLISHED.json').exists()
review=json.loads((D.parent/'MOD4_D4_WORLD_DISPATCH_REVIEW_20261008/reports/D4_TRUE_WORLD_SCOPE_REVIEW.json').read_text(encoding='utf8'))
assert review['decision']['candidate_all_three_complete']
assert review['candidate28633']['world']['facts']['passed']==63
source=review['candidate28633']['world']['result']['checkpoint']['sha256']
assert source=='8cb04bd8ad8379eb58bd5ce3347766965761400d0dce93fe29a3d5bdc3708053'
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'))
from remote_io import connect
root='/home/egde/rl_candidates/MOD4_D5_SPRING_LAW_PREPARE_20261008'
c=connect()
try:
    _,o,e=c.exec_command('mkdir -p '+shlex.quote(root+'/reports'),timeout=15)
    assert o.channel.recv_exit_status()==0,e.read().decode()
    with c.open_sftp() as f:
        for name in ('spring_nominal_sdk_readback.py',):
            raw=(D/name).read_bytes();compile(raw.decode(),name,'exec')
            with f.open(root+'/'+name,'wb') as out:out.write(raw)
            assert f.open(root+'/'+name).read()==raw
    code=r"""
from pathlib import Path
import json,time,zipfile,hashlib,os
D=Path('/home/egde/rl_candidates/MOD4_D5_SPRING_LAW_PREPARE_20261008');E=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007');R=D/'reports'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (R/'SPRING_NOMINAL_SDK_PUBLISHED.json').exists()
a=read(E/'reports/PLAN_APPROVAL.json');assert a['approved'] and 'S0E' in a['allowed_stages'] and a['approved_plan_sha256']=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
base=E/'artifacts/d4-clock2500-solver32-world-dispatch-reviewed-frozen.zip';assert sha(base)=='347ca4183e4f4cfa4ab98492637718996b62b9d4b1cb9f7f4119514484356ce5'
with zipfile.ZipFile(base) as z:
 m=read_manifest=json.loads(z.read('SOURCE_MANIFEST.json'));payload={n:z.read(n) for n in m['files']}
for n,h in m['files'].items():assert hashlib.sha256(payload[n]).hexdigest()==h,n
name='runtime/isaac/mod4/frozen_history_flat.py';text=payload[name].decode()
needle='class Mod4Env(ActionDelayMod4Env):\n';assert text.count(needle)==1
text=text.replace(needle,needle+'''    def __init__(self,*a,**kw):
        super().__init__(*a,**kw)
        from spring_nominal_sdk_readback import NominalSpringReadback
        self._spring_nominal_sdk=NominalSpringReadback(self)
''')
needle='    for step in range(args.steps):';assert text.count(needle)==1
text=text.replace(needle,'    spring_calls_start=env._spring_nominal_sdk.calls\n    contact_tick_start=env._integrated_contact.tick\n'+needle)
needle="    result['D4_closed_loop_actual_physical_target_delay']=True";assert text.count(needle)==1
text=text.replace(needle,needle+'''
    result['D5_nominal_spring_actual_SDK']=env._spring_nominal_sdk.audit()
    result['D5_nominal_spring_physical_write_delta']=env._spring_nominal_sdk.calls-spring_calls_start
    result['actual_physics_callback_delta']=env._integrated_contact.tick-contact_tick_start
    assert result['D5_nominal_spring_physical_write_delta']==result['actual_physics_callback_delta']==args.steps*4
    assert result['D5_nominal_spring_actual_SDK']['preload_active_environment_writes']>args.steps*4
    result['D5_nominal_only_no_randomization_or_PPO']=True
''')
compile(text,name,'exec');payload[name]=text.encode();payload['runtime/isaac/mod4/spring_nominal_sdk_readback.py']=(D/'spring_nominal_sdk_readback.py').read_bytes()
assert hashlib.sha256(payload['assets/robot.usd']).hexdigest()=='694e9d5414401972d9186c44baef25aa785e1e07409ce9acf1ef553b9279dd87'
manifest=dict(m,files={n:hashlib.sha256(v).hexdigest() for n,v in payload.items()},nominal_spring_read_only_SDK=True,no_spring_randomization_or_nominal_parameter_change=True,base_immutable_SHA=sha(base),actual_separate_PhysX_drive_or_hardware_force_not_claimed=True)
dest=E/'artifacts/d5-nominal-spring-si-sdk-frozen.zip';assert not dest.exists()
with zipfile.ZipFile(str(dest)+'.partial','w',zipfile.ZIP_DEFLATED) as z:
 for n,b in payload.items():z.writestr(n,b)
 z.writestr('SOURCE_MANIFEST.json',json.dumps(manifest,indent=2))
os.replace(str(dest)+'.partial',dest)
checkpoint=E/'artifacts/d4-own-8cb04bd8ad8379eb58bd5ce3347766965761400d0dce93fe29a3d5bdc3708053.pt';assert sha(checkpoint)=='8cb04bd8ad8379eb58bd5ce3347766965761400d0dce93fe29a3d5bdc3708053'
job='clk2500-closure-episode-d3-65-d5-nominal-spring-sdk';target=E/'eval_queue'/(job+'.json');assert not target.exists()
runtime=dict(path=str(dest),sha256=sha(dest),bytes=dest.stat().st_size)
row=dict(job_id=job,stage='S0E',immutable=True,plan_id=a['plan_id'],plan_sha256=a['approved_plan_sha256'],published_epoch=time.time(),kind='flat',profile='white_v3',sensor_profile='noise_bias_mild_v1',feedback_delay_profile='control_0_10ms_v1',action_delay_profile='physical_target_0_2500_5000us_v1',seed=20261002,num_envs=10,steps=300,max_wall_seconds=1800,architecture_variant='A0',role='Nominal gas-drive actualSDK parameters and approximate effort SI readback; noD5 DR or learning',physics_dt_s=.0025,control_dt_s=.01,solver_position=32,solver_velocity=4,artifacts=dict(runtime=runtime,checkpoint=dict(path=str(checkpoint),sha256=sha(checkpoint),bytes=checkpoint.stat().st_size)),no_learning=True,canonical_write_authority=False,GPU_concurrency=1,platform_scope_not_yet_accepted=True)
tmp=target.with_suffix('.partial');tmp.write_text(json.dumps(row,indent=2));os.replace(tmp,target)
v=dict(epoch=time.time(),job=row,runtime=runtime,source_actor_full_behavior_reviewed=True,production243_unchanged=True,nominal_spring_parameters_unchanged=True,actual_SDK_pending=True,no_PPO_or_budget_write=True)
(R/'SPRING_NOMINAL_SDK_PUBLISHED.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
"""
    compile(code,'nominal spring isolated publication','exec')
    _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=40)
    raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
    value=json.loads(raw);(R/'SPRING_NOMINAL_SDK_PUBLISHED.json').write_text(json.dumps(value,indent=2),encoding='utf8')
    print(json.dumps(value))
finally:c.close()
