"""Derive a read-only 2k shadow collector, preserving old actuator AST.
New information branch. Normal 100Hz packet/controller input is unchanged.
"""
from pathlib import Path
import ast
import hashlib
import json
R=Path(__file__).resolve().parent
D=R/'RAW2K_SHADOW_V1'
base=(R/'physics_bridge_v3.py').read_text(encoding='utf-8')
s=base.replace('from mesh_support import TireMeshSupport','from mesh_support import TireMeshSupport\nfrom RAW2K_SHADOW_V1.publisher import ShadowPublisher')
needle='self.rate_sum=np.zeros(6)'
assert s.count(needle)==1
s=s.replace(needle,needle+';self.raw2k_publisher=ShadowPublisher();self.raw2k_records=[];self.raw2k_shadow_frame=None')
needle='self.total_highrate_IMU_samples=0;self.rate_sum[:]=0.'
assert s.count(needle)==1
s=s.replace(needle,needle+';self.raw2k_publisher=ShadowPublisher();self.raw2k_records=[];self.raw2k_shadow_frame=None')
needle=' def sensor_packet(self):\n'
assert s.count(needle)==1
s=s.replace(needle,needle+'  self._raw2k_register_source()\n')
needle='self.last_packet=packet;self.imu_window_count=0'
assert s.count(needle)==1
s=s.replace(needle,'self.last_packet=packet;self.raw2k_shadow_frame=self.raw2k_publisher.publish(packet);self.raw2k_records=[];self.imu_window_count=0')
needle='self.rate_sum+=self.d.qvel[self.vids];mujoco.mj_step'
assert s.count(needle)==1
s=s.replace(needle,'private_raw=self._raw2k_before_step();'+needle)
needle='self.total_highrate_IMU_samples+=1'
assert s.count(needle)==1
s=s.replace(needle,needle+';self._raw2k_after_step(private_raw)')
s+='''
 def _raw2k_before_step(self):
  stamp=int(round(float(self.d.time)*1e6));q=self.d.qpos[self.qids].copy();qd=self.d.qvel[self.vids].copy()
  return dict(sampled_us=stamp,encoder_pos_sampled_us=stamp,encoder_rate_sampled_us=stamp,joint_pos4=q[[0,1,3,4]].copy(),joint_vel4=qd[[0,1,3,4]].copy(),wheel_vel2=qd[[2,5]].copy())
 def _raw2k_after_step(self,record):
  # mj_step reports dynamics-stage IMU at the PRE-step epoch, same as saved q/qd.
  record.update(gyro_body=self.d.sensor('base_gyro').data.copy(),accel_proper_body=self.d.sensor('base_acceleration').data.copy());self.raw2k_records.append(record)
 def _raw2k_register_source(self):
  epoch=int(round(float(self.d.time)*1e6));count=int(self.imu_window_count);endpoint=self.d.qpos[self.qids[[0,1,3,4]]].copy()
  if count:
   assert count==20 and len(self.raw2k_records)==20
   rates=self.rate_sum/count;clean_mean=dict(gyro_body=self.imu_omega_sum/count,accel_proper_body=self.imu_acc_sum/count,joint_vel4=rates[[0,1,3,4]],wheel_vel2=rates[[2,5]])
   self.raw2k_publisher.register(epoch,epoch-10000,self.raw2k_records,clean_mean,endpoint)
  else:
   record=self._raw2k_before_step();record.update(gyro_body=self.d.sensor('base_gyro').data.copy(),accel_proper_body=self.d.sensor('base_acceleration').data.copy());clean_mean={k:record[k]for k in('gyro_body','accel_proper_body','joint_vel4','wheel_vel2')};self.raw2k_publisher.register(epoch,epoch,[record],clean_mean,endpoint,instant=True)
'''
ast.parse(s)
def method(source,name):
    tree=ast.parse(source)
    cls=next(n for n in tree.body if isinstance(n,ast.ClassDef)and n.name=='BufferedImuPlant')
    return next(n for n in cls.body if isinstance(n,ast.FunctionDef)and n.name==name)
class RemoveReadOnlyHooks(ast.NodeTransformer):
    def visit_Assign(self,node):
        if len(node.targets)==1 and isinstance(node.targets[0],ast.Name)and node.targets[0].id=='private_raw':
            return None
        return self.generic_visit(node)
    def visit_Expr(self,node):
        if isinstance(node.value,ast.Call)and isinstance(node.value.func,ast.Attribute)and node.value.func.attr=='_raw2k_after_step':
            return None
        return self.generic_visit(node)
