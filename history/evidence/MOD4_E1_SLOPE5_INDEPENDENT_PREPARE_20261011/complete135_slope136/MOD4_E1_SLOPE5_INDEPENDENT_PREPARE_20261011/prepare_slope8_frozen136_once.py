"""Accept the complete135 scoped evidence and prepare one new8degree frozen scope."""
from slope_io import *
import ast,zipfile,importlib.util,traceback
import numpy as np
ROOT='/home/egde/rl_candidates/MOD4_S3_E1_SLOPE5_SNAPSHOT_REVIEWED_20261011'
CP_SHA='24b18846fcff1e0b8da7fd478314fca9cd2ed2b97461ca34f65ef5b7c7ff2411'
PROTOCOL='approved_E1_SLOPE_derived8deg_mirrored_fullroute_behavior_v1'

def main():
 review_path=sorted(R.glob('SLOPE135_SCHEMA_REVIEW_[0-9]*.json'))[-1];v=json.loads(review_path.read_bytes())
 own_path=sorted(R.glob('SNAPSHOT_OWN_FORMAL_CPU_[0-9]*.json'))[-1];own=json.loads(own_path.read_bytes())
 assert v['review_complete'] and own['ready'] and not own['pending'] and own['checkpoint']['sha256']==CP_SHA
 assert own['canonical']['active'] is None and all(x['free'] for x in own['two_real_OS_locks'])
 assert all(x['actual'] is None or x['actual']['state']=='Z' for x in own['actual_parent_guardian_child'])
 assert all(v['terrain']['groups'][g]['complete_envs']==v['terrain']['groups'][g]['contact_confirmed_envs']==27 for g in ('ascending','descending'))
 decision=dict(epoch=time.time(),trial_id='E1-SLOPE5-135-COMPLETE-SCOPE-DECISION-01',complete_review=str(review_path),own_cpu=str(own_path),
  complete135_twohost_fullraw_contract_reviewed=True,selected_checkpoint=own['checkpoint'],source_count=404,actual_snapshot_count=79,
  terrain_groups=v['terrain']['groups'],scoped_5degree_mirrored_traversal_accepted=True,freeze_5degree_scope_candidate=True,
  qualified_full_SLOPE_or_MoE_deployment=False,gate_trained=False,hardware_calibrated=False,
  source364_and_own_both_complete54_routes=True,no_claimed_causal_learning_gain=True,
  old_skill_diagnostic=v['summary']['retention'],negative4pi_source7_candidate5_of8_decline_preserved=True,
  no_permanent_anti_forgetting_proof=True,old_strict_false_and_all_raw_prefix_cost_preserved=True,
  no_more_same5degree_PPO=True,next_axis='approved_RM003_8degree_continuous_ramp_frozen_scope_first',
  next8degree_learning_not_admitted_before_actual_scope_contracts=True,no_budget_extension=True)
 save('SLOPE135_COMPLETE_SCOPE_DECISION.json',decision)
 save('SELECTED_E1_SLOPE8_FROZEN_SOURCE.json',dict(epoch=time.time(),selection='complete135_own404_scoped5degree_candidate',
  checkpoint=own['checkpoint'],complete_review=str(review_path),own_cpu=str(own_path),previous364_source_remains_immutable=True,
  previous_Wave_CURB_not_selected=True,reason='Own independent SLOPE5 complete mirrored ascending/descending54 routes with original contact and data tolerances; advance only geometry angle in approved5-to8 branch.',
  negative4pi_decline_is_diagnostic_and_not_erased=True,no_gate_or_whole_RM_qualification=True))
 (D/'next_slope8_scope').mkdir(exist_ok=True);impl=D/'next_slope8_scope'
 old_geometry=(PRE/'implementation/slope5_geometry.py').read_text(encoding='utf8')
 geometry=old_geometry.replace('5degree','8degree').replace('5deg','8deg').replace('slope5','slope8').replace("p['angle_deg']==5.","p['angle_deg']==8.").replace('angle_deg=5.','angle_deg=8.')
 assert geometry!=old_geometry;compile(geometry,'slope8_geometry.py','exec')
 gp=impl/'slope8_geometry.py';assert not gp.exists();gp.write_text(geometry,encoding='utf8')
 h=2.*np.tan(np.deg2rad(8.));xs=[-4.5,-1.,1.,4.5];zs=[0.,0.,h,h]
 vertices=[[x,y,z] for x,z in zip(xs,zs) for y in (-4.5,4.5)];faces=[]
 for j in range(3):k=2*j;faces.extend([[k,k+2,k+3],[k,k+3,k+1]])
 profile=dict(schema='derived_continuous8deg_ramp_cpu_component_v1',angle_deg=8.,ramp_length_m=2.,height_m=float(h),
  ramp_start_x_m=-1.,ramp_end_x_m=1.,tile_size_m=[9.,9.],vertices=vertices,triangles=faces,no_vertical_riser=True,
  lower_upper_support_m=3.5,derived_not_actual_RM_geometry=True,RM003_local8deg_branch_only=True,
  previous5deg_scope_unchanged=True,not_stair_flight=True,not_physical_traversal_pass=True)
 pp=impl/'slope8_profile.json';assert not pp.exists();pp.write_bytes(json.dumps(profile,indent=2).encode())
 spec=importlib.util.spec_from_file_location('slope8_component',gp);component=importlib.util.module_from_spec(spec);spec.loader.exec_module(component)
 spec=importlib.util.spec_from_file_location('slope8_ray',W/'MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_20261010/prepare_curb_component_once.py');raymod=importlib.util.module_from_spec(spec);spec.loader.exec_module(raymod)
 errs=[];angle_errors=[]
 for mirrored in (False,True):
  mesh,origin=component.make_mesh((9.,9.),mirrored);vertices=mesh.vertices.copy();vertices[:,:2]-=4.5;orientation=-1 if mirrored else 1
  for x in np.r_[np.linspace(-4.4,4.4,31),[-1.,1.]]:
   for y in (-4.,0.,4.):
    hit=raymod.ray(np.array([orientation*x,y,2.]),np.array([0.,0.,-1.]),vertices,mesh.faces)
    errs.append(abs(hit[2]-np.clip((x+1.)/2,0,1)*h))
  triangles=vertices[mesh.faces];incline=np.ptp(triangles[:,:,2],axis=1)>1e-10
  angle_errors.extend(abs(np.rad2deg(np.arccos(mesh.face_normals[incline,2]))-8.).tolist())
 assert max(errs)<1e-10 and max(angle_errors)<1e-10
 parent=PRE/'artifacts/e1-slope5-derived-mirrored-fullroute-frozen-v1.zip';assert H(parent.read_bytes())=='f94fc989a1dd8a02a7b535aa7974a8172a9441762563518970a756a46fcb8bc9'
 with zipfile.ZipFile(parent) as z:members={n:z.read(n) for n in z.namelist()}
 manifest=json.loads(members['SOURCE_MANIFEST.json']);assert all(H(members[n])==sha for n,sha in manifest['files'].items())
 old=members['runtime/isaac/mod4/frozen_history_flat.py'].decode();new=old.replace('from slope5_geometry import configure_slope as configure_intro','from slope8_geometry import configure_slope as configure_intro')
 new=new.replace('np.deg2rad(5.)','np.deg2rad(8.)').replace('angle_deg=5.','angle_deg=8.').replace('continuous5deg','continuous8deg').replace('approved_E1_SLOPE_derived5deg_mirrored_fullroute_behavior_v1',PROTOCOL)
 assert new!=old and 'np.deg2rad(5.)' not in new
 loop=lambda s:next(n for n in next(x for x in ast.parse(s).body if isinstance(x,ast.FunctionDef) and x.name=='main').body if isinstance(n,ast.For) and ast.unparse(n.target)=='step')
 assert ast.dump(loop(old),include_attributes=False)==ast.dump(loop(new),include_attributes=False)
 compile(new,'frozen_history_flat_SLOPE136.py','exec');(impl/'frozen_history_flat_SLOPE136.py').write_text(new,encoding='utf8')
 changes={'runtime/isaac/mod4/frozen_history_flat.py':new.encode(),'runtime/isaac/mod4/slope8_geometry.py':gp.read_bytes(),'runtime/isaac/mod4/slope8_profile.json':pp.read_bytes()}
 members.update(changes);manifest.update(protocol=PROTOCOL,parent_archive_sha256=H(parent.read_bytes()),current_geometry_revision004='E1_SLOPE8',current_geometry_is_G3_wave=False,current_geometry_is_CURB=False,
  derived_not_actual_RM_geometry=True,current_frozen_scope=dict(angle_deg=8.,ramp_length_m=2.,mirrored=True,approach_m=.4,after_support_m=.2,steps=1500,num_envs=80,seconds=15,optimizer_updates=0))
 manifest['files']={n:H(b) for n,b in members.items() if n!='SOURCE_MANIFEST.json'};manifest['new_or_changed_members']={n:H(b) for n,b in changes.items()};members['SOURCE_MANIFEST.json']=json.dumps(manifest,indent=2).encode()
 pkg=impl/'e1-slope8-derived-mirrored-fullroute-frozen-v1.zip';assert not pkg.exists()
 with zipfile.ZipFile(pkg,'w',zipfile.ZIP_DEFLATED) as z:
  for name,raw in members.items():z.writestr(name,raw)
 with zipfile.ZipFile(pkg) as z:assert all(H(z.read(n))==sha for n,sha in manifest['files'].items())
 prior=json.loads((PRE/'reports/SLOPE5_FROZEN_PREPARED.json').read_bytes())['jobs'][0];job=dict(prior)
 cp=dict(path=E+'/artifacts/e1-slope5-own-'+CP_SHA+'.pt',bytes=17615794,sha256=CP_SHA)
 pkginfo=dict(path=str(pkg.resolve()),bytes=pkg.stat().st_size,sha256=H(pkg.read_bytes()))
 job.update(job_id='clk2500-closure-episode-d3-136-e1-slope8-source404-mirrored-fullroute-flat',role='E1_SLOPE8_complete135_source404_frozen_anchor',protocol=PROTOCOL,
  actual_behavior_scope='Approved single angle5to8 axis: derived8degree2m mirrored ramp, same0.4m approach and200mm after support; frozen only.',
  artifacts=dict(runtime=dict(path=E+'/artifacts/'+pkg.name,bytes=pkginfo['bytes'],sha256=pkginfo['sha256']),checkpoint=cp))
 save('SLOPE8_FROZEN136_PREPARED.json',dict(epoch=time.time(),trial_id='E1-SLOPE8-MIRRORED-FROZEN-SCOPE-01',package=pkginfo,jobs=[job],
  profile=profile,source_own_checkpoint=own['checkpoint'],source_complete135_review=str(review_path),
  immutable_files_map_exact=len(manifest['files']),old_unchanged_members=len(members)-len(changes)-1,
  changed_members={n:H(b) for n,b in changes.items()},independent_triangle_rays=len(errs),max_vertical_ray_error_m=float(max(errs)),
  max_mesh_slope_angle_error_deg=float(max(angle_errors)),physical_step_health_hardware_contact_auditor_AST_exact=True,
  CPU_component_and_package_passed_only=True,new_SDK_native_fullstate_PPO_learning_executor_pending=True,
  no_GPU_PPO_queue_or_canonical_write=True,new_budget_seconds=0))
 work=R/'NEXT_E1_SLOPE8_FROZEN_AND_INDEPENDENT_WORK_ORDER.md';assert not work.exists()
 work.write_text('''# 已批准坡面单轴5°→8°冻结验收与后续独立范围

135四case完整实际审查：独立source404 own24b18846全5°/2m镜像上下行各27/27且1N接触支撑吻合，站立26不要求跨坡。来源3643c97同5°也各27/27，不声称因果学习收益。负4π7→5/8诊断下降与原strictfalse保持；world64/64、直线误差.020943796/.055501711。冻结本次5°范围候选，不是整个SLOPE/RM或MoE部署合格，E0一直冻结，gate未训。

下一仅批准RM003坡面分支角度5→8：派生连续8°/2m高约.281081669m，9m格左右镜像、同0.4m接近和两轮完整坡段后200mm支撑。新136仅frozen，无PPO，来源实际完整135 own40424b、CPU102/79snapshot/ownPID/PASSED/唯一段。不同8°几何不得冒同5°精确初始化；不改原5°成功或旧失败。

136实际complete/errorfree后，取两hostprobe/result字节SHA与完整NPZ；核root30q/参数recipesassignments/6000callback/ground-contact积分COMlinkhardware原容差、真实镜像方向、sameepisode prereset-before轨迹排除reset teleport、上下坡两轮后支撑/原1N接触与位置分列、站立/ordinary/truncation及所有有效prefix。未完成不是自动延窗缩接近重标成功。

只有实际结果合理且确实需要学习时才新独立8°root/geometryassignmentgroundcontactresetfullsavefullresumeownership合同；完整来源actorcriticstdoptimizer/allD0D7/globalnamed/dictprivateCPUCUDA先exact验证，再明确5→8新geometry/assignment迁移和CUDA磁盘roundtrip/savedsourceepisode+1，非PhysXexactresume。旧named严格集合、旧assignment身份不能放宽。同8°恢复须exact。必要新CPU/SDK10x300/native20k24warm120timed/128x2和20kx4完整PPO弃权重各一次同canonical，旧clock/DR证据exactreuse不重45minclock；全部准入通过后首300s含load-learn-save-exit/15s本机guardian，完整保存后新的terrain/flat/spin/world匹配审查。没有这些证据不自动PPO/升10°；若冻结能力已足够，优先冻结范围并按下一单轴，避免机械重复训练。

E0/Wave/CURB/已有5°权重及optimizer输出不覆盖，004hardtop1完整6action/gate未训保持。预算828000s/六扩展各一次/新增0，CPU/native/frozen无PPO不扣；新GPU权只actual旧ownfullsave/PASSED/三进程exit/twoOSlocksfree/唯一结清。禁止旧once/main/resume/replay、hotpatch/kill/dual20k/clear账。人类WASD播放器不干预。所有失败/false/raw/cost/source/schema/同步/monitor/工作单及后136报告Git补交，大weights/rawNPZ/USD/ZIP只实际path-size-SHA。
''',encoding='utf8')
 print(json.dumps(dict(package=pkginfo,rays=len(errs),max_error=float(max(errs)),files=len(manifest['files']),source_SHA=CP_SHA,frozen_prepared_not_physical_pass=True)))

if __name__=='__main__':
 try:main()
 except BaseException:save('SLOPE8_PREPARE_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),CPU_only=True,do_not_blind_replay=True));raise
