"""Retain first tested adapter and test the separate current-frame COM adapter."""
from pathlib import Path
import json,sys,shlex,hashlib
D=Path(__file__).resolve().parent;R=D/'reports'
assert not (R/'CHASSIS_CURRENT_FRAME_TARGET_CPU_PASSED.json').exists()
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect();root='/home/egde/rl_candidates/MOD4_D7_COM_PD_PREPARE_20261009'
try:
 with c.open_sftp() as f:
  # First target CPU proof was for the constructor-frame adapter; keep those bytes separately.
  first=f.open(root+'/chassis_com_sdk_adapter.py').read()
  (R/'chassis_com_sdk_adapter_FIRST_CPU.py').write_bytes(first)
  frame=(D/'chassis_com_sdk_adapter.py').read_bytes()
  assert frame!=first and b'orientation_after_parent_reset' in frame
  (D/'chassis_com_frame_sdk_adapter.py').write_bytes(frame)
  (D/'chassis_com_sdk_adapter.py').write_bytes(first)
  test=(D/'test_chassis_com_adapter_cpu.py').read_text(encoding='utf8')
  test=test.replace('chassis_com_sdk_adapter','chassis_com_frame_sdk_adapter')
  test=test.replace("r=SimpleNamespace(body_names=", "r=SimpleNamespace(pose=pose,body_names=")
  needle="    state=a.state_dict();a.component.delta_m.zero_();a.load_state_dict(state);"
  assert test.count(needle)==1
  extra="    r.pose[ids,:,3:]=torch.tensor([0.,1.,0.,0.]);r.data.body_com_pose_b.copy_(r.pose)\n    env._reset_idx(ids)\n    assert torch.equal(r.root_view.get_coms()[ids,...,3:],torch.tensor([0.,1.,0.,0.]).expand(3,5,4))\n    a.audit_parameters();passed.append('current_D0_principal_axis_orientation_preserved_after_parent_reset')\n"
  test=test.replace(needle,extra+needle)
  (D/'test_chassis_current_frame_cpu.py').write_text(test,encoding='utf8')
  env=(D/'chassis_com_training_env.py').read_text(encoding='utf8')
  (R/'chassis_com_training_env_FIRST_DRAFT.py').write_text(env,encoding='utf8')
  env=env.replace('from chassis_com_sdk_adapter import','from chassis_com_frame_sdk_adapter import')
  (D/'chassis_com_frame_training_env.py').write_text(env,encoding='utf8')
  hashes={}
  for name in ('chassis_com_frame_sdk_adapter.py','chassis_com_frame_training_env.py','test_chassis_current_frame_cpu.py'):
   raw=(D/name).read_bytes();compile(raw.decode('utf8'),name,'exec');dest=root+'/'+name
   try:f.stat(dest)
   except FileNotFoundError:pass
   else:raise AssertionError('Existing frame source; do not rerun')
   with f.open(dest,'wb') as o:o.write(raw)
   assert f.open(dest).read()==raw;hashes[name]=hashlib.sha256(raw).hexdigest()
 code='import sys;sys.path.insert(0,'+repr('/home/egde/rl_candidates/MOD4_D6_FULL_CONTRACT_20261009/isaac/mod4')+');sys.path.insert(0,'+repr(root)+');from test_chassis_current_frame_cpu import test_contracts;import json,torch;print(json.dumps(dict(passed=test_contracts(),torch_version=torch.__version__,CUDA_initialized=torch.cuda.is_initialized(),actual_SDK=False)))'
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=30)
 raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
 v=json.loads(raw);assert len(v['passed'])==13 and not v['CUDA_initialized'];v['source_SHA']=hashes
 v['first_adapter_source_retained_SHA']=hashlib.sha256(first).hexdigest()
 (R/'CHASSIS_CURRENT_FRAME_TARGET_CPU_PASSED.json').write_text(json.dumps(v,indent=2),encoding='utf8')
 with c.open_sftp() as f:
  with f.open(root+'/reports/CHASSIS_CURRENT_FRAME_TARGET_CPU_PASSED.json','wb') as out:out.write((R/'CHASSIS_CURRENT_FRAME_TARGET_CPU_PASSED.json').read_bytes())
 print(json.dumps(v))
finally:c.close()
