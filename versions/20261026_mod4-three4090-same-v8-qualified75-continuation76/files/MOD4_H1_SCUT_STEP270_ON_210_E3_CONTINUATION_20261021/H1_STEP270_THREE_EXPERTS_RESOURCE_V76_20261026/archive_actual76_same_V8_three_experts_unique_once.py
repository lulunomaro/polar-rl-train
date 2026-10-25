"""Unique actual76 training stage; original75 closure is an already committed ordinary supplement."""
from pathlib import Path
import json, time, tomllib, traceback

N=Path(__file__).resolve().parent; T=N.parent; W=T.parent; G=W/'polar-rl-train'; R=N/'reports'
P=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V75_20261026'
engine=T/'MOD4_SAMPLING_THROUGHPUT_OPTIMIZATION_PREPARATION_20261025/archive_current_implementation_and_MOE_preparation_stages_unique_once.py'
s=engine.read_text('utf8')
def patch(old,new):
    global s
    assert s.count(old)==1,old
    s=s.replace(old,new,1)
patch("'t2z':'mod4-whole-moe-rl-t2z-dual4090-preparation'", "'t2z':'mod4-whole-moe-rl-t2z-dual4090-preparation','stage76':'mod4-three4090-same-v8-qualified75-continuation76'")
patch("nr=(S if kind=='performance' else T/'MOD4_MOE_RL_T2Z_TRANSFER_PAPER_PREPARATION_20261025')/'reports'", "nr=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V76_20261026'/'reports'")
patch("TAG='trial-20261025-'+ID;D=G/('versions/20261025_'+ID)", "TAG='trial-20261026-'+ID;D=G/('versions/20261026_'+ID)")
patch("'--kind','diagnostic'", "'--kind','training'")
ns={'__name__':'archive76_utilities_only','__file__':str(engine)}
exec(compile(s,str(engine),'exec'),ns); git=ns['git']

