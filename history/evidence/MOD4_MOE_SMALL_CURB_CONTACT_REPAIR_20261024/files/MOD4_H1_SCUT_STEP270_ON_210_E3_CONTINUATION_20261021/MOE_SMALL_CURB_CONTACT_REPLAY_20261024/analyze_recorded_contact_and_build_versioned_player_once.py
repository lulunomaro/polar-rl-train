from pathlib import Path
import ast,hashlib,json,time,xml.etree.ElementTree as ET
import numpy as np
D=Path(__file__).resolve().parent;T=D.parent;W=T.parent;R=D/'reports';PLAYER=W/'MOD4_LOCAL_LATEST_MOE_PLAYER_REQUESTED_20261023';P=PLAYER/'player'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def write(p,s):
 ast.parse(s)
 with p.open('x',encoding='utf8') as f:f.write(s)
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
put('LOCAL_CONTACT_GEOMETRY_READER_SIX_VERTEX_ASSUMPTION_ERROR_ACTUAL.json',dict(epoch=time.time(),error='ValueError: operands could not be broadcast together with shapes (5,3) (3,3)',scope='Original inline saved-array analysis, before report or derived plot writes. Full inline source retained in conversation, not saved separately.',cause='Assumed every selected thin surface mesh has6vertices; rm_col6588 has8, a thin quadrilateral prism. Original geometric thinness inference still needs exact source readback.',new_reader='This file handles2N paired vertices and reports cardinality; original V3 rollout unchanged.',not_training_or_physics_failure=True))
out=D/'actual_contact_V3_4090/out';meta=json.loads((out/'ACTUAL_CUDA_SOURCE_AND_PROTOCOL.json').read_bytes());v=json.loads((R/'4090_SMALL_CURB_V3_FROZEN_FINITE_RETURNED_ACTUAL.json').read_bytes());schema=json.loads((out/'CONTACT_AND_PHYSICS_COLUMNS.json').read_bytes());summaries=[];seen={};saved=None
for row in v['final']['cases']:
 if row['artifact']['SHA'] in seen:
  summaries.append(dict(case=row['case'],literal_complete_NPZ_SHA_equal_to=seen[row['artifact']['SHA']],SHA=row['artifact']['SHA']));continue
 seen[row['artifact']['SHA']]=row['case'];a=np.load(out/(row['case']+'.npz'));p=a['physics'];c=a['contacts'];indices=c[:,0].astype(np.int64)-1;frame=c[:,7:16].reshape(-1,3,3);force=np.einsum('nji,nj->ni',frame,c[:,16:19]);sign=np.asarray([1. if schema['geometry_names'][str(int(x))]['body']=='world' else -1. for x in c[:,1]]);force*=sign[:,None];net=np.zeros((len(p),3));np.add.at(net,indices,force);active=np.zeros(len(p),dtype=np.int64);np.add.at(active,indices,c[:,16]>0)
 longest=count=0
 for zero in active==0:count=count+1 if zero else 0;longest=max(longest,count)
 dv=np.r_[0,np.diff(p[:,6])];k=int(np.argmax(dv));contact=[]
 for q in c[indices==k]:contact.append(dict(geom1=schema['geometry_names'][str(int(q[1]))],geom2=schema['geometry_names'][str(int(q[2]))],distance_m=float(q[3]),normal=q[7:10].tolist(),local_wrench=q[16:22].tolist()))
 summaries.append(dict(case=row['case'],largest_recorded_upward_velocity_step=dict(index=k,time_s=float(p[k,0]),dt=.0005,vz_before=float(p[max(k-1,0),6]),vz_after=float(p[k,6]),delta_vz=float(dv[k]),base_xyz=p[k,1:4].tolist(),base_generalized_constraint_force_xyz_N=p[k,38:41].tolist(),world_contact_force_sum_xyz_N=net[k].tolist(),max_abs_motor_command_Nm=float(np.abs(p[k,20:26]).max()),contacts=contact),max_abs_contact_sum_minus_base_constraint_N=float(np.max(np.abs(net-p[:,38:41]))),longest_zero_positive_ground_normal_force_seconds=longest*.0005,zero_positive_ground_force_callbacks=int((active==0).sum()),actual_fault=row['fault']))
 if row['case']=='E0_vx_0p65':saved=(p.copy(),net.copy())
