"""Retained native COM witness + exact SDK arithmetic review. CPU only."""
from pathlib import Path
import ast,hashlib,importlib.util,json,time,traceback
import torch
W=Path('C:/Users/lulu/Desktop/claude/mjcf');D=W/'MOD4_4090_WINDOWS_TEMP20GB_20261013';O=D/'cpu_review'
S=W/'MOD4_4090_WINDOWS_REPAIR_20261013/repair_payload/CPU_SOURCE_ASSEMBLY_FIXTURE_V5_FINAL_BOUND_SOURCE/sdk_exact/source/isaaclab/isaaclab'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),bytes=Path(p).stat().st_size,sha256=H(p))
def main():
 assert not torch.cuda.is_initialized()
 proof_path=D/'reports/COM_JIT_SAVED_WITNESS_V11_ACTUAL.json';proof=json.loads(proof_path.read_bytes())
 math=S/'utils/math.py';asset=S/'assets/articulation/articulation_data.py'
 assert H(math)==proof['math_source']['sha256']=='260c7248653e26e7e4563031a50208fef5098eb69c50b3a9fcf264e0e766a899'
 tree=ast.parse(math.read_text(encoding='utf8'));names=('quat_mul','quat_apply','combine_frame_transforms')
 funcs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names];assert len(funcs)==3
 for f in funcs:assert any(ast.unparse(x)=='torch.jit.script' for x in f.decorator_list)
 code='import torch\nfrom typing import Optional, Tuple\n'+'\n\n'.join(ast.unparse(n) for n in funcs)
 cp=O/'independently_frozen_SDK_arithmetic_COM_v11_CPU.py'
 assert not cp.exists();cp.write_text(code,encoding='utf8');compile(code,str(cp),'exec')
 assert H(cp)==proof['frozen_arithmetic']['sha256']
 spec=importlib.util.spec_from_file_location('COM_repr_CPU_v11_exact',cp);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 articulation=ast.parse(asset.read_text(encoding='utf8'));cls=next(n for n in articulation.body if isinstance(n,ast.ClassDef) and n.name=='ArticulationData')
 com=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='body_com_pose_w')
 comtxt=ast.unparse(com)
 assert 'math_utils.combine_frame_transforms(self.body_link_pos_w, self.body_link_quat_w, self.body_com_pos_b, self.body_com_quat_b)' in comtxt
 assert 'torch.cat((pos, quat), dim=-1)' in comtxt
 cpu_rng=torch.get_rng_state().clone();rows=[]
 for version in (9,10):
  path=D/('native128_COM_failure_witness_v'+str(version)+'.pt');witness=torch.load(path,map_location='cpu',weights_only=False)
  assert all(r['witness_sha256']==H(path) for r in proof['rows'] if r['version']==version)
  for phase,row in witness.items():
   link=row['link_pose_wxyz'].float();local=row['local_COM_pose_wxyz'].float();actual=row['world_COM_pos']
   expected_cold,_=m.combine_frame_transforms(link[...,:3],link[...,3:7],local[...,:3],local[...,3:7])
   for _ in range(8):expected_warm,_=m.combine_frame_transforms(link[...,:3],link[...,3:7],local[...,:3],local[...,3:7])
   # Eager API operation order equals the scripted source expression, but has
   # different backend optimization semantics. Actualoutput is only compared.
   q=link[...,3:7].reshape(-1,4);v=local[...,:3].reshape(-1,3);xyz=q[:,1:];t=xyz.cross(v,dim=-1)*2
   eager=link[...,:3]+(v+q[:,0:1]*t+xyz.cross(t,dim=-1)).view(local[...,:3].shape)
   cold=(expected_cold.double()-actual).abs();warm=(expected_warm.double()-actual).abs();eager_error=(eager.double()-actual).abs()
   pos=int(eager_error.reshape(-1).argmax());flat_actual=actual.reshape(-1)[pos].float();ulp=(torch.nextafter(flat_actual,torch.full_like(flat_actual,float('inf')))-flat_actual).abs().item()
   rows.append(dict(version=version,phase=phase,control=row['control'],callback=row['callback'],witness=ref(path),env_ids=row['env_ids'],CPU_float32_script_cold_vs_GPU_saved_m=float(cold.max()),CPU_float32_script_warm_vs_GPU_saved_m=float(warm.max()),CPU_eager_vs_GPU_saved_m=float(eager_error.max()),CPU_eager_vs_CPU_script_m=float((eager-expected_warm).abs().max()),max_CPU_eager_error_at_world_coordinate=float(flat_actual),world_float32_ULP_m=ulp,original_observer_saved_COM_error_m=float(row['COM_error'].max()),comparison_GPU_pass_not_inferred_from_CPU=True))
 assert torch.equal(cpu_rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 asset_ast_SHA=hashlib.sha256(ast.unparse(com).encode()).hexdigest()
 report=dict(epoch=time.time(),CPU_review_completed=True,source_refs=[ref(math),ref(asset),ref(cp),ref(proof_path)],exact_AST_clone_SHA_matches_root_actual_CUDA_math_probe=True,body_COM_property_AST_SHA=asset_ast_SHA,retained_CPU_witness_replay=rows,
  actual_root_CUDA_math_evidence=proof,
  interpretation=dict(root_retained_first_last_v9_v10_math_replay_error_zero=True,expected_operands_only_link_pose_and_local_COM=True,actual_world_COM_never_used_to_choose_expected=True,source_same_wxyz_shape_dtype_and_operation_order=True,original_COM_tolerance_m=1e-5,old_eager_or_double_false_not_relabelled=True,unrounded_double_discrepancy_must_remain_diagnostic=True,SDK_derived_representation_consistency_only=True,independent_physical_COM_or_hardware_calibration_not_proven=True),
  minimal_new_observer_fix=['Freeze these3 exact sourceAST TorchScript functions into an independently saved companion; bind its sourceSHA and actualSDKmathSHA in manifest/sourcefreeze.','Call the frozen combine_frame_transforms with actual link and local COM float32 inputs, including local quaternion, same device/shape/stride conventions. Compare its represented translation against stored worldCOM under unchanged1e-5.','Optionally warm frozen arithmetic8 times before attaching callback audit using current link/local inputs; this is pure arithmetic only, no step/reset/obs/RNG. Record cold and warm math values diagnostically so JIT profiling phase is explicit.','Retain actual native-localCOM vsSDKbuffer exact check, original COM link velocity/hardware/contact checks, and unrounded-double COM diagnostic. Do not loosen any tolerance or use actualCOM output to select algorithm.'],
  caveats=['The SDK worldCOM buffer is itself derived from the same link/local operands; an exact clone checks representation, timestamps, frame and buffer consistency, not independently calibrated physical COM.','TorchScript CUDA fusion, profiling warmup, device, dtype, rank and strides can change rounding. CPU equality cannot establish liveGPU allcallback correctness; rootactual CUDA savedwitness proof covers only the retained rows.','Rootmath probe recorded final output after8 additional calls, not a separatecold output. New observerlive initialcalls should not be labelled already allcallbackpassed.','Original failuresv9/v10 remain failed scopes. Mathematical replay alone is not a physics/PPO/native admission or full50mm route certificate.'])
 path=O/('COM_JIT_REPRESENTATION_CPU_INTERPRETATION_V11_'+str(time.time_ns())+'.json');path.write_text(json.dumps(report,indent=2),encoding='utf8')
 print(json.dumps(dict(report=str(path),sha256=H(path),frozen_arithmetic=ref(cp),CPU_completed=True,original_tol_unchanged=True,no_GPU=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  (O/('COM_REVIEW_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_no_network=True),indent=2),encoding='utf8');raise
