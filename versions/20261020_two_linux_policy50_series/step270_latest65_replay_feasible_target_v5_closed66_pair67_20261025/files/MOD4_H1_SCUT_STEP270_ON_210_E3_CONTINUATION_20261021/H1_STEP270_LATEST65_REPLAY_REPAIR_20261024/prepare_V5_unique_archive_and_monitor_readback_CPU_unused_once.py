from pathlib import Path
import ast,hashlib,json,re,subprocess,time,tomllib
S=Path(__file__).resolve().parent;T=S.parent;W=T.parent;C=W/'MOD4_WORKSPACE_CLEANUP_AUTHORIZED_20261021_V88';R=S/'reports';G=W/'polar-rl-train'
old=C/'archive_closed65_listener66V2_unique_once.py';new=C/'archive_latest65_replay_feasible_reward_closed66_pair67_unique_once.py'
a=old.read_text('utf8')
changes={'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V65_20261024':'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V66_LISTENER_V2_20261024','H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V66_LISTENER_V2_20261024':'H1_STEP270_REWARD_AIRBORNE_FEASIBLE_V5_RESOURCE_V67_20261025','NEXT_ACTUAL_CURRENT_CLEARANCE_V4_CLOSED65_118_75_CURRENT65_OLD63_PEER_PAIR66_LISTENER_V2_BOTH_PPO_WORK_ORDER.json':'NEXT_ACTUAL_AIRBORNE_FEASIBLE_V5_CLOSED66_118_76_CURRENT66_OLD26_30_PEER_PAIR67_BOTH_PPO_WORK_ORDER.json','V4_closed65_118_75PPO_current65_old63_pair66_listenerV2_bothPPO':'V5_latest65_replay_closed66_118_76_current66_old26_30_pair67_bothPPO'}
pattern=re.compile('|'.join(re.escape(x) for x in sorted(changes,key=len,reverse=True)));a=pattern.sub(lambda m:changes[m[0]],a)
a=a.replace("ID='mod4-owner-listener-ready-pair66v2';TAG='trial-20261024-'+ID","ID='mod4-step270-airborne-feasible-target-replay-v5';TAG='trial-20261025-'+ID")
a=a.replace("record_rel='history/experiments/20261024-'+ID", "record_rel='history/experiments/20261025-'+ID")
a=a.replace("len(tags.splitlines())==1432","len(tags.splitlines())==1433").replace("len(git('tag','--list').splitlines())==1433","len(git('tag','--list').splitlines())==1434").replace('total_tags=1433','total_tags=1434').replace('all1432_old_tag_objects_and_peels_unchanged','all1433_old_tag_objects_and_peels_unchanged')
a=a.replace('LISTENER66V2_UNIQUE_STAGE_NOTE.md','V5_REPLAY_FEASIBLE_TARGET_UNIQUE_STAGE_NOTE.md')
a=a.replace('unique_listener_repair_no_training_or_ledger_write','unique_replay_reward_archive_no_training_or_ledger_write').replace('unique_listener_readiness_repair_stage','unique_airborne_feasible_target_repair_stage').replace('unique_listener_repair_recorded_once','unique_airborne_feasible_target_repair_recorded_once')
a=a.replace('Original66 owner unregistered expiry, both-host allout and canonical unchanged; three synthetic listener clock CPU cases; actual66V2 two GO and first PPO, no policy/physics change.','Latest65 saved controls only: measured clearance/edge timing and airborne crank saturation; V5 reward-only local and installed SDK CPU; latest66 full-state sources and original cost; actual67 paired GO/positive PPO/new reward table; no command/action/PPO/physics or budget change.')
needle=" sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact"
insert=""" replay=T/'H1_STEP270_LATEST65_REPLAY_REPAIR_20261024'
 def artifact_rows(v):
  if isinstance(v,dict):
   if v.get('path') and v.get('SHA') and isinstance(v.get('bytes'),int):yield v
   for child in v.values():yield from artifact_rows(child)
  elif isinstance(v,list):
   for child in v:yield from artifact_rows(child)
 for report in (replay/'reports').glob('*.json'):
  for row in artifact_rows(json.loads(report.read_bytes())):
   p=Path(row['path'])
   if p.is_absolute() and p.is_file():known[str(p.resolve())]=row['SHA']
"""
assert a.count(needle)==1;a=a.replace(needle,insert+needle)
assert 'read_capture_index' in a and "TAG='trial-20261025-'+ID" in a;ast.parse(a)
with new.open('x',encoding='utf8') as f:f.write(a)
base=subprocess.check_output(['git','-C',str(G),'rev-parse','HEAD'],text=True).strip();assert base=='c277a4ffff276079ac292dc528046c4d7cba2dc0'
cfg=dict(destination='step270_latest65_replay_feasible_target_v5_closed66_pair67_20261025',base_HEAD=base,title='Repair airborne infeasible leg-target reward after saved step270 replay; continue latest66 pair67')
with (C/'reports/V5_REPLAY_FEASIBLE_TARGET_UNIQUE_CONFIG.json').open('x',encoding='utf8') as f:json.dump(cfg,f,ensure_ascii=False,indent=2)
note="""# MOD4 step270 saved replay and airborne feasible-target reward V5

Human request: 继续看回放修复上台阶; 继续. This authorizes saved-data diagnosis and a reward-only repair at a safe boundary; no local agent inference/physics rollout or active training hotpatch.

Latest65's retained prefixes116/117 (48 controls, .48s, 20k environments) were read once on host72 and reduced to97 selected cases. Reconstruction uses unchanged authored USD kinematics, not new physics integration or frozen FINAL policy evaluation. Env9908 clears270mm at a front gap of233.75mm but reaches the near-edge region after descending. Selected paid-tuck frames retain median body-to-wheel lengths447.6/447.3mm; left/right raw crank inputs exceed clip6 in77.16/72.81 percent. The original tuck reward formula matches reconstructed recorded contributions within5.4e-7; it was computing.

V5 adds only a-.05 measured-airborne infeasible delayed-leg-target cost. It reads actual delayed raw actions/scale/default offset and the original authored joint/CAD difference bounds; the feasible reference is used only for reward. No action projection, command, actor inputs, mesh/physics, runtime0ec7, PPO/STD/17Adam, save/accounting or strict270mm contact+200callback goal changes. Original tuck1.7/.22 and all old V4 reward AST are retained. Local vectorized20k float32 cases and actual installed SDK RewardManager.compute pass. Original local filename/schema/import errors and the first in-place synthetic backward failure are preserved with new unused corrected variants, not relabelled pass.

Current66_LISTENER_V2 closed both full models: H1 update118/Adam787640 SHA7abb4d219d68229a380d68c382bb2046a5b08ae1e8597abad60bf6b23b5afb24; E3 update76/Adam835700 SHA20f8dd5024564238ddb6899a477063fbe84a207ebe632e6cb59faefc888ffaef. Whole-model CPU, original independent fees sum7284.433926343918s and allout pass. Closure remaining780246.4296452999 is a snapshot, not a new ledger. Total remains2268000s630h/nine extensions; no extra grant/refund/second writer or guard reduction.

Current66's three NPZ alone failed capacity planning with no target/controller. Fresh joint selection moved only five necessary complete originals:66's0/116/117, old26's117 and old30's117. Producer/source/target full SHA, inode/mtime and signed acknowledgements precede removal of true source duplicates; all sender/receivers exit. All FINAL/preupdate/PT/source/errors/logs stay preserved. Original25GiB gate passed again after actual67 payload copy.

New namespace H1_STEP270_REWARD_AIRBORNE_FEASIBLE_V5_RESOURCE_V67_20261025 / remote H1step270_reward_airfeasible5_2510v67 uses only latest complete66 sources and unchanged original owner. Both actualGO/first positivePPO/UUID/exe argv/create and new-.05 live reward table pass. This is not full-window, future FINAL, all tensor change, skill graduation or proof the repair enables the step. Future68 is source-only; after67 full close/CPU/health/original fees, analyze its new saved replay before selecting the next continuation. Legacy unused plain67 V4 remains intact.

All original trial tags/objects/peels and failed/unused sources are preserved. This stage uses one new repair record/tag; subsequent reports append ordinary commits. Binary originals are indexed by actual path/size/existing producer SHA, with no Git-driven PT/raw/USD rehash. PostGit checks remain tool receipts.
"""
with (C/'reports/V5_REPLAY_FEASIBLE_TARGET_UNIQUE_STAGE_NOTE.md').open('x',encoding='utf8') as f:f.write(note)
# Verify saved monitor against the exact app update payload; no terminal LF.
args=json.loads((R/'CURRENT67_AIRBORNE_FEASIBLE_V5_MONITOR_UPDATE_ARGS_ACTUAL.json').read_bytes());actual=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
assert actual['prompt']==args['prompt'] and not actual['prompt'].endswith('\n') and actual['status']=='ACTIVE' and actual['rrule']==args['rrule']
put=R/'V5_MONITOR_AND_UNIQUE_ARCHIVE_SOURCE_AST_ACTUAL.json'
with put.open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed=True,archive_helper=str(new),archive_helper_SHA=hashlib.sha256(new.read_bytes()).hexdigest(),archive_unique_ID='mod4-step270-airborne-feasible-target-replay-v5',tag_date='20261025',old_tag_count=1433,part_aware_complete_capture_reader=True,monitor_exact_prompt_status_rrule=True,monitor_no_terminal_LF=True,base_HEAD=base,no_hostquery_or_training_write=True),f,indent=2)
print(json.dumps(dict(archive_helper=str(new),base_HEAD=base,old_tags=1433,monitor_passed=True)))