xml=ET.parse(P/'rm7v7_latest_moe.xml').getroot();geometry={}
for name in ('rm_col_6588','rm_col_6809','rm_col_6813'):
 m=xml.find("asset/mesh[@name='%s']"%name);verts=np.fromstring(m.get('vertex'),sep=' ').reshape(-1,3);half=len(verts)//2;assert len(verts)%2==0;geometry[name]=dict(attributes=m.attrib,vertices_count=len(verts),paired_vertex_spacing_m=np.linalg.norm(verts[half:]-verts[:half],axis=1).tolist(),source_geometry_not_modified=True)
put('V3_RECORDED_CONTACT_NET_FORCE_AND_FIXED_E0_LAUNCH_CPU_ACTUAL.json',dict(epoch=time.time(),primary_runtime=meta['mujoco_version'],primary_ORT=meta['onnxruntime_version'],summaries=summaries,selected_collision_source_geometry=geometry,method='Read only recorded physical-step arrays and source XML. Transform actual contact wrenches into world frame; their sum corroborates independently recorded free-root generalized constraint forces. This is not a fresh mj_forward contact reconstruction.',scope='Fixed E0 also launches/falls; MoE switching is not necessary. Not an exact replay of absent original human command history, not an exact energy balance, not a universal physical guarantee. Huge individual opposing forces must not be described as the net external force.',no_local_policy_or_physics_rollout=True))
native=[json.loads(p.read_bytes()) for p in (D/'actual_contact_V4_4090/out').glob('*_COMPLETE.json')];multi=json.loads((R/'4090_SMALL_CURB_V5_FROZEN_FINITE_RETURNED_ACTUAL.json').read_bytes());assert len(native)==4 and multi['actual_returncode']==0 and len(multi['final']['cases'])==4 and all(x['fault'] is None for x in native+multi['final']['cases']);assert len({x['initial_state_SHA'] for x in native+multi['final']['cases']+v['final']['cases']})==1
baseline={x['case']:x for x in v['final']['cases']};comparisons=[]
for x in native+multi['final']['cases']:
 key=x['variant']+'_vx_'+str(x['target_vx']).replace('.','p');b=baseline[key];comparisons.append(dict(case=x['case'],collision_mode=x['collision_mode'],original_case=key,original_fault=b['fault'],new_fault=x['fault'],original_max_upward_v=b['max_root_upward_v_m_s'],new_max_upward_v=x['max_root_upward_v_m_s'],original_max_tilt=b['max_tilt_deg'],new_max_tilt=x['max_tilt_deg'],original_max_individual_contact_N=b['max_contact_normal_force_N'],new_max_individual_contact_N=x['max_contact_normal_force_N'],original_controls=b['controls'],new_controls=x['controls'],route_end_stop=x['route_endpoint_stop']))
