"""Archive new actual three4090 expert72 stage once; never replay a training helper."""
from pathlib import Path
import json,time,tomllib,traceback
S=Path(__file__).resolve().parent;T=S.parent;W=T.parent;G=W/'polar-rl-train';N=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V72_20261025';R=S/'reports'
engine=T/'MOD4_SAMPLING_THROUGHPUT_OPTIMIZATION_PREPARATION_20261025/archive_current_implementation_and_MOE_preparation_stages_unique_once.py'
source=engine.read_text('utf8')
a="'t2z':'mod4-whole-moe-rl-t2z-dual4090-preparation'";assert source.count(a)==1
source=source.replace(a,a+",'triple72':'mod4-three4090-h1-v7-e2-e3-training72'")
a="nr=(S if kind=='performance' else T/'MOD4_MOE_RL_T2Z_TRANSFER_PAPER_PREPARATION_20261025')/'reports'";assert source.count(a)==1
source=source.replace(a,"nr=T/'MOD4_THREE4090_EXPERT_REACTIVATION_20261025'/'reports'")
a="'--kind','diagnostic'";assert source.count(a)==1;source=source.replace(a,"'--kind','training'")
ns={'__name__':'triple72_archive_utilities_only','__file__':str(engine)}
exec(compile(source,str(engine),'exec'),ns)
git=ns['git']
def main():
 assert git('rev-parse','HEAD')=='155950bb8b80942c62d2f0c9de1dea77af6b64d8' and not git('status','--porcelain')
 assert len(git('tag','--list').splitlines())==1443
 first=json.loads((N/'reports/THREE_EXPERT_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json').read_bytes());assert first['passed'] and first['actual_finite_returned']
 a=tomllib.loads((Path.home()/'.codex/automations/mod4-10/automation.toml').read_text('utf8'));assert a['prompt']==(N/'reports/CURRENT_ACTUAL_THREE4090_H1_V7_E2_E3_MONITOR_SOURCE.txt').read_text('utf8') and a['status']=='ACTIVE' and a['target_thread_id']=='01a07a2d-9036-7531-a012-692df9f56353'
 for p in [G/'versions/20261025_mod4-step270-closed70-http-channel-lifetime-fix71/COMPLETE_FILE_CAPTURE_INDEX.json',G/'versions/20261025_mod4-step270-closed70-http-channel-lifetime-fix71/ordinary_closed71_completion_before_three_gpu/ORDINARY_CAPTURE_INDEX.json',G/'versions/20261025_mod4-step270-optimized70-qualified69-continuation/COMPLETE_FILE_CAPTURE_INDEX.json',G/'versions/20261025_mod4-step270-optimized70-qualified69-continuation/ordinary_closed70_control_failure_saved_replay/ORDINARY_CAPTURE_INDEX.json']:
  ns['prior'](p)
 note="""Human authorized use of all three4090 cards to continue repairing H1 step270 and training other existing experts. New72 now actually runs H1 on the single4090, E2 and E3 on the two distinct cards of host72, with installed source/SDK/RSL/fullstate CPU, after-copy resources, valid_ready, actual GO and each first complete PPO update verified. This is a running snapshot, not final-model or skill graduation.

H1 V7 changes only three recipe literals: version and upward-push reward gate start/full front_x -.05/.15 to .10/.25 with edge.35 unchanged. Early-apex saved cases lose premature push reward; actual installed SDK RewardManager CPU compute passed. No extra actor input, command or physical action was added. V6A sagittal tuck, FP32, PPO, physics and success standard remain unchanged. E2 resumes complete52 through explicit cross-host50Hz typed-source and target SDK CPU admission. H1/E3 resume complete71 only. Original single canonical writer now accepts h1/e2/recovery; independent actual GO-to-terminal charging is unchanged. Three-slot11700reserve and strict remaining86412.86069250107 were applied, no new budget grant, copied ledger, refund or second writer.

Complete71 original writer settled7297.521332502365s, both normal duration flags true, two full finite models and all actor/critic/Adam changes passed, all children/locks/canonical closed; newly collected E3 control-error count0. Complete71 reports are a prior ordinary supplement, not a repeated trial. Source H1 127/Adam798240, E3 80/840840, E2 178/839920 from52; their full producer hashes are in exact bindings. Third GPU startup-empty and original private/shared lock evidence is a bounded snapshot, no unknown-peer identity query or interference.

All new source/controllers/CPU/source guards/auth/bindings/remote installation/GO-PPO/completion-protocol/monitor/overall-plan reports and original local errors are retained. Initial local E2 owner inventory omission was corrected before installation in V2, with exact pre-correction bytes kept. Nonfatal AST backslash-S warnings and local path-reader errors remain distinct from training failures. Full text only; weights, bank and other binaries retain actual paths/bytes/existing producer SHA without rereading content for Git. No consumed once, model/raw/GPU query, training pause or budget change for this archive.

Overall plan remains expert skill completion and acceptance: E0 and W35 frozen within scope, CURB/SLOPE partial, H1/E2/E3 trained but not graduated, low-posture tunnel untrained, independent continuous stairs and extended flight/landing curricula incomplete. Gate148 learns E0/W35 only; full-expert learned routing and T2-z training remain future work. No subagents, no additional model download or automatic T2-z launch.
"""
 extras=[T/'H1_STEP270_REWARD_PATH_V1_20261022'/('same_authorized_session_compressed_transport_v'+str(i)+'.py') for i in range(106,110)]+[engine]
 ns['run_stage']('triple72',[S,N],extras,note,'Train H1 V7, E2 and E3 concurrently on three4090 cards with one original writer')
if __name__=='__main__':
 try:main()
 except BaseException:
  p=R/('ARCHIVE_THREE72_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')
  with p.open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),actual_HEAD=git('rev-parse','HEAD'),resume_existing_objects_if_record_started=True,no_repeat_record_tag_or_training=True),f,ensure_ascii=False,indent=2)
  raise
