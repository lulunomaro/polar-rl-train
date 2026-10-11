"""Accept only the observed8degree scope and prepare the approved next10degree component."""
from slope_io import *
import numpy as np,importlib.util,traceback

def main():
 rp=sorted(R.glob('SLOPE137_ACTUAL_REVIEW_[0-9]*.json'))[-1];review=json.loads(rp.read_bytes());assert review['review_complete']
 colp=sorted(R.glob('SLOPE137_COLLECTED_[0-9]*.json'))[-1];col=json.loads(colp.read_bytes());row=next(iter(col['cases'].values()));p=row['probe'];sc=p['route_scope']
 scope=next(iter(review['review'].values()));assert scope['base_review']['ordinary']==0 and all(scope['groups'][g]['complete_envs']==scope['groups'][g]['contact_confirmed_envs']==27 for g in ('ascending','descending'))
 decision=dict(epoch=time.time(),trial_id='E1-SLOPE8-137-COMPLETE-SCOPE-DECISION-01',complete_review=str(rp),collection=str(colp),
  source_checkpoint=row['manifest']['artifacts']['checkpoint'],scoped8deg_mirrored_frozen_behavior_accepted=True,
  scope_groups=scope['groups'],actual_scope_ground_contract_passed=True,ground_tolerance_m=1e-6,
  full_raw= p['full_route_raw'],source_is_scoped5deg_own404_full135_reviewed=True,
  no8deg_PPO_or_fulllearningstate_resume_executed=True,no_mechanical8deg_PPO_needed_for_observed_scope=True,
  source24b_frozen_for_5_and8deg_observed_scopes=True,qualified_full_SLOPE_or_MoE=False,gate_trained=False,
  different8deg_not_same5deg_initialization_pair=True,original136_failed_raw_cost_not_relabelled=True,
  old135_negative4pi_decline_and_all_strict_false_kept=True,no_permanent_anti_forgetting_proof=True,
  next_axis='approved_RM003_10degree_geometry_normal_and_actualray_contract_then_new_frozen_scope',
  no10deg_GPU_PPO_before_new_geometry_query_contract=True,new_budget_seconds=0)
 save('SLOPE137_COMPLETE_SCOPE_DECISION.json',decision)
 nd=D/'next_slope10_cpu';nd.mkdir(exist_ok=True)
 geometry=(D/'next_slope8_scope/slope8_geometry.py').read_text(encoding='utf8').replace('8degree','10degree').replace('8deg','10deg').replace('slope8','slope10').replace("p['angle_deg']==8.","p['angle_deg']==10.").replace('angle_deg=8.','angle_deg=10.')
 gp=nd/'slope10_geometry.py';assert not gp.exists();gp.write_bytes(geometry.encode());compile(geometry,gp.name,'exec')
 profile=json.loads((D/'next_slope8_scope/slope8_profile.json').read_bytes());height=2.*np.tan(np.deg2rad(10.));profile.update(schema='derived_continuous10deg_ramp_cpu_component_v1',angle_deg=10.,height_m=float(height),RM003_local10deg_branch_only=True)
 profile.pop('RM003_local8deg_branch_only');profile['vertices']=[[x,y,z] for x,z in zip([-4.5,-1.,1.,4.5],[0.,0.,height,height]) for y in (-4.5,4.5)]
 pp=nd/'slope10_profile.json';assert not pp.exists();pp.write_bytes(json.dumps(profile,indent=2).encode())
 spec=importlib.util.spec_from_file_location('slope10_cpu_geometry',gp);component=importlib.util.module_from_spec(spec);spec.loader.exec_module(component)
 spec=importlib.util.spec_from_file_location('slope10_cpu_triangle_ray',W/'MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_20261010/prepare_curb_component_once.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 errors=[];angle_error=[]
 for mirrored in (False,True):
  mesh,_=component.make_mesh((9.,9.),mirrored);v=mesh.vertices.copy();v[:,:2]-=4.5;o=-1 if mirrored else 1
  for x in np.r_[np.linspace(-4.4,4.4,31),[-1.,1.]]:
   for y in (-4.,0.,4.):
    hit=m.ray(np.array([o*x,y,2.]),np.array([0.,0.,-1.]),v,mesh.faces);errors.append(abs(hit[2]-np.clip((x+1.)/2,0,1)*height))
  triangles=v[mesh.faces];ramp=np.ptp(triangles[:,:,2],axis=1)>1e-10;angle_error.extend(abs(np.rad2deg(np.arccos(mesh.face_normals[ramp,2]))-10.).tolist())
 assert max(errors)<1e-10 and max(angle_error)<1e-10
 cosine=float(np.cos(np.deg2rad(10.)));assert cosine<.99
 save('SLOPE10_CPU_COMPONENT_PREPARED.json',dict(epoch=time.time(),trial_id='E1-SLOPE10-NEXT-CPU-COMPONENT-01',profile=profile,
  geometry=dict(path=str(gp.resolve()),bytes=gp.stat().st_size,sha256=H(gp.read_bytes())),profile_file=dict(path=str(pp.resolve()),bytes=pp.stat().st_size,sha256=H(pp.read_bytes())),
  independent_triangle_rays=len(errors),max_vertical_error_m=float(max(errors)),max_normal_angle_error_deg=float(max(angle_error)),
  expected_incline_normal_z=cosine,old8deg_sample_normal_threshold_099_inapplicable_to10deg=True,
  next_normal_query_contract_requires_actual_analytic10deg_triangle_normals_original1e6_tolerance=True,
  original_ground_tolerance_m=1e-6,positive_normal_contact_safety_data_thresholds_unchanged=True,
  new_frozen_package_SDK_native_fullstate_PPO_learning_executor_not_deployed=True,
  no_GPU_or_queue_or_PPO_or_budget_write=True,new_budget_seconds=0))
 work=R/'NEXT_E1_SLOPE10_GEOMETRY_QUERY_AND_FROZEN_WORK_ORDER.md';assert not work.exists()
 work.write_text('''# 完整8°冻结通行证据与下一10°独立单轴

先读E1_SLOPE8_137_COMPLETE_ACTUAL_COLLECTION/REVIEW/SCOPE_DECISION，完整137同source404own24b两hostJSONbyteexact/fullNPZ、原1e-6actualrayinput合同与6000callbacks/ground-contact积分COMlinkhardware通过，镜像8°2m上下各27/27且1N接触支撑吻合，ordinary0。只接受观测到的8°scope，5°完整135负4pi下降和原strictfalse保持；不是整个SLOPE/RM或MoE/gate部署，无永久抗遗忘证明。8°已足够，不机械追加8°PPO或复播137/136/135等旧case。

已积极准备下一批准RM00310°CPU组件：派生连续10°/2m高.352653961m、9m格镜像和上下平台，198独立三角射线/法向通过，仅CPU组件，尚无新frozenjob/package/SDK/native/fullstate/PPO/executor部署。source只完整135own40424b及完整137实际审查来源，不借old364/365/Wave/CURB盲替换。下一先新唯一10°冻结范围，可用same.4m接近、两轮全2m与200mm后支撑/80env1500control15s/20260928white3。geometry不同不冒同8°精确初始化。

当前8°dispatcher的sample normal_z>.99是该浅坡初始化几何检查，cos10°=.984807753低于.99，不能直接套用导致正确10°几何被拒绝，更不能静默放宽安全阈值。先独立CPU合同与新manifest显式10°三角面解析法向，在actualworldfloat32射线输入位置验证坡段expected normal与height，保留ground1e-6/原normal归一化与正z、原contact/COMlink/hardware容差。平支撑仍按水平面法向核，接缝三角面法向歧义应在新合同披露。生产ordinary/integrity阈值不改。新scope准备/CPU/packageexact以后才发布唯一新job，实际newresult/errorfree/fullraw合同和全部有效prefix审查；没有这些不得称10°通过或自动训练。

若新的冻结10°能力已足够，冻结范围候选并按实际下一轴/其它专家职责，避免每档固定PPO。真正需要10°学习才新独立root/output：先完整source24b actorcriticstdoptimizer/allD0D7/globalnamed/dictprivateCPUCUDA/旧5°terraincommand身份exact，显式5→10新geometry/assignment迁移与CUDA磁盘roundtrip/savedsourceepisode+1，非same8/PhysXexactresume；后续same10恢复必须exact。必要新CPU/SDK10x300/native20k24warm120timed480/576/128x2和20kx4完整PPO弃权重各一次同canonical，旧clock/DR精确SHA复用，不重45minclock，全部PASSED才首300s保存复评。E0/Wave/CURB与已冻结5°/8°不覆盖，不装pure/S7/S8/teacher/拒绝70-20-10。

新权只source404actualownfullsave/PASSED/三进程exit/two真实OS锁free/唯一结清/active-Sactive空，预算828000s六扩展各一次新增0；frozen/CPU无PPO不扣，不clear/复制/重tail/kill/hotpatch/双20k。健康E1_SLOPE8_QUERY_REVIEW工作器不重启，actualCIM/argv/creation/results/attention优先；旧G3attention为136历史，93/94paused与本地WASD播放器不干预。所有新资料/失败/schema/source/同步/监控/Gitreceipt补Git，大weights/rawNPZ/USD/ZIP只actualpath-size-SHA。
''',encoding='utf8')
 print(json.dumps(dict(scope8_ascending=27,scope8_descending=27,original_ground_tolerance_m=1e-6,scope8_no_PPO_added=True,next10deg_CPU_rays=len(errors),CPU_error_m=float(max(errors)),next_normal_z=cosine,no_next10deg_GPU_package_or_job=True)))

if __name__=='__main__':
 try:main()
 except BaseException:save('SLOPE137_DECISION_SLOPE10_CPU_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),CPU_only=True));raise
