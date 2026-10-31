"""Local report/app-request preparation only; no model/raw/SDK/network actions."""
from pathlib import Path
import json,time
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
P=T/'E0_JUMP32066_GROUND10_THREE_HOUR_V210_20261031'
A=T/'E0_NEW210_FORMAL_MEAN_PLANE_FLIGHT_SOURCE_V220_20261101'
B=T/'E0_ACTUAL220_ACTION_CLAMP_NUMERIC_SOURCE_V221_20261101'
def read(p):return json.loads(Path(p).read_bytes())
def put(p,v):
 with Path(p).open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2)
parent=read(A/'reports/ROOT220V2_ORIGINAL_N1_PARENT_CASE_OR_ERROR_RETURNED_ACTUAL.json')
case=parent['original_parent']['result'];diag=read(B/'reports/ROOT221_ACTUAL_NEW_NPZ_ACTION_CLAMP_NUMERIC_RETURNED.json')
assert parent['passed_execution'] is False and case['passed'] and diag['passed']
assert case['controls']==1000 and case['plane_flight_evidence']['candidate_rows']==0
analysis=diag['result']['analysis'];counts=diag['result']['actual_read_counts']
assert counts['physical_file_byte_passes']==counts['np_loads']==1 and all(v==1 for v in counts['member_accesses'].values())
assert analysis['raw_action_channels'][0]['negative_lt_minus6_fraction']==1 and analysis['clip6_reordered_global_max_abs_residual']==0
evidence={}
for row in parent['full_UTF8']:
 if row['path'].endswith(('ACTUAL220_ALL_WAITED_PRIVATE_SHARED_EX_RELEASED.json','ACTUAL220_WAITED_EXIT.json')):
  evidence[Path(row['path']).name]=json.loads(row['UTF8'])
clarification=dict(epoch=time.time(),kind='LOCAL_DERIVED220_221_READER_AND_NUMERIC_HANDOFF',
 original_parent_passed_execution=False,original_parent_error=parent['original_parent']['parent_error'],
 physical_case_result=case,actual_original_wait_and_release=evidence,
 missing_marker='APP220_CLOSED.json absent; original parent failure retained; no replacement marker fabricated',
 shutdown_explanation='Worker source calls real.close and app.close before its marker. Process exit before marker is consistent with observed wait0; SDK fast-shutdown mechanism remains inference.',
 diagnostic221=dict(passed=True,actual_read_counts=counts,raw_action_channels=analysis['raw_action_channels'],
  recorded_action_comparison=analysis['recorded_action_comparison'],clip6_reordered_max_abs_residual=0.,
  actual_leg_q_channels=[r for r in analysis['q_channels']if r['joint']in('left_hip','left_crank','right_hip','right_crank')],
  authored_bottom_reference=analysis['authored_bottom_reference'],root_reference=analysis['root_reference'],commands=analysis['commands']),
 source_model_activation='ELU matches original training runner; source-only check already performed',
 all220_model_and221_NPZ_purposes='CONSUMED; no reexecution or raw/model reopening for stats/Git',
 no_unique_cause_or_population_success_claim=True,no_reward_guard_STD_or_actor_patch_selected=True,
 new_E0_learning_window_started=False,original_E0_reference_immutable=True)
clarification_name='ROOT220_221_ACTUAL_NO_FLIGHT_LEFT_CRANK_CLAMP_AND_PARENT_MARKER_SCOPE.json'
put(A/'reports'/clarification_name,clarification)
work=read(R/'CURRENT_ACTUAL219V3_W35_FIRST_AND_CLOSED210_E0_THREE_HOUR_WORK_ORDER.json')
work['epoch']=time.time();work['E0_210_closed']['actual_jump_skill_not_yet_evaluated']=False
work['source220']['status']='ACTUAL_NEW_N1_CONSUMED_NO_FLIGHT; original parent envelope FALSE retained'
work['actual220_221']=dict(clarification_path=str(A/'reports'/clarification_name),
 model_SHA=case['model_SHA'],model_iteration=32341,physical_controls=1000,physics_callbacks=8000,
 seconds=20.,terminal_flags=case['terminal_flags'],flight_status='NOT_OBSERVED',
 common_authored_wheel_bottom_peak_m=analysis['authored_bottom_reference']['common_authored_collision_bottom_peak_m'],
 left_crank_raw_range=[analysis['raw_action_channels'][0]['raw_min'],analysis['raw_action_channels'][0]['raw_max']],
 left_crank_negative_saturation_fraction=1.,executed_left_crank_action=-6.,
 other5_channels_abs_gt6_fraction=[r['raw_abs_gt6_fraction']for r in analysis['raw_action_channels'][1:]],
 clip6_reorder_residual=0.,original_parent_passed_execution=False,
 no_rerun_or_NEW_E0_learning_selected=True)
