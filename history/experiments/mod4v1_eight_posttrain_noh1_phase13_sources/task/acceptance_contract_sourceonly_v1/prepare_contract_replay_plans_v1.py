"""Append V2 referenceclosure and executableSOURCE_ONLY taskemission metadata.
Doesnotconstruct/load/step any simulator/model or edit an oldseal/parentfile.
"""
from pathlib import Path
import ast,csv,hashlib,json,time
B=Path(__file__).resolve().parent;T=B.parent
v=json.loads((B/'ORIGINAL_ACCEPTANCE_CONTRACT_MATRIX_V1.json').read_bytes());p=B/'PARENT_SCOPE_STATEMENTS_V1.json';raw=p.read_bytes();v['references']['PARENT_SCOPE_ONLY']=dict(id='PARENT_SCOPE_ONLY',path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),kind='DIRECT_SCOPE_STATEMENT_NOT_A_MEASUREMENT')
W=Path(r'C:\Users\lulu\Desktop\claude\mjcf');own=W/'MOD4_THREE_EXPERTS_AND_CURB878_EVAL_20261016/curb113_frozen_v2/eval_payload_v2/full80_runtime_native_v1.py';raw=own.read_bytes();assert hashlib.sha256(raw).hexdigest()==v['references']['CURB_EVAL_FACTORY']['SHA'];x=dict(v['references']['CURB_EVAL_FACTORY']);x.update(id='CURB113_OWN_EVAL_FACTORY',path=str(own),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),same_SHA_as_original_protected_common_factory=True);v['references']['CURB113_OWN_EVAL_FACTORY']=x
profile=T/'staged_sources/E1_SLOPE_INDEPENDENT50_40050_MOD4V1_SOURCE_V2/runtime/isaac/mod4/slope5_profile.json';raw=profile.read_bytes();j=json.loads(raw);v['references']['SLOPE50_OWN_GEOMETRY']=dict(id='SLOPE50_OWN_GEOMETRY',path=str(profile),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),kind='OWNexecuted_geometry_profile',original_values={k:j[k] for k in ('angle_deg','ramp_length_m','height_m','ramp_start_x_m','ramp_end_x_m','tile_size_m')})
for rr in v['rows']:
 if rr['lineage']=='CURB113':rr['original_reference_ids']=[('CURB113_OWN_EVAL_FACTORY' if z=='CURB_EVAL_FACTORY' else z) for z in rr['original_reference_ids']]
 if rr['lineage']=='SLOPE50':rr['original_reference_ids'].append('SLOPE50_OWN_GEOMETRY')
v['schema']='mod4.original_acceptance_contract_SOURCEONLY.v2';v['V1_preserved_revision']='V2adds Parent_scope refclosure, CURB113 ownexactSHA factory, Slope50 ownprofile refs and executableplanlabels, no predicateoractualsource change'
for r in v['rows']:
 if r['lineage']=='SLOPE50':r['original_episode_limit_seconds']=20;r['episode_limit_source_gap']=None
 for ref in r['original_reference_ids']:assert ref in v['references'],(r['lineage'],ref)
with (B/'ORIGINAL_ACCEPTANCE_CONTRACT_MATRIX_V2.json').open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
plans=[];deps=[]
for r in v['rows']:
 name=r['lineage'];window=r['original_replay_window_seconds'];ids=r['original_reference_ids'];deps0=[]
 for i in ids+([r['current_native24_integration']['reference']] if name!='W35' else []):
  x=v['references'][i];d=dict(lineage=name,reference_id=i,path=x['path'],SHA=x['SHA'],bytes=x['bytes'],role=x['kind']);deps.append(d);deps0.append(d)
 original_observation_only=name in ('E3','W35');gaps=list(r['saved_evidence_gaps'])
 if name in ('CURB878','CURB113','SLOPE135'):gaps.append('Futureadapter mustexplicitlydeclare originalN80freshDRskill cohort vswholeN20k savedfullrestore integration. No fullstate20k->80 projection/slicing/claim; originalscope80 success isseparate fromcurrent20k native proof.')
 if name=='E0':windows=[dict(seconds=20,controls50Hz=1000,physics400Hz=8000,feedback100Hz=2000,warmup_seconds=2,steady_seconds=18)]
 elif name=='E2':windows=[dict(seconds=18,controls50Hz=900,physics400Hz=7200,feedback100Hz=1800,warmup_seconds=2,steady_seconds=16),dict(seconds=24,controls50Hz=1200,physics400Hz=9600,feedback100Hz=2400,warmup_seconds=2,steady_seconds=22)]
 elif name in ('CURB878','CURB113','SLOPE135'):windows=[dict(seconds=15,controls50Hz=750,physics400Hz=6000,feedback100Hz=1500,original100Hzcontrols1500_kept_seconds=True)]
 elif name=='H1_NORMAL':windows=[dict(source_base_default_episode_seconds=20,source_declared_task_request_seconds=[1,1.8],physical_callbacks=dict(ready=80,air=16,land=12,recover=200),actual_accepted_original_skill_window='GAP_notinferredfromdefault20')]
 else:windows=[]
 plan=dict(schema='mod4.future_replay.source_only_descriptor.v1',lineage=name,original_model_SHA=r['original_source_SHA'],status='EXCLUDED_PARENT_LIVE_NO_TASK_EMIT' if name=='W35' else 'ALREADY_CONSUMED160_OBSERVATION_NO_REPEAT' if name=='E3' else 'SOURCE_DERIVED_UNEXECUTED_NOT_READY',actual_SDK_permission=False,dispatch_or_model_io=False,source_only_plan_emitter=True,own_original_cohort=r['seed_or_cohort'],own_command_geometry=r['commands_geometry'],own_original_metric_predicate=r['original_metric_predicate'],physical_seconds_windows=windows,restore_dependency=dict(reuse='OWN acceptednativeNOUPDATE completecached restore driver only, actualfutureparentbinding required',selected_physical_source='Useownpinned actualtyped/native source receipt, no latest/noactor-tensor equivalence',samecache='Onephysicalbyte/hash/decode peradmittedpurpose, 17Adam/LR/iter/STD intact, ownqueue/RNG/helperrestore, ONEoriginalreset/newnominal retained',checkpoint_metadata_newkeys=False,never_borrow_W35_E0_factory_command_map_RNG=True),metric_capture_contract=dict(read='Originalnatural before/aftercontrol+pre-reset terminalbuffers; source-only dependencyhook only, no actor/RNG/setter/force/query amplification',timers='Retainoriginalphysicsseconds; control50Hz/feedback100Hz/physics400Hz. Public100Hzage+=2, physicalcallbackgates unchanged',failure='Keepordinary/integrity/timeouts/routeboundarytruncations +allpartial/right/leftcensors, no populationpassrate added',old_current_boundary='Firstoriginalboundary cutslogicalmetricprefix only; no runtimehotpatch. Earliernewintegrationreset =>current-integration-censored, notoriginalskillfailure; no crossreset/prefixstitch',independence='Differentplants/guards/seedcohorts are unpaired, no migrationcausalclaim'),original_numeric_aggregate_acceptance_rule=None,dependency_table=deps0,exact_saved_evidence_gaps=gaps,current_runtime_or_newthreshold_changes=False,needs_parent_independent_admission_and_sourcebound_adapter_review=True)
 plans.append(plan)
