from pathlib import Path
import ast,json,time,hashlib
D=Path('C:\\Users\\lulu\\Desktop\\claude\\mjcf\\MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021\\MOE_SMALL_CURB_CONTACT_REPLAY_20261024');T=D.parent;W=T.parent;R=D/'reports';PLAYER=W/'MOD4_LOCAL_LATEST_MOE_PLAYER_REQUESTED_20261023';P=PLAYER/'player'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def write(p,s):
 ast.parse(s)
 with p.open('x',encoding='utf8') as f:f.write(s)
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
driver=(P/'drive_rm7v7_moe.py').read_text('utf8');assert driver.count('from rm7v7_moe_sim import RM7V7MoESim, ROUTES')==1
driver=driver.replace('from rm7v7_moe_sim import RM7V7MoESim, ROUTES','from rm7v7_contact_stable_candidate_v1 import ContactStableRM7V7MoESim as RM7V7MoESim, ROUTES').replace("self.root.title('MOD4 最新 MoE · RM 7v7 真实CAD全场')","self.root.title('MOD4 小坎碰撞修正版 · 原专家与全场CAD')").replace('MOD4 · RM 7v7 全场 / 最新 MoE','MOD4 · 小坎碰撞修正版 / 同一 MoE').replace('MuJoCo · H1/普通100 Hz，自旋/恢复50 Hz · 无扶正/航向辅助','MuJoCo · 小坎碰撞修正版 · 原专家与控制频率不变').replace('双方地板1.5°坡度、起伏路、飞坡、中心岛、狗洞均保留。','双方地板1.5°坡度、起伏路、飞坡、中心岛、狗洞均保留。\\n本版已测平地小坎；跳跃、恢复和全场稳定性尚未据此合格。')
write(P/'drive_rm7v7_contact_stable_candidate_v1.py',driver)
with (PLAYER/'试玩小坎碰撞修正版.bat').open('x',encoding='utf8') as f:f.write('@echo off\nchcp 65001 >nul\ncd /d "%~dp0"\n"'+str(W/'.venv/Scripts/pythonw.exe')+'" -B -X utf8 "player/drive_rm7v7_contact_stable_candidate_v1.py"\n')
with (PLAYER/'小坎碰撞修正版说明.md').open('x',encoding='utf8') as f:f.write('本版只切换播放器的碰撞多接触选项，保留全场地形、机器人尺寸、原专家与门控、控制参数及频率。初始暂停，按P开始。\n\n4090同版本对照中，原配置固定E0在0.65和1.0m/s弹起失稳；关闭multiCCD后的四组普通驾驶对照未出现相同失稳。测试最长5秒或到原路段终点，不能当作全场、跳跃或恢复合格。\n\n原入口与全部失败证据保留。后续训练不会自动替换这个包。\n')
put('VERSIONED_PLAYER_CONTACT_REPAIR_SOURCE_AST_AND_LIMITS_ACTUAL.json',dict(epoch=time.time(),entry=str(PLAYER/'试玩小坎碰撞修正版.bat'),original_player_driver_unchanged=True,original_XML_and_mesh_unchanged=True,all_actor_and_gate_ONNX_unchanged=True,new_files={str(p):dict(bytes=p.stat().st_size,SHA=H(p)) for p in (P/'rm7v7_contact_stable_candidate_v1.py',P/'drive_rm7v7_contact_stable_candidate_v1.py')},physical_change='disableflags |= mjDSBL_MULTICCD, value524288; no dt/gain/mass/action/terrain change',remote_evidence='Actual V5 four complete500-or-route-end runs with same flag value, runtime3.14 and primaryORT1.30; originalV4 error and four native-off prefixes retained.',local_no_policy_or_physics_test=True,not_original_human_trace_reproduced_exactly=True,not_all_skill_qualification=True,not_launched_yet=True))
print(json.dumps(dict(new_entry=str(PLAYER/'试玩小坎碰撞修正版.bat'),source_AST=True,no_local_rollout=True)))
