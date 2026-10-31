"""Answer exact-reward question from source and saved runtime receipts, no new rollout."""
from pathlib import Path
import hashlib,json,time,tomllib
B=Path(__file__).resolve().parent;T=B.parent;R=B/'reports'
E=T/'E0_82_LITERAL_FUDAN_JUMP72_ONE_HOUR_SOURCE_V198_20261031'
N=T/'FUDAN_JUMP_PARALLEL_SINGLE_WRITER_HANDOFF_V197_20261031'
P=T/'JUMP_E0_FINAL32066_HEADLESS_SAME_PLANE_V201_20261031_V2';PR=P/'reports'
def read(p):return json.loads(Path(p).read_bytes())
def put(p,v):
    with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False)
em=read(E/'PACKAGE198_MANIFEST.json');pm=read(N/'PRIMARY197_COMPLETE_MANIFEST.json')
sources=[]
for name in ('literal_original_methods.py','literal_original_config.py'):
    a=next(x for x in em['files'] if x['relative']==name)
    b=next(x for x in pm['files'] if x['relative']==name)
    raw=(E/a['local_relative']).read_bytes();sha=hashlib.sha256(raw).hexdigest()
    assert sha==a['SHA']==b['SHA'] and len(raw)==a['bytes']==b['bytes']
    sources.append(dict(name=name,bytes=len(raw),SHA=sha,actual_E0_package_and_primary_pinned_package_byte_equal=True,
        path=str(E/a['local_relative']),source_content_reads=1))
cpu=read(T/'FUDAN_JUMP_LITERAL_PLANE_400N50_DR_TWO_HOUR_V194_20261031/reports/ROOT194_NEW_LITERAL_JUMP50_SOURCE_CPU_ACTUAL.json')
assert cpu['passed'] and cpu['groups'][0]['name']=='literal19methods_and_full_reward_config_text' and cpu['groups'][0]['passed']
traincapture=read(N/'reports/ROOT197_NORMAL900_E0_72_FULL_UTF8_AND_FORMAL_ACTUAL.json')
row=next(x for x in traincapture['full_UTF8'] if x['path'].endswith('/ACTUAL_SOURCE198_LITERAL_REWARD_AND_TARGET_PLANT_BEFORE_ACTION.json'))
train=json.loads(row['UTF8'])
ev=read(PR/'ROOT201V2_ORIGINAL_TARGET_FROZEN_EVAL_RETURNED_ACTUAL.json')
evalrow=next(x for x in ev['full_UTF8'] if x['path'].endswith('/ACTUAL201_LITERAL_JUMP_PLANE_BEFORE_MODEL.json'))
evaluation=json.loads(evalrow['UTF8'])
assert train['literal_reward_functions']==evaluation['literal_reward_names']
assert train['original_reward_scales_per_second']==evaluation['original_weights_per_second']
assert train['original_clip_single_reward']==evaluation['original_clip_single']==2.5
assert train['original_total_positive_clip']==evaluation['original_total_positive_clip']==False
assert train['outer_SDK_dt_cancelled_only'] and train['measured_mapping']['source_original_methods_unchanged']
assert evaluation['binding']['original_contact_filter_and_base_air_time_preserved_across_reset']
audit=dict(epoch=time.time(),human_exact='e0支线走的是纯复旦的跳跃奖励函数吗？没乱改什么东西吧',
    model='Separate trained E0 jump branch32066 /not overwritten frozen E0_82',
    pinned_commit='8204e853dfd2ed06d85a322e1a998c3d20a3be2c',pinned_snapshot='jump/wheel_legged_gym/envs/base/legged_robot.py',
    source_19_methods_and_entire_reward_config_literal=True,source=sources,
    original19_methods=cpu['groups'][0]['methods'],original_source_CPU_receipt='ROOT194_NEW_LITERAL_JUMP50_SOURCE_CPU_ACTUAL.json, already consumed, not rerun',
    original16scales=evalrow and evaluation['original_weights_per_second'],
    actual_training_receipt_path=row['path'],actual_training_receipt_SHA=row['SHA'],
    actual20k_training_and_N1_eval_reward_names_scales_clip_equal=True,
    original_clip_single=2.5,total_positive_clip=False,original_stateful_flight_and_contact_memory=True,
    source_reward_formula_weights_no_extra_custom_JUMP_terms=True,
    external_total_plan_adaptation=dict(robot='MOD4 actual SDK own hip-wheel BODY/contact/state/action mapping',
        gas='nominal400N engineeringk2000',policy_Hz=50,feedback_Hz=100,physics_dt=.0025,TGS=[32,4],DR='D0white_v3 D1-D7',
        self_dt=.02,outer_Lab_extra_dt_cancelled_only=True,physical_guard='OriginalMOD4 perenv2mm/mimic.01 unchanged, not foreignFudantermination'),
    original_E0_file_frozen_and_separate=True,
    current32066_training_mix='Completed prior round was100percentJUMP, no extra flat reward mixed into this round',
    new202_mix='Future90percentJUMP10percentoriginalE0ground is spec only; originalJUMPreward stays separate/unchanged',
    numeric201V1_eval_script_failure='Before model/actions, unchanged training reward files; NEWV2 corrected version-substitution error',
    checkpoint_raw_NPZ_SDK_GPU_remote_reads_for_this_audit=0,old_CPU_or_GPU_purpose_not_replayed=True)
