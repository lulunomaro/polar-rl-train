"""Publish one new corrected COM-on SDK; successful91-off is reused exactly."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports';receipt=R/'D7_COM_BUFFER_SDK_PUBLISHED.json';assert not receipt.exists()
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 code=r'''
from pathlib import Path
import json,zipfile,hashlib,os,time
D=Path('/home/egde/rl_candidates/MOD4_D7_COM_PD_PREPARE_20261009');R=D/'reports';E=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
assert not (R/'D7_COM_BUFFER_SDK_PUBLISHED.json').exists()
cpu=read(R/'CHASSIS_BUFFER_REFRESH_TARGET_CPU_PASSED.json');assert len(cpu['passed'])==14 and not cpu['CUDA_initialized']
prior=read(E/'eval_queue/clk2500-closure-episode-d3-91-d7-com-sdk-on.json');base=Path(prior['artifacts']['runtime']['path'])
assert sha(base)==prior['artifacts']['runtime']['sha256']=='54b058f63a1818aa2fb3f2f04c71c6c412e424fc89ac37fbfff21b08dfe57045'
with zipfile.ZipFile(base) as z:
 m=json.loads(z.read('SOURCE_MANIFEST.json'));payload={n:z.read(n) for n in m['files']}
assert all(hashlib.sha256(payload[n]).hexdigest()==h for n,h in m['files'].items())
key='runtime/isaac/mod4/frozen_history_flat.py';t=payload[key].decode();needle='from chassis_com_frame_training_env import ChassisCOMMod4Env as ActionDelayMod4Env'
assert t.count(needle)==1;t=t.replace(needle,'from chassis_com_buffer_training_env import ChassisCOMMod4Env as ActionDelayMod4Env');compile(t,key,'exec');payload[key]=t.encode()
for name in ('chassis_com_buffer_sdk_adapter.py','chassis_com_buffer_training_env.py'):
 raw=(D/name).read_bytes();assert sha(D/name)==cpu['source_SHA'][name];payload['runtime/isaac/mod4/'+name]=raw
manifest=dict(m,files={n:hashlib.sha256(b).hexdigest() for n,b in payload.items()},base91_on_SHA=sha(base),same_tick_COM_buffer_refresh_review=True,successful91_off_reused=True)
dest=E/'artifacts/d7-chassis-com-buffer-reviewed-on-frozen.zip';assert not dest.exists()
with zipfile.ZipFile(str(dest)+'.partial','w',zipfile.ZIP_DEFLATED) as z:
 for n,b in payload.items():z.writestr(n,b)
 z.writestr('SOURCE_MANIFEST.json',json.dumps(manifest,indent=2))
os.replace(str(dest)+'.partial',dest)
job='clk2500-closure-episode-d3-92-d7-com-buffer-sdk-on';row=dict(prior,job_id=job,published_epoch=time.time(),role='New COM-on SDK: refresh current full-row PhysX COM read buffer before selected partial setter; original91 failure retained, successfuloff reused',artifacts=dict(prior['artifacts'],runtime=dict(path=str(dest),sha256=sha(dest),bytes=dest.stat().st_size)))
target=E/'eval_queue'/(job+'.json');assert not target.exists();temp=target.with_suffix('.partial');temp.write_text(json.dumps(row,indent=2));os.replace(temp,target)
v=dict(epoch=time.time(),job=row,original91_failed_held_not_replayed=True,successful91_off_exactly_reused=True,SDK_pending=True,production_GPU_PPO_canonical_changes=0)
(R/'D7_COM_BUFFER_SDK_PUBLISHED.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''
 _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=40);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
 v=json.loads(raw);receipt.write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(dict(job=v['job']['job_id'],package=v['job']['artifacts']['runtime'],no_training_or_budget_change=True)))
finally:c.close()
