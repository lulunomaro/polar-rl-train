"""New immutable read-only chassis/PD SDK job; no trainer or canonical writes."""
from pathlib import Path
import json,shlex,sys
D=Path(__file__).resolve().parent; R=D/'reports';R.mkdir(exist_ok=True)
assert not (R/'D7_NOMINAL_SDK_PUBLISHED.json').exists()
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect();root='/home/egde/rl_candidates/MOD4_D7_COM_PD_PREPARE_20261009'
try:
 with c.open_sftp() as f:
  for p in (root,root+'/reports'):
   try:f.mkdir(p)
   except IOError:
    assert f.stat(p)
  raw=(D/'chassis_pd_nominal_readback.py').read_bytes()
  dest=root+'/chassis_pd_nominal_readback.py'
  try:
   existing=f.open(dest).read();assert existing==raw
  except FileNotFoundError:
   with f.open(dest,'wb') as o:o.write(raw)
  assert f.open(dest).read()==raw
 code=r'''
from pathlib import Path
import json,zipfile,hashlib,os,time
D=Path('/home/egde/rl_candidates/MOD4_D7_COM_PD_PREPARE_20261009');R=D/'reports'
E=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007');N=Path('/home/egde/rl_candidates/MOD4_D6_FULL_CONTRACT_20261009')
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (R/'D7_NOMINAL_SDK_PUBLISHED.json').exists()
approval=read(E/'reports/PLAN_APPROVAL.json');assert approval['approved'] and 'S0E' in approval['allowed_stages'] and 'S2' in approval['allowed_stages']
base=E/'artifacts/d6-clock2500-solver32-gas265-closedloop-frozen.zip'
assert sha(base)=='0f51e024c9f5c2cc7448b814203e2f21c810618fb246138c7cdcab92a5dbb3c7'
with zipfile.ZipFile(base) as z:
 m=json.loads(z.read('SOURCE_MANIFEST.json'));payload={n:z.read(n) for n in m['files']}
assert all(hashlib.sha256(payload[n]).hexdigest()==h for n,h in m['files'].items())
key='runtime/isaac/mod4/frozen_history_flat.py';original=payload[key];t=original.decode()
needle='    for step in range(args.steps):';assert t.count(needle)==1
t=t.replace(needle,'    from chassis_pd_nominal_readback import read_chassis_pd\n    D7_initial=read_chassis_pd(env)\n    D7_contact_start=env._integrated_contact.tick\n'+needle)
needle="    result['D6_closed_loop_gas_damping_engineering_pressure']=True";assert t.count(needle)==1
t=t.replace(needle,needle+"\n    result['D7_nominal_chassis_PD_initial']=D7_initial\n    result['D7_nominal_chassis_PD_final']=read_chassis_pd(env)\n    result['D7_actual_contact_callbacks']=env._integrated_contact.tick-D7_contact_start\n    assert result['D7_actual_contact_callbacks']==args.steps*4\n    assert result['D7_nominal_chassis_PD_initial']['static']==result['D7_nominal_chassis_PD_final']['static']\n    result['D7_read_only_nominal_SDK']=True")
compile(t,key,'exec');payload[key]=t.encode();payload['runtime/isaac/mod4/chassis_pd_nominal_readback.py']=(D/'chassis_pd_nominal_readback.py').read_bytes()
manifest=dict(m,files={n:hashlib.sha256(b).hexdigest() for n,b in payload.items()},base_D6_archive_SHA=sha(base),D7_only_readback_no_parameter_writes=True)
archive=E/'artifacts/d7-chassis-explicit-pd-nominal-readback-sdk-frozen.zip';assert not archive.exists()
with zipfile.ZipFile(str(archive)+'.partial','w',zipfile.ZIP_DEFLATED) as z:
 for n,b in payload.items():z.writestr(n,b)
 z.writestr('SOURCE_MANIFEST.json',json.dumps(manifest,indent=2))
os.replace(str(archive)+'.partial',archive)
passed=read(N/'reports/d6_stable_block1_PASSED.json'); source=passed['checkpoint']
assert sha(Path(source['path']))=='df0654a6eaf7c62933b869043a340333391f60b44fae184ef0bb458c1f1fc4e5'==source['sha256']
artifact=E/'artifacts'/('d7-sdk-source-'+source['sha256']+'.pt')
assert not artifact.exists(); import shutil;shutil.copy2(source['path'],artifact);assert sha(artifact)==source['sha256']
checkpoint=dict(path=str(artifact),sha256=sha(artifact),bytes=artifact.stat().st_size)
row=read(E/'eval_queue/clk2500-closure-episode-d3-85-d6-gas-anchor-flat.json')
job='clk2500-closure-episode-d3-88-d7-chassis-pd-nominal-sdk'
row.update(job_id=job,published_epoch=time.time(),num_envs=10,steps=300,role='Read-only actual chassis link COM frame/index/mass fraction and explicit PD model versus zero implicit motor drives; not D7 randomization or skill graduation',artifacts=dict(runtime=dict(path=str(archive),sha256=sha(archive),bytes=archive.stat().st_size),checkpoint=checkpoint))
dest=E/'eval_queue'/(job+'.json');assert not dest.exists(); temp=dest.with_suffix('.partial');temp.write_text(json.dumps(row,indent=2));os.replace(temp,dest)
v=dict(epoch=time.time(),job=row,read_only_parameter_setter_calls=0,production265_and_canonical_unchanged=True,D7_learning_authority=False,actual_SDK_pending=True)
(R/'D7_NOMINAL_SDK_PUBLISHED.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''
 compile(code,'new D7 read-only SDK publication','exec')
 _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
 v=json.loads(raw);(R/'D7_NOMINAL_SDK_PUBLISHED.json').write_text(json.dumps(v,indent=2),encoding='utf8')
 print(json.dumps(dict(job=v['job']['job_id'],package=v['job']['artifacts']['runtime'],no_PPO_canonical_or_parameter_writes=True)))
finally:c.close()
