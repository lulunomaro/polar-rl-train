"""Preserve actual inertia within the original frozen D0 numerical audit, retain raw deltas."""
from pathlib import Path
import sys,json,shlex,hashlib
D=Path(__file__).resolve().parent;R=D/'reports';receipt=R/'D7_COM_INERTIA_ROUNDTRIP_SDK_PUBLISHED.json';assert not receipt.exists()
reference=(R/'PD_REFERENCE_mild_dr.py').read_bytes()
assert hashlib.sha256(reference).hexdigest()=='a8c4fb06f16dbad215b3a380420909a80680f9819d9bdcfbf5f816061222fb7e'
assert b"checks['inertia_absolute_error'] < 1e-6" in reference
proof=(D/'chassis_com_pose_roundtrip_sdk_proof.py').read_text(encoding='utf8')
assert proof.count("for key in ('mass','inertia','q','qd'):assert torch.equal(before[key],after[key]),key")==2
proof=proof.replace("            for key in ('mass','inertia','q','qd'):assert torch.equal(before[key],after[key]),key", "            for key in ('mass','q','qd'):assert torch.equal(before[key],after[key]),key\n            inertia_error=float((before['inertia'].double()-after['inertia'].double()).abs().max())\n            assert inertia_error<1e-6,('COM setter inertia roundtrip exceeds original frozen D0 tolerance',inertia_error)\n            inertia_raw_exact=torch.equal(before['inertia'],after['inertia'])")
proof=proof.replace('mass_inertia_joint_state_D5_D6_and_global_RNG_unchanged=True,','mass_joint_state_D5_D6_global_RNG_exact_inertia_original_tolerance_pass=True,raw_inertia_bytes_exact=inertia_raw_exact,inertia_absolute_roundtrip_error=inertia_error,original_frozen_D0_inertia_tolerance=1e-6,')
proof=proof.replace('same_tick_actor_COM_translation_joint_state_exact=True,','same_tick_actor_COM_translation_joint_state_exact=True,raw_inertia_bytes_exact=inertia_raw_exact,inertia_absolute_roundtrip_error=inertia_error,original_frozen_D0_inertia_tolerance=1e-6,')
compile(proof,'chassis_com_inertia_roundtrip_sdk_proof.py','exec');assert not (D/'chassis_com_inertia_roundtrip_sdk_proof.py').exists();(D/'chassis_com_inertia_roundtrip_sdk_proof.py').write_text(proof,encoding='utf8')
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 with c.open_sftp() as f:
  path='/home/egde/rl_candidates/MOD4_D7_COM_PD_PREPARE_20261009/chassis_com_inertia_roundtrip_sdk_proof.py'
  try:f.stat(path)
  except FileNotFoundError:pass
  else:raise AssertionError('New proof already staged; never rerun')
  raw=(D/'chassis_com_inertia_roundtrip_sdk_proof.py').read_bytes()
  with f.open(path,'wb') as o:o.write(raw)
  assert f.open(path).read()==raw
 code=r'''
from pathlib import Path
import json,zipfile,hashlib,os,time
D=Path('/home/egde/rl_candidates/MOD4_D7_COM_PD_PREPARE_20261009');R=D/'reports';E=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
assert not (R/'D7_COM_INERTIA_ROUNDTRIP_SDK_PUBLISHED.json').exists()
prior=read(E/'eval_queue/clk2500-closure-episode-d3-92-d7-com-rotation-roundtrip-sdk-on.json');base=Path(prior['artifacts']['runtime']['path']);assert sha(base)==prior['artifacts']['runtime']['sha256']
with zipfile.ZipFile(base) as z:
 m=json.loads(z.read('SOURCE_MANIFEST.json'));payload={n:z.read(n) for n in m['files']}
assert all(hashlib.sha256(payload[n]).hexdigest()==h for n,h in m['files'].items())
reference=payload['runtime/isaac/mod4/mild_dr.py'];assert hashlib.sha256(reference).hexdigest()=='a8c4fb06f16dbad215b3a380420909a80680f9819d9bdcfbf5f816061222fb7e' and b"checks['inertia_absolute_error'] < 1e-6" in reference
key='runtime/isaac/mod4/frozen_history_flat.py';t=payload[key].decode();old='from chassis_com_pose_roundtrip_sdk_proof import ActualChassisCOMProof';assert t.count(old)==1;t=t.replace(old,'from chassis_com_inertia_roundtrip_sdk_proof import ActualChassisCOMProof');compile(t,key,'exec');payload[key]=t.encode()
payload['runtime/isaac/mod4/chassis_com_inertia_roundtrip_sdk_proof.py']=(D/'chassis_com_inertia_roundtrip_sdk_proof.py').read_bytes()
manifest=dict(m,files={n:hashlib.sha256(b).hexdigest() for n,b in payload.items()},raw_inertia_roundtrip_delta_recorded=True,original_frozen_D0_inertia_1e6_audit_unchanged=True,no_production_or_task_hardware_tolerance_changes=True)
dest=E/'artifacts/d7-chassis-com-inertia-roundtrip-on-frozen.zip';assert not dest.exists()
with zipfile.ZipFile(str(dest)+'.partial','w',zipfile.ZIP_DEFLATED) as z:
 for n,b in payload.items():z.writestr(n,b)
 z.writestr('SOURCE_MANIFEST.json',json.dumps(manifest,indent=2))
os.replace(str(dest)+'.partial',dest)
job='clk2500-closure-episode-d3-92-d7-com-inertia-roundtrip-sdk-on';row=dict(prior,job_id=job,published_epoch=time.time(),role='Actual COM-on SDK: physical quaternion preserved; raw inertia roundtrip reported and original frozen D0 tolerance unchanged; mass/joint/RNG exact',artifacts=dict(prior['artifacts'],runtime=dict(path=str(dest),sha256=sha(dest),bytes=dest.stat().st_size)))
target=E/'eval_queue'/(job+'.json');assert not target.exists();temp=target.with_suffix('.partial');temp.write_text(json.dumps(row,indent=2));os.replace(temp,target)
v=dict(epoch=time.time(),job=row,all_original_failed_SDK_raws_preserved=True,successful91_off_reused=True,SDK_pending=True,original_frozen_D0_inertia_tolerance_unchanged=True,production_GPU_PPO_or_canonical_changes=0)
(R/'D7_COM_INERTIA_ROUNDTRIP_SDK_PUBLISHED.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''
 _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=40);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
 v=json.loads(raw);receipt.write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(dict(job=v['job']['job_id'],package=v['job']['artifacts']['runtime'],original_audit_tolerance_unchanged=True)))
finally:c.close()
