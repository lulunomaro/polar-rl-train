from pathlib import Path
import ast,json,time
N=Path(__file__).resolve().parent
s=(N/'remote188_postcopy_CPU_and_native_admission.txt').read_text(encoding='utf8')
s=s.replace('20261031v188/seed27','20261031v188_v2/seed27')
s=s.replace("assert {n:s/.02 for n,s in k.reward_scales.items()}==t['reward_selected16']", "from literal_stairs3_original_config import OriginalStairs3Cfg,class_to_dict\nassert class_to_dict(OriginalStairs3Cfg.rewards.scales)==t['reward_selected16']")
ast.parse(s);(N/'remote188V2_postcopy_CPU_and_native_admission.txt').write_text(s,encoding='utf8')
s=(N/'install188_literal_STAIRS3_native_admission_once.py').read_text(encoding='utf8')
s=s.replace('20261031v188/seed27','20261031v188_v2/seed27').replace('ROOT188ADMIT_','ROOT188ADMITV2_').replace('remote188_postcopy_CPU_and_native_admission.txt','remote188V2_postcopy_CPU_and_native_admission.txt').replace('install188_literal_STAIRS3_native_admission_once','install188_literal_STAIRS3_native_admission_V2_once')
ast.parse(s);(N/'install188_literal_STAIRS3_native_admission_V2_once.py').write_text(s,encoding='utf8')
with (N/'reports/ROOT188_ADMISSION_V1_CPU_FLOAT_DIVIDE_CHECK_FALSE_RETAINED.json').open('x',encoding='utf8') as f:
 json.dump(dict(epoch=time.time(),original_target_CPU_returncode=1,original_CPU_error='AssertionError <string> line8; comparing Python weights after multiply and divide by dt with exact float equality',GPU_or_App_entered=False,model_reads=0,training_started=False,original_source_reward_not_changed=True,repair='Distinct V2 caller checks original literal class_to_dict reward table, already pinned by sourceSHA and text identity. No reward, Task, physics, guard or model change.',original_report='ROOT188ADMIT_ORIGINAL_TARGET_FROZEN_EVAL_RETURNED_ACTUAL.json'),f,indent=2)
