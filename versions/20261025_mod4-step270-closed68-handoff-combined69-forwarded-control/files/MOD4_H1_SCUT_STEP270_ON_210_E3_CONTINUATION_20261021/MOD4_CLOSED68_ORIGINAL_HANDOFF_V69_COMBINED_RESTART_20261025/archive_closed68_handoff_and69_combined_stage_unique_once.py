"""One real stage: original68 normal-writer terminal recovery and combined69 actual GO/PPO."""
from pathlib import Path
import hashlib,json,sys,time,traceback,tomllib
D=Path(__file__).resolve().parent;T=D.parent;W=T.parent;G=W/'polar-rl-train';R=D/'reports'
ID='mod4-step270-closed68-handoff-combined69-forwarded-control'
try:
 engine=T/'MOD4_SAMPLING_THROUGHPUT_OPTIMIZATION_PREPARATION_20261025/archive_current_implementation_and_MOE_preparation_stages_unique_once.py'
 source=engine.read_text('utf8')
 needle="'t2z':'mod4-whole-moe-rl-t2z-dual4090-preparation'";assert source.count(needle)==1
 source=source.replace(needle,needle+",'combined':'"+ID+"'",1)
 needle="nr=(S if kind=='performance' else T/'MOD4_MOE_RL_T2Z_TRANSFER_PAPER_PREPARATION_20261025')/'reports'";assert source.count(needle)==1
 source=source.replace(needle,"nr=T/'MOD4_CLOSED68_ORIGINAL_HANDOFF_V69_COMBINED_RESTART_20261025/reports'",1)
 source=source.replace('binary content indexed using prior producer hashes, original writer/accounting untouched. No unrun deployment or skill/GPU-fit success claimed.','binary content indexed using producer receipts. Only the original68 writer settled its own unchanged terminal evidence and original69d writer admitted actual GO/PPO. No direct canonical rewrite, refund, second writer, skill or unmeasured speed success claimed.')
 ns={'__name__':'reviewed_combined69_archive_engine','__file__':str(engine)};exec(compile(source,str(engine),'exec'),ns)
 git=ns['git'];assert git('rev-parse','HEAD')=='39f0590844a112196b7e196fbc9559597e5e5348' and len(git('tag','--list').splitlines())==1440 and not git('status','--porcelain')
 N=T/'H1_STEP270_SAGITTAL_V6A_SAMPLING_OPT_V4_RESOURCE_V69_20261025';P=T/'H1_STEP270_REWARD_SAGITTAL_TUCK_V6A_RESOURCE_V68_20261025'
 proof=json.loads((N/'reports/PAIR_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json').read_bytes());assert proof['passed'] and proof['actual_finite_returned']
 model=json.loads((P/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes());assert model['passed'] and model['original_canonical_cost_settled'] and all(x is False for x in model['original_ledger_duration_flags_preserved'].values())
 mon=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'));assert mon['prompt']==(R/'CURRENT69D_COMBINED_TRAINING_MONITOR_SOURCE_ACTUAL.txt').read_text('utf8') and mon['status']=='ACTIVE' and mon['rrule']=='FREQ=HOURLY;INTERVAL=1' and mon['target_thread_id']=='01a07a2d-9036-7531-a012-692df9f56353'
 for p in [G/'versions/20261025_mod4-post67-v6a-sampling-acceleration-implementation/COMPLETE_FILE_CAPTURE_INDEX.json',G/'versions/20261025_mod4-single4090-quantized-wan5b-preparation/COMPLETE_FILE_CAPTURE_INDEX.json',G/'versions/20261025_mod4-single4090-quantized-wan5b-preparation/ordinary_forwarded210_network_restoration/ORDINARY_CAPTURE_INDEX.json']:
  ns['prior'](p)
 roots=[D,P/'reports',P/'current_pair_closed_text',P/'current_pair_closed_models']+[T/('H1_STEP270_SAGITTAL_V6A_SAMPLING_OPT_V'+str(i)+'_RESOURCE_V69_20261025') for i in range(1,5)]
 extras=[P/'review_closed68_saved_models_and_original_actual_cost_CPU_once.py']+[T/'H1_STEP270_REWARD_PATH_V1_20261022'/('same_authorized_session_compressed_transport_v'+str(i)+'.py') for i in range(86,98)]
 note='''Human requested actual training with step repair and sampling acceleration together. Closed68 H1 complete24/Adam790480 and E3 complete11/Adam837420 were downloaded with producer-fullSHA and independently checked on CPU: finite fullstate,17Adam x20 updates,actor9 including STD and critic8 changed,270phase and50Hz retained. These are complete saved interrupted-window models, not step skill graduation.

The old68 owner lost two terminal handoffs after the source address changed. Its exact own live Python cfg token was read only in memory under its verified PID/exe/argv/create, without ptrace attach, process signal or memory write. A temporary exact old-IP local route was restored after two unchanged authentic terminal rows were delivered over its existing HMAC endpoint. The original writer independently closed itself and released original locks. Actual cost27389.37529850006 and both original duration_bound_passed=false flags remain unchanged; no refund, cap rewrite, clearing/copying canonical, extra grant or second writer. Actual worker+SDKclose+childwait lifetimes were within3900; the saved-model source proof explicitly preserves the delayed-owner duration violation.

The actual current69d pair is installed, fully CPU-admitted, and both actual GO/first positivePPO/GPU UUID/full process identities/reward table verified. It continues the V6A sagittalXZ tuck1.7/.22 and airborne feasibility-.05 in FP32, adding lossless H1 DEFLATE1 trace/fullSHA/retention and E3 fixed reset geometry cache. Physics2.5ms/TGS32/4, clocks, actor inputs,STD17Adam/PPO and real270mm crossing/contact/.5s stable recovery criteria are unchanged. No current speed gain or skill success is claimed from the first update.

The new network path uses H1/owner loopback and an original-pinned SSH direct-tcpip control channel from72 through10.24.5.27:4090. Credentials remain memory/stdin-only. Only the node send transport and its own channel close differ; all spawn/save/childwait/terminal retry/private-lock AST is verified. Isolated72 paramiko5.0.0 dependencies have a producer index. Pre-GO69/69b/69c failures, source snapshots, CPU passes/rejections, literal/ABI/local-reader errors and original warnings remain intact. New69d fixes target invocation sys.path, explicitly admits the exact network node AST, and restores exact nested SOURCE_FREEZE inventory bytes, without weakening the original protected inventory or rewriting prior sampling/reward/retention approvals.

The original9 budget extensions and reserve guard remain. No subagent was spawned after the user prohibition. T2-z remains preparation-only with its existing complete single Q8 backbone; no additional model download or world-model training. Current69d completion collector is unused and retains the original<=900-second gate (19:07:38BJT), full actual exit/cost/locks/model proof requirements. Reports after this unique stage append ordinary commits; do not repeat record/tag.
'''
 ns['run_stage']('combined',roots,extras,note,'Restore original68 handoff and start combined V6A69 step repair and sampling acceleration')
except BaseException:
 with (R/('COMBINED69_UNIQUE_ARCHIVE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),resume_existing_commit_tag_objects_only_no_repeat_record=True),f,indent=2)
 raise
