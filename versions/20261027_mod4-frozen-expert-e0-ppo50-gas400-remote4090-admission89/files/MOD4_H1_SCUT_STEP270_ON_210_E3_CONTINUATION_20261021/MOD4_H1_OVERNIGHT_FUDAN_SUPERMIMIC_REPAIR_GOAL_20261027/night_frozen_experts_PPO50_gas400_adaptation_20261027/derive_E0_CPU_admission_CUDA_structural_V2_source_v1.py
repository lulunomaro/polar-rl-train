"""Retain failedCPU readerV1; do not reinterpret CUDA RNG bytes as CPU RNG."""
from pathlib import Path
import ast,hashlib,importlib.util,json,time
HERE=Path(__file__).resolve().parent
def H(raw):return hashlib.sha256(raw).hexdigest()
HELPER='''
def validate_original_CUDA_queue_structure_CPU(queue,state):
 # Keep all existing queue field/timestamp/lag checks. Omit ONLY the attempt
 # to load a saved CUDA RNG codec into a CPUGenerator. Do not substitute
 # fabricated CPU RNG bytes and do not claim actual CUDA restore here.
 import inspect,textwrap,hashlib
 import torch
 module=__import__(type(queue).__module__,fromlist=['FIELDS','WIDTHS'])
 source=textwrap.dedent(inspect.getsource(type(queue).validate_state))
 old="        generator=torch.Generator(device=self.device);generator.set_state(state['rng'][key].cpu())"
 new="        value=state['rng'][key]\\n        assert torch.is_tensor(value) and value.device.type=='cpu' and value.dtype==torch.uint8 and value.ndim==1 and value.numel()==16, 'Original source-specific CUDA RNG byte structure differs'"
 assert source.count(old)==1
 structural=source.replace(old,new)
 scope=dict(torch=torch,FIELDS=module.FIELDS,WIDTHS=module.WIDTHS)
 exec(compile(structural,'<actual queue validator: CPU structural only>','exec'),scope)
 untouched={key:value.clone() for key,value in state['rng'].items()}
 assert scope['validate_state'](queue,state) is True
 assert all(torch.equal(state['rng'][key],value) for key,value in untouched.items())
 return dict(validator_scope='CPU queue fields/timestamps/lag and original CUDA uint8[16] byte structure only',
             original_validator_source_SHA=hashlib.sha256(source.encode()).hexdigest(),
             structural_validator_source_SHA=hashlib.sha256(structural.encode()).hexdigest(),
             original_CUDA_rng_bytes_untouched=True,CPU_generator_set_state_not_called=True,
             CPU_rng_substitution_used=False,actual_CUDA_generator_restore_passed=False,
             actual_worker_CUDA_restore_still_mandatory=True)

'''
def main():
 old=HERE/'E0_target_source_SDK_CPU_admission_v1.py';new=HERE/'E0_target_source_SDK_CPU_admission_v2_CUDA_structural_only.py'
 raw=old.read_bytes();assert H(raw)=='9784ef7b9f6561f51c834128461273b3f1fe0580fa4caad6cbeed53cb87154fa'
 s=raw.decode();assert s.count('def main():')==1;s=s.replace('def main():',HELPER+'def main():')
 before="queue=PhysicsActionQueue(20000,'cpu',20260928,control_us=20000);queue.validate_state(ck['physical_action_delay_state'])"
 after="queue=PhysicsActionQueue(20000,'cpu',20260928,control_us=20000);queue_structure_proof=validate_original_CUDA_queue_structure_CPU(queue,ck['physical_action_delay_state'])"
 assert s.count(before)==1;s=s.replace(before,after)
 s=s.replace("report=root/'E0_SOURCE_SDK_CPU_ADMISSION_ACTUAL_V1.json'","report=root/'E0_SOURCE_SDK_CPU_ADMISSION_ACTUAL_V2.json'")
 before="queue20ms_state_CPU_valid=True,reset_bank_source_CPU=reset"
 after="queue20ms_fields_CPU_structurally_valid=True,queue_structure_proof=queue_structure_proof,admission_reader_version='V2_CUDA_structural_only',reset_bank_source_CPU=reset"
 assert s.count(before)==1;s=s.replace(before,after)
 ast.parse(s);assert not new.exists();new.write_text(s,encoding='utf8')
 # Synthetic component fixture only. No model/normalizer/USD/NPZ is opened.
 import sys,torch
 torch.set_num_threads(2);rng=torch.get_rng_state().clone()
 runtime=HERE/'E0_runtime50_gas400_candidate_v1/isaac/mod4';sys.path.insert(0,str(runtime))
 from action_delay_physics_queue import PhysicsActionQueue
 queue=PhysicsActionQueue(3,'cpu',20260928,control_us=20000);state=queue.state_dict()
 state['rng']={key:torch.arange(16,dtype=torch.uint8) for key in state['rng']}
 spec=importlib.util.spec_from_file_location('CPU_admission_V2_structural_fixture',new);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 proof=module.validate_original_CUDA_queue_structure_CPU(queue,state)
 cases=[]
 import copy
 for name,mutate in [('wrong_control_us',lambda z:z.update(control_us=10000)),
                     ('wrong_CUDA_rng_width',lambda z:z['rng'].update(legs=torch.zeros(5056,dtype=torch.uint8))),
                     ('wrong_CUDA_rng_dtype',lambda z:z['rng'].update(legs=torch.zeros(16,dtype=torch.float32))),
                     ('lag_outside_original_range',lambda z:z['groups']['legs']['lag_steps'].fill_(3)),
                     ('nonfinite_pending_target',lambda z:z['groups']['legs']['pending'].fill_(float('nan')))]:
  bad=copy.deepcopy(state);mutate(bad)
  try:module.validate_original_CUDA_queue_structure_CPU(queue,bad)
  except AssertionError:cases.append(name)
  else:raise AssertionError(name+' admitted')
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 report=dict(attempt_id='E0_CPU_READER_CUDA16_TO_CPU5056_CODEC_ERROR_REPAIRED_STRUCTURAL_ONLY_20261027_V2',epoch=time.time(),
  failed_original_reader_V1=dict(path=str(old),bytes=len(raw),SHA=H(raw)),
  original_actual_error_path=str(HERE.parents[1]/'MOD4_E0_PPO50_GAS400_REMOTE4090_RESOURCE_V89B_20261027/reports/E0_SOURCE_SDK_CPU_ORIGINAL_ERROR_1793097776553402500.json'),
  original_error='CPU PhysicsActionQueue.validate_state attempted CPUGenerator.set_state(original saved CUDA uint8[16]); CPU expected5056bytes. After initial newtyped CPU load; noGPU/Task/GO/fee.',
  V2=dict(path=str(new),bytes=new.stat().st_size,SHA=H(new.read_bytes())),
  fix='Run the exact installed queue field validator with only the CUDA-to-CPU Generator.set_state statement replaced by source-specific uint8[16] structural checks. Original CUDA bytes are not replaced/mutated.',
  fixture=dict(kind='synthetic3envqueue+syntheticCUDA-shaped bytes, not real CUDA RNG restoration',proof=proof,rejected_cases=cases),
  actual_CUDA_generator_restore_still_pending=True,actual_worker_full_CUDA_restore_required=True,
  all_other_source_core_Adam_LR_D1_D7_USD_and_SDK_checks_unchanged=True,no_old_or_new_model_or_asset_read=True,
  no_GPU_remote_GO_or_accountwrite=True,CPU_global_RNG_unchanged=True,Git_status='pending_root_ordinary_supplement')
 p=HERE/'reports/E0_CPU_ADMISSION_V2_CUDA_STRUCTURAL_FIXTURE_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(report,indent=2),encoding='utf8')
 (HERE/'E0_CPU_ADMISSION_V2_CUDA_STRUCTURAL_HANDOFF.md').write_text('''# E0 CPU admission V2 preserves original CUDA RNG

Actual89B V1 failed after the first newtyped CPU checkpoint load, before GPU scene/Task/GO/fee, because its CPU queue validator tried to load original CUDA16byte RNG state into a CPUGenerator requiring5056bytes. Keep that V1/error and source checkpoint unchanged.

V2 performs CPU structural validation only. It derives the actual queue validator and retains every existing field/shape/dtype/finite/lag/timestamp/ordering check, replacing only the CUDA-to-CPU Generator.set_state statement with uint8[16] structural validation and explicit unchanged-byte proof. No fabricated CPU RNG is substituted into the checkpoint; no CUDA restoration is claimed. The worker must still execute the original real CUDA queue load/Generator.set_state and full D1-D7/private/global RNG restore.

Use `CUDA_VISIBLE_DEVICES='' <actual_remote_python> -u -B E0_target_source_SDK_CPU_admission_v2_CUDA_structural_only.py --job-root <new_unused_root>`. It produces E0_SOURCE_SDK_CPU_ADMISSION_ACTUAL_V2.json. All other typed checkpoint/core/Adam/LR, original manifest, pressure/damping/COM-PD, exact reset-bank and actual USD CPU composition checks remain unchanged. Bind the actual V2 reportSHA to sole72 TASK/GO source_CPU_SHA, and retain E0 workerV3 SHA1858c6395083bb7104385ec82d3dce6db4f79898a6346a250916ad7217524152. New real source admission may reuse the already verified installed bytes in a new unused namespace; no model or producerhash was reread for this source repair/Git. Pending root ordinary supplementation.
''',encoding='utf8')
 print(json.dumps(dict(V2=report['V2'],synthetic_CPU_fields_passed=True,negative_cases=cases,original_CUDA_bytes_untouched=True,actual_CUDA_restore_passed=False)))
if __name__=='__main__':main()
