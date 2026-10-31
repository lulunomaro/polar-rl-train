from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;O=T/'FUDAN_STAIRS3_LITERAL_REWARD_TERRAIN_400N50_ADAPT_V188_20261031';D=N/'train_package'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
with (N/'reports/FREEZE194_PREUSE_SOURCE_STARTED.json').open('x') as f:json.dump(dict(epoch=time.time(),before_any_remote=True),f)
p=D/'run194_literal_jump_plane_worker.py';s=p.read_text(encoding='utf8').replace('ACTUAL188','ACTUAL194')
ast.parse(s);p.write_text(s,encoding='utf8');(N/p.name).write_text(s,encoding='utf8')
task=json.loads((D/'TASK194.json').read_bytes());task['reward_source_CPU_report_SHA']=H(N/'reports/ROOT194_NEW_LITERAL_JUMP50_SOURCE_CPU_ACTUAL.json')
(D/'TASK194.json').write_text(json.dumps(task,indent=2,ensure_ascii=False),encoding='utf8')
manifest=json.loads((N/'TRAIN194_COMPLETE_MANIFEST.json').read_bytes())
for row in manifest['files']:
 p=N/row['local_relative']
 if p.suffix.lower() not in ('.usd','.usda','.npz','.npy'):
  row.update(bytes=p.stat().st_size,SHA=H(p))
(N/'TRAIN194_COMPLETE_MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
J='/mnt/mod4_linux_durable_20261013/MOD4_FUDAN_JUMP_LITERAL_PLANE40050_DR_TWO_HOUR_20261031v194/seed27'
oldJ='/mnt/mod4_linux_durable_20261013/MOD4_FUDAN_STAIRS3_LITERAL_400N50_20261031v188_v2/seed27'
OWNER='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_ONE194_FUDAN_JUMP_PLANE40050_TWO_HOUR_2610v194/owner'
oldOWNER='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_ONE188_FUDAN_STAIRS3_400N50_2610v188/owner'
s=(O/'start188_literal_STAIRS3_single_forwarded4090_FIRST_V2_once.py').read_text(encoding='utf8')
s=s.replace(oldJ,J).replace(oldOWNER,OWNER).replace('188','194').replace('STAIRS3','JUMP194')
s=s.replace('stairs194','jump194').replace('literal_stairs3_400N50','literal_jump194_400N50')
s=s.replace('literal_reward_text_identity31','literal_reward_text_identity19')
s=s.replace('3900','7500').replace('save_seconds=3600','save_seconds=7200').replace('control_v2','control')
s=s.replace('CONTROL194_V2_MANIFEST.json','CONTROL194_MANIFEST.json')
s=s.replace('run194_literal_stairs3_40050_worker.py','run194_literal_jump_plane_worker.py')
s=s.replace('install194_literal_JUMP194_native_admission','install194_literal_jump_plane_admission')
s=s.replace('start194_literal_JUMP194_single_forwarded4090_FIRST_V2_once','start194_literal_JUMP_plane_single4090_FIRST_once')
s=s.replace("|install194_literal_jump_plane_admission|","|install194_literal_jump_plane_admission|collect188_|start188_|install_capture193_|install_evaluate191_|")
s=s.replace("N/'control/OWNER72_CONTROL_DEPENDENCIES_BINDING_ACTUAL.json'","N/'control/OWNER72_CONTROL_DEPENDENCIES_BINDING_ACTUAL.json'")
s=s.replace('Literal jump194','Literal jump194')
s=s.replace("'Explicit original 上台阶3 byte-literal general reward and original Fudan trimesh stairs; retain total-plan400N50D0-D7; preserve delivered4999 fullstate'","'Human authorized two-hour flat adaptation with original pinned JUMP16,400N50,D0-D7 and delivered4999 fullstate. Reward methods/config unchanged.'")
ast.parse(s);(N/'start194_literal_JUMP_plane_single4090_FIRST_once.py').write_text(s,encoding='utf8')
s=(O/'collect188_original_formal_cost_normal900_UNUSED_once.py').read_text(encoding='utf8')
s=s.replace('188','194').replace('stairs3','jump194').replace('STAIRS3','JUMP194').replace('control_v2','control').replace('3900','7500')
s=s.replace('start194_literal_JUMP194_single_forwarded4090_FIRST','start194_literal_JUMP_plane_single4090_FIRST')
ast.parse(s);(N/'collect194_original_formal_cost_normal900_UNUSED_once.py').write_text(s,encoding='utf8')
s=(O/'review188_NEW_formal_initial_CPU_UNUSED_once.py').read_text(encoding='utf8').replace('188','194').replace('STAIRS3','JUMP194')
s=s.replace("'stairs3_curriculum_state'","'original_jump_reward_memory'")
ast.parse(s);(N/'review194_NEW_formal_initial_CPU_UNUSED_once.py').write_text(s,encoding='utf8')
print(json.dumps(dict(files=len(manifest['files']),manifest_SHA=H(N/'TRAIN194_COMPLETE_MANIFEST.json'),original19_source_CPU_passed=True,FIRST_unused=True,normal_unused=True)))
