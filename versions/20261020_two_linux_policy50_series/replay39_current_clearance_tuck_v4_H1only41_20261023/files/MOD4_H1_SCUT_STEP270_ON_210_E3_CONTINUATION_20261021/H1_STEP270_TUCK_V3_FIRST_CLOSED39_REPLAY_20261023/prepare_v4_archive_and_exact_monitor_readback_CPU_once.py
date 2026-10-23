from pathlib import Path
import ast,hashlib,json,time,tomllib
D=Path(__file__).resolve().parent;T=D.parent;W=T.parent;C=W/'MOD4_WORKSPACE_CLEANUP_AUTHORIZED_20261021_V88';R=D/'reports'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
args=json.loads((R/'ACTUAL41_CURRENT_CLEARANCE_TUCK_V4_MONITOR_UPDATE_ARGS_ACTUAL.json').read_bytes())
actual=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
for key in ('name','status','rrule','kind','prompt'):assert actual[key]==args[key],key
assert actual['target_thread_id']==args['targetThreadId'] and actual['id']=='mod4-10'
put(R/'ACTUAL41_CURRENT_CLEARANCE_TUCK_V4_MONITOR_EXACT_READBACK_ACTUAL.json',dict(epoch=time.time(),passed=True,id=actual['id'],status=actual['status'],kind=actual['kind'],targetThreadId=actual['target_thread_id'],rrule=actual['rrule'],prompt_SHA=hashlib.sha256(actual['prompt'].encode()).hexdigest(),exact_prompt_readback=True,no_second_monitor=True))
template=C/'record_replay36_airborne_tuck_reward_v3_and_pair39_once.py';text=template.read_text('utf8')
text=text.replace('"""Copy to a fresh once helper after actual closure and following two-PPO evidence."""','"""Unique V4 archive after closed39 CPU and actual installed H1-only41 PPO."""')
text=text.replace("P=T/'H1_STEP270_REWARD_REPLAY_V2_RESOURCE_V36_20261023'", "P=T/'H1_STEP270_REWARD_AIRBORNE_TUCK_V3_RESOURCE_V39_20261023'")
text=text.replace("B/'H1_STEP270_REWARD_AIRBORNE_TUCK_V3_RESOURCE_V39_20261023/reports/PAIR_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json'", "B/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V41_20261023/reports/H1_ONLY_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_ACTUAL.json'")
text=text.replace("diagnostic=T/'H1_STEP270_LEG_TUCK_REPLAY36_20261023'", "diagnostic=T/'"+D.name+"'")
text=text.replace("kind='replay36_airborne_tuck_reward_v3_actual39'", "kind='replay39_current_clearance_tuck_reward_v4_H1only41'")
text=text.replace('current_paired_actual_GO_PPO_reward_table_reference=active','current_H1_only_actual_GO_PPO_reward_table_reference=active').replace("deferred=['e2']","deferred=['e2','recovery']")
text=text.replace('NEXT_ACTUAL_REPLAY36_TUCK_V3_FAILED38_READER_FIXED_PAIR39_PPO_WORK_ORDER.json','NEXT_ACTUAL_CLOSED39_REPLAY_CURRENT_CLEARANCE_TUCK_V4_H1ONLY41_PPO_WORK_ORDER.json')
text=text.replace("trial_id='h1-step270-replay36-airborne-tuck-reward-v3'", "trial_id='h1-step270-replay39-current-clearance-tuck-reward-v4'")
selected=[
 T/'H1_STEP270_REWARD_AIRBORNE_TUCK_V3_RESOURCE_V39_20261023/reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json',
 T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V41_20261023/reports/H1_FULL_INSTALLED_SOURCE_SDK_RSL_CPU_ACTUAL.json',
 T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V41_20261023/reports/H1_ONLY_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_ACTUAL.json',
 T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V41_20261023/repair_sources/H1_REWARD_CHANGE_AUTH_AND_SOURCE_CPU_ACTUAL.json',
 D/'candidate_clearance_v4/h1_step270_path_reward_v1.py',D/'candidate_clearance_v4/step270_reward_installed_CPU_v1.py',
 R/'V3_FIRST_WINDOW_NEAR_GROUND_TUCK_MASK_GAP_AND_EXISTING_CLEARANCE_SCOPE_ACTUAL.json',R/'CURRENT_CLEARANCE_TUCK_V4_ACTUAL_SDK_CPU_ACTUAL.json',R/'FIRST_CLOSED39_ACTUAL_TUCK_AFTER_REQUEST_AND_KINEMATIC_SCOPE_CPU_ACTUAL.json',R/'RECORDED39_TUCK_NEAR_GROUND_PLOT_CPU_ACTUAL.json',
 T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V41_20261023/reports/NEXT_E3_BOUNDARY_RESOURCE_COMPONENTS_ACTUAL.json',
 T/'reports/NEXT_ACTUAL_CLOSED39_REPLAY_CURRENT_CLEARANCE_TUCK_V4_H1ONLY41_PPO_WORK_ORDER.json']
assert all(p.is_file() for p in selected)
start=text.index(' selected_sources=');end=text.index('\n selected=list(',start)
text=text[:start]+' selected_sources=['+','.join('Path('+repr(str(p))+')' for p in selected)+']'+text[end:]
text=text.replace('Actual new recorded36 replay, bounded airborne tuck SDK checks, failed38 and reader errors preserved, installed39 both GO/positivePPO; no270mm skill claim.','New recorded39 replay and near-ground mask gap, existing-runtime clearance reward correction SDK checks, installed H1-only41 GO/positivePPO; all failures retained; no270mm skill claim.')
text=text.replace('Archive full airborne tuck V3 replay, errors, costs, installed deployment and handoff','Archive current-clearance tuck V4 replay, costs, storage boundaries and H1-only41 handoff')
ast.parse(text)
dest=C/'record_replay39_current_clearance_tuck_reward_v4_and_H1only41_once.py'
assert not dest.exists();dest.write_text(text,encoding='utf8')
cfg=dict(destination='replay39_current_clearance_tuck_v4_H1only41_20261023',base_HEAD='37234bdc0b354054bf37ddb58a0d950dd9617cfb',title='Repair near-ground tuck reward eligibility from H1 closed39 replay; verify installed H1-only41')
put(C/'reports/CURRENT_CLEARANCE_TUCK_V4_H1ONLY41_ARCHIVE_CONFIG.json',cfg)
put(R/'CURRENT_CLEARANCE_TUCK_V4_UNIQUE_ARCHIVE_HELPER_SOURCE_AST_ACTUAL.json',dict(epoch=time.time(),passed_AST_only=True,new_helper=str(dest),helper_SHA=H(dest),original_consumed_V3_helper_not_executed=True,unique_trial_id='h1-step270-replay39-current-clearance-tuck-reward-v4',old_tags_expected=1425,new_tags_expected=1426,selected_sources=[str(p) for p in selected],no_record_executed_yet=True))
print(json.dumps(dict(passed=True,monitor_exact=True,archive_helper_ready=str(dest),not_recorded_yet=True)))
