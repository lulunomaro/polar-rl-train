"""Separate SDK cache repair. Preserve all already published frame-adapter bytes."""
from pathlib import Path
import json,sys,shlex,hashlib
D=Path(__file__).resolve().parent;R=D/'reports'
receipt=R/'CHASSIS_BUFFER_REFRESH_TARGET_CPU_PASSED.json';assert not receipt.exists()
old=(D/'chassis_com_frame_sdk_adapter.py').read_text(encoding='utf8')
needle='        expected=self.expected_full_pose()\n        if self.component.enabled:'
assert old.count(needle)==1
addition='''        expected=self.expected_full_pose()
        # D0 can change inertia/principal-axis orientation without advancing simulation time.
        # Installed set_coms_index writes partial body data into a cached full-row buffer,
        # then sends that FULL selected-environment row to PhysX. Refresh the read cache
        # first so unrelated current body orientations cannot be overwritten by stale data.
        self.robot.data._body_com_pose_b.timestamp=-float('inf')
        current=tensor(self.robot.root_view.get_coms()).to(expected.device)
        refreshed=tensor(self.robot.data.body_com_pose_b).to(expected.device)
        assert torch.equal(current,refreshed),'Full-row COM buffer must reflect current PhysX before partial write'
        assert torch.equal(current[...,3:],self.orientation_after_parent_reset)
        if self.component.enabled:'''
adapter=old.replace(needle,addition)
env=(D/'chassis_com_frame_training_env.py').read_text(encoding='utf8').replace('chassis_com_frame_sdk_adapter','chassis_com_buffer_sdk_adapter')
test=(D/'test_chassis_current_frame_cpu.py').read_text(encoding='utf8').replace('chassis_com_frame_sdk_adapter','chassis_com_buffer_sdk_adapter')
test=test.replace('    data=SimpleNamespace(body_com_pose_b=pose.clone())', '''    class Data:
        def __init__(self):
            self._body_com_pose_b=SimpleNamespace(data=pose.clone(),timestamp=5.)
        @property
        def body_com_pose_b(self):
            if self._body_com_pose_b.timestamp<5.:
                self._body_com_pose_b.data.copy_(pose);self._body_com_pose_b.timestamp=5.
            return self._body_com_pose_b.data
    data=Data()''')
needle2='        pose[ids[:,None],torch.tensor(bid)[None,:]]=p;data.body_com_pose_b.copy_(pose);r.writes.append((ids.clone(),p.clone()))'
assert test.count(needle2)==1
test=test.replace(needle2,'''        # Mirror installed setter: update cached selected body, send FULL selected row.
        data._body_com_pose_b.data[ids[:,None],torch.tensor(bid)[None,:]]=p
        pose[ids]=data._body_com_pose_b.data[ids];r.writes.append((ids.clone(),p.clone()))''')
test=test.replace('    r.pose[ids,:,3:]=torch.tensor([0.,1.,0.,0.]);r.data.body_com_pose_b.copy_(r.pose)', '''    r.pose[ids,:,3:]=torch.tensor([0.,1.,0.,0.])
    assert not torch.equal(r.data._body_com_pose_b.data,r.pose)
    passed.append('same_tick_parent_orientation_changes_leave_stale_full_row_cache')''')
test=test.replace("'current_D0_principal_axis_orientation_preserved_after_parent_reset'", "'same_tick_refresh_prevents_full_row_orientation_clobber'")
sources={'chassis_com_buffer_sdk_adapter.py':adapter,'chassis_com_buffer_training_env.py':env,'test_chassis_buffer_cpu.py':test}
for name,value in sources.items():
    assert not (D/name).exists();compile(value,name,'exec');(D/name).write_text(value,encoding='utf8')
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect();root='/home/egde/rl_candidates/MOD4_D7_COM_PD_PREPARE_20261009'
try:
 with c.open_sftp() as f:
  hashes={}
  for name in sources:
   raw=(D/name).read_bytes();dest=root+'/'+name
   try:f.stat(dest)
   except FileNotFoundError:pass
   else:raise AssertionError('Existing new buffer-review source; never rerun')
   with f.open(dest,'wb') as o:o.write(raw)
   assert f.open(dest).read()==raw;hashes[name]=hashlib.sha256(raw).hexdigest()
 code='import sys;sys.path.insert(0,'+repr('/home/egde/rl_candidates/MOD4_D6_FULL_CONTRACT_20261009/isaac/mod4')+');sys.path.insert(0,'+repr(root)+');from test_chassis_buffer_cpu import test_contracts;import json,torch;print(json.dumps(dict(passed=test_contracts(),torch_version=torch.__version__,CUDA_initialized=torch.cuda.is_initialized(),actual_SDK=False)))'
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=30)
 raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
 v=json.loads(raw);assert len(v['passed'])==14 and not v['CUDA_initialized'];v['source_SHA']=hashes
 v['original91_failed_source_preserved']=True;v['installed_full_row_setter_and_same_tick_cache_contract_checked']=True
 receipt.write_text(json.dumps(v,indent=2),encoding='utf8')
 with c.open_sftp() as f:
  with f.open(root+'/reports/'+receipt.name,'wb') as o:o.write(receipt.read_bytes())
 print(json.dumps(v))
finally:c.close()
