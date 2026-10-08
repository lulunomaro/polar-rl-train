"""Publish one genuinely new read-only joint-property SDK inspection on3060."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports';assert not (R/'D6_NOMINAL_JOINT_SDK_PUBLISHED.json').exists()
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect();root='/home/egde/rl_candidates/MOD4_D6_DAMPING_SOURCE_PREPARE_20261008'
try:
 with c.open_sftp() as f:
  raw=(D/'nominal_damping_joint_readback.py').read_bytes()
  with f.open(root+'/nominal_damping_joint_readback.py','wb') as o:o.write(raw)
  assert f.open(root+'/nominal_damping_joint_readback.py').read()==raw
 code=r'''
from pathlib import Path
import json,zipfile,hashlib,os,time
D=Path('/home/egde/rl_candidates/MOD4_D6_DAMPING_SOURCE_PREPARE_20261008');E=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007');read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=read(E/'reports/PLAN_APPROVAL.json');assert a['approved'] and 'S0E' in a['allowed_stages'] and 'S2' in a['allowed_stages']
base=E/'artifacts/d5-clock2500-solver32-spring255-closedloop-frozen.zip';assert sha(base)=='fe8dc6bcb027215739a9edf7a8b5fa46240326b402e05ae0d0463db87044452c'
with zipfile.ZipFile(base) as z:
 m=json.loads(z.read('SOURCE_MANIFEST.json'));payload={n:z.read(n) for n in m['files']}
assert all(hashlib.sha256(payload[n]).hexdigest()==h for n,h in m['files'].items())
key='runtime/isaac/mod4/frozen_history_flat.py';text=payload[key].decode();needle='    for step in range(args.steps):';assert text.count(needle)==1
text=text.replace(needle,"    from nominal_damping_joint_readback import read_joint_parameters\n    joint_parameters_initial=read_joint_parameters(env)\n    contact_tick_start=env._integrated_contact.tick\n"+needle)
needle="    result['D5_closed_loop_stiffness_engineering_pressure']=True";assert text.count(needle)==1
text=text.replace(needle,needle+"\n    result['D6_nominal_joint_parameters_initial']=joint_parameters_initial\n    result['D6_nominal_joint_parameters_final']=read_joint_parameters(env)\n    result['D6_actual_contact_callback_delta']=env._integrated_contact.tick-contact_tick_start\n    assert result['D6_actual_contact_callback_delta']==args.steps*4\n    assert result['D6_nominal_joint_parameters_initial']==result['D6_nominal_joint_parameters_final']\n    result['D6_nominal_joint_property_inspection_only']=True")
compile(text,key,'exec');payload[key]=text.encode();payload['runtime/isaac/mod4/nominal_damping_joint_readback.py']=(D/'nominal_damping_joint_readback.py').read_bytes()
manifest=dict(m,files={n:hashlib.sha256(b).hexdigest() for n,b in payload.items()},base_D5_package_SHA=sha(base),D6_read_only_joint_parameters=True,D6_damping_randomization=False)
dest=E/'artifacts/d6-nominal-damping-friction-readback-sdk-frozen.zip';assert not dest.exists()
with zipfile.ZipFile(str(dest)+'.partial','w',zipfile.ZIP_DEFLATED) as z:
 for n,b in payload.items():z.writestr(n,b)
 z.writestr('SOURCE_MANIFEST.json',json.dumps(manifest,indent=2))
os.replace(str(dest)+'.partial',dest)
source=read(E/'eval_queue/clk2500-closure-episode-d3-70-d5-anchor-flat.json')['artifacts']['checkpoint'];assert sha(Path(source['path']))==source['sha256']
package=dict(path=str(dest),sha256=sha(dest),bytes=dest.stat().st_size)
row=read(E/'eval_queue/clk2500-closure-episode-d3-70-d5-anchor-flat.json')
job='clk2500-closure-episode-d3-71-d6-nominal-joint-sdk';row.update(job_id=job,published_epoch=time.time(),num_envs=10,steps=300,role='New read-only installedSDK PhysX and buffers joint static-dynamic-viscous friction and gas damping inspection; not D6 DR or skill graduation',artifacts=dict(runtime=package,checkpoint=source))
target=E/'eval_queue'/(job+'.json');assert not target.exists();temp=target.with_suffix('.partial');temp.write_text(json.dumps(row,indent=2));os.replace(temp,target)
v=dict(epoch=time.time(),job=row,D6_parameter_writes=0,D6_GPU_PPO_training_deployed=False,4090_runtime_and_canonical_unchanged=True,SDK_pending=True)
(D/'reports/D6_NOMINAL_JOINT_SDK_PUBLISHED.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''
 # Python identifiers cannot start with digits; the property name remains an explicit JSON key.
 code=code.replace('4090_runtime_and_canonical_unchanged=True','production_runtime_and_canonical_unchanged=True')
 compile(code,'D6 nominal reader publication','exec')
 _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=40);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');v=json.loads(raw)
 (R/'D6_NOMINAL_JOINT_SDK_PUBLISHED.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(dict(job=v['job']['job_id'],package=v['job']['artifacts']['runtime'],SDK_pending=True)))
finally:c.close()
