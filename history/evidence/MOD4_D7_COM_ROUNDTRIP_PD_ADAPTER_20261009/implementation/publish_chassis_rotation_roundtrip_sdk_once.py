"""New COM-on interface validates physical rotation and records raw SDK normalization."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports';receipt=R/'D7_COM_ROTATION_ROUNDTRIP_SDK_PUBLISHED.json';assert not receipt.exists()
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 code=r'''
from pathlib import Path
import json,zipfile,hashlib,os,time
D=Path('/home/egde/rl_candidates/MOD4_D7_COM_PD_PREPARE_20261009');R=D/'reports';E=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
assert not (R/'D7_COM_ROTATION_ROUNDTRIP_SDK_PUBLISHED.json').exists()
cpu=read(R/'CHASSIS_POSE_ROUNDTRIP_TARGET_CPU_PASSED.json');assert len(cpu['passed'])==19 and not cpu['CUDA_initialized']
prior=read(E/'eval_queue/clk2500-closure-episode-d3-92-d7-com-buffer-sdk-on.json');base=Path(prior['artifacts']['runtime']['path']);assert sha(base)==prior['artifacts']['runtime']['sha256']
with zipfile.ZipFile(base) as z:
 m=json.loads(z.read('SOURCE_MANIFEST.json'));payload={n:z.read(n) for n in m['files']}
assert all(hashlib.sha256(payload[n]).hexdigest()==h for n,h in m['files'].items())
key='runtime/isaac/mod4/frozen_history_flat.py';t=payload[key].decode()
for old,new in [('from chassis_com_buffer_training_env import ChassisCOMMod4Env as ActionDelayMod4Env','from chassis_com_pose_roundtrip_training_env import ChassisCOMMod4Env as ActionDelayMod4Env'),('from chassis_com_actual_sdk_proof import ActualChassisCOMProof','from chassis_com_pose_roundtrip_sdk_proof import ActualChassisCOMProof')]:
 assert t.count(old)==1;t=t.replace(old,new)
compile(t,key,'exec');payload[key]=t.encode()
for name in ('chassis_com_pose_roundtrip_sdk_adapter.py','chassis_com_pose_roundtrip_training_env.py','chassis_com_pose_roundtrip_sdk_proof.py'):
 assert sha(D/name)==cpu['source_SHA'][name];payload['runtime/isaac/mod4/'+name]=(D/name).read_bytes()
manifest=dict(m,files={n:hashlib.sha256(b).hexdigest() for n,b in payload.items()},measured_float32_quaternion_normalization_recorded=True,physical_rotation_error_bound_from_dtype_precision=True,no_task_or_hardware_tolerance_changes=True)
dest=E/'artifacts/d7-chassis-com-rotation-roundtrip-on-frozen.zip';assert not dest.exists()
with zipfile.ZipFile(str(dest)+'.partial','w',zipfile.ZIP_DEFLATED) as z:
 for n,b in payload.items():z.writestr(n,b)
 z.writestr('SOURCE_MANIFEST.json',json.dumps(manifest,indent=2))
os.replace(str(dest)+'.partial',dest)
job='clk2500-closure-episode-d3-92-d7-com-rotation-roundtrip-sdk-on';row=dict(prior,job_id=job,published_epoch=time.time(),role='Actual COM-on +/-5mm: independent physical rotation audit, measured raw float32 normalization retained, no PD/PPO/new task threshold',artifacts=dict(prior['artifacts'],runtime=dict(path=str(dest),sha256=sha(dest),bytes=dest.stat().st_size)))
target=E/'eval_queue'/(job+'.json');assert not target.exists();temp=target.with_suffix('.partial');temp.write_text(json.dumps(row,indent=2));os.replace(temp,target)
v=dict(epoch=time.time(),job=row,all_original_failed_SDK_raws_preserved=True,successful91_off_reused=True,SDK_pending=True,production_GPU_PPO_or_canonical_changes=0)
(R/'D7_COM_ROTATION_ROUNDTRIP_SDK_PUBLISHED.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''
 _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=40);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
 v=json.loads(raw);receipt.write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(dict(job=v['job']['job_id'],package=v['job']['artifacts']['runtime'],no_task_or_hardware_tolerance_changes=True)))
finally:c.close()
