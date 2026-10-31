from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports';D=N/'D_BEFORE_USE_CWD_REPAIR_SOURCE';DR=D/'reports'
def read(p):return json.loads(p.read_bytes())
def put(name,v):
 with(R/name).open('x',encoding='utf8')as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
first=read(DR/'ROOT227D_W35_FIRST_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json')
state=read(DR/'ROOT227D_ORIGINAL_SOLO_OWNER_AND_CANONICAL_AFTER_FIRST_ACTUAL.json')
closed=read(DR/'ROOT227D_START_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')
launch=read(DR/'ROOT227D_ORIGINAL_SOLO_OWNER_LAUNCH_ACTUAL.json');node=read(DR/'ROOT227D_ORIGINAL_W35_NODE_LAUNCH_ACTUAL.json')
assert first['passed'] and first['actual_material_limit_error_count']==0 and state['current_owner_matched'] and closed['global_serial_control_client_lease']=='FREE'
go=state['current']['go']['w35_72'];value=first['first'];saved=value['first_complete'];owner=launch['owner']
assert set(state['current']['go'])=={'w35_72'} and go['run_id']==launch['run_id'] and go['original_owner_pid']==owner['pid'] and go['original_owner_creation']==owner['creation']
assert value['actual_new_PPO_updates']==1 and saved['saved_iteration']==32405 and saved['Adam_min']==saved['Adam_max']==649740
assert go['source_SHA']=='343e0fd8f4950ffea2b09808a3bf88d9dd68e14b06f84c7bdaad462dbc8a51bd'
assert go['max_parent_seconds']==3900 and go['exit_headroom_seconds']==300 and go['save_deadline']-go['learning_started_epoch']==3600
texts=first['full_selected_UTF8'];workerrows=[x for x in texts if x['path'].endswith('/WORKER_ORIGINAL_IDENTITY_BEFORE_WAIT.json')]
assert len(workerrows)==1;worker=json.loads(workerrows[0]['UTF8'])
def iso(t):return datetime.fromtimestamp(t,timezone(timedelta(hours=8))).isoformat()
binding=dict(epoch=time.time(),run_id=launch['run_id'],owner=owner,go={'w35_72':go},canonical_generation='MOD4_SINGLE_WRITER72_20261026',role='w35_72',scope='Every newremote fresh72 must match current exactowner/run/GO. Close72 before otherhost. After closing this is HISTORICAL;do not assume active or CNone.')
put('KNOWN_ACTIVE227D_AUTHORITY_BINDING_FOR_FUTURE_SERIAL_READONLY.json',binding)
out=dict(epoch=time.time(),kind='ACTUAL227D_W35_QUALIFIED343E_FULL_RM70_CONTINUATION_FIRST_PPO_AND_ORIGINAL_NORMAL_WORK_ORDER',
 run_id=launch['run_id'],owner=owner,node=node,worker_identity_actual_first_UTF8=worker,
 first=dict(value=value,native24=first['native24'],actual64Kerrors=0,scope='Snapshot atoneoriginalFIRST;not continuoushealth/final/fullskill/SuperMimic'),
 source=dict(SHA=go['source_SHA'],bytes=17619269,iteration=32404,Adam17=649720,LR=.00017085937500000009,source_model_installer_stat_hash_copy_read=0,worker_necessary_byte_read_decode=1,formal_original_frozen_untouched=True),
 schedule=dict(GO_epoch=go['learning_started_epoch'],GO=iso(go['learning_started_epoch']),SAVE_epoch=go['save_deadline'],SAVE=iso(go['save_deadline']),NOMINAL_epoch=go['nominal_end_epoch'],NOMINAL=iso(go['nominal_end_epoch']),normal_earliest_epoch=go['nominal_end_epoch']-900,normal_earliest=iso(go['nominal_end_epoch']-900),learning_seconds=3600,max_parent_seconds=3900,exit_seconds=300,time_not_completion=True),
 recipe='Own400N nominalengineeringk2000/50policy100feedback400physics2.5msTGS32/4F32/fixedSI35actor38critic/6motorclip6/PD/torque-speed/delay/D0white_v3D1-D7/perenv2mm/mimic.01/originalCAD full70mmpeak-to-trough RM70/originalW35rewardcommands. Not FudanJUMP or a newreward.',
 CAD=dict(peak_to_trough_mm=70,period_mm=240.641934,length_m=2.406423,width_m=2.0845,slope_deg=1.5,not_plusminus70_or35=True,shared_original_material_and_geometry_onlyprototype=True),
 fullstate='Fullactor/critic/STD/17Adam/LR/targetDR and originalprofile/commandstreams restored;freshphysical episode/reset/queue explicitly not exactPhysXresume. No new architecture or nativeWM conversion.',
 before_use_C_D_repair='C source/INDEX retained,neverexecuted. D restored actual219V3 owner+node globalcwd distincttaskroot,correctsender andwx unchanged. ActualDmetadata/CNone/resources/Ready/sourcefullstate/native24/FIRST admitted.',
 next_only=dict(collector=str(D/'collect227D_original_W35_formal_cost_normal900_UNUSED_once.py'),CPU=str(D/'review227D_NEW_W35_formal_initial_whole_CPU_UNUSED_once.py'),caller_INDEX_SHA='4ed43e0ea67798bd4a1e610a49807bb7a5ce32d16dd2b9e751be19f0ca442e0f',state='FROZEN_UNUSED',auth_provider=str(T.parent/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py'),normal_lease_prefix='ROOT227D_EXCLUSIVE_NORMAL900_',
  collector_rules='FreshLOCALexactCIM+globalserialleaseFREE;original signedLOCAL AND REMOTE nominal-now<=900;owner850/node180 unchanged. ActualCOHORT_FINAL/OWNER_EXIT/NODE_EXIT/allownwaitout/private+two sharedfree/freshCNone/exactoriginalGO+uniqueoriginalownersegment;one original rawfeeSUMONCE;onlyqualifiedNEWformaltransfer1/twohostSHA. PartialFAIL notpromoted.',
  CPU_rules='FullJSONguards before1NEWformalbyte/hash/decode;CUDAhiddeninsidePython;old343/E0/native/normal86zero. Allfinite35/38/STD6/17Adam=649720+20updates/iter32404+updates/fullD0-D7/newRM70command+terrain+typed227. Originaldeadline actualepoch,LRtruthful. No repeatedonceforstats/Git.'),
 closed_client=closed,other_remote_rule='Fresh exact227D authority untilclosed;old219bindingHISTORICAL;nohotadd/secondwriter/healthyjobstartupGPUrecheck/secondwatcher/earlycollector',
 E0_repair225230=dict(status='IndependentcopyCPUqualified+four10sregressions completed,9sampledwheelairruns;headingdrift andpartialnonwheelcontactsremain;notstablejumpor270;noE0learningselected',work_order=str(T/'E0_CAD_MEAN_OUTPUT_REPAIR_CANDIDATE_SOURCE_V225_20261101/reports/CURRENT_ACTUAL225_COPY_230_BILATERAL_WHEEL_AIR_AND_REMAINING_HEADING_WORK_ORDER.json'),phase225_consumed_HEAD='95fa755677dd0567b1a3fdc8dddc606177c5045a',phase225_tag_object='2ed6415798028077e6fa50290683145bb4ac2e73',protected_prior_tag_count=1507),
 pending=dict(W35_full32s_skill='227BsourceREADY_only,222partial14.8s preserved;notprerequisiteforindependentW35PPO',E2='226source andnewtargetmetadataTaskinterface inpreparation,notactualskill',E3='NOT_GRADUATED',full_SuperMimic=False,true270=False),
 original_canonical_no_new_grant_copy_refund_or_secondwriter=True,Git_phase='mod4-w35-qualified343e-original-full-rm70-continuation-ppo227',any_existing_phase_tag_consumed_do_not_rerecord=True)
put('CURRENT_ACTUAL227D_QUALIFIED_W35_CONTINUATION_FIRST_AND_NORMAL_WORK_ORDER.json',out)
print(json.dumps(dict(passed=True,run_id=launch['run_id'],schedule=out['schedule'],first=saved,worker=worker)))
