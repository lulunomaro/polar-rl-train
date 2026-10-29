"""Source metadata and parameter-free normalizer fixture, never load a checkpoint."""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
from pathlib import Path
import ast,copy,hashlib,json,time,sys,traceback
N=Path(__file__).resolve().parent;R=N/'reports';B=N/'payloads_v2/seed27';T=N.parent
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def main():
 put('SOURCE114_V2_Task_GO_CPU_CONSUMED_BEFORE_ANY_MODEL.json',dict(epoch=time.time(),model_reads=0,source_only=True))
 spec=read(R/'NEW114_V2_ONE_SOURCE111_TYPED_PAYLOAD_PREPARED_NOT_ADMITTED_ACTUAL.json');m=read(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');c=read(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json');task=spec['task'];rows={x['relative']:x for x in m['files']}
 assert H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')==spec['manifest_SHA']
 assert set(c['approved_python'])=={p.relative_to(B).as_posix() for p in B.rglob('*.py')}
 for rel,sha in c['approved_python'].items():assert H(B/rel)==sha==rows[rel]['SHA'];ast.parse((B/rel).read_bytes())
 assert all(rows[k]['SHA']==v for k,v in c['protected_current88C_files'].items())
 prior=read(T/'MOD4_H1_FUDAN270_REWARD_COHERENCE_RESOURCE_V111_20261029/payloads_v2/seed27/FLAT90_SOURCE_CONTRACT_ACTUAL.json')['protected_current88C_files']
 changed=[k for k in prior if prior[k]!=c['protected_current88C_files'][k]]
 assert changed==['source/supermimic_wheel_leg_v3/augmented_wheel_leg_world_model_v1.py'] and len(prior)==1252
 sys.path[:0]=[str(B),str(B/'source')]
 from native_flat90_source_guard_v1 import validate_task_go
 from native114_WM_heading_pins_v1 import NATIVE_CONTRACT,SOURCE_PINS
 go=copy.deepcopy(task);go.update(payload_manifest_SHA=spec['manifest_SHA'],num_envs=4096,max_parent_seconds=3900,exit_headroom_seconds=300)
 validate_task_go(task,go,spec['manifest_SHA'])
 rejected=[]
 for field in ('candidate_WM_source_SHA','original_WM_source_SHA','source_CPU_report_SHA','input_width','changed_input_columns','raw_cue_scale','actual_target_norm_and_input_readback_required'):
  bad=copy.deepcopy(go);bad['fudan_step_task']['world_model_input_heading'][field]='WRONG'
  try:validate_task_go(task,bad,spec['manifest_SHA'])
  except (ValueError,AssertionError):rejected.append(field)
  else:raise AssertionError('new heading Task/GO not bound '+field)
 for field in ('source_SHA','source_progress','native_learning_seed','native_reference_SHA','source_qualification_kind'):
  bad=copy.deepcopy(go);bad[field]='WRONG'
  try:validate_task_go(task,bad,spec['manifest_SHA'])
  except (ValueError,AssertionError,TypeError):rejected.append(field)
  else:raise AssertionError('source Task/GO not bound '+field)
 # Check the actual selected new readback helper using no learned parameters.
 import torch
 torch.set_num_threads(2)
 from supermimic_wheel_leg_v3.augmented_wheel_leg_world_model_v1 import AugmentedWheelLegWorldModel,WheelLegStateLayout
 from supermimic_wheel_leg_v3.networks import RunningNorm
 from wm114_actual_input_norm_readback_cpu_v1 import check
 class NoNetwork(torch.nn.Module):
  terrain_relative=AugmentedWheelLegWorldModel.terrain_relative
  inputs=AugmentedWheelLegWorldModel.inputs
  def __init__(self):
   super().__init__();self.layout=WheelLegStateLayout();self.action_dim=6;self.context_dim=31;self.edge_x_m=.35;self.platform_top_z_m=.27
   self.in_norm=RunningNorm(167);self.out_norm=RunningNorm(126,eps=1e-4)
   self.in_norm.var.zero_()
 wm=NoNetwork();p=torch.tensor([[.1,0.,.38],[.2,0.,.35]]);state=(p,torch.eye(3).expand(2,-1,-1),torch.zeros(2,3),torch.zeros(2,3),torch.zeros(2,30),torch.zeros(2,30),torch.zeros(2,54))
 helper=check(wm,state,torch.zeros(2,31));assert helper['passed'] and not list(wm.parameters()) and not torch.cuda.is_initialized()
 from compact_episode_static31_v1 import normalize_static31
 assert normalize_static31(torch.zeros(2,31)).shape==(2,31)
 entry=ast.parse((B/'source/native_flat5cm_training_entry_candidate_v4_typed_producer.py').read_bytes())
 values={x.arg:x.value.value for x in ast.walk(entry) if isinstance(x,ast.keyword) and x.arg in ('private_phase_frame_source_SHA','real_callback_counter_source_SHA','source_reference_artifact_SHA') and isinstance(x.value,ast.Constant)}
 assert values['source_reference_artifact_SHA']==SOURCE_PINS['producer']['reference_artifact_SHA']==task['native_reference_SHA']
 assert values['private_phase_frame_source_SHA']==H(B/'source/private_phase_frame_v1.py') and values['real_callback_counter_source_SHA']==H(B/'h1_step270_sdk_runtime_candidate.py')
 assert task['native_learning_seed']==task['native_seed']==27 and task['source_progress']==dict(updates=18597,world_updates=185970,policy_updates=17893)
 put('SOURCE114_V2_PREINSTALL_TASK_GO_HELPER_PRODUCER_CPU_ACTUAL.json',dict(passed=True,epoch=time.time(),negative_fields_rejected=rejected,source_Python_files_verified=len(c['approved_python']),protected_entries1252_declared_changed_only_WM=changed,other1251_protected_rows_unchanged=True,actual_selected_paramfree_readback_helper_fixture=helper,source_producer_three_literal_pins=values,original111_input_reference_and_new_output_reference_from_actual_publication=True,model_or_binary_reads=0,no_actual_SDK_GPU_GO_yet=True))
 print(json.dumps(dict(passed=True,negative_checks=len(rejected),no_model_or_binary_reads=True)))
if __name__=='__main__':
 try:main()
 except BaseException:put('SOURCE114_V2_PREINSTALL_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),traceback=traceback.format_exc(),model_reads=0,no_target_SDK_GPU_GO=True));raise
