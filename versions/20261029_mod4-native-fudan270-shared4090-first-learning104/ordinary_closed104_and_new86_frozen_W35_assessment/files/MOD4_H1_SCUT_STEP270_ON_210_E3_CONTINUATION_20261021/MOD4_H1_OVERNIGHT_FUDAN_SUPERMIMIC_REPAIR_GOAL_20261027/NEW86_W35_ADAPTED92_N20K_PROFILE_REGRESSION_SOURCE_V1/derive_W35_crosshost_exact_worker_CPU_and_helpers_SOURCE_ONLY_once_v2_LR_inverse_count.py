"""Small-code derivation only; no source model, USD, bank or remote reads."""
from pathlib import Path
import ast,hashlib,json,time
B=Path(__file__).resolve().parent;L=B.parent
def H(x):return hashlib.sha256(x).hexdigest()
def main():
 source=L/'W35_210_V2_PRECLOSE_EXCEPTION_DIAGNOSTIC_SOURCE_V1/evaluate_W35_adapted92_originalN20K_frozen_profiles_once_v1.py';raw=source.read_bytes();assert H(raw)=='6b88da01def5676f95cdbfa523d7d90b0fe8afff473683ce8bc44a4db8e63a48';new=raw;ops=[]
 def replace(a,b,count=1):
  nonlocal new
  a=a.encode();b=b.encode();assert new.count(a)==count,(a,new.count(a));new=new.replace(a,b);ops.append((a,b))
 replace('GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e','GPU-90a66ae2-f536-7033-79c0-487536ae36d3')
 replace('MOD4_W35_ADAPTED92_ORIGINAL_N20K_FROZEN_PROFILES_V1','MOD4_W35_ADAPTED92_NEW86_ORIGINAL_N20K_FROZEN_PROFILES_V1')
 replace('actual_source210_SDK_admission_passed','actual_target86_SDK_admission_passed')
 replace("assert task['actual_target86_SDK_admission_passed']", "assert H(job/'W35_SOURCE_SDK_CPU_ADMISSION_ACTUAL_V1.json')==task['actual_CPU_report_SHA'] and H(job/'W35_NEW86_CPU_ORIGINAL_WAIT_PROOF.json')==task['actual_CPU_waited_proof_SHA'];cpu_wait=read(job/'W35_NEW86_CPU_ORIGINAL_WAIT_PROOF.json');assert cpu_wait['actual_waited'] and cpu_wait['returncode']==0 and cpu_wait['passed']\n assert task['actual_target86_SDK_admission_passed']")
 back=new
 for a,b in reversed(ops):assert back.count(b)==1;back=back.replace(b,a)
 assert back==raw;ast.parse(new);((B/source.name).read_bytes()==new or (_ for _ in ()).throw(AssertionError('existing worker differs'))) if (B/source.name).exists() else (B/source.name).write_bytes(new)
 cpu_source=L/'W35_PPO50_gas400_source_preparation_20261027/W35_target_source_SDK_CPU_admission_v1.py';cpu_old=cpu_source.read_bytes();cpu=cpu_old;cpu_ops=[]
 def cp(a,b,count=1):
  nonlocal cpu
  a=a.encode();b=b.encode();assert cpu.count(a)==count,(a,cpu.count(a));cpu=cpu.replace(a,b);cpu_ops.append((a,b))
 cp('36825921fb3e4a368791be7802c8ff16977e899240ac21ed2c067b2287bb9393','ad504fec819b22f10fd1caf7befc59c1988c7609fe15373ab8851ef95942df3f')
 cp('MOD4_W35_PPO50_GAS400_FULLSTATE_SOURCE_CPU_V1','MOD4_W35_ADAPTED92_NEW86_CROSSHOST_FULLSTATE_SOURCE_CPU_V1')
 cp('W35_PPO50_gas400_finite_worker_v1.py','evaluate_W35_adapted92_originalN20K_frozen_profiles_once_v1.py')
 cp('W35_N20K_PPO50_GAS400_SOURCE_NOT_GPU_ADMITTED.pt','W35_ADAPTED92_FINAL78.pt')
 cp("ck['iter']==32259","ck['iter']==32336")
 cp('{646800}','{648360}')
 cp('.00001','.00011390625000000003',3)
 cp("assert ck['spring_pressure_recipe']['nominal_stiffness_N_m']==2000", "assert ck['PPO50_gas400_new_updates']==78 and ck['PPO50_gas400_clock']==dict(policy_hz=50,physics_dt_s=.0025,decimation=8,feedback_hz=100,gamma=.9801,lam=.9025)\n assert ck['spring_pressure_recipe']['nominal_stiffness_N_m']==2000")
 cp('W35_TARGET_SOURCE_SDK_CPU_20261027_V1','W35_ADAPTED92_NEW86_TARGET_INITIAL_WHOLE_CPU_20261029_V1')
 cp("assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()", """copy_root=Path(os.environ['MOD4_PROVEN_CLONE_ROOT']).resolve()
 assert versions=={'torch':'2.10.0+cu128','rsl-rl-lib':'5.0.1','isaacsim':'6.0.1.0','isaaclab':'6.1.14'} and all(Path(x).resolve().is_relative_to(copy_root) for x in modules.values())
 installed=json.loads((root/'W35_NEW86_COMPLETE_INPUT_MANIFEST_V1.json').read_bytes());rsl=Path(modules['rsl_rl']).parent;lab=Path(modules['isaaclab']).parent
 for item in installed['RSL_sources']:assert (rsl/item['relative']).stat().st_size==item['bytes'] and H(rsl/item['relative'])==item['SHA']
 assert H(lab/'utils/math.py')==installed['SDK_math_SHA']
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()""")
 back=cpu
 for a,b in reversed(cpu_ops):assert back.count(b)>=1;back=back.replace(b,a)
 assert back==cpu_old;ast.parse(cpu);(B/'W35_new86_target_FINAL92_source_SDK_CPU_admission_v1.py').write_bytes(cpu)
 proven=L/'NORMAL_H1_NEW86_PROJECT_WHOLECPU_NATIVE24_ADMISSION_SOURCE_V2_LIGHT_POLICY/remote_project_source_and_waited_admission_v2_user_light_GPU.py';tree=ast.parse(proven.read_bytes());functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('H','own_identity','environment','argv')];assert len(functions)==4
 module=ast.Module(body=ast.parse("from pathlib import Path\nimport hashlib,os\nGPU='GPU-90a66ae2-f536-7033-79c0-487536ae36d3'\n").body+functions,type_ignores=[]);ast.fix_missing_locations(module);helper=(ast.unparse(module)+'\n').encode();ast.parse(helper);(B/'project_clone_launch_helpers_v1.py').write_bytes(helper)
 proof=dict(epoch=time.time(),source_only=True,worker_old_SHA=H(raw),worker_new_SHA=H(new),worker_exact_reverse_bytes=True,worker_changes=[dict(old=a.decode(),new=b.decode()) for a,b in ops],original_entire_profile_loop_DR_RNG_reset_task_reward_coverage_and_error_paths_unchanged=True,CPU_old_source_SHA=H(cpu_old),CPU_new_source_SHA=H(cpu),CPU_exact_reverse_bytes=True,CPU_changes=[dict(old=a.decode(),new=b.decode()) for a,b in cpu_ops],clone_launch_helpers_same_AST_as_actual_passed_new86_source=True,no_model_USD_NPZ_raw_or_remote_read=True)
 (B/'W35_NEW86_EXACT_CROSSHOST_SOURCE_DERIVATION_ONLY.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(worker_SHA=H(new),CPU_SHA=H(cpu),source_only=True)))
if __name__=='__main__':main()
