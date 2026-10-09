"""Separate physical-rotation audit for measured PhysX float32 quaternion normalization."""
from pathlib import Path
import json,sys,shlex,hashlib
D=Path(__file__).resolve().parent;R=D/'reports';receipt=R/'CHASSIS_POSE_ROUNDTRIP_TARGET_CPU_PASSED.json';assert not receipt.exists()
helper='''
def verify_rotation_preserved(before,after):
    # PhysX normalizes supplied orientations in float32. Compare normalized double
    # rotations, with a bound derived solely from source dtype arithmetic precision.
    # Translation, mass/inertia and all task/hardware tolerances remain independent.
    if before.shape!=after.shape or before.dtype!=after.dtype:raise ValueError('Quaternion representation mismatch')
    if not bool(torch.isfinite(before).all()) or not bool(torch.isfinite(after).all()):raise AssertionError('Nonfinite quaternion')
    eps=torch.finfo(before.dtype).eps
    a=before.double();b=after.double();na=a.norm(dim=-1,keepdim=True);nb=b.norm(dim=-1,keepdim=True)
    assert bool(((na-1).abs()<=8*eps).all()) and bool(((nb-1).abs()<=8*eps).all()),'Quaternion must remain unit within dtype roundtrip precision'
    a=a/na;b=b/nb
    dot=(a*b).sum(-1,keepdim=True);b=torch.where(dot<0,-b,b)
    maxdiff=float((a-b).abs().max())
    assert maxdiff<=8*eps,('Actual physical orientation changed',maxdiff,eps)
    return dict(raw_quaternion_bytes_exact=torch.equal(before,after),raw_max_component_delta=float((before-after).abs().max()),
                normalized_double_quaternion_max_component_delta=maxdiff,dtype_epsilon=eps,
                rotation_preserved_within_dtype_roundtrip=True,no_task_or_hardware_tolerance_change=True)
'''
old=(D/'chassis_com_buffer_sdk_adapter.py').read_text(encoding='utf8')
adapter=old.replace('class ChassisCOMSDK:',helper+'\nclass ChassisCOMSDK:')
adapter=adapter.replace('        self.setter_calls=0;self.reset_calls=0;self.cache_invalidations=0','        self.setter_calls=0;self.reset_calls=0;self.cache_invalidations=0;self.orientation_roundtrip_max=0.;self.raw_quaternion_bytes_always_exact=True')
needle='            assert torch.equal(tensor(self.robot.root_view.get_coms()).to(expected.device)[...,3:],before_orientation)'
assert adapter.count(needle)==1
adapter=adapter.replace(needle,'''            after=tensor(self.robot.root_view.get_coms()).to(expected.device).clone()
            proof=verify_rotation_preserved(before_orientation,after[...,3:])
            self.orientation_roundtrip_max=max(self.orientation_roundtrip_max,proof['normalized_double_quaternion_max_component_delta'])
            self.raw_quaternion_bytes_always_exact &= proof['raw_quaternion_bytes_exact']
            # Adopt the independently checked actual normalized representation for exact
            # subsequent buffer/backend audit; never adopt an unchecked physical rotation.
            self.orientation_after_parent_reset[ids]=after[ids,...,3:]
            self.robot.data._body_com_pose_b.timestamp=-float('inf')
            assert torch.equal(tensor(self.robot.data.body_com_pose_b).to(expected.device),after)''')
