from pathlib import Path
import ast,datetime,hashlib,json,re,time,tomllib,xml.etree.ElementTree as ET
import numpy as np
D=Path(__file__).resolve().parent;T=D.parent;W=T.parent;R=D/'reports';OLD=T/'H1_STEP270_TUCK_V3_FIRST_CLOSED39_REPLAY_20261023';C=W/'MOD4_WORKSPACE_CLEANUP_AUTHORIZED_20261021_V88';G=W/'polar-rl-train'
read=lambda p:json.loads(Path(p).read_bytes())
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def write(p,s):
 ast.parse(s)
 with p.open('x',encoding='utf8') as f:f.write(s)
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
P=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V48_20261023';N=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V49_20261023';F=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V50_20261024'
receipt=read(R/'4090_SERIES_BASELINE_FROZEN_FINITE_RETURNED_ACTUAL.json');final=receipt['final'];assert receipt['actual_returncode']==0 and receipt['actual_child_waited'] and receipt['own_eval_lock_released'] and len(final['cases'])==6
rows={x['case']:x for x in final['cases']};matches={}
for speed in ('0p6','1p5'):
 a=rows['auto_vx_'+speed];b=rows['W35_vx_'+speed];assert a['artifact']['SHA']==b['artifact']['SHA'] and a['expert_switches']==0 and a['selected_expert_counts']['W35']==500;matches[speed]=dict(auto_fixed_W35_complete_NPZ_SHA_equal=True,SHA=a['artifact']['SHA'])
old=read(W/'MOD4_LOCAL_WASD_SERIES_20261011/e0_forward_REVIEW.json');new=rows['E0_vx_1p5'];end_error=np.asarray(new['last_health']['base_xyz'])-np.asarray(old['end_xyz'])
runtime0=(W/'MOD4_LOCAL_WASD_SERIES_20261011/sim_runtime.py').read_text('utf8');runtime1=(W/'MOD4_LOCAL_LATEST_MOE_PLAYER_REQUESTED_20261023/player/sim_runtime.py').read_text('utf8')
assert ast.dump(ast.parse(runtime0.replace('TorchPolicy','OnnxPolicy')),include_attributes=False)==ast.dump(ast.parse(runtime1),include_attributes=False)
route=next(x for x in read(W/'MOD4_LOCAL_LATEST_MOE_PLAYER_REQUESTED_20261023/player/routes.json') if x['id']=='flat_run');normal=np.asarray(route['spawn_surface_normal']);tilt=float(np.degrees(np.arccos(normal[2]/np.linalg.norm(normal))))
xml=ET.parse(W/'MOD4_LOCAL_LATEST_MOE_PLAYER_REQUESTED_20261023/player/rm7v7_latest_moe.xml').getroot();surfaces={}
for name in ('rm_col_6768','rm_col_3553','rm_col_2430'):
 v=np.fromstring(xml.find("asset/mesh[@name='%s']"%name).get('vertex'),sep=' ').reshape(-1,3);n=np.cross(v[1]-v[0],v[2]-v[0]);n/=np.linalg.norm(n)
 surfaces[name]=dict(first_triangle_normal=n.tolist(),absolute_slope_from_horizontal_deg=float(np.degrees(np.arccos(abs(n[2])))),min_xyz=v.min(0).tolist(),max_xyz=v.max(0).tolist(),scope='Source vertices only, not fresh contact forces or sole failure causality')
