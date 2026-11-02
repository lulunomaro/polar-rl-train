"""Source-onlydependency/interface review+finalindex, no SDK/model/raw.
Onlyfour childworkers. Parentownsother5/supervisor/actualadmission/collector.
"""
from pathlib import Path
import ast,hashlib,json,time,traceback
B=Path(__file__).resolve().parent;T=B.parent
H=lambda b:hashlib.sha256(b).hexdigest()
def record(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=H(b))
def put(name,x):
 p=B/name
 with p.open('x',encoding='utf-8') as f:json.dump(x,f,ensure_ascii=False,indent=2)
 return record(p)

def main():
 contracts=json.loads((B/'ROLE_CONTRACTS.json').read_bytes());m=json.loads((B/'FOUR_E1_SOURCE_ONLY_MOCK_PROOF_V1.json').read_bytes());assert m['passed'] and m['check_count']==60
 deps=[];graphs=[]
 files=['e1_reset_evidence_training_env.py','e1_terrain_training_env.py','e1_terrain_runtime.py','chassis_pd_training_env.py','gas_damping_training_env.py','spring_pressure_training_env.py','action_delay_training_env.py','feedback_delay_runtime.py','sensor_a0_runtime.py','mild_dr.py','explicit_pd_sdk_adapter.py','chassis_com_pose_roundtrip_sdk_adapter.py','action_delay_sdk_adapter.py','action_delay_physics_queue.py','mod4v1_fresh_dr_guard.py','mod4v1_e1_collision_bank_compat.py','e1_full_pose_reset.py','mod4_task.py','launcher_mod4v1_e1_actual.py','frozen_history_policy.py']
 for role,c in contracts.items():
  root=Path(c['own_runtime_source_root']);mod=root/'runtime/isaac/mod4';rows=[]
  for name in files:
   p=mod/name;raw=p.read_bytes();parse=raw.replace(b'\r\r\n',b'\r\n') if b'\r\r\n' in raw else raw;tr=ast.parse(parse,filename=str(p));row=record(p);row.update(role=role,relative='runtime/isaac/mod4/'+name,AST_SHA=H(ast.dump(tr,include_attributes=False).encode()),classes=[dict(name=n.name,bases=[ast.unparse(x) for x in n.bases]) for n in tr.body if isinstance(n,ast.ClassDef)]);deps.append(row);rows.append(row)
  extra=['independent_expert_axis_v1.py','train_independent_owned_axis_v1.py'] if role=='SLOPE_INDEPENDENT50' else ['curb20_geometry.py','curb20_profile.json'] if role.startswith('CURB') else ['slope5_geometry.py','slope5_profile.json']
  for name in extra:
   p=mod/name;row=record(p);row.update(role=role,relative='runtime/isaac/mod4/'+name);deps.append(row)
  graphs.append(dict(role=role,physical_factory='Own original E1ResetEvidenceLearningEnv(cfg)' if role!='SLOPE_INDEPENDENT50' else 'Own exacttrain_independent_owned_axis_v1.build_env AST->RetentionLearningEnv',freshDR_chain='E1ResetEvidence->E1Terrain->E1ChassisTerrain->ChassisPD(D7COM/PD)->GasDamping(D6)->SpringPressure(D5)->ActionDelay(D4)->DelaySensor(D3/D1-D2)->Mod4Env +cfgMildDR(D0)',fresh_seed=20260928,physical_saved20k_restore_helper_calls=0,physical_slice_or_projection_calls=0,model_core='A0liveactor9inclSTD,critic8/17Adam/LR/iter+unknownroot remainwholecacheexact',auditor='ExistingFreshDRNominalGuard/API+originalMildDR/D7+D5/D6componentmemoryparameters, notbackendindependentqualification',sources=rows))
 put('FULL_FRESH_N80_D0_D7_SOURCE_DEPENDENCY_GRAPH_V1.json',dict(graphs=graphs,files=deps,PT_SDK_calls=0,no_physical_audit_executed=True))
 # ExactAPI bindings and sourcebackendunknowns areexplicit, no invalidglobalclaim.
 interface=dict(kind='SOURCE_ONLY_FOUR_E1_CHILD_WORKER_INTERFACE',purpose='N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_NOT_FULL20K_RESUME',root=str(B),worker_basenames={r:c['worker_basename'] for r,c in contracts.items()},CLI='python -B WORKER --task CASE/task.json --group-root GROUP_ROOT',source_roots={r:c['own_runtime_source_root'] for r,c in contracts.items()},group_parent_fields=['group_id','GPU_UUID','actual_group_admission.source_SDK_admitted','actual_group_admission.private_GPU_EX_held','actual_group_admission.global_finite_EX_held','actual_group_admission.inherited_lock_fds','absolute_worker_deadline_epoch'],no_child_gpu_or_finite_lock_acquisition=True,barrier=dict(ready='CASE/WORKER_SCENE_READY.json',start='GROUP_ROOT/GROUP_EVAL_START.json',start_fields=['group_id','GPU_UUID','members','all_members_ready'],abort='GROUP_ROOT/GROUP_STARTUP_ABORT.json',maximum_wait_seconds=900,wait_no_actor_step_RNG=True),output=['FINAL.json','PRE_CLOSE.json','WORKER_ERROR.json','OWN_NEW_SKILL_RAW.npz','OWN_PARTIAL_SKILL_RAW.npz'],Appclose='FINAL/PRE_CLOSE beforeAppclose; actualparentwaitRC0andnoERROR required foractualPASS',fresh_scope='AllfourN80freshoriginalrecipes+constructor+ONEreset, not20ksavedDR/histories/RNGphysicalapplication; sourceoncedecodeddictunchanged',group_singleGPU='9SDKscenes requested byparent, childowns4casesonly; notmultiGPU/DDP/BPTT/PPO, actualresourceeligibilityunassessedhere',scope_limits=['NoSDK/memory/performance/resourceavailability measured inthissourcephase','SLOPE50 originalacceptedfullroutecohort/predicateGAP remains;1000control20s owntrainingaxisscreen descriptivenot135 borrowed','OldN80CurbsourceexplicitlydocumentsRSLwrapperreset; newONEfreshresetA0bridge doesnotconstructRSLwrapper. NotpairedoldfreshDRinitialassignments.','ActualN80freshfullDRAPIaudits/ownbankcomposition/actorload needparentfreshSDKsourceadmission andonegroupactualrun; notpredeclaredPASS','No Modelbytes/NPZ/USD/raw observed here. Runtime/source/bodybank binaries referencesonly.','Existingwhole20knativerestorePASS isseparateproof; cachedcritic17Adam isnotliveoptimizerrestore.'])
 put('FOUR_E1_WORKER_PARENT_INTERFACE_SOURCE_V1.json',interface)
 lines=['# 四个E1子worker：单GPU并行N80 fresh-fullDR技能screen（SOURCE_ONLY）','','**尚未实际执行；没有SDK/GPU/PT/预算/GO操作。** 父进程负责9成员总调度、单GPU原privateEX+globalfiniteEX、actualwait/RC0与全9结果。这里仅4个E1子worker。','','## 稳定接口','`python -B WORKER --task <case/task.json> --group-root <groupRoot>`','','| role | worker | N80窗口 | 解释 |','|---|---|---|---|']
 for role,c in contracts.items():lines.append('|'+role+'|['+c['worker_basename']+'](<'+(B/c['worker_basename']).as_posix()+'>)|'+str(c['controls'])+'control /'+str(c['controls']*8)+'physical /'+str(c['controls']*2)+'feedback|'+c['scope']+'|')
 lines+=['','## 目的分域与原条件','- 每个case保留完整typed PT的一次bytes/SHA/decode缓存，全部unknownroot/nested/20k savedDR历史不改不投影；live原A0 actor+learnedSTD strict载入，critic/17Adam/LR/iter前后cache identity，不冒liveoptimizer/full20kDR恢复。旧whole20k nativePASS分立。','- N80全D0–D7由各自原构造器、privatefresh seeds和ONE本次explicitreset生成，2c/bae新constructor nominal保护；D0白名单mass/inertia/material/motorgain，D1-D2噪声bias，D3 100Hz反馈lag，D4独立leg4/wheel2物理lag，D5 k2000，D6原gasdamping，D7 COM/PD不删。API/component-memory审计不是backend独立资格。','- 前三原factory40x40/80独立tile、40+40镜像、27up27down26stand、seed20260928；15s=750×.02、6000×.0025、1500反馈。Curb端点±.275，Slope135端点±1.2，两轮before/after同episode/firstordinary前且meanload>1N；stand不强cross，不增加总体率。','- Slope50只用自身train_independent_owned_axis_v1.build_env AST+原freshbinder、自然commands/RNG20s，描述自己的trainingaxis/fullramp目标family，不借135的80cohort/27+27成绩。','- 原Curb源码明记RSLwrapper额外reset；新A0无reset数据bridge规避第二reset，以此明确是新的N80freshDR cohort，不称旧assignments配对。','','## 并行屏障与退出','四子worker不抢privateGPU/finite锁、不检查空卡、不执行nvidia查询。验证父已held且passfd有效（只fstat），CUDA_VISIBLE_DEVICES与groupUUID匹配，cuda:0。每case唯一Kit/warp缓存与-B。','scene/actor/freshDR准备好写WORKER_SCENE_READY.json，此时0physics/actorforward；等GROUP_EVAL_START.json最长900s，wait无step/actor/RNG。任何WORKER_ERROR由父取消整个自己group scope，不单case重试。FINAL/PRE_CLOSE先写，原Appclose可能exit，actualparentwaitRC0才为最终退出证据。','','## 本地验证','4来源整cache/unknownroot不可变/禁止20khistory暴露/组fd与GPU/abort与900s/零callbarrier/双轮端点跨reset禁止拼接等60项纯stdlib合成MOCK通过；不是Torch/SDK或物理PASS。3个原80factory前缀的授权替换逆变换AST完全一致；S50只抽自身build_env AST、不执行entrymain/第二App/restore helper。','模型metadata和完整源码依赖详见机器索引，父fresh实际资源/源SDK准入后才可统一一次group执行。','','## 主要文件']
 for name in ['ROLE_CONTRACTS.json','FOUR_E1_WORKER_PARENT_INTERFACE_SOURCE_V1.json','FULL_FRESH_N80_D0_D7_SOURCE_DEPENDENCY_GRAPH_V1.json','FOUR_E1_ORIGINAL_FACTORY_AST_DIFF_PROOF_V1.json','FOUR_E1_SOURCE_ONLY_MOCK_PROOF_V1.json','emit_four_e1_descriptors_sourceonly.py']:
  lines.append('- ['+name+'](<'+(B/name).as_posix()+'>)')
 with (B/'FOUR_E1_PARALLEL_N80_SOURCE_README_V1.md').open('x',encoding='utf-8') as f:f.write('\n'.join(lines)+'\n')
 # AllsourcepyAST compileonly, noimportSDK/Torch.
 astrows=[]
 for p in B.glob('*.py'):
  raw=p.read_bytes();tr=ast.parse(raw,filename=str(p));compile(tr,str(p),'exec');astrows.append(dict(**record(p),AST_SHA=H(ast.dump(tr,include_attributes=False).encode())))
 put('FINAL_FOUR_E1_LOCAL_AST_VALIDATION_V1.json',dict(passed=True,AST=astrows,source_MOCK_checks=60,noSDK_orPToperations=True))
 print(json.dumps(dict(ready_for_parent_SOURCE_review=True,actualSDK_ready=False,workers=4,freshDR_dependency_files=len(deps),MOCK60=True,PT_SDK_calls=0),indent=2))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (B/('FINALIZE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf-8') as f:json.dump(dict(error=traceback.format_exc(),model_SDK_operations=0),f,indent=2)
  raise