adapter=adapter.replace('other_body_COM_quaternions_unchanged=True,','other_body_physical_rotations_preserved=True,raw_quaternion_bytes_always_exact=self.raw_quaternion_bytes_always_exact,normalized_rotation_roundtrip_max=self.orientation_roundtrip_max,')
env=(D/'chassis_com_buffer_training_env.py').read_text(encoding='utf8').replace('chassis_com_buffer_sdk_adapter','chassis_com_pose_roundtrip_sdk_adapter')
env=env.replace('original_quaternion_mass_inertia_PD_preserved=True','original_physical_orientation_mass_inertia_PD_preserved=True,raw_float32_quaternion_normalization_recorded=True')
proof=(D/'chassis_com_actual_sdk_proof.py').read_text(encoding='utf8')
proof=proof.replace('from chassis_com_component import ChassisCOM','from chassis_com_component import ChassisCOM\nfrom chassis_com_pose_roundtrip_sdk_adapter import verify_rotation_preserved')
proof=proof.replace("            assert torch.equal(after['local'][...,3:],before['local'][...,3:])", "            rotations=verify_rotation_preserved(before['local'][...,3:],after['local'][...,3:])")
proof=proof.replace('only_chassis_translation_changes=True,current_all_body_quaternions_exact=True,','only_chassis_translation_changes=True,current_all_body_quaternions_exact=rotations[\'raw_quaternion_bytes_exact\'],physical_rotations_preserved_float32_roundtrip=rotations,')
proof=proof.replace("            for key in ('local','mass','inertia','q','qd'):assert torch.equal(before[key],after[key]),key", "            for key in ('mass','inertia','q','qd'):assert torch.equal(before[key],after[key]),key\n            assert torch.equal(before['local'][...,:3],after['local'][...,:3])\n            rotations=verify_rotation_preserved(before['local'][...,3:],after['local'][...,3:])")
proof=proof.replace('same_tick_actor_and_actual_COM_joint_state_exact=True,','same_tick_actor_COM_translation_joint_state_exact=True,physical_rotations_preserved_float32_roundtrip=rotations,')
test=(D/'test_chassis_buffer_cpu.py').read_text(encoding='utf8').replace('chassis_com_buffer_sdk_adapter','chassis_com_pose_roundtrip_sdk_adapter')
test=test.replace('    return passed', '''    from chassis_com_pose_roundtrip_sdk_adapter import verify_rotation_preserved
    q=torch.tensor([[.035981763154268265,.32348647713661194,.10452976077795029,.9397527575492859]])
    after=torch.tensor([[.03598176687955856,.3234865069389343,.10452977567911148,.9397528767585754]])
    p=verify_rotation_preserved(q,after);assert not p['raw_quaternion_bytes_exact'];passed.append('measured_PhysX_float32_normalization_geometric_equivalence')
    assert verify_rotation_preserved(q,-q)['rotation_preserved_within_dtype_roundtrip'];passed.append('quaternion_sign_equivalent_rotation')
    bad=q.clone();bad[0,0]+=.001
    try:verify_rotation_preserved(q,bad/bad.norm(dim=-1,keepdim=True))
    except AssertionError:pass
    else:raise AssertionError('Physical orientation change was accepted')
    passed.append('actual_orientation_change_rejected')
    try:verify_rotation_preserved(q,q*1.001)
    except AssertionError:pass
    else:raise AssertionError('Nonunit quaternion accepted')
    passed.append('nonunit_parameter_change_rejected')
    try:verify_rotation_preserved(q,q*float('nan'))
    except AssertionError:pass
    else:raise AssertionError('Nonfinite orientation accepted')
    passed.append('nonfinite_orientation_rejected')
    return passed''')
sources={'chassis_com_pose_roundtrip_sdk_adapter.py':adapter,'chassis_com_pose_roundtrip_training_env.py':env,'chassis_com_pose_roundtrip_sdk_proof.py':proof,'test_chassis_pose_roundtrip_cpu.py':test}
for name,value in sources.items():assert not (D/name).exists();compile(value,name,'exec');(D/name).write_text(value,encoding='utf8')
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect();root='/home/egde/rl_candidates/MOD4_D7_COM_PD_PREPARE_20261009'
try:
 with c.open_sftp() as f:
  hashes={}
  for name in sources:
   raw=(D/name).read_bytes();dest=root+'/'+name
   try:f.stat(dest)
   except FileNotFoundError:pass
   else:raise AssertionError('New roundtrip source already exists; never rerun')
   with f.open(dest,'wb') as o:o.write(raw)
   assert f.open(dest).read()==raw;hashes[name]=hashlib.sha256(raw).hexdigest()
 code='import sys;sys.path.insert(0,'+repr('/home/egde/rl_candidates/MOD4_D6_FULL_CONTRACT_20261009/isaac/mod4')+');sys.path.insert(0,'+repr(root)+');from test_chassis_pose_roundtrip_cpu import test_contracts;import json,torch;print(json.dumps(dict(passed=test_contracts(),torch_version=torch.__version__,CUDA_initialized=torch.cuda.is_initialized(),actual_SDK=False)))'
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=30);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
 v=json.loads(raw);assert len(v['passed'])==19 and not v['CUDA_initialized'];v['source_SHA']=hashes;v['actual_SDK_pending']=True;v['all_original_failures_retained']=True
 receipt.write_text(json.dumps(v,indent=2),encoding='utf8')
 with c.open_sftp() as f:
  with f.open(root+'/reports/'+receipt.name,'wb') as o:o.write(receipt.read_bytes())
 print(json.dumps(v))
finally:c.close()