with (B/'NEWPLANT_SOURCE_ONLY_REPLAY_PLANS_V1.json').open('x',encoding='utf-8') as f:json.dump(dict(schema='mod4.newplant.replayplan.sourceonly.v1',plans=plans,no_runtime_or_model_operations=True,no_duplicated_W35case_or_E3_160=True),f,ensure_ascii=False,indent=2)
with (B/'SOURCE_ONLY_REPLAY_DEPENDENCY_TABLE_V1.csv').open('x',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['lineage','reference_id','path','SHA','bytes','role']);w.writeheader();w.writerows(deps)
lines=['# 九谱系原技能验收证据矩阵（SOURCE_ONLY）','','冻结/原PPO完整保存、native24集成、原技能范围接受是三类独立事实；当前全长技能未统一毕业。','本包仅本地文本/JSON/AST/MOCK，无模型或SDK操作；W35父活case及数据排除，E3已160控制观察不重复。','','| 谱系 | 原接受/观测范围 | 当前newplant | 关键不足 |','|---|---|---|---|']
for r in v['rows']:
 native='native24/192/48集成PASS；非长技能' if r['lineage']!='W35' else '父live独评排除不读'
 lines.append('|'+r['lineage']+'|'+r['original_accepted_scope']+'|'+native+'|'+r['saved_evidence_gaps'][0]+'|')
lines+=['','## 关键原值与时间','- E0：20s、20k、1000个50Hz控制；命令12–16s，原完整事件、reset-ended、0控制和窗口尾分别统计；无保存全局数值毕业规则。','- E2：独立18s/24s；signed2π同UID/episode/direction/sign，沿向0.5±0.05m/s、横向±0.05m/s、yaw误差±0.2rad/s，term或timeout即非有效完整样本。原53140complete/52588false/552fact及42timeout-at-complete保留，不做新通过率。','- Curb/Slope135：原1500×.01s=15s，50Hz为750control/6000physical/1500feedback；原27/27、26/27以及stand不cross逐样例语义保留。当前native24=.48s不是15s验收。','- H1：真270mm平台/实际轮底、跨边/平台contact/footprint；ready80/air16/land12/recover200均400Hz物理回调，分别.2/.04/.03/.5s。原publicrequest[1,1.8)s；不是COM/轮中心高度。','- E3：recipe0–11固定倒地、12正常；public100Hzage<300=3s；stable50 ageunits=.5s=25个50Hz控制，age/stable每control+2。原ownercredit不含新MCI门，当前133/18462不是旧1cd技能通过。','','## 旧与当前边界分域','旧E0/E2 snapshot closure.002/mimic.05，与当前newplant closure.01/mimic.01并列；不是同物理门槛复测。仅采first-original-boundary-hit prefix；current-integration先截断标censored/不完整，不冒原skill失败。旧closure先触发也截止原prefix，不续拼完整成功。无运行时热改、无新更严gate/事后总体通过率。','','## 完整证据路径与SHA']
for id,x in v['references'].items():lines.append('- **'+id+'** ['+Path(x['path']).name+'](<'+Path(x['path']).as_posix()+'>) `'+x['SHA']+'`')
with (B/'ACCEPTANCE_CONTRACT_MATRIX_SOURCE_ONLY_V1.md').open('x',encoding='utf-8') as f:f.write('\n'.join(lines)+'\n')
print(json.dumps(dict(matrixV2=True,lineages=9,dependency_rows=len(deps),sourceonly_plans=len(plans),no_runtime_model_operations=True),indent=2))