def main():
    assert git('rev-parse','HEAD')=='bc50796563b302ac0cf064bec8051dae45bdac0e'
    assert len(git('tag','--list').splitlines())==1447 and not git('status','--porcelain')
    first=json.loads((R/'THREE_EXPERT_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json').read_bytes())
    assert first['passed'] and first['actual_finite_returned'] and first['all_three_actual_GO_and_positive_PPO']
    assert first['H1_V8_sampled_excess_reward_and_original_success_standard']
    cpu=json.loads((R/'H1_FULL_INSTALLED_SOURCE_SDK_RSL_CPU_ACTUAL.json').read_bytes())
    assert cpu['new_reward_integration_CPU']['actual_installed_sampled_excess_SDK_compute_tested']
    assert cpu['sampling_acceleration_CPU']['V8_reward_publication_AST']['passed']
    proof=json.loads((P/'reports/THREE_EXPERT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes())
    assert proof['passed'] and proof['all_owner_nodes_children_actual_out'] and proof['original_canonical_cost_settled']
    a=tomllib.loads((Path.home()/'.codex/automations/mod4-10/automation.toml').read_text('utf8'))
    assert a['prompt']==(R/'CURRENT_ACTUAL76_THREE4090_SAME_V8_MONITOR_SOURCE.txt').read_text('utf8')
    assert a['status']=='ACTIVE' and a['target_thread_id']=='01a07a2d-9036-7531-a012-692df9f56353'
    for p in [G/'versions/20261026_mod4-three4090-h1-sampled-leg-excess-v8-training75/COMPLETE_FILE_CAPTURE_INDEX.json',
              G/'versions/20261026_mod4-three4090-h1-sampled-leg-excess-v8-training75/ordinary_closed75_models_cost_saved_motion/ORDINARY_CAPTURE_INDEX.json']:
        ns['prior'](p)
    note='Continue H1 step270, E2 world-moving and E3 recovery on all three4090 cards from complete75. H1 132/Adam808760 SHA35bdf98b54352bc16a2a15faea2813bb6ae9f3c23e2c1ecd298df56c2617b251, E2 88/846900 SHAba5f7daee60f9a67e1cf8cb60136218135915dc278cd657c9f8c9dc8767e9a6c, E3 83/847500 SHA31ff232abe7d791967b1afb47228a2608ee5697e05e0d3a26eb20639b56b1c2a passed full twohostSHA, finite wholeCPU17Adam x20, actor9 inclsixSTD/critic8 changes,270phase and50Hz checks. Three normal originalduration flags true, originalwriter sumonce10912.09224820137s and closed snapshot679427.3249001503. Allownprocesses/children/canonical/locks actually closed. Closed75 originals and saved-only diagnostics already ordinary-committed in bc50796563b302ac0cf064bec8051dae45bdac0e, not a repeated trial.\n\n75 actual V8 reward scalar is nonzero and matches saved raw sample formula within1.862645149230957e-9; executed actions remain exactlyclip(raw,-6,6). This is actual runtime evidence, not a matched-cohort learning gain. New saved48controls across20k have389 takeoff increments,2342 recorded bothcrossed envframes, landing/recovery0;95 selected cases include noreset takeoff and recordedcrossed examples with sufficient AABB height but no stable topcontact/recovery. FINALcurrent-retainedepisodes42crossedenvs, landing/recovery/success0 are not wholewindow/frozen evaluation. New E3 current-retainedepisode diagnostic was added during the original initial model read, without a second checkpoint read or new gate: creditedfallen0 and maxstable8 vs original50feedbacktick criterion, not wholewindow failure. E2/E3 logged Metrics/success_rate denotes commandvelocity tracking, not expert graduation. Original per-env closure resets remain unchanged.\n\nNew76 strictly retains actual V8 reward/trace/checkers and original actor35/sixSTD/17Adam/PPO/DR/commands/physical2.5ms/TGS32/4/save/success standards. It adds a narrow same-V8 source guard, requiring exact rootPython exceptguardrole and exact E3 sourceAdam assertion; the four H1 V8 files are no longer migration allowances.14 clearly synthetic inventory/AST cases do not replace actual source admission. New76 passed installed source/SDK/RSL/fullCPU, actual payload-after-copy25GiB/GPU/RAM, original valid_ready, allthreeGO and each firstcompletePPO, exact UUID/process identity, and H1 existing traceindex V8term and Taskrecipe. E2 installer only exact76/75 owned namespace literals differ; original copyloop and producer/source closure/private/shared guards preserved. The original helper assertion returns reward_migration true to false; original valid_ready unchanged. All current76 originalwriter fees remain pending, earlysaves not latestqualified FINALs.\n\nAll actual source histories, reports, nonfatal backslash-S warnings and original localreader errors are preserved. Source-only76 preparation, saved75 reader additions, local stdout formatter SyntaxError and overbroad numericfilename discovery/truncation were archived in75 ordinary supplement; no training failure is inferred from those reader issues. Budget2268000/9,86412.86069250107 strict three-slot guard and single original canonical writer remain; no refund/grant/copiedledger/clearactive/secondwriter/oldonce replay. No subagents or automatic T2-z training. Existing hourly monitor updated to actual76 schedule and quiet unless meaningful. Binary originals only indexed by realpath/bytes/priorproducerSHA, no binary read/hash for Git. One unique actual76 stage, later additions ordinary only.\n'
    ns['run_stage']('stage76',[N],[T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v118.py',engine],note,'Continue three experts from complete75 with the same H1 V8 and sampling acceleration')

if __name__=='__main__':
    try:main()
    except BaseException:
        with (R/('ARCHIVE76_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:
            json.dump(dict(epoch=time.time(),error=traceback.format_exc(),actual_HEAD=git('rev-parse','HEAD'),resume_existing_objects_if_record_started=True,no_repeated_record_tag_or_training=True),f,ensure_ascii=False,indent=2)
        raise