before=ast.dump(method(base,'apply_torque_request'),include_attributes=False)
after=ast.dump(RemoveReadOnlyHooks().visit(method(s,'apply_torque_request')),include_attributes=False)
assert before==after,'old actuation/contact/IMU-mean AST must remain exactly unchanged after removing collector hooks'
assert s.count('mujoco.mj_step(')==base.count('mujoco.mj_step(')==1
with(R/'physics_bridge_raw2k_v1.py').open('x',encoding='utf-8',newline='\n')as f:f.write(s)
g=(R/'physics_bridge_v4_grade.py').read_text(encoding='utf-8').replace('from physics_bridge_v3 import BufferedImuPlant as PreviousPlant','from physics_bridge_raw2k_v1 import BufferedImuPlant as PreviousPlant')
ast.parse(g)
with(R/'physics_bridge_raw2k_grade_v1.py').open('x',encoding='utf-8',newline='\n')as f:f.write(g)

s=(R/'run_heading_hold_case_v3.py').read_text(encoding='utf-8')
s=s.replace('from physics_bridge_v4_grade import BufferedImuPlant as RobustPlant','from physics_bridge_raw2k_grade_v1 import BufferedImuPlant as RobustPlant')
s=s.replace("ROOT/'physics_bridge_v4_grade.py',", "ROOT/'physics_bridge_v4_grade.py',ROOT/'physics_bridge_raw2k_v1.py',ROOT/'physics_bridge_raw2k_grade_v1.py',ROOT/'RAW2K_SHADOW_V1/publisher.py',")
needle="rows=StreamedRows(out/'trace.jsonl');p=None;"
assert s.count(needle)==1
s=s.replace(needle,"rows=StreamedRows(out/'trace.jsonl');shadow_rows=StreamedRows(out/'sensor_shadow.jsonl');p=None;")
needle=";grade_before=p.grade();p.apply_torque_request"
assert s.count(needle)==1
s=s.replace(needle,";shadow_rows.append(p.raw2k_shadow_frame);grade_before=p.grade();p.apply_torque_request")
needle="result['kinematic_radius_m']=chart.radius;"
assert s.count(needle)==1
s=s.replace(needle,"result['raw2k_shadow_artifact']=dict(path=str(shadow_rows.path),bytes=shadow_rows.bytes,SHA=shadow_rows.sha.hexdigest(),frames=len(shadow_rows),producer_streamed_once=True);result['raw2k_private_validation']=p.raw2k_publisher.receipt();result['shadow_raw_not_used_for_actuation']=True;result['new_information_shadow_branch_not_H4_or_hardware']=True;"+needle)
s=s.replace("trace_prefix_bytes=rows.bytes,no_samepurpose_retry=True", "trace_prefix_bytes=rows.bytes,shadow_prefix_rows=len(shadow_rows),shadow_prefix_SHA=shadow_rows.sha.hexdigest(),shadow_prefix_bytes=shadow_rows.bytes,no_samepurpose_retry=True")
s=s.replace('R36_NEW_PYTHON_heading_TRAIN_streamed_notC_H4_or_hardware','RAW2K_SHADOW_NEW_INFORMATION_NO_CHANGE_TO_100HZ_CONTROLLER')
ast.parse(s)
with(R/'run_raw2k_shadow_case_v1.py').open('x',encoding='utf-8',newline='\n')as f:f.write(s)
files=[]
for p in (Path(__file__),R/'physics_bridge_v3.py',R/'physics_bridge_v4_grade.py',R/'RAW2K_SHADOW_V1/publisher.py',R/'physics_bridge_raw2k_v1.py',R/'physics_bridge_raw2k_grade_v1.py',R/'run_raw2k_shadow_case_v1.py'):
    raw=p.read_bytes();files.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
with(D/'BRIDGE_PRECHECK.json').open('x',encoding='utf-8')as f:json.dump(dict(kind='DERIVED_READONLY_2K_COLLECTOR_AST_PRECHECK',physics_steps=0,actuation_AST_unchanged_after_removing_readonly_capture_hooks=True,actuation_AST_SHA=hashlib.sha256(before.encode()).hexdigest(),old_standard_100Hz_controller_input_unchanged_by_design=True,mean_preserving_correlated_branch_is_extra_information=True,source=files),f,indent=2)
print('RAW2K_DERIVED_BRIDGE_AST_MATCH_0PHYSICS_NEW_RUNNER_READY')
