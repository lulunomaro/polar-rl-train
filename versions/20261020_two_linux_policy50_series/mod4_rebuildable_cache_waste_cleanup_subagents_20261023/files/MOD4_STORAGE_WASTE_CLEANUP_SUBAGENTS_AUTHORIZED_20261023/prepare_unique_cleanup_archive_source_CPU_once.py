from pathlib import Path
import ast,hashlib,json,time
K=Path(__file__).resolve().parent;W=K.parent;C=W/'MOD4_WORKSPACE_CLEANUP_AUTHORIZED_20261021_V88';T=W/'MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021';R=K/'reports'
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
src=C/'record_replay39_current_clearance_tuck_reward_v4_and_H1only41_once.py';s=src.read_text('utf8')
s=s.replace("ROOT=G/'versions/20261020_two_linux_policy50_series';NAME=", "ROOT=G/'versions/20261020_two_linux_policy50_series';K=W/'MOD4_STORAGE_WASTE_CLEANUP_SUBAGENTS_AUTHORIZED_20261023';NAME=")
s=s.replace("P=T/'H1_STEP270_REWARD_AIRBORNE_TUCK_V3_RESOURCE_V39_20261023'", "P=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V42_20261023'")
s=s.replace("proof=json.loads((P/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json')", "proof=json.loads((P/'reports/H1_ONLY_COMPLETE_MODEL_ORIGINAL_COST_CPU_ACTUAL.json')")
s=s.replace('H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V41_20261023/reports/H1_ONLY_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_ACTUAL.json','H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V43_20261023/reports/H1_ONLY_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_ACTUAL.json')
s=s.replace("T/'H1_STEP270_REWARD_REPLAY_V2_RESOURCE_V35_20261023',P)", "T/'H1_STEP270_REWARD_REPLAY_V2_RESOURCE_V35_20261023',T/'H1_STEP270_REWARD_AIRBORNE_TUCK_V3_RESOURCE_V39_20261023')")
s=s.replace("diagnostic=T/'H1_STEP270_TUCK_V3_FIRST_CLOSED39_REPLAY_20261023'", 'diagnostic=K')
s=s.replace('S,C):','S,C,K):').replace('S,C) for p in base.rglob','S,C,K) for p in base.rglob')
s=s.replace("kind='replay39_current_clearance_tuck_reward_v4_H1only41'", "kind='human_this_turn_subagents_rebuildable_cache_waste_cleanup'")
s=s.replace('NEXT_ACTUAL_CLOSED39_REPLAY_CURRENT_CLEARANCE_TUCK_V4_H1ONLY41_PPO_WORK_ORDER.json','NEXT_ACTUAL_CURRENT_CLEARANCE_V4_CLOSED42_114_OLD39_41_FOUR_H1ONLY43_PPO_WORK_ORDER.json')
s=s.replace("trial_id='h1-step270-replay39-current-clearance-tuck-reward-v4'", "trial_id='mod4-rebuildable-cache-waste-cleanup-subagents'")
start=s.index(' selected_sources=');end=s.index('\n selected=list(',start)
selected=[R/'HUMAN_THIS_TURN_SUBAGENT_STORAGE_WASTE_CLEANUP_AUTH_ACTUAL.json',R/'HOST210_EXACT_CACHE_CLEANUP_RETURNED_ACTUAL.json',R/'HOST72_EXACT_CACHE_CLEANUP_RETURNED_ACTUAL.json',R/'HOST210_ALL_AUDIT_RAW_TEXT_SHA_AND_ACTION_SET_EXACT_ACTUAL.json',R/'HOST72_ALL_AUDIT_RAW_TEXT_SHA_AND_ACTION_SET_EXACT_ACTUAL.json',R/'local_agent/EXACT_OLD_SHADER_CACHE_COMPLETE_ACTUAL.json',R/'local_agent/EXACT_UV_NATIVE_CACHE_CLEAN_COMPLETE_ACTUAL.json',R/'ALL_ACTUAL_CLEANUP_RECEIPTS_INDEPENDENT_CPU_AND_SPACE_SUMMARY_ACTUAL.json',R/'host210_agent/INDEPENDENT_210_CACHE_ACTIONS_CPU_VERIFIED_ACTUAL.json',R/'host72_agent/INDEPENDENT_72_CACHE_ACTIONS_CPU_VERIFIED_ACTUAL.json']
s=s[:start]+' selected_sources=['+','.join('Path('+repr(str(p))+')' for p in selected)+']'+s[end:]
s=s.replace('New recorded39 replay and near-ground mask gap, existing-runtime clearance reward correction SDK checks, installed H1-only41 GO/positivePPO; all failures retained; no270mm skill claim.','Explicit this-turn cleanup authorization; independent subagent audits; exact rebuildable cache cleanup with raw action receipts, space snapshots and uv native return; protected training sources and all failures retained.')
s=s.replace('Archive current-clearance tuck V4 replay, costs, storage boundaries and H1-only41 handoff','Archive full human-authorized cache waste cleanup, subagent audits, actions and actual space receipts')
needle="put(R/(NAME+'_STARTED_ACTUAL.json'),dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,configuration=cfg,ordinary_followup_no_training_or_ledger_write=True));prior={}"
assert needle in s;s=s.replace(needle,"assert json.loads((K/'reports/ALL_ACTUAL_CLEANUP_RECEIPTS_INDEPENDENT_CPU_AND_SPACE_SUMMARY_ACTUAL.json').read_bytes())['passed']\n "+needle)
ast.parse(s);dest=C/'record_mod4_rebuildable_cache_waste_cleanup_subagents_once.py';assert not dest.exists();dest.write_text(s,encoding='utf8')
put(C/'reports/MOD4_REBUILDABLE_CACHE_WASTE_CLEANUP_SUBAGENTS_ARCHIVE_CONFIG.json',dict(destination='mod4_rebuildable_cache_waste_cleanup_subagents_20261023',base_HEAD='bbc95f8476a79356e8dcf1e432ccb728bfde790f',title='Clean verified rebuildable cache waste after explicit human-requested subagent storage audit'))
put(R/'UNIQUE_CACHE_CLEANUP_ARCHIVE_HELPER_SOURCE_AST_ACTUAL.json',dict(epoch=time.time(),passed_AST_only=True,new_helper=str(dest),source_SHA=hashlib.sha256(dest.read_bytes()).hexdigest(),unique_id='mod4-rebuildable-cache-waste-cleanup-subagents',new_tag='trial-20261023-mod4-rebuildable-cache-waste-cleanup-subagents',expected_old_tags=1426,expected_new_tags=1427,all_new_scope_directory_in_full_capture=True,not_executed_yet=True))
print(json.dumps(dict(prepared=True,no_record_yet=True,helper=str(dest))))
