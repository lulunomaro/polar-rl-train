from pathlib import Path
import ast
N=Path(__file__).resolve().parent;T=N.parent
old=T/'DELIVERED_JUMP4999_TOTAL_PLAN_400N50_DR_270_CHECK_V187_20261031/V2_EXISTING_NORMALIZED_CLOCK_AND_FEEDBACK_SOURCE/install_evaluate187_totalplan_frozen_once.py'
s=old.read_text(encoding='utf8')
s=s.replace("T=N.parent.parent;W=T.parent;","T=N.parent;W=T.parent;")
s=s.replace('MOD4_DELIVERED4999_PLAN40050_DR_STEP270_EVAL_20261031v187_v2','MOD4_FUDAN_STAIRS3_LITERAL_400N50_20261031v188/seed27')
s=s.replace('FROZEN_EVAL187_COMPLETE_MANIFEST.json','TRAIN188_COMPLETE_MANIFEST.json')
s=s.replace('remote187_postcopy_and_frozen_eval.txt','remote188_postcopy_CPU_and_native_admission.txt')
s=s.replace('ROOT187V2_','ROOT188ADMIT_').replace('install_evaluate187_totalplan_frozen_once','install188_literal_STAIRS3_native_admission_once')
s=s.replace('new_GPU_model_decodes=1','new_GPU_model_decodes=0').replace('old_H1_models=0','old_H1_models=0')
s=s.replace("human_request='Do not resume; check total-plan DR/400N/50Hz and actual270mm, then continue total plan'","human_request='Latest: resume selected4999 with byte-literal 上台阶3 general reward and original Fudan trimesh stairs, own400N50/DR retained; this entry is necessary0PT admission only'")
s=s.replace("worker=result['actual_worker_identity'],",'')
s=s.replace("result['actual_worker_identity']",'None')
ast.parse(s)
(N/'install188_literal_STAIRS3_native_admission_once.py').write_text(s,encoding='utf8')