put(R/'ACTUAL204_E0_BRANCH_LITERAL_JUMP_REWARD_SOURCE_AND_RUNTIME_AUDIT.json',audit)
start=read(B/'VISIBLE_MUJOCO203_ACTUAL_V2/DISPLAY203_WINDOW_STARTED_ACTUAL.json')
exit_=read(B/'VISIBLE_MUJOCO203_ACTUAL_V2/DISPLAY203_WINDOW_EXIT_ACTUAL.json')
mapping=read(B/'VISIBLE_MUJOCO203_ACTUAL_V2/DISPLAY203_SINGLE_PASS_POSE_MAPPING_ACTUAL.json')
assert start['pid']==40848 and start['model_iteration']==32066 and mapping['raw_visual_byte_opens']==1
view=dict(epoch=time.time(),human_exact='e0分支的mujoco播放给我看',
    actual_window_start=start,actual_window_exit=exit_,actual_visual_mapping=mapping,
    closed_now=True,no_autoreopen_or_kill=True,
    local_render_frame_native_vision_verified=True,
    render_observed='E0 JUMP BRANCH CLOSED TRAINING /FINALPPO32066/NEW203VIEWof201CASE; truegrayMOD4/plane/400N50/JUMP19 source labelled',
    native_live_window_screenshot_not_obtained=True,
    UI_receipts=['First UI list call error sky is not defined; initialized existing ComputerUse module, no app action',
        'Fresh app inventory returned0 matchingE0 windows; original exitreceipt shows ownwindowclosed after20.2423713s, no reopen',
        'Root directly inspected original localrenderinitial PNG, not an invented current-window screenshot'],
    primary200_window_not_queried_or_modified=True,
    selected201_pose_first_visual_bytepass=1,old_primary_raw_model_reads=0,new_neural_or_physics_calls=0)
put(R/'CURRENT_ACTUAL203_E0_BRANCH_VIEW_EXIT_AND204_LITERAL_REWARD_PROOF.json',view)
a=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
req=read(PR/'AUTOMATION201_E0_ACTUAL_AND_FROZEN_BASE_MIX202_UPDATE_REQUEST.json')
prefix=f'''CURRENT_ACTUAL203_USER_E0_VIEW_CLOSED_AND204_LITERAL_REWARD_CONFIRMED_20261031: FIRST READ {R.as_posix()}/CURRENT_ACTUAL203_E0_BRANCH_VIEW_EXIT_AND204_LITERAL_REWARD_PROOF.json and ACTUAL204_E0_BRANCH_LITERAL_JUMP_REWARD_SOURCE_AND_RUNTIME_AUDIT.json then201/202spec. Human freshlyaskedE0MuJoCo, soNEW203 displayedalready-produced201 E0branch32066 artifact, notprimary5367. One firstlocal201NPZbytepass/integrity/eachmember1 CONSUMED; no newGPU/model/physics/SSH. Actualvisible40848/create1793458645.4389153/277meshes31bodies thenownwindowEXITafter20.2423713s; don'tautoquery/reopen/replay/kill. InitialrenderPNGlabeledE0final32066 wasdirectlynativelyinspected, butno liveSkywindowframe captured: firstskyundefinedsessionfixedbyinit, laterinventory0targetswithactualexitretained. Do notfakeUIcurrentalive/nativewindowscreenshot. Primary65960notqueriedormodified. OriginallegacyPNGfilenameLATEST188 isbasenameonly; actualSHA/title/model32066proved.
Humanthenasked“e0支线走的是纯复旦的跳跃奖励函数吗？没乱改什么东西吧”。ROOT204 local-source/saved-runtimeaudit(0model/raw/SDK/GPU/remote) confirmedE0package methodSHA514822b6d86c02bb7501d04a2c63c04b46e3b0aac07e1de204111b70b42ac244/8959B andconfigSHA8d3403cfeff086966e736332e42db54c13124761a96b6d23fbdca8caf7b8ccd7/3456B equalpinnedprimarypackage; consumed194CPUproof19method/fullconfigtextPASS notrerun. Actual20ktraining198 BEFORE_ACTION andnew201N1evaluation16names/scales/clip2.5/no totalpositiveclip/contactflightmemoryreadbackmatch. Rewardformulas/weightsremainliteral pinnedFudanJUMP19/config16, externalMOD4stategeometry/400N50DR/SDKdtadaptation explicit; don'tcallentireforeignFudanenvunchanged. FrozenoriginalE0model notoverwritten. Completed32066round was100percentJUMP; future20290/10 groundmix notstarted, JUMPfunctionnotaddwalkingterms. UserlatestfrozenE0+smallground requirementbelowdominatesnexttraining. 203/204 source/display/audit+originalUIerrors/exit arepartofnewactual201 initialarchive ifunused, otherwiseordinary201appendonly/no203/204GPUtag. Existing201NPZvisualpurpose nowCONSUMED; neverreopenforstats/Git.\n\n'''
req['prompt']=prefix+req['prompt']
put(PR/'AUTOMATION201_203_204_FINAL_E0_AND_FROZEN_MIX202_UPDATE_REQUEST.json',req)
print(json.dumps(dict(passed=True,literal_JUMP_source_and_actual_runtime_confirmed=True,E0_viewer_closed=True,raw_model_reads=0)))
