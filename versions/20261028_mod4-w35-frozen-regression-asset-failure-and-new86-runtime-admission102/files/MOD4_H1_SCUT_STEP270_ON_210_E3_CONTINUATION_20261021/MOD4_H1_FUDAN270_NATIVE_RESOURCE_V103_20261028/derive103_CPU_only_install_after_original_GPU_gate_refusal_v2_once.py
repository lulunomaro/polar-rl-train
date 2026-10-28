from pathlib import Path
import ast,json,time
N=Path(__file__).resolve().parent
s=(N/'install_two103_fudan270_source_SDK_initial_CPU_once.py').read_text('utf8')
old="assert line[0].strip()==gpu and line[1].strip()=='NVIDIA GeForce RTX 4090' and int(line[2])>15669 and gpu not in apps"
new="assert line[0].strip()==gpu and line[1].strip()=='NVIDIA GeForce RTX 4090'\n# CPU source admission does not initialize CUDA; actual training still requires\n# a fresh original idle-GPU/VRAM gate at the genuine scheduling boundary."
assert s.count(old)==1;s=s.replace(old,new)
s=s.replace("root=spec['job_root']","root=spec['job_root'].replace('MOD4_H1_FUDAN270_NATIVE_2610v103/','MOD4_H1_FUDAN270_CPU_ADMISSION_2610v103CPUv2/')")
s=s.replace("free_MiB=int(line[2]),RAM_available=","free_MiB=int(line[2]),selected_compute_UUID_output=apps,CPU_only_not_GPU_training_admission=True,RAM_available=")
s=s.replace("TWO103_INSTALL_SOURCE_SDK_CPU_ENTRY_CONSUMED_ACTUAL.json","TWO103_CPU_ONLY_V2_INSTALL_ENTRY_CONSUMED_ACTUAL.json")
s=s.replace("actual_finite_returned=True)","actual_finite_returned=True,actual_job_root=root)")
s=s.replace("TWO103_SOURCE_INSTALL_ORIGINAL_ERROR_ACTUAL.json","TWO103_CPU_ONLY_V2_INSTALL_ORIGINAL_ERROR_ACTUAL.json")
ast.parse(s)
with (N/'install_two103_CPU_only_source_SDK_initial_CPU_v2_once.py').open('x',encoding='utf8') as f:f.write(s)
with (N/'reports/CPU103_V2_PURPOSE_AFTER_GPU_PREFLIGHT_REFUSAL_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),original_GPU_preflight_refusal_preserved=True,original_refused_before_any_remote_directory_copy_model_or_GPU=True,new_purpose='CPU-only installed SDK and typed task/source admission',new_remote_namespace='MOD4_H1_FUDAN270_CPU_ADMISSION_2610v103CPUv2',CUDA_VISIBLE_DEVICES='',training_idle_GPU_VRAM_RAM_disk_allout_account_guards_still_required_fresh_before_GO=True,no_shared_account_write_no_GO=True),f,indent=2)
