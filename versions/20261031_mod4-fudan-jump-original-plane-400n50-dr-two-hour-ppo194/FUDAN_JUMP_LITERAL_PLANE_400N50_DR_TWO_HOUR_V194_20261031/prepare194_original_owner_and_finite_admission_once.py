from pathlib import Path
import ast,hashlib,json,shutil,time
N=Path(__file__).resolve().parent;T=N.parent;O=T/'FUDAN_STAIRS3_LITERAL_REWARD_TERRAIN_400N50_ADAPT_V188_20261031';C=N/'control';C.mkdir()
J='/mnt/mod4_linux_durable_20261013/MOD4_FUDAN_JUMP_LITERAL_PLANE40050_DR_TWO_HOUR_20261031v194/seed27'
oldJ='/mnt/mod4_linux_durable_20261013/MOD4_FUDAN_STAIRS3_LITERAL_400N50_20261031v188_v2/seed27'
for p in (O/'control_v2').iterdir():
 if not p.is_file():continue
 if p.suffix!='.py':shutil.copyfile(p,C/p.name);continue
 s=p.read_text(encoding='utf8').replace('stairs188_protocol','jump194_protocol')
 s=s.replace('STAIRS3','JUMP194').replace('STAIRS3_LITERAL_400N50','JUMP194_LITERAL_PLANE_400N50')
 s=s.replace('literal_stairs3_400N50','literal_jump194_400N50').replace('original_STAIRS3_reward_and_terrain','original_JUMP194_reward_and_plane')
 s=s.replace('literal_reward_text_identity31','literal_reward_text_identity19')
 s=s.replace('literal_STAIRS3_reward_terrain','literal_JUMP194_reward_plane')
 s=s.replace('3900','7500').replace('+3600','+7200')
 s=s.replace('control_v2','control')
 name=p.name.replace('stairs188','jump194')
 ast.parse(s);(C/name).write_text(s,encoding='utf8')
# The original HMAC and actual elapsed charge functions remain exactly the same.
a=ast.parse((O/'control_v2/three_slot_common_v1.py').read_bytes());b=ast.parse((C/'three_slot_common_v1.py').read_bytes())
for name in ('authenticated_row','charge_values'):
 x=next(n for n in a.body if isinstance(n,ast.FunctionDef) and n.name==name);y=next(n for n in b.body if isinstance(n,ast.FunctionDef) and n.name==name)
 assert ast.dump(x,include_attributes=False)==ast.dump(y,include_attributes=False)
rows=[dict(relative=p.name,local_path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(C.iterdir()) if p.is_file()]
(N/'CONTROL194_MANIFEST.json').write_text(json.dumps(dict(files=rows),indent=2),encoding='utf8')
s=(O/'remote188V2_postcopy_CPU_and_native_admission.txt').read_text(encoding='utf8')
s=s.replace(oldJ,J).replace('188','194').replace('stairs3_measured_boundary194 import LiteralStairs3Kernel','jump194_boundary import LiteralJump194').replace("k=LiteralStairs3Kernel(2,'cpu',.02)","k=LiteralJump194(2,'cpu',.02,['chassis','left_wheel','right_wheel']+['fixture_'+str(i) for i in range(28)])")
s=s.replace('literal_stairs3_original_config import OriginalStairs3Cfg','literal_original_config import LiteralOriginalConfig').replace('OriginalStairs3Cfg','LiteralOriginalConfig')
s=s.replace('run194_literal_stairs3_40050_worker.py','run194_literal_jump_plane_worker.py')
(N/'remote194_postcopy_CPU_and_native_admission.txt').write_text(s,encoding='utf8')
s=(O/'install188_literal_STAIRS3_native_admission_V2_once.py').read_text(encoding='utf8')
s=s.replace(oldJ,J).replace('188','194').replace('STAIRS3','JUMP194').replace('install194_literal_JUMP194_native_admission_V2_once','install194_literal_jump_plane_admission_once')
s=s.replace('remote194V2_postcopy_CPU_and_native_admission.txt','remote194_postcopy_CPU_and_native_admission.txt')
s=s.replace("human_request='Latest: resume selected4999 with byte-literal 上台阶3 general reward and original Fudan trimesh stairs, own400N50/DR retained; this entry is necessary0PT admission only'","human_request='Literal pinned Fudan JUMP on plane; retain delivered4999 PPO and400N50D0-D7. Human authorized two-hour window; this entry is new0PT admission only'")
s=s.replace("'install194_literal_jump_plane_admission_once|", "'install194_literal_jump_plane_admission_once|install_capture193_|install_evaluate191_|collect188_|start188_|")
ast.parse(s);(N/'install194_literal_jump_plane_admission_once.py').write_text(s,encoding='utf8')
with (N/'reports/ROOT194_FINITE_CONTROL_SOURCE_TYPED_TWO_HOUR_AUTHORITY.json').open('x',encoding='utf8') as f:
 json.dump(dict(epoch=time.time(),user='先按照复旦的奖励训平地跳跃适应dr和400n 50hz 先训2个小时；复旦的跳跃别乱改瞎适配',
  task_changed_only_duration_and_reward_plane_readiness=True,save_seconds=7200,max_parent_seconds=7500,exit_headroom_seconds=300,
  original_HMAC_and_actual_charge_functions_AST_literal=True,no_budget_grant_or_canonical_write=True,original_guard_and_privateEX=True),f,indent=2,ensure_ascii=False)
print(json.dumps(dict(control_files=len(rows),prepared_new_admission=True)))