work_name='CURRENT_ACTUAL219V3_W35_FIRST_CLOSED210_AND220_221_NO_FLIGHT_CLAMP_WORK_ORDER_V2.json'
put(R/work_name,work)
req=read(R/'AUTOMATION219_ACTUAL_FIRST_CLOSED210_AND220_SOURCE_UPDATE_REQUEST.json')
old=req['prompt'];start=old.index('220源已FROZEN');end=old.index('219原pre-GO失败保留',start)
actual='''CURRENT_ACTUAL220_221_E0_32341_NO_FLIGHT_AND_LEFT_CRANK_CLAMP_20261101。ROOT220V2新N1实际1000controls/8000physics/2000feedback/20s，原time_out ONLY/bad_orientation闭链等全false，但未观察到双轮腾空：两轮force norm<=1N行0/候选0/confirmedrun0。新模型32341/e629...538 GPU必要字节读1/解码1，无CriticWM/optimizer/account写。原JUMP字节一致，yaw0仅controlled eval，实际vx-.3947384/height.1312777，最终yaw偏.7704007rad。common轮心最高.064149m不是离地高度。ROOT221独立冻结新CPU目的实际RC0，唯一NEW220 NPZ865215B/SHA16b81b77577aefe9eccf3a6aa2d70e68e807ac3d4c974ae112d9966d72e73bd4字节1pass/hash同bytes/np.load1/9members各1，模型SDKGPU0/下载0。实际左crank raw范围[-111.477562,-60.967148]，1000/1000controls低于-6，执行reward motor action全程-6；其它5通道超6比例均0。clip6+policy→motor排列[0,1,4,2,3,5]残差0，原训练ELU也同源核对，不是已证明动作顺序/activation错。真实left_hip q约.4915..5000rad，右hip范围.1831..4524，不能把raw值当真实关节瞬变或测得扭矩。common authored轮底peak.0000199303m，几何1000行KNOWN；没有新飞行证据，不单凭训练不足解释。只是一条case饱和证据，不证明唯一原因/整个人群/所有Pi梯度死锁；未选actor/STD/reward/clip/guard修补，不盲续同一E0窗口。原冻结E0本体保持不变。\n220原parent passed_execution=false保留：真实workerwait0/allownOUT/private+sharedEX释放，实际result已完整，但post-app.close的APP220_CLOSED.json未产生导致父reader FileNotFound；SDK fastshutdown只推断，不能伪造marker或改原false。新220原源未执行，ROOTV2仅before-use区分实际nativePlane top0与cuboid top，原rewards/physics没改。新221 fullreport和LOCALclarification并列保存。所有220/221模型/NPZ/physics目的均CONSUMED，不再跑原入口、为统计/Git重开raw/model/重做0PT；以后新目的需新冻结countadmission。没有fresh GUI请求，不显示NPZ/自动重开旧窗口，PPO不能造蓝WM。\n'''
req['prompt']='LATEST_ACTUAL220_221_NO_FLIGHT_CLAMP_NOT_FIXED; W35_219V3_FIRST_PPO_CONTINUES.\nFIRST READ '+str(R/work_name)+' and '+str(A/'reports'/clarification_name)+'; then original219V3 binding/FIRST/GO.\n'+old[:start]+actual+old[end:]
req['prompt']+='\n219归档本次必须包括220与221所有source/原未用入口/原plane解释修复/actual父markerfalse/NPZ一次CPU完整数值与读数、同app新receipt。唯一219phase仍mod4-w35-original-full-rm70-shared-material-400n50-ppo219，ANY219tag已存在即CONSUMED；实际Git refs/index优先。归档后219正常结束只是ordinaryappend，不能重record219。\n'
req_name='AUTOMATION219_ACTUAL220_221_NO_FLIGHT_CLAMP_UPDATE_REQUEST.json';put(R/req_name,req)
roots=[P,N,A,B];metadata={}
binary_ext={'.pt','.pth','.onnx','.npz','.npy','.usd','.usda','.usdc','.stl','.obj','.mtl','.zip','.tar','.gz','.7z','.png','.jpg','.jpeg','.mp4','.avi','.mat','.slx','.jsonl','.bin','.pyc','.pyd','.dll','.hf'}
def scan(v):
 if isinstance(v,dict):
  p=v.get('local_path')or v.get('path');sha=v.get('SHA')or v.get('sha256')
  if isinstance(p,str)and Path(p).is_absolute()and Path(p).suffix.lower()in binary_ext and sha:
   metadata.setdefault(str(Path(p).resolve()).lower(),dict(path=p,SHA=sha,producer='Existing saved source/producer JSON metadata; no binary read for Git'))
  for x in v.values():scan(x)
 elif isinstance(v,list):
  for x in v:scan(x)
for root in roots:
 for p in root.rglob('*.json'):
  try:scan(read(p))
  except(UnicodeDecodeError,json.JSONDecodeError):pass
