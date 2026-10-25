"""One real70 continuation trial; preserve prior1441 objects and all preparation history."""
from pathlib import Path
import json,sys,time,tomllib,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports';G=W/'polar-rl-train'
ID='mod4-step270-optimized70-qualified69-continuation'
try:
 engine=T/'MOD4_SAMPLING_THROUGHPUT_OPTIMIZATION_PREPARATION_20261025/archive_current_implementation_and_MOE_preparation_stages_unique_once.py'
 source=engine.read_text('utf8');needle="'t2z':'mod4-whole-moe-rl-t2z-dual4090-preparation'";assert source.count(needle)==1
 source=source.replace(needle,needle+",'optimized70':'"+ID+"'",1)
 needle="nr=(S if kind=='performance' else T/'MOD4_MOE_RL_T2Z_TRANSFER_PAPER_PREPARATION_20261025')/'reports'";assert source.count(needle)==1
 source=source.replace(needle,"nr=T/'H1_STEP270_SAGITTAL_V6A_SAMPLING_OPT_V4_RESOURCE_V70_20261025/reports'",1)
 ns={'__name__':'actual70_archive_engine','__file__':str(engine)};exec(compile(source,str(engine),'exec'),ns)
 git=ns['git'];assert git('rev-parse','HEAD')=='db1b6296d0ee3abf007c4878deb454ce5727df48' and len(git('tag','--list').splitlines())==1441 and not git('status','--porcelain')
 proof=json.loads((R/'PAIR_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json').read_bytes())
 assert proof['passed'] and proof['actual_finite_returned'] and proof['H1_new_step270_actual_GO_and_positive_PPO'] and proof['E3_same50Hz_actual_GO_and_positive_PPO']
 mon=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
 assert mon['prompt']==(R/'CURRENT_ACTUAL70_MONITOR_SOURCE.txt').read_text('utf8') and mon['status']=='ACTIVE' and mon['rrule']=='FREQ=HOURLY;INTERVAL=1' and mon['target_thread_id']=='01a07a2d-9036-7531-a012-692df9f56353'
 prior=G/'versions/20261025_mod4-step270-closed68-handoff-combined69-forwarded-control'
 for p in (prior/'COMPLETE_FILE_CAPTURE_INDEX.json',prior/'ordinary_source70_metadata_closed68_log_baseline/ORDINARY_CAPTURE_INDEX.json',prior/'ordinary_closed69d_full_speed_saved_replay_source70/ORDINARY_CAPTURE_INDEX.json'):ns['prior'](p)
 note='''Human authorized continued real step270 training and sampling acceleration together. Actual70 continues only complete69 H1 130/17Adam793080 SHA73c90c4e2141d9056613f454d3b9e6c76ebd429d6c695823bba97bbd1b09aae4 and E3 80/839020 SHAe535ae3f1cb4a0c63d1d4c83d4a6e609144bf714dc449c1edd23a08c0d276f05. Closed69 original independent fee7268.916699886322s, both original duration-bound flags true and closed remaining734944.3502614498 remain historical snapshots. No account rewrite, refund, second writer or new extension.

Actual installed70 source/SDK/RSL full CPU, postcopy25GiB/start GPU/RAM guards and original valid_ready passed, followed by both actual GO/positivePPO, exact process identities and expected ownGPU UUIDs. First-update evidence is not continuousalive, whole-window health, completeFINAL, new speed or step skill. Both source clone and all runtime/controller/physical contracts retain qualified69, FP32 and V6A sagittalXZ tuck target.22/weight1.7 plus airborne feasibility-.05. Lossless H1 trace/save/fullSHA/retention and E3 fixed-bank geometry cache remain identical. No new reward, actor35/STD17Adam/PPO, physical clocks or270mm crossing/topcontact/.5s stable recovery standards were introduced. Latest qualified source stays complete69 until actual70 closes fully.

The new installed source guardV3 admits normal closed69 source and original cost proof, old actual terminal/childwait/EXIT, same protected runtime/asset inventory and exact prior Python source. The sole worker difference is E3 saved-Adam assertion837420->839020, proved by exact AST substitution and four meaningful negative rejection fixtures; sourceguard role and one metadata validator are explicitly admitted. Original reward/retention/sampling approvals remain byte-identical; new continuation sourceauth is separate. An uninstalledV2 candidate assumed a wrong savedclock filename; local source review corrected it to actual POLICY50_ACTUAL_CLOCK_AND_INHERITANCE.json before any deployment and retained all V2 source/auth/q/manifests as exact historical bytes. This was preinstallation source review, not a failed training run. Actual target original50Hz clock then passed. Previously synthetic metadata and AST-only candidates retain their original limited evidence classification.

The original-pinned forwarded210 route, owner/H1loopback and E3 pinned SSHdirect-tcpip control module/controllers are unchanged. Secrets stay session-memory/stdin; isolated control dependencies remain outside training environment. Unique new transport100 and101 add only exact70 deploy/firstPPO/unused finalcollector basenames. Current original70 writer alone accounts each actualGO->terminal; completion collector retains <=900 gate,3900lifecycle/3600save/300exit and sequential fulltwoFINAL/cost/allout/locks requirements. Whole-model CPU final reviewer is unused. All source-only candidate/prebind history, source snapshots, actual CPU and GO/PPO receipts, and sameACTIVE/hourly originaltarget monitor are retained in full.

Saved69 descriptive replay showed launch height ahead of edge arrival with no crossing/landing in the saved48controls; not whole-window/frozen evaluation. Current70 does not yet demonstrate timing repair or skill qualification. No subagents were spawned. T2-z remains preparation-only with its previously complete singleQ8 visual backbone; no additional downloads, model hash/header probes, cleanup or T2-z training. Old mistakes/false/fee history and every oldtag object/peel remain. Later reports append ordinary commits; do not repeat this trialrecord/tag. PostGit verification remains conversation-only.
'''
 extras=[T/'H1_STEP270_REWARD_PATH_V1_20261022'/('same_authorized_session_compressed_transport_v'+str(i)+'.py') for i in (100,101)]
 ns['run_stage']('optimized70',[N],extras,note,'Continue optimized step270 training70 from complete69 models with exact same-source admission')
except BaseException:
 with (R/('ACTUAL70_UNIQUE_ARCHIVE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),resume_existing_commit_tag_objects_only_no_repeat_record=True),f,indent=2)
 raise
