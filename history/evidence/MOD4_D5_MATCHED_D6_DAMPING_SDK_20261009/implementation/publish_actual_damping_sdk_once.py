"""Publish new D6 off/on SDK jobs; no production edits or GPU/PPO on 4090."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports'
assert not (R/'D6_ACTUAL_DAMPING_SDK_PUBLISHED.json').exists()
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect();root='/home/egde/rl_candidates/MOD4_D6_DAMPING_SOURCE_PREPARE_20261008'
try:
    with c.open_sftp() as f:
        path=root+'/gas_damping_actual_sdk_proof.py'
        try:f.stat(path);raise AssertionError('Proof source already staged')
        except FileNotFoundError:pass
        raw=(D/'gas_damping_actual_sdk_proof.py').read_bytes()
        with f.open(path,'wb') as o:o.write(raw)
        assert f.open(path).read()==raw
    code=r'''
from pathlib import Path
import json,zipfile,hashlib,os,time
D=Path('/home/egde/rl_candidates/MOD4_D6_DAMPING_SOURCE_PREPARE_20261008');E=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007')
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (D/'reports/D6_ACTUAL_DAMPING_SDK_PUBLISHED.json').exists()
approval=read(E/'reports/PLAN_APPROVAL.json')
assert approval['approved'] and 'S2' in approval['allowed_stages'] and approval['approved_plan_sha256']=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
cpu=read(D/'reports/D6_DAMPING_ADAPTER_TARGET_CPU_PASSED.json');assert cpu['passed'] and cpu['count']==13 and not cpu['CUDA_initialized']
base=E/'artifacts/d5-clock2500-solver32-spring255-closedloop-frozen.zip';assert sha(base)=='fe8dc6bcb027215739a9edf7a8b5fa46240326b402e05ae0d0463db87044452c'
with zipfile.ZipFile(base) as z:
    m=json.loads(z.read('SOURCE_MANIFEST.json'));payload={n:z.read(n) for n in m['files']}
assert all(hashlib.sha256(payload[n]).hexdigest()==h for n,h in m['files'].items())
key='runtime/isaac/mod4/frozen_history_flat.py';text=payload[key].decode()
def replace_once(old,new):
    global text
    assert text.count(old)==1,old;text=text.replace(old,new)
replace_once('from spring_pressure_training_env import SpringPressureMod4Env as ActionDelayMod4Env','from gas_damping_training_env import GasDampingMod4Env as ActionDelayMod4Env')
replace_once('                self._reset_idx(ids)','                self._d6proof.before_selected_reset(ids)\n                self._reset_idx(ids)\n                self._d6proof.after_selected_reset(ids)')
replace_once('            self._platform_sensor_sdk.append(self.sensor_sdk_audit())','            self._platform_sensor_sdk.append(self.sensor_sdk_audit())\n            self._d6proof.after_control()')
replace_once('    for step in range(args.steps):','    from gas_damping_actual_sdk_proof import ActualGasDampingProof\n    env._d6proof=ActualGasDampingProof(env)\n    for step in range(args.steps):')
replace_once("    result['D5_closed_loop_stiffness_engineering_pressure']=True","    result['D5_closed_loop_stiffness_engineering_pressure']=True\n    result['D6_actual_gas_damping_SDK']=env._d6proof.finish()")
compile(text,key,'exec');payload[key]=text.encode()
for n in ('gas_damping_factor.py','gas_damping_sdk_adapter.py','gas_damping_training_env.py','gas_damping_actual_sdk_proof.py'):
    raw=(D/n).read_bytes();compile(raw.decode(),n,'exec');payload['runtime/isaac/mod4/'+n]=raw
prior=read(E/'eval_queue/clk2500-closure-episode-d3-75-d5-b1-flat.json');checkpoint=prior['artifacts']['checkpoint']
assert checkpoint['sha256']=='9f865a7a75ed62d8fa704cae4dbe320f310f15e79269fd10ed84aa5462515b98' and sha(Path(checkpoint['path']))==checkpoint['sha256']
jobs=[]
for kind,profile in [('off','off'),('on','gas_damping_independent_episode_090_110_v1')]:
    env=json.loads(payload['runtime/isaac/mod4/env.json']);env['RM_GAS_DAMPING_PROFILE']=profile
    this=dict(payload);this['runtime/isaac/mod4/env.json']=json.dumps(env,indent=2).encode()
    manifest=dict(m,files={n:hashlib.sha256(b).hexdigest() for n,b in this.items()},base_D5_package_SHA=sha(base),
        D6_actual_gas_damping_SDK_only=True,D6_profile=profile,D5_damping_unchanged_recipe_superseded_by_D6=True)
    dest=E/'artifacts'/('d6-gas-damping-actual-sdk-'+kind+'-frozen.zip');assert not dest.exists()
    with zipfile.ZipFile(str(dest)+'.partial','w',zipfile.ZIP_DEFLATED) as z:
        for n,b in this.items():z.writestr(n,b)
        z.writestr('SOURCE_MANIFEST.json',json.dumps(manifest,indent=2))
    os.replace(str(dest)+'.partial',dest)
    job='clk2500-closure-episode-d3-80-d6-gas-sdk-'+kind
    row=dict(prior,job_id=job,published_epoch=time.time(),num_envs=10,steps=300,
        role='Actual D6 gas damping '+kind+' SDK 3s, independent .9-1.1*3Ns/m, selected reset/CUDA state; not skill graduation',
        artifacts=dict(runtime=dict(path=str(dest),sha256=sha(dest),bytes=dest.stat().st_size),checkpoint=checkpoint))
    target=E/'eval_queue'/(job+'.json');assert not target.exists()
    temp=target.with_suffix('.partial');temp.write_text(json.dumps(row,indent=2));os.replace(temp,target);jobs.append(row)
v=dict(epoch=time.time(),jobs=jobs,new_budget_seconds=0,no_4090_GPU_PPO_or_active_source_changes=True,
    D6_GPU_PPO_learning_deployed=False,SDK_pending=True,source_kind='D5 complete healthy and matched30649')
(D/'reports/D6_ACTUAL_DAMPING_SDK_PUBLISHED.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''
    compile(code,'actual D6 SDK publication','exec')
    _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=45)
    raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
    v=json.loads(raw);(R/'D6_ACTUAL_DAMPING_SDK_PUBLISHED.json').write_text(json.dumps(v,indent=2),encoding='utf8')
    print(json.dumps(dict(jobs=[dict(id=j['job_id'],package=j['artifacts']['runtime']) for j in v['jobs']],SDK_pending=True,new_budget_seconds=0)))
finally:c.close()