model=work['E0_210_closed']['source_model'];metadata[str(Path(model['path']).resolve()).lower()]=dict(path=model['path'],SHA=model['SHA'],producer='Original210 normal single-transfer two-host SHA and NEW formal CPU; both consumed')
scope=dict(epoch=time.time(),automation_request_file=req_name,roots=[str(p)for p in roots],
 trials=['210 original three-hour normal and NEW formal CPU; old W35 -9/0PPO retained',
 '219 source and SFTP write-mode before-use repair; old219 V2 pre-GO role refusal/timeout/readonly exit; ROOT219V3 sender repair/native24/fullrestore/new FIRST PPO',
 '220 frozen source; ROOT220V2 native-plane metadata before-use repair; new32341 N1 noflight; original post-App marker readerfalse retained',
 '221 frozen minimal source and synthetic fixtures; actual single NPZ CPU diagnostic with 100% negative left-crank clamp'],
 pending_excluded=['Healthy219 original normal/formal CPU not consumed until signed normal window',
 'Full RM70/E2/E3 skill graduation and complete SuperMimic conversion incomplete',
 'No NEW E0 training/actor repair selected; saturation not unique cause proof','True270 jump/landing/stable not achieved'],
 binary_local_producer_metadata=list(metadata.values()),
 remote_artifacts_metadata_only=[work['actual_first']['first_complete'],case['artifact'],
 dict(path='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_JUMP32066_GROUND10_THREE_HOUR_20261031v210/e0_72/production/model_final_complete.pt',bytes=model['bytes'],SHA=model['SHA'])])
put(R/'CAPTURE219_ACTUAL_FROZEN_SCOPE.json',scope)
note='''# Actual219 W35 full RM70 PPO, closed210 E0 and new220/221 review\n\nW35 now actually passed full20k restoration, native24 and one new PPO update (480000 own transitions), iteration32337/17Adam648380. The original full CAD course has70mm peak-to-trough relief. Shared-material repair preserves geometry, friction sampling and training physics. This is PPO, not complete SuperMimic conversion or RM70 skill graduation. Original source ad504...d3f is retained; selected FIRST a13f...961. GO03:34:32.418197 BJT, save04:34:32.418197, nominal04:39:32.418197, original normal earliest04:24:32.418197.\n\nPreserve original219 source xb mode and before-use wx correction; original actual219V2 sender rejects w35_72 before GO/SDK/model, followed by its natural timeout, no training fee. New219V3 uses the already-authorized original210v2 sender in a new namespace; HMAC, budget and physics retained. All original false reports remain.\n\nE0 completed the requested three-hour210 window with275 new PPO updates/132000000 transitions; iteration32341/17Adam648340, final22961801B/e6291fc50e692b9921dfe8ddcbfcc678e9b5916441229c2fd7a4f2c2cc75a538. Whole CPU259 finite tensors/full actor35/critic38/STD6/17Adam/DR/mixed2000ground+18000literalJUMP state passed, save after requested deadline. Original waits/locks/CNone verified at closure. Independent rawfees10868.937447786331 and failed W352123.434983730316 sum12992.372431516647 once; historical closing416398.6869106293. Original frozen E0 is unchanged.\n\nNew220 controlled yaw0 first-episode test of that new formal completed20s/1000controls/8000physics/2000feedback, only time_out. No sampled double-wheel flight: force-low rows0, candidate0, confirmed runs0. Original JUMP reward remains literal,400N50DR/2.5msTGS32/4/perenv2mm unchanged. Parent envelope remains false because its post-app.close marker is absent; actual workerwait0/allownOUT/private+sharedEX release and physical result are retained separately. No replacement marker or physics rerun. Before-use nativePlane top0 interpretation fix is source metadata, not reward/plant change.\n\nIndependent frozen221 necessary CPU read consumed one byte pass/hash and one np.load of the NEW220 producer NPZ, each of9 selected members once. Left-crank raw action is -111.477562..-60.967148 throughout1000controls and clips to constant-6; other five channels do not exceed6. Executed clip6+motor permutation residual0; ELU matches original training source. Common authored collision-bottom peak is.0000199303m; this is a conditional action-saturation finding, not torque/unique-cause/population evidence. No new E0 learning window or actor/STD/reward/guard repair selected.\n\nAll source fixtures, unused drafts, source/reader errors, full UTF8 receipts, count admissions, app request/receipt and closures are captured. Binary model/raw/NPZ/USD/media are metadata only; no content/hash/model/GPU reads for Git. No new grant/canonical copy/clearactive/second writer. Protect all1504 older tag objects/peels. True270 and full old-expert/SuperMimic graduation remain incomplete.\n'''
with(R/'ACTUAL219_EXPERIMENT_NOTE_WITH_CLOSED210.md').open('x',encoding='utf8')as f:f.write(note)
print(json.dumps(dict(passed=True,local_source_and_saved_metadata_only=True,request=str(R/req_name),workorder=str(R/work_name),roots=len(roots),known_binary_rows=len(metadata))))