analysis=dict(epoch=time.time(),human_confirmed_baseline=['本机 MuJoCo 播放器','平地／起伏／小陀螺系列播放器（可切 E0、W35）'],actual_remote_rc=0,complete_cases=6,all6_controls_500_no_UI_fault=True,protocol=read(D/'SERIES_BASELINE_CONFIG.json'),cases=final['cases'],auto_fixed_W35_matches=matches,old_series_E0_1p5_end_xyz=old['end_xyz'],new_remote_E0_end_xyz=new['last_health']['base_xyz'],new_minus_old_end_xyz_m=end_error.tolist(),same_E0_baseline_reproduced_to_sub_micrometre_end_position=True,not_general_bitwise_or_skill_gate=True,runtime_AST_exact_except_TorchPolicy_to_OnnxPolicy_name=True,geometry_route=route,declared_flat_route_surface_tilt_deg=tilt,selected_recorded_contact_geometry_source=surfaces,conclusions=['Known-good E0 old series behavior reproduced on remote4090; original local old summary HUD frame was also wrong, preserved unchanged.','Automatic gate selected W35 all500 at both forward speeds; complete NPZ exact to fixedW35, no switching instability in these tested cases.','The two player environments differ: ideal level series plane versus full CAD arena with 1.5degree cross-slope and local collision features.','New full-arena and old level-plane fixedE0 differ too; cannot attribute this to MoE alone.','At1.5m/s auto/W35 has about0.496m lateral drift over5s, E0 about0.266m; stability/straightness is not solved globally.'],not_proven=['Unique reason for every user observed slowdown or fall','MoE gate optimality or terrain transition safety','270mm jump success or landing stability','MuJoCo3.12/3.14 and CUDA/CPU bitwise equivalence'],local_scope='Saved arrays, source XML and reports only; no local policy inference or MuJoCo run',no_new_router_reward_training_or_auto_export=True)
put(R/'CONFIRMED_OLD_SERIES_REMOTE_6CASE_AND_FULL_ARENA_SCOPE_CPU_ACTUAL.json',analysis)
note='''旧单专家对照已在4090复现：E0与原系列播放器同检查点，1.5m/s五秒终点差不到1微米（描述本次结果，非新门槛）。自动门控在0.6和1.5m/s两档全程选W35，与固定W35完整轨迹一致。

新播放器全赛场的“平地跑”几何段带1.5°横坡，并有局部碰撞面；旧系列是独立水平面，二者不能直接作为MoE/单专家优劣对照。已修正速度HUD惯性坐标系误读；未改门控或策略。高速直行横偏、地形适配及270mm跳跃落台仍未解决。

最新请求时固定包的启动文件：MOD4_LOCAL_LATEST_MOE_PLAYER_REQUESTED_20261023/试玩最新MoE.bat。后续训练不会自动替换这个包。
'''
with (W/'MOD4_LOCAL_LATEST_MOE_PLAYER_REQUESTED_20261023/4090对照结果说明.md').open('x',encoding='utf8') as f:f.write(note)
# Reuse only the source-building prefix; all already-consumed old builders remain untouched.
src=(OLD/'prepare_closed47_pair48_future49_actual_handoff_ordinary_once.py').read_text('utf8');src=src[:src.index('    oldprompt=tomllib.loads')]
names={'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V47_20261023':P.name,'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V48_20261023':N.name,'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V49_20261023':F.name,'H1step270_reward_tuckclear4_2310v48':'H1step270_reward_tuckclear4_2410v49','H1step270_reward_tuckclear4_2310v49':'H1step270_reward_tuckclear4_2410v50','CURRENT47_CLOSED':'CURRENT48_CLOSED','CURRENT48_CLOSED':'CURRENT49_CLOSED','UNUSED48_PAIRED_COLLECTOR':'UNUSED49_PAIRED_COLLECTOR','actual_closed47_collector':'actual_closed48_collector','NEXT49_CURRENT_CLEARANCE':'NEXT50_CURRENT_CLEARANCE','actual48_both_closed_CPU':'actual49_both_closed_CPU','no_stale47_or39_E3_fallback':'no_stale48_or39_E3_fallback','review_closed47_current_clearance':'review_closed48_current_clearance','review_closed48_current_clearance':'review_closed49_current_clearance','CLOSED47_CURRENT_CLEARANCE_TEXT_CPU_ORIGINAL_ERROR_':'CLOSED48_CURRENT_CLEARANCE_TEXT_CPU_ORIGINAL_ERROR_','CLOSED48_CURRENT_CLEARANCE_TEXT_CPU_ORIGINAL_ERROR_':'CLOSED49_CURRENT_CLEARANCE_TEXT_CPU_ORIGINAL_ERROR_','ACTUAL48_SAME_REWARD_PAIRED':'ACTUAL49_SAME_REWARD_PAIRED','Both actual complete47 models':'Both actual complete48 models','CLOSED47_ACTUAL_PAIR_COLLECTION_COST_AND_PAIR48_GO_TIMING_SCOPE_ACTUAL.json':'CLOSED48_ACTUAL_PAIR_COLLECTION_COST_AND_PAIR49_GO_TIMING_SCOPE_ACTUAL.json','NEXT_ACTUAL_CURRENT_CLEARANCE_V4_CLOSED47_118_76_ONE_PEER_PAIR48_BOTH_PPO_WORK_ORDER.json':'NEXT_ACTUAL_CURRENT_CLEARANCE_V4_CLOSED48_118_76_FOUR_OLD_PEER_PAIR49_BOTH_PPO_AND_HUMAN_MOE_WORK_ORDER.json','CURRENT_CLEARANCE_V4_CLOSED47_ONE_PEER_PAIR48':'CURRENT_CLEARANCE_V4_CLOSED48_FOUR_OLD_PEER_PAIR49','closed47_pair_complete_CPU':'closed48_pair_complete_CPU','fresh_closed47_storage':'fresh_closed48_storage','closed47_exact_log_snapshot_branch_executed':'closed48_exact_log_snapshot_branch_executed'}
pat=re.compile('|'.join(re.escape(x) for x in sorted(names,key=len,reverse=True)));src=pat.sub(lambda m:names[m[0]],src)
src=src.replace('PEER_FORENSICS_VERIFIED_RETAINED_ON72_SPACE_RELEASED_ACTUAL.json','CLOSED48_OLD46_45_MINIMAL_VERIFIED_RETAINED_ON72_SPACE_RELEASED_ACTUAL.json').replace(" and storage['all_full_SHA_retained_on72']",'')
src=src.replace('verified_one_current_NPZ_relocated=storage','verified_four_old_NPZ_relocated=storage')
# Current49 root kept October23 basename. Only FUTURE50 gets October24 path.
src=src.replace("'H1step270_reward_tuckclear4_2410v49','H1step270_reward_tuckclear4_2410v50'","'H1step270_reward_tuckclear4_2310v49','H1step270_reward_tuckclear4_2410v50'")
src+="\nif __name__=='__main__':main()\n";write(D/'prepare_closed48_pair49_future50_source_workorder_once.py',src.replace("D=Path(__file__).resolve().parent;T=D.parent;W=T.parent;R=D/'reports'","D=Path(__file__).resolve().parent.parent/'H1_STEP270_TUCK_V3_FIRST_CLOSED39_REPLAY_20261023';T=D.parent;W=T.parent;R=D/'reports'"))
print(json.dumps(dict(analysis_saved=True,old_E0_end_delta=end_error.tolist(),route_tilt_deg=tilt,contact_geometry=surfaces,future_source_builder_only=True)))