put('CONTROLLED_COLLISION_PIPELINE_REPAIR_AND_COMPLETE_PREFIX_SCOPE_ACTUAL.json',dict(epoch=time.time(),comparisons=comparisons,original_V4_whole_returncode=1,original_V4_no_FINAL=True,original_V4_four_native_off_complete_prefixes=True,V5_only_missing_multi_off_four_complete_and_FINAL=True,no_consumed_case_or_native_off_replay=True,selected_player_candidate='disable MULTICCD bit524288, keep nativeCCD and original models, gains, commands, actuators, observations and all expert/gate weights',all8_ablation_cases_no_UI_fall=True,protocol_max500controls_or_original_flat_route_end=True,baseline_E0_two_falls_eliminated_in_these_cases=True,not_all_terrain_or_jump_or_recovery_graduation=True,no_automatic_new_reward_training_or_original_player_hotpatch=True,primary_references=['https://mujoco.readthedocs.io/en/3.7.0/computation/index.html','https://github.com/google-deepmind/mujoco/issues/3691'],upstream_issue_similarity_is_hypothesis_not_proven_same_bug=True))
candidate='''from rm7v7_moe_sim import RM7V7MoESim, ROUTES
import mujoco

class ContactStableRM7V7MoESim(RM7V7MoESim):
    """Versioned player candidate: same terrain and actors, single-contact native CCD."""
    def __init__(self):
        super().__init__()
        self.model.opt.disableflags |= int(mujoco.mjtDisableBit.mjDSBL_MULTICCD)
        self.reset_route('flat_run')
    def parameter_readback(self):
        result=super().parameter_readback()
        disabled=int(self.model.opt.disableflags)
        assert disabled & int(mujoco.mjtDisableBit.mjDSBL_MULTICCD)
        result.update(mujoco_version=mujoco.__version__,collision_candidate='nativeCCD with multiCCD disabled',actual_disableflags=disabled,actual_enableflags=int(self.model.opt.enableflags),validated_scope='Only finite flat-route small-contact comparisons, not jump/recovery/all terrain qualification')
        return result
'''
write(P/'rm7v7_contact_stable_candidate_v1.py',candidate)
driver=(P/'drive_rm7v7_moe.py').read_text('utf8');assert driver.count('from rm7v7_moe_sim import RM7V7MoESim, ROUTES')==1
driver=driver.replace('from rm7v7_moe_sim import RM7V7MoESim, ROUTES','from rm7v7_contact_stable_candidate_v1 import ContactStableRM7V7MoESim as RM7V7MoESim, ROUTES').replace("self.root.title('MOD4 最新 MoE · RM 7v7 真实CAD全场')","self.root.title('MOD4 小坎碰撞修正版 · 原专家与全场CAD')").replace('MOD4 · RM 7v7 全场 / 最新 MoE','MOD4 · 小坎碰撞修正版 / 同一 MoE').replace('MuJoCo · H1/普通100 Hz，自旋/恢复50 Hz · 无扶正/航向辅助','MuJoCo · 小坎碰撞修正版 · 原专家与控制频率不变').replace('双方地板1.5°坡度、起伏路、飞坡、中心岛、狗洞均保留。','双方地板1.5°坡度、起伏路、飞坡、中心岛、狗洞均保留。\n本版已测平地小坎；跳跃、恢复和全场稳定性尚未据此合格。')
write(P/'drive_rm7v7_contact_stable_candidate_v1.py',driver)
with (PLAYER/'试玩小坎碰撞修正版.bat').open('x',encoding='utf8') as f:f.write('@echo off\nchcp 65001 >nul\ncd /d "%~dp0"\n"'+str(W/'.venv/Scripts/pythonw.exe')+'" -B -X utf8 "player/drive_rm7v7_contact_stable_candidate_v1.py"\n')
with (PLAYER/'小坎碰撞修正版说明.md').open('x',encoding='utf8') as f:f.write('本版只切换播放器的碰撞多接触选项，保留全场地形、机器人尺寸、原专家与门控、控制参数及频率。初始暂停，按P开始。\n\n4090同版本对照中，原配置固定E0在0.65和1.0m/s弹起失稳；关闭multiCCD后的四组普通驾驶对照未出现相同失稳。测试最长5秒或到原路段终点，不能当作全场、跳跃或恢复合格。\n\n原入口与全部失败证据保留。后续训练不会自动替换这个包。\n')
put('VERSIONED_PLAYER_CONTACT_REPAIR_SOURCE_AST_AND_LIMITS_ACTUAL.json',dict(epoch=time.time(),entry=str(PLAYER/'试玩小坎碰撞修正版.bat'),original_player_driver_unchanged=True,original_XML_and_mesh_unchanged=True,all_actor_and_gate_ONNX_unchanged=True,new_files={str(p):dict(bytes=p.stat().st_size,SHA=H(p)) for p in (P/'rm7v7_contact_stable_candidate_v1.py',P/'drive_rm7v7_contact_stable_candidate_v1.py')},physical_change='disableflags |= mjDSBL_MULTICCD, value524288; no dt/gain/mass/action/terrain change',remote_evidence='Actual V5 four complete500-or-route-end runs with same flag value, runtime3.14 and primaryORT1.30; originalV4 error and four native-off prefixes retained.',local_no_policy_or_physics_test=True,not_original_human_trace_reproduced_exactly=True,not_all_skill_qualification=True,not_launched_yet=True))
np.savez_compressed(D/'E0_0p65_LAUNCH_PLOT_DERIVED.npz',physics=saved[0],world_contact_force=saved[1])
put('LAUNCH_PLOT_DERIVED_PRODUCER_ACTUAL.json',dict(epoch=time.time(),path=str(D/'E0_0p65_LAUNCH_PLOT_DERIVED.npz'),bytes=(D/'E0_0p65_LAUNCH_PLOT_DERIVED.npz').stat().st_size,SHA=H(D/'E0_0p65_LAUNCH_PLOT_DERIVED.npz'),scope='Derived plot arrays from actual V3 saved physics, no rollout'))
print(json.dumps(dict(controlled_ablation_cases=8,no_new_falls=True,new_entry=str(PLAYER/'试玩小坎碰撞修正版.bat'),all_recorded_source_and_errors_retained=True)))
