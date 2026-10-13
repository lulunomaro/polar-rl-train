from pathlib import Path
import shutil,json,time
D=Path(__file__).resolve().parent
q=D/'CPU_intermediate';assert not q.exists();q.mkdir()
shutil.copyfile(D/'template_v3_intermediate/expanded_source_projection.py',q/'expanded_source_projection.py')
shutil.copyfile(D/'CPU_projection/PERENV128_SCHEMA_V1.json',q/'PERENV128_SCHEMA_V1.json')
s=(D/'CPU_projection/review_expanded128_projection_cpu_v1.py').read_text(encoding='utf8')
for a,b in [('OWN_PPO_CPU_INPUTS_1791891584295189300','OWN_PPO_CPU_INPUTS_1791894571823537900'),('8d33147fbda9ca7c97ea1be925be379077a3c59a92d266ca82db47ef93dbdeda','f1d3ddf129c81cfc83735d230058abce6b81702cd9a479776d7e31d826636db3'),('for n in e.ALLOWED_TARGETS:','for n in (640,768):'),('source_is_actual_two_update_activity_snapshot_not_final=True','source_is_actual_121_update_complete_own128_final=True'),('latest_STOP_fullsave_source_must_be_used_by_root_after_boundary=True','latest_STOP_fullsave_source_used_after_actual_boundary=True'),('EXPANDED128_256_512_1024_CPU_ACTUAL_REVIEW_V1.json','EXPANDED_OWN_FINAL128_TO640_768_CPU_ACTUAL_REVIEW.json')]:
 assert a in s;s=s.replace(a,b)
lines=s.splitlines();lines=[line if 'fresh(schema,dict' not in line else " assert fields==json.loads(schema.read_bytes())['fields']" for line in lines]
s='\n'.join(lines)+'\n';compile(s,str(q/'review_intermediate_CPU_once.py'),'exec');(q/'review_intermediate_CPU_once.py').write_text(s,encoding='utf8')
(D/'reports/CAPACITY_INTERMEDIATE_INLINE_GENERATOR_PREEXEC_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),original_error='PowerShell native Python -c nested quote unterminated string SyntaxError before generator ran; subsequent CPU file absent. Independent saved generator prepared.',GPU_PPO_replay=False,original_roots_not_modified=True),indent=2),encoding='utf8')
